import json
import os
from typing import Literal

from jinja2 import Environment, FileSystemLoader

from runcodeeval import data, ROOT_DIR
from runcodeeval import logger as log

env = Environment(loader=FileSystemLoader("runcodeeval/templates"))

import signal


# Define NoCompletion error
class NoCompletionError(Exception):
    pass


# Define the timeout error
class TimeoutError(Exception):
    pass


# Define the function to be called on timeout
def handler(signum, frame):
    raise TimeoutError("Function execution took longer than 1 minute")


# Set the signal handler
signal.signal(signal.SIGALRM, handler)


def get_template_name(benchmark: dict) -> str:
    if benchmark["object"] == "class":
        return "class_test.tpl"
    elif benchmark["object"] == "function":
        return "function_test.tpl"
    elif benchmark["object"] == "text":
        return "text_test.tpl"
    else:
        raise ValueError(f"Invalid object type for {benchmark}")


def render_template(
    candidate: dict, benchmark: dict, model_name: str, out_dir: str, debug: bool = False
) -> str:
    template = env.get_template(get_template_name(benchmark))
    test_cases = eval(benchmark["tests"])

    if not candidate["solution"]:
        raise NoCompletionError("Candidate solution is empty")

    render_params = {
        "model_name": model_name,
        "task_id": candidate["task_id"],
        "generated_code_string": candidate["solution"],
        "test_cases": test_cases,
        "out_dir": out_dir,
    }
    if "name" in benchmark.keys():
        render_params["object_name"] = benchmark["name"]
    return template.render(**render_params)


def execute_template(content: str, task_id: str, model_name: str, out_dir: str) -> dict:
    res = {}
    signal.alarm(60)  # Set the timeout
    try:
        exec(content, locals())
    except NameError:
        log.error(f"NameError in {task_id}")
        res.update({"model_name": model_name, "task_id": task_id, "error": "NameError"})
    except SyntaxError:
        log.error(f"SyntaxError in {task_id}")
        res.update({"model_name": model_name, "task_id": task_id, "error": "SyntaxError"})
    except TimeoutError:
        log.error(f"TimeoutError in {task_id}")
        res.update({"model_name": model_name, "task_id": task_id, "error": "TimeoutError"})
    except Exception as e:
        log.error(f"Error in {task_id}\n{e}")
        res.update({"model_name": model_name, "task_id": task_id, "error": "Error"})
    else:
        with open(f"{out_dir}/_result_{task_id}.txt", "r") as f:
            res = json.load(f)
        os.remove(f"{out_dir}/_result_{task_id}.txt")
    finally:
        signal.alarm(0)
    return res


def run_functional_test(
    candidate: dict, benchmark: dict, model_name: str, out_dir: str, debug: bool = False
):
    log.info(f"Testing {candidate['task_id']}")
    template = env.get_template(get_template_name(benchmark))
    test_cases = eval(benchmark["tests"])
    try:
        content = render_template(candidate, benchmark, model_name, out_dir, debug=debug)
    except NoCompletionError:
        log.info(f"No completion for {candidate['task_id']}")
        return {
            "model_name": model_name,
            "task_id": candidate["task_id"],
            "error": "NoCompletionError",
        }
    if debug:
        log.info(content)
    res = execute_template(content, candidate["task_id"], model_name, out_dir)
    return res


def functional_test_one(
    task_id: str, generated_file: str, benchmark_file: str, model_name, debug: bool = True
):
    candidates = data.stream_jsonl(generated_file)
    for candidate in candidates:
        if candidate["task_id"] == task_id:
            break
    else:
        raise ValueError("Given task id not found in generated file")

    benchmarks = data.jsonl_to_dict(benchmark_file)
    benchmarks = {
        k: v
        for k, v in benchmarks.items()
        if "tests" in v.keys() and v["object"] in ["function", "class", "text"]
    }
    if task_id not in benchmarks.keys():
        raise ValueError("Task ids do not match")

    benchmark = benchmarks[task_id]
    out_dir = os.path.dirname(generated_file)
    res = run_functional_test(candidate, benchmark, model_name, out_dir, debug=debug)
    if res:
        log.info(f"Results: {res}")


