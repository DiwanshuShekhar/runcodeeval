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
