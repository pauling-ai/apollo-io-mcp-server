"""CLI entry point for the Apollo MCP server."""

import argparse
import asyncio
import logging
import sys


def get_version() -> str:
    try:
        from importlib.metadata import version

        return version("apollo-mcp-server")
    except Exception:
        pass
    try:
        import os
        import tomllib

        pyproject_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "pyproject.toml"
        )
        with open(pyproject_path, "rb") as f:
            return tomllib.load(f)["project"]["version"]
    except Exception:
        return "unknown"


def check_status_and_exit() -> None:
    """Verify the API key is valid and exit."""
    from apollo_mcp_server.client import get_client
    from apollo_mcp_server.config import get_config

    try:
        get_config()
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    client = get_client()

    async def _check() -> bool:
        return await client.check_auth()

    print("Checking Apollo API key...")
    try:
        valid = asyncio.run(_check())
    except Exception as e:
        print(f"❌ Could not reach Apollo API: {e}")
        sys.exit(1)

    if valid:
        print("✅ API key is valid")
        sys.exit(0)
    else:
        print("❌ API key is invalid or rejected by Apollo")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="apollo-mcp",
        description="Apollo.io MCP server for contact and company enrichment",
    )
    parser.add_argument("--status", action="store_true", help="Check API key and exit")
    parser.add_argument(
        "--log-level",
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: WARNING)",
    )
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "streamable-http"],
        help="MCP transport mode (default: stdio)",
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit")

    args = parser.parse_args()

    if args.version:
        print(f"apollo-mcp-server {get_version()}")
        sys.exit(0)

    # Configure logging
    import os

    log_level = args.log_level or os.getenv("LOG_LEVEL", "WARNING")
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.WARNING),
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    if args.status:
        check_status_and_exit()

    # Validate config before starting server
    try:
        from apollo_mcp_server.config import get_config

        get_config()
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    from apollo_mcp_server.server import create_mcp_server

    mcp = create_mcp_server()
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
