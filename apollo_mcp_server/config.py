"""Configuration loaded from environment variables."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

APOLLO_CONFIG_DIR = Path.home() / ".apollo-mcp"
APOLLO_CONFIG_FILE = APOLLO_CONFIG_DIR / ".env"
APOLLO_BASE_URL = "https://api.apollo.io/api/v1"

# Load from ~/.apollo-mcp/.env first; explicit env vars always take precedence
load_dotenv(APOLLO_CONFIG_FILE)


@dataclass
class Config:
    api_key: str
    base_url: str = field(default=APOLLO_BASE_URL)
    log_level: str = field(default="WARNING")


def get_config() -> Config:
    api_key = os.getenv("APOLLO_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "Apollo API key not found.\n"
            "Run: apollo-mcp --setup\n"
            "Or get your key at: https://developer.apollo.io/#/keys"
        )
    return Config(
        api_key=api_key,
        log_level=os.getenv("LOG_LEVEL", "WARNING").upper(),
    )
