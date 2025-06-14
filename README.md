# RunCodeEval: A framework to evaluate LLMs trained on code using CodeEval benchmark dataset

CodeEval is an innovative, pedagogy-based benchmarking dataset that targeted evaluation of code-trained LLMs. It assesses LLMs across 27 distinct aspects of Python programming at three proficiency levels: beginner, intermediate, and advanced. CodeEval allows for comprehensive evaluation as it includes both function and class level tasks. The RunCodeEval software framework facilitates model evaluation using the CodeEval dataset. The framework yields detailed insights into the strengths and weaknesses of code-trained models

# How to use RunCodeEval Framework
RunCodeEval is self-contained and doesn't need any external dependencies to run evaluation. In order to run evaluation, develop an input file with LLM generated solutions to each problem in the CodeEval benchmark dataset. Example input files generated using different LLMs are present in the [completions folder](completions) of this repo. Running the evaluation requires path to `completion file` and the path to the `CodeEval benchmark` which can be downloaded from it's permanent doi [link](https://doi.org/10.5281/zenodo.15620594) or you can simply run the command `python driver.py --download-benchmark` from the project root. The following command runs evaluation using [this input file](completions/phi2_candidates.jsonl) and the downloaded CodeEval benchmark dataset which we recommend to put in the [benchmark folder](runcodeeval/benchmark) of this repo.

The following example shows how to run evaluation with CodeEval - 
```
python driver.py -ft completions/phi2_candidates.jsonl runcodeeval/benchmark/codeeval_v1.jsonl phi-2
```
The first argument is the path to the input file containing the model generated solutions for each problem in the CodeEval benchmark dataset whose path is provided as second argument. The third argument is the `model name` which is used to name the directory to contain all results generated by the above command. For example, the above command generates the result files - `[test_results_score.json](results/phi-2/test_results_score.json), [test_results_score.json](results/phi-2/test_results_score.json) and [test_results.jsonl](results/phi-2/test_results.jsonl) in the folder [results/phi-2](results/phi-2)

The framework has a convenience feature to run evaluation for only one model generated solution. This can be used for debugging and random testing of model generated code. An example command that runs evaluation for an instance of CodeEval benchmark dataset identifier by `codeeval-20` is shown below - 

```
python driver.py -fto codeeval-20 completions/phi2_candidates.jsonl runcodeeval/benchmark/codeeval_v1.jsonl phi-2
```
The RunCodeEval framework has built-in log which is generated as `app.log` in the project root directory.

# CodeEval Benchmark dataset
We intentionally removed CodeEval benchmark dataset from this repository to prevent contamination of code-trained LLMs that are trained on Github. We encourage the community to refrain from adding CodeEval benchmark dataset to any public GitHub repositories. CodeEval can be freely and independently downloaded from its permanent doi [link](https://doi.org/10.5281/zenodo.11100073) 
