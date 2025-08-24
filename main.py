#!/usr/bin/env python3
"""
Run logging examples from the command line.
This is a simple wrapper to run specific examples from logging_examples.py.
"""

import argparse
import logging
import sys

from examples import logging_examples


def main() -> None:
    """Run the logging examples based on command line arguments."""
    # Setup basic logging for this script
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description="Run Python logging examples")
    parser.add_argument(
        "example",
        nargs="?",
        type=int,
        default=0,
        help="Example number to run (1-9), or 0 for all examples",
    )
    args = parser.parse_args()

    # Set up a map of example numbers to functions
    examples = {
        1: logging_examples.example_1_simplest_logger,
        2: logging_examples.example_2_logging_levels,
        3: logging_examples.example_3_formatting_logs,
        4: logging_examples.example_4_logger_handler_formatter,
        5: logging_examples.example_5_multiple_handlers,
        6: logging_examples.example_6_text_formatter,
        7: logging_examples.example_7_json_formatter,
        8: logging_examples.example_8_csv_formatter,
        9: logging_examples.example_9_best_practices,
    }

    # Run the specified example, or all examples
    if args.example == 0:
        logging.info("Running all examples...\n")
        logging_examples.run_all_examples()
    elif args.example in examples:
        logging.info(f"Running example {args.example}...\n")
        examples[args.example]()
    else:
        logging.error(
            f"Error: Example {args.example} not found. Choose from 1-9 or 0 for all examples."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
