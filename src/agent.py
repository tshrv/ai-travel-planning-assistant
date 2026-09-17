from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from config import settings
from llm.gcp import chat_gcp
from mcp_servers.manager import create_mcp_adapter
from tools import datetime_now, search_knowledge_base


def get_system_prompt():
    """Get system prompt from path in config"""
    with open(settings.system_prompt_path) as f:
        system_prompt = f.read()
        return system_prompt


async def create_travel_planner_agent():
    """Build the agent with tools and memory"""
    mcp_adapter = create_mcp_adapter()
    async with mcp_adapter:
        mcp_tools = await mcp_adapter.list_tools()
        tools = [search_knowledge_base, datetime_now, *mcp_tools]

        checkpointer = InMemorySaver()

        tp_agent = create_agent(
            model=chat_gcp,
            tools=tools,
            system_prompt=get_system_prompt(),
            checkpointer=checkpointer,
        )

        return tp_agent
