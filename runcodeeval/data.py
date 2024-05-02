from collections.abc import Generator
import json
import logging as log

def stream_jsonl(path) -> Generator:
    with open(path, "r") as f:
        for line in f:
            try:
                line_dict: dict = json.loads(line)
                # if "skip" in line_dict.keys() and line_dict["skip"]:
                #     log.info(f"Skipping {line_dict['task_id']}")
                #     continue
                yield line_dict
            except json.decoder.JSONDecodeError:
                log.info(f"Error parsing line: {line}")
                raise

def jsonl_to_dict(path: str) -> dict:
    result: dict = dict()
    with open(path, "r") as f:
        try:
            for line in f:
                line_dict: dict = json.loads(line)
                result.update({line_dict["task_id"]: line_dict})
        except json.decoder.JSONDecodeError:
            log.info(f"Error parsing line: {line}")
            raise
    return result