def functional_test(
    generated_file: str, benchmark_file: str, model_name: str, debug: bool = False
):
    candidates = data.stream_jsonl(generated_file)
    benchmarks = data.jsonl_to_dict(benchmark_file)
    benchmarks = {
        k: v
        for k, v in benchmarks.items()
        if "tests" in v.keys() and v["object"] in ["function", "class", "text"]
    }

    # create output directory in results whose name is the same as the generated file
    os.makedirs(os.path.join(ROOT_DIR, 'results', model_name), exist_ok=True)
    out_dir = os.path.join(ROOT_DIR, 'results', model_name)

    results = []
    errors = []
    for candidate in candidates:
        if candidate["task_id"] not in benchmarks.keys():
            raise ValueError(f"Task ids not found in benchmark: {candidate['task_id']}")

        benchmark = benchmarks[candidate["task_id"]]
        res = run_functional_test(candidate, benchmark, model_name, out_dir, debug=debug)
        results.append(res)
        if "error" in res:
            errors.append(candidate["task_id"])

    log.info(f"Errors: {errors}")
    log.info(f"Results: {results}")

    # write results to file
    with open(f"{out_dir}/test_results.jsonl", "w") as f:
        for res in results:
            json.dump(res, f)
            f.write("\n")

    # write error to file
    error = analyze(f"{out_dir}/test_results.jsonl", benchmarks, analysis="error")
    with open(f"{out_dir}/test_results_errors.json", "w") as f:
        json.dump(error, f)
        f.write("\n")
    log.info(f"Error: {error}")

    # write score to file
    score = analyze(f"{out_dir}/test_results.jsonl", benchmarks, analysis="score")
    with open(f"{out_dir}/test_results_score.json", "w") as f:
        json.dump(score, f)
        f.write("\n")
    log.info(f"Score: {score}")


def calculate_total_score(results: list[dict]):
    num_problems = len(results)
    score = 0
    for res in results:
        if "error" in res:
            continue
        num_tests_passed = res["total"] - len(res["failed"])
        score += num_tests_passed / res["total"]
    return score / num_problems * 100


def calculate_total_error(results: list[dict]):
    num_problems = len(results)
    results_with_error = [res for res in results if "error" in res]
    num_errors = len(results_with_error)
    if num_errors == 0:
        return {}
    num_name_errors = sum([1 for res in results_with_error if res["error"] == "NameError"])
    num_syntax_errors = sum([1 for res in results_with_error if res["error"] == "SyntaxError"])
    num_timeout_errors = sum([1 for res in results_with_error if res["error"] == "TimeoutError"])
    num_no_completion_errors = sum(
        [1 for res in results_with_error if res["error"] == "NoCompletionError"]
    )
    num_other_errors = sum([1 for res in results_with_error if res["error"] == "Error"])
    res = {
        "name_error": num_name_errors,
        "syntax_error": num_syntax_errors,
        "timeout_error": num_timeout_errors,
        "no_completion_error": num_no_completion_errors,
        "other_error": num_other_errors,
        "total_error": num_errors,
        "total_problems": num_problems,
        "total_error_rate": num_errors / num_problems * 100,
        "name_error_pct": num_name_errors / num_errors * 100,
        "syntax_error_pct": num_syntax_errors / num_errors * 100,
        "timeout_error_pct": num_timeout_errors / num_errors * 100,
        "no_completion_error_pct": num_no_completion_errors / num_errors * 100,
        "other_error_pct": num_other_errors / num_errors * 100,
    }
    return res


def analyze_by_category(
    results: list[dict], benchmarks: dict, category: str, analysis: Literal["score", "error"]
):
    report = {}
    category_values = set([benchmark[category] for benchmark in benchmarks.values()])
    for cv in category_values:
        benchmarks_by_cv = [k for k, v in benchmarks.items() if v[category] == cv]
        results_by_cv = [r for r in results if r["task_id"] in benchmarks_by_cv]
        if analysis == "score":
            report[cv] = calculate_total_score(results_by_cv)
        elif analysis == "error":
            report[cv] = calculate_total_error(results_by_cv)
    return report


def analyze(results_file: str, benchmarks: dict, analysis: Literal["score", "error"]):
    res = {}
    results = list(data.stream_jsonl(results_file))
    if analysis == "score":
        total = calculate_total_score(results)
    elif analysis == "error":
        total = calculate_total_error(results)
    by_complexity = analyze_by_category(results, benchmarks, "complexity", analysis=analysis)
    by_problem_type = analyze_by_category(results, benchmarks, "object", analysis=analysis)
    by_topic = analyze_by_category(results, benchmarks, "topic", analysis=analysis)
    res["total"] = total
    res["by_complexity"] = by_complexity
    res["by_problem_type"] = by_problem_type
    res["by_topic"] = by_topic
    return res
