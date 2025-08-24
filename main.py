#!/usr/bin/env python3
"""
Pydantic Settings Example

This script demonstrates how to use the Pydantic Settings classes defined in examples/settings.py.
It shows how settings are loaded from environment variables and .env files, and how they can be
accessed and manipulated in your application.
"""

import json
import os
from pathlib import Path

# Import the settings classes and pre-created instances from examples/settings.py
from examples.settings import (
    # Import the classes for type annotations
    AppSettings,
    DatabaseSettings,
    LoggerSettings,
    # Import the pre-created instances
    app_settings,
    database_settings,
    logger_settings,
)


def main() -> None:
    """
    Demonstrate Pydantic Settings functionality using the settings from examples/settings.py.
    """
    # SECTION 1: Using pre-created instances
    print("\n===== PRE-CREATED SETTINGS INSTANCES =====")
    print("These are singleton instances already created in settings.py")

    # The settings are already loaded when imported
    print(f"App Name: {app_settings.name}")
    print(f"App Version: {app_settings.version}")
    print(f"Debug Mode: {app_settings.debug}")

    print(f"\nLogger Level: {logger_settings.level}")
    print(f"Logger Format: {logger_settings.format}")

    # Mask the password in the connection URL
    masked_url = database_settings.connection_url.replace(
        database_settings.password, "*****"
    )
    print(f"\nDatabase Host: {database_settings.host}")
    print(f"Database Name: {database_settings.name}")
    print(f"Database Connection URL: {masked_url}")

    # SECTION 2: Understanding model_config with SettingsConfigDict
    print("\n===== PYDANTIC SETTINGS CONFIGURATION =====")
    print("SettingsConfigDict is used to configure how settings are loaded:")
    print("  - env_file: Path to .env file")
    print("  - env_file_encoding: Encoding of .env file")
    print("  - env_prefix: Prefix for env vars")
    print("  - env_nested_delimiter: Delimiter for nested settings")
    print("  - extra: How to handle extra fields ('ignore', 'allow', 'forbid')")

    # SECTION 3: Environment Variable Prefixes
    print("\n===== ENVIRONMENT VARIABLE PREFIXES =====")
    print("Different setting classes use different env variable prefixes:")
    print("AppSettings uses prefix: 'APP_'")
    print("LoggerSettings uses prefix: 'LOG_'")
    print("DatabaseSettings uses prefix: 'DATABASE_'")
    print("For example:")
    print("  - APP_NAME maps to app_settings.name")
    print("  - LOG_LEVEL maps to logger_settings.level")
    print("  - DATABASE_HOST maps to database_settings.host")

    # SECTION 4: Environment Variable Override
    print("\n===== ENVIRONMENT VARIABLE OVERRIDE =====")
    # Save original value
    original_name = app_settings.name

    # Set environment variable to override the setting
    os.environ["APP_NAME"] = "Overridden App Name"

    # Create a new instance which will use the new env var
    # This directly uses the AppSettings class imported above
    override_settings = AppSettings()

    # Show the difference
    print(f"Original name: {original_name}")
    print(f"Overridden name: {override_settings.name}")

    # Reset the environment variable
    del os.environ["APP_NAME"]

    # SECTION 5: Runtime Override
    print("\n===== RUNTIME OVERRIDE =====")
    # Create an instance with custom values at initialization
    # This directly uses the AppSettings class imported above
    custom_settings = AppSettings(name="Custom App", debug=True, port=9000)

    # Demonstrate using DatabaseSettings and LoggerSettings classes
    # This directly uses the classes imported above to fix "unused import" warnings
    print("\nCreating custom database and logger settings:")
    db_settings = DatabaseSettings(host="example.com", port=3306)
    log_settings = LoggerSettings(level="DEBUG")

    print(f"Custom DB Host: {db_settings.host}")
    print(f"Custom DB Port: {db_settings.port}")
    print(f"Custom Logger Level: {log_settings.level}")

    print(f"Custom name: {custom_settings.name}")
    print(f"Custom debug: {custom_settings.debug}")
    print(f"Custom port: {custom_settings.port}")

    # SECTION 6: Field Validators and Computed Properties
    print("\n===== FIELD VALIDATORS AND COMPUTED PROPERTIES =====")

    # Field validators (see LoggerSettings._normalize_level)
    print("Field Validators:")
    print(f"  - Logger level is automatically uppercase: {logger_settings.level}")

    # Properties (computed values)
    print("\nComputed Properties:")
    print(f"  - Database connection URL: {masked_url}")
    print(f"  - Log level as integer: {logger_settings.get_log_level_int()}")

    # SECTION 7: Convert to Dict
    print("\n===== CONVERTING TO DICTIONARY =====")
    # Convert settings to dictionary
    app_dict = app_settings.model_dump()
    print(json.dumps(app_dict, indent=2, default=str))

    # SECTION 8: Nested Settings with model composition
    print("\n===== NESTED SETTINGS STRUCTURE =====")
    print("Settings classes can inherit from each other:")
    print("  - BaseConfigSettings: Shared configuration")
    print("  - AppSettings: Extends BaseConfigSettings with app-specific settings")
    print(
        "  - LoggerSettings: Extends BaseConfigSettings with logging-specific settings"
    )
    print(
        "  - DatabaseSettings: Extends BaseConfigSettings with database-specific settings"
    )

    # SECTION 9: Check for .env file
    print("\n===== .ENV FILE =====")
    env_file = Path(".env")
    if env_file.exists():
        print(f".env file exists at: {env_file.absolute()}")
        print("First few non-sensitive lines:")
        with open(env_file) as f:
            for i, line in enumerate(f):
                if i >= 5:  # Show just the first 5 lines
                    break
                # Skip sensitive data
                if (
                    "PASSWORD" not in line.upper()
                    and "SECRET" not in line.upper()
                    and line.strip()
                ):
                    print(f"  {line.strip()}")
    else:
        print(f".env file not found at: {env_file.absolute()}")

    print("\n===== End of Demonstration =====")


if __name__ == "__main__":
    main()
