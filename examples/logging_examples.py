#!/usr/bin/env python3
"""
Python Logging Examples

This file contains all the examples from the README.md guide on Python logging.
Each example is contained in its own function to allow for isolated execution.
"""

import json
import logging
import os
from typing import Any


def example_1_simplest_logger() -> None:
    """
    Example 1: The Simplest Logger
    Shows basic usage with default configuration
    """
    print("\n=== Example 1: The Simplest Logger ===")  # noqa: T201

    # Reset logging configuration
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Basic configuration
    logging.basicConfig(level=logging.WARNING)

    # Log messages at different levels
    logging.debug("Debug message")  # NOT shown (below WARNING level)
    logging.info("Info message")  # NOT shown (below WARNING level)
    logging.warning("Warning message")  # ✅ shown
    logging.error("Error message")  # ✅ shown
    logging.critical("Critical message")  # ✅ shown


def example_2_logging_levels() -> None:
    """
    Example 2: Logging Levels
    Demonstrates different logging levels
    """
    print("\n=== Example 2: Logging Levels ===")  # noqa: T201

    # Reset logging configuration
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configuration showing all levels (DEBUG is the lowest)
    logging.basicConfig(level=logging.DEBUG)

    # Log at all available levels
    logging.debug("DEBUG level - Very detailed info, useful only for developers.")
    logging.info("INFO level - Normal events that confirm the program is working.")
    logging.warning(
        "WARNING level - Something unexpected happened, but program still runs fine."
    )
    logging.error(
        "ERROR level - A problem that prevented part of the program from working."
    )
    logging.critical("CRITICAL level - A very serious problem, the program may crash.")

    print("\nLogging levels by numeric value:")  # noqa: T201
    print(f"DEBUG: {logging.DEBUG}")  # 10  # noqa: T201
    print(f"INFO: {logging.INFO}")  # 20  # noqa: T201
    print(f"WARNING: {logging.WARNING}")  # 30  # noqa: T201
    print(f"ERROR: {logging.ERROR}")  # 40  # noqa: T201
    print(f"CRITICAL: {logging.CRITICAL}")  # 50  # noqa: T201


def example_3_formatting_logs() -> None:
    """
    Example 3: Formatting Logs
    Shows how to control the appearance of log messages
    """
    print("\n=== Example 3: Formatting Logs ===")  # noqa: T201

    # Reset logging configuration
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Configure with custom format
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Log some messages with the new format
    logging.info("App started")
    logging.error("Something went wrong")

    print("\nCommon format fields:")  # noqa: T201
    print("%(asctime)s → Time")  # noqa: T201
    print("%(name)s → Logger name")  # noqa: T201
    print("%(levelname)s → Level")  # noqa: T201
    print("%(message)s → The log text")  # noqa: T201


def example_4_logger_handler_formatter() -> None:
    """
    Example 4: Loggers, Handlers, and Formatters
    Demonstrates the logging pipeline with separate components
    """
    print("\n=== Example 4: Loggers, Handlers, and Formatters ===")  # noqa: T201

    # Reset logging configuration
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Create a logger
    logger = logging.getLogger("my_app")
    logger.setLevel(logging.DEBUG)

    # Create handler (send logs to file)
    log_file = "app.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.ERROR)

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(file_handler)

    # Log messages at different levels
    logger.debug("Debug message (won't go to file)")
    logger.info("Info message (won't go to file)")
    logger.warning("Warning message (won't go to file)")
    logger.error("Error message (will go to file)")
    logger.critical("Critical message (will go to file)")

    print(f"Check {log_file} - it should contain only ERROR and CRITICAL messages")  # noqa: T201


def example_5_multiple_handlers() -> None:
    """
    Example 5: Multiple Handlers
    Shows how to send logs to different destinations with different levels
    """
    print("\n=== Example 5: Multiple Handlers ===")  # noqa: T201

    # Reset logging configuration
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Create logger
    logger = logging.getLogger("multi")
    logger.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # File handler
    log_file = "errors.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.ERROR)

    # Formatter
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Log messages
    logger.debug("This is debug - not shown anywhere")
    logger.info("This goes to console only")
    logger.warning("This goes to console only")
    logger.error("This goes to console AND file")
    logger.critical("This goes to console AND file")

    print(f"\nCheck {log_file} - it should contain only ERROR and CRITICAL messages")  # noqa: T201


def example_6_text_formatter() -> None:
    """
    Example 6: Text Formatter (default style)
    Shows the standard text formatter
    """
    print("\n=== Example 6: Text Formatter ===")  # noqa: T201

    # Reset logging configuration
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Create logger
    logger = logging.getLogger("text_example")
    logger.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()

    # Text formatter
    text_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(text_formatter)

    # Add handler
    logger.addHandler(console_handler)

    # Log message
    logger.info("This is a text log example")


