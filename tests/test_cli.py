"""Tests for the CLI entry point."""

import pytest
from unittest.mock import patch


def _run_returning(value):
    """asyncio.run replacement that closes the coroutine instead of running it."""
    def _inner(coro):
        coro.close()
        return value
    return _inner


class TestCheckStatus:
    def test_valid_key_exits_0(self, capsys):
        with (
            patch("apollo_mcp_server.config.get_config"),
            patch("apollo_mcp_server.client.get_client"),
            patch("asyncio.run", side_effect=_run_returning(True)),
            pytest.raises(SystemExit) as exc_info,
        ):
            from apollo_mcp_server.cli_main import check_status_and_exit
            check_status_and_exit()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "✅" in captured.out

    def test_invalid_key_exits_1(self, capsys):
        with (
            patch("apollo_mcp_server.config.get_config"),
            patch("apollo_mcp_server.client.get_client"),
            patch("asyncio.run", side_effect=_run_returning(False)),
            pytest.raises(SystemExit) as exc_info,
        ):
            from apollo_mcp_server.cli_main import check_status_and_exit
            check_status_and_exit()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "❌" in captured.out

    def test_missing_api_key_exits_1(self, capsys):
        with (
            patch(
                "apollo_mcp_server.config.get_config",
                side_effect=ValueError("APOLLO_API_KEY environment variable is not set."),
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            from apollo_mcp_server.cli_main import check_status_and_exit
            check_status_and_exit()

        assert exc_info.value.code == 1


class TestGetVersion:
    def test_returns_string(self):
        from apollo_mcp_server.cli_main import get_version
        version = get_version()
        assert isinstance(version, str)
        assert len(version) > 0
