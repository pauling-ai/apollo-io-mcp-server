"""Configuration loaded from environment variables."""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()

APOLLO_BASE_URL = "https://api.apollo.io/api/v1"


@dataclass
class Config:
    api_key: str
    base_url: str = field(default=APOLLO_BASE_URL)
    log_level: str = field(default="WARNING")


def get_config() -> Config:
    api_key = os.getenv("APOLLO_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "APOLLO_API_KEY environment variable is not set.\n"
            "Get your API key at: https://app.apollo.io/#/settings/integrations/api_keys\n"
            "Then set it in your environment or a .env file:\n"
            "  APOLLO_API_KEY=your_key_here"
        )
    return Config(
        api_key=api_key,
        log_level=os.getenv("LOG_LEVEL", "WARNING").upper(),
    )
