from langchain.mcp import MCPAdapter
from loguru import logger

from config import settings


def create_mcp_config() -> dict:
    """Build config for all integrated mcp servers"""
    logger.info("building mcp config")
    servers = {
        "weather_forecast": {
            "url": settings.weather_forecast_mcp_url,
        }
    }

    return {
        "mcpServers": servers,
    }


def create_mcp_adapter() -> MCPAdapter:
    return MCPAdapter(create_mcp_config())
