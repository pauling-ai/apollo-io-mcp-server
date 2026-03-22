"""FastMCP server creation and tool registration."""

import logging

from fastmcp import FastMCP

from apollo_mcp_server.tools.companies import register_company_tools
from apollo_mcp_server.tools.people import register_people_tools

logger = logging.getLogger(__name__)


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with all Apollo tools."""
    mcp = FastMCP("apollo", mask_error_details=True)

    register_people_tools(mcp)
    register_company_tools(mcp)

    return mcp
