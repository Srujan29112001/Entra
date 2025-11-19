"""
Production Configuration Validator.

Ensures all required configuration is present and valid before starting the application.
NO MORE PLACEHOLDERS IN PRODUCTION!
"""

from typing import Dict, List, Tuple, Optional
import os
import re
from dataclasses import dataclass
from enum import Enum


class ConfigLevel(str, Enum):
    """Configuration requirement levels."""

    REQUIRED = "required"  # Must be set for production
    RECOMMENDED = "recommended"  # Should be set but not critical
    OPTIONAL = "optional"  # Nice to have


@dataclass
class ConfigItem:
    """Configuration item definition."""

    key: str
    level: ConfigLevel
    description: str
    example: str
    pattern: Optional[str] = None  # Regex pattern for validation
    min_length: Optional[int] = None


# Define all configuration items
CONFIG_ITEMS = [
    # Database & Auth
    ConfigItem(
        key="SUPABASE_URL",
        level=ConfigLevel.REQUIRED,
        description="Supabase project URL",
        example="https://your-project.supabase.co",
        pattern=r"^https://[a-zA-Z0-9-]+\.supabase\.co$",
    ),
    ConfigItem(
        key="SUPABASE_ANON_KEY",
        level=ConfigLevel.REQUIRED,
        description="Supabase anonymous key",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        min_length=100,
    ),
    ConfigItem(
        key="SUPABASE_SERVICE_KEY",
        level=ConfigLevel.REQUIRED,
        description="Supabase service role key (server-side only)",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        min_length=100,
    ),
    # LLM APIs
    ConfigItem(
        key="OPENAI_API_KEY",
        level=ConfigLevel.REQUIRED,
        description="OpenAI API key",
        example="sk-proj-...",
        pattern=r"^sk-(proj-)?[a-zA-Z0-9]{20,}$",
    ),
    ConfigItem(
        key="ANTHROPIC_API_KEY",
        level=ConfigLevel.REQUIRED,
        description="Anthropic Claude API key",
        example="sk-ant-...",
        pattern=r"^sk-ant-[a-zA-Z0-9-_]{95,}$",
    ),
    # Economic Data APIs
    ConfigItem(
        key="FRED_API_KEY",
        level=ConfigLevel.REQUIRED,
        description="FRED (Federal Reserve Economic Data) API key",
        example="a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
        min_length=32,
    ),
    ConfigItem(
        key="ALPHA_VANTAGE_API_KEY",
        level=ConfigLevel.RECOMMENDED,
        description="Alpha Vantage financial data API key",
        example="DEMO",
        min_length=4,
    ),
    ConfigItem(
        key="NEWS_API_KEY",
        level=ConfigLevel.RECOMMENDED,
        description="NewsAPI key for market news",
        example="a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
        min_length=32,
    ),
    # Monitoring & Observability
    ConfigItem(
        key="HELICONE_API_KEY",
        level=ConfigLevel.RECOMMENDED,
        description="Helicone API key for LLM observability",
        example="sk-helicone-...",
        pattern=r"^sk-helicone-[a-zA-Z0-9-]+$",
    ),
    ConfigItem(
        key="SENTRY_DSN",
        level=ConfigLevel.RECOMMENDED,
        description="Sentry DSN for error tracking",
        example="https://[key]@[org].ingest.sentry.io/[project]",
        pattern=r"^https://[a-f0-9]+@[a-z0-9-]+\.ingest\.sentry\.io/\d+$",
    ),
    # Environment
    ConfigItem(
        key="ENVIRONMENT",
        level=ConfigLevel.REQUIRED,
        description="Deployment environment",
        example="production",
        pattern=r"^(development|staging|production)$",
    ),
]


class ConfigValidator:
    """Validates application configuration."""

    def __init__(self, environment: str = None):
        """Initialize validator."""
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def validate_all(self) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate all configuration items.

        Returns:
            Tuple of (is_valid, messages_by_level)
        """
        print("=" * 60)
        print(f"🔍 CONFIGURATION VALIDATION ({self.environment.upper()})")
        print("=" * 60)
        print()

        for item in CONFIG_ITEMS:
            self._validate_item(item)

        # Summary
        print()
        print("=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)

        if self.errors:
            print(f"❌ ERRORS: {len(self.errors)}")
            for error in self.errors:
                print(f"   • {error}")
            print()

        if self.warnings:
            print(f"⚠️  WARNINGS: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   • {warning}")
            print()

        if self.info:
            print(f"ℹ️  INFO: {len(self.info)}")
            for info in self.info:
                print(f"   • {info}")
            print()

        is_valid = len(self.errors) == 0

        if is_valid:
            print("✅ Configuration is valid!\n")
        else:
            print("❌ Configuration has errors. Please fix before deploying.\n")

        return is_valid, {
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
        }

    def _validate_item(self, item: ConfigItem):
        """Validate a single configuration item."""
        value = os.getenv(item.key)

        # Check if set
        if not value:
            if item.level == ConfigLevel.REQUIRED:
                if self.environment == "production":
                    self.errors.append(
                        f"{item.key} is REQUIRED in production but not set"
                    )
                else:
                    self.warnings.append(f"{item.key} is not set (example: {item.example})")
            elif item.level == ConfigLevel.RECOMMENDED:
                self.warnings.append(
                    f"{item.key} is recommended but not set (example: {item.example})"
                )
            else:
                self.info.append(f"{item.key} is optional and not set")
            return

        # Check for placeholder values
        placeholder_patterns = [
            r"placeholder",
            r"demo",
            r"example",
            r"your-.*",
            r"sk-proj-xxx",
            r"sk-ant-xxx",
        ]

        for pattern in placeholder_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                if self.environment == "production":
                    self.errors.append(
                        f"{item.key} contains placeholder value: {value[:20]}..."
                    )
                else:
                    self.warnings.append(
                        f"{item.key} contains placeholder value: {value[:20]}..."
                    )
                return

        # Check pattern
        if item.pattern and not re.match(item.pattern, value):
            self.errors.append(
                f"{item.key} does not match expected pattern. "
                f"Expected format like: {item.example}"
            )
            return

        # Check minimum length
        if item.min_length and len(value) < item.min_length:
            self.errors.append(
                f"{item.key} is too short (min {item.min_length} chars, got {len(value)})"
            )
            return

        # Valid!
        print(f"✓ {item.key}: configured")


def validate_config(environment: str = None) -> bool:
    """
    Validate configuration and return whether it's valid.

    Args:
        environment: Environment name (development/staging/production)

    Returns:
        True if valid, False otherwise
    """
    validator = ConfigValidator(environment)
    is_valid, _ = validator.validate_all()
    return is_valid


def require_valid_config(environment: str = None):
    """
    Validate config and exit if invalid in production.

    Args:
        environment: Environment name
    """
    validator = ConfigValidator(environment)
    is_valid, messages = validator.validate_all()

    if not is_valid and validator.environment == "production":
        print("❌ FATAL: Configuration validation failed in production!")
        print("Please fix all errors before deploying.")
        print()
        exit(1)

    return is_valid, messages


if __name__ == "__main__":
    import sys

    env = sys.argv[1] if len(sys.argv) > 1 else None
    is_valid = validate_config(env)
    sys.exit(0 if is_valid else 1)
