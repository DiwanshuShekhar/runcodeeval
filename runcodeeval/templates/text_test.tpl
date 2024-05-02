{# class_test #}
from runcodeeval import logger as log
import json
from collections.abc import Callable

task_id = "{{ task_id }}"
model_name = "{{ model_name }}"
out_dir = "{{ out_dir }}"

text = {{ generated_code_string }}

def test_a_text(tests: list[str]):
    tests_failed = []
    for idx, test in enumerate(tests):
        if "ctx" in test.keys(): exec(test["ctx"])
        try:
            assert eval(test["assertion"])
        except AssertionError:
            tests_failed.append(idx)
    return len(tests), tests_failed

log.info(f"Running test for prompt: {task_id}")
test_result = test_a_text({{ test_cases }})
res = f"{task_id}: {test_result[0]} tests ran, {test_result[1]} tests failed"
log.info(res)
with open(f"{out_dir}/_result_{task_id}.txt", 'w') as f:
    json.dump({"model_name": model_name, "task_id": task_id, "total": test_result[0], "failed": test_result[1]}, f)
