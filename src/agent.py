from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from llm import llm
from mcp_servers.manager import create_mcp_adapter
from tools import datetime_now, search_knowledge_base


async def create_travel_planner_agent():
    mcp_adapter = create_mcp_adapter()
    async with mcp_adapter:
        mcp_tools = await mcp_adapter.list_tools()
        tools = [search_knowledge_base, datetime_now, *mcp_tools]

        checkpointer = InMemorySaver()

        tp_agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt="""
        You are a travel planning assistant.
        You have access to:
        1. A knowledge base containing information about tourism data of destinations.
        2. Tool to get today's date, can do specific timezones.
        3. External services provided through MCP tools.
        Use search_knowledge_base when the requested information may be available in the knowledge base.
        You don't necessarily have to pass the exact user query to search_knowledge_base. You can formulate a better, more specific search query.
        You may call available tools multiple times with different queries when necessary.
        Always cite the source URL for information obtained from search_knowledge_base.
        Use the appropriate MCP tool when the user asks for information requiring an external service, such as weather, flights, hotels, etc.
        Do not invent information.
        If the knowledge base does not contain enough information to answer the question, clearly say so.
        Answer concisely and accurately.
        """,
            checkpointer=checkpointer,
        )

        return tp_agent
