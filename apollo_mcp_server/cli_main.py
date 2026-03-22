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


def setup_and_exit() -> None:
    """Interactively save the Apollo API key to ~/.apollo-mcp/.env and exit."""
    from apollo_mcp_server.config import APOLLO_CONFIG_DIR, APOLLO_CONFIG_FILE

    print("Apollo MCP Server — Setup")
    print("=" * 40)
    print("Get your API key at: https://developer.apollo.io/#/keys")
    print()

    try:
        api_key = input("Enter your Apollo API key: ").strip()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled")
        sys.exit(0)

    if not api_key:
        print("❌ No key entered, setup cancelled")
        sys.exit(1)

    APOLLO_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    APOLLO_CONFIG_FILE.write_text(f"APOLLO_API_KEY={api_key}\n")
    print(f"✅ API key saved to {APOLLO_CONFIG_FILE}")
    print()
    print("Verifying key...")

    # Reload env so get_client picks up the new key
    import os
    os.environ["APOLLO_API_KEY"] = api_key

    from apollo_mcp_server.client import get_client
    client = get_client()

    async def _check() -> bool:
        return await client.check_auth()

    try:
        valid = asyncio.run(_check())
    except Exception as e:
        print(f"❌ Could not reach Apollo API: {e}")
        sys.exit(1)

    if valid:
        print("✅ Key is valid — you're all set!")
        sys.exit(0)
    else:
        print("❌ Key was saved but Apollo rejected it — double-check it at https://developer.apollo.io/#/keys")
        sys.exit(1)


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
    parser.add_argument("--setup", action="store_true", help="Save API key to ~/.apollo-mcp/.env and exit")
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

    if args.setup:
        setup_and_exit()

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