def example_7_json_formatter() -> None:
    """
    Example 7: JSON Formatter
    Creates a custom formatter for structured JSON logs
    """
    print("\n=== Example 7: JSON Formatter ===")  # noqa: T201

    # Reset logging configuration
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Create JSON formatter class
    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            log_record: dict[str, Any] = {
                "time": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            return json.dumps(log_record)

    # Create logger
    logger = logging.getLogger("json_example")
    logger.setLevel(logging.DEBUG)

    # Console handler with JSON formatter
    console_handler = logging.StreamHandler()
    json_formatter = JsonFormatter()
    console_handler.setFormatter(json_formatter)

    # Add handler
    logger.addHandler(console_handler)

    # Log message
    logger.info("This is a JSON log example")


def example_8_csv_formatter() -> None:
    """
    Example 8: CSV Formatter
    Creates a custom formatter for CSV logs (good for data analysis)
    """
    print("\n=== Example 8: CSV Formatter ===")  # noqa: T201

    # Reset logging configuration
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Create CSV formatter class
    class CsvFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            return f"{self.formatTime(record, self.datefmt)},{record.levelname},{record.name},{record.getMessage()}"

    # Create logger
    logger = logging.getLogger("csv_example")
    logger.setLevel(logging.DEBUG)

    # Set up CSV file for logging
    csv_file = "logs.csv"
    # Add header if file doesn't exist or is empty
    if not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0:
        with open(csv_file, "w") as f:
            f.write("timestamp,level,logger,message\n")

    # Console handler for viewing output
    console_handler = logging.StreamHandler()
    csv_formatter_console = CsvFormatter()
    console_handler.setFormatter(csv_formatter_console)

    # File handler for actual CSV file
    file_handler = logging.FileHandler(csv_file, mode="a")  # Append mode
    csv_formatter_file = CsvFormatter()
    file_handler.setFormatter(csv_formatter_file)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Log message
    logger.warning("This is a CSV log example")
    logger.info("Another CSV log entry for data analysis")

    print(f"\nCheck {csv_file} - it should contain the CSV-formatted log entries")  # noqa: T201


def example_9_best_practices() -> None:
    """
    Example 9: Best Practices Demo
    Shows a more complete logging setup with best practices
    """
    print("\n=== Example 9: Best Practices Demo ===")  # noqa: T201

    # Reset logging configuration
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Create loggers for different components
    app_logger = logging.getLogger("app")
    db_logger = logging.getLogger("database")
    api_logger = logging.getLogger("api")

    # Set level for all loggers
    app_logger.setLevel(logging.DEBUG)
    db_logger.setLevel(logging.DEBUG)
    api_logger.setLevel(logging.DEBUG)

    # Console handler - for development (INFO level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_format)

    # File handler - for all logs (DEBUG level)
    all_file_handler = logging.FileHandler("all_logs.log")
    all_file_handler.setLevel(logging.DEBUG)
    all_file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    all_file_handler.setFormatter(all_file_format)

    # Error file handler - for errors only (ERROR level)
    error_file_handler = logging.FileHandler("error_logs.log")
    error_file_handler.setLevel(logging.ERROR)
    error_file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(module)s:%(lineno)d]"
    )
    error_file_handler.setFormatter(error_file_format)

    # Add handlers to loggers
    for logger in [app_logger, db_logger, api_logger]:
        logger.addHandler(console_handler)
        logger.addHandler(all_file_handler)
        logger.addHandler(error_file_handler)

    # Example logs
    app_logger.info("Application started")
    db_logger.debug("Database connection established")
    api_logger.info("API server listening on port 8000")
    db_logger.warning("Database query took longer than expected")
    api_logger.error("Failed to process API request: Invalid input")

    print("\nCheck all_logs.log and error_logs.log to see the different log files")  # noqa: T201


def run_all_examples() -> None:
    """Run all examples in sequence"""
    example_1_simplest_logger()
    example_2_logging_levels()
    example_3_formatting_logs()
    example_4_logger_handler_formatter()
    example_5_multiple_handlers()
    example_6_text_formatter()
    example_7_json_formatter()
    example_8_csv_formatter()
    example_9_best_practices()


if __name__ == "__main__":
    # Run all examples
    run_all_examples()

    # To run a specific example, modify this file:
    # 1. Comment out the run_all_examples() line above
    # 2. Call the specific example function you want to run
