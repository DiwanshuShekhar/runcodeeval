import argparse
from runcodeeval import evaluate

parser = argparse.ArgumentParser(description="Evaluate model performance using functional tests")

parser.add_argument(
    "-ft",
    "--functional-test",
    nargs="+",
    help="evaluate model performance using functional tests for all generations",
)

parser.add_argument(
    "-fto",
    "--functional-test-one",
    required=False,
    type=str,
    nargs="+",
    help="evaluate model performance using functional tests for one generation",
)

parser.add_argument(
    "--download-benchmark",
    action="store_true",
    help="Export dataset records from metadata.json to benchmark/benchmark.json",
)


if __name__ == "__main__":
    args = parser.parse_args()
    if args.functional_test:
        evaluate.functional_test(
            args.functional_test[0], args.functional_test[1], args.functional_test[2]
        )
    if args.functional_test_one:
        evaluate.functional_test_one(
            args.functional_test_one[0],
            args.functional_test_one[1],
            args.functional_test_one[2],
            args.functional_test_one[3],
            debug=True,
        )
    
    if args.download_benchmark:
        import os
        import json
        import mlcroissant as mlc

        metadata_path = os.path.join("runcodeeval", "benchmark", "metadata.json")
        output_path = os.path.join("runcodeeval", "benchmark", "benchmark.jsonl")

        dataset = mlc.Dataset(jsonld=metadata_path)
        records = dataset.records(record_set="jsonl")

        with open(output_path, "w") as f:
            for record in records:
                # a record is a dictionary where each value is a byte string
                record_str = {k: v.decode("utf-8", errors="replace") if isinstance(v, bytes) else str(v) for k, v in record.items()}
                f.write(json.dumps(record_str) + "\n")
        print(f"Exported records to {output_path}")
