from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage

from state import State
from flight_agent import flight_agent_node
from hotel_agent import hotel_agent_node
from general_agent import general_agent_node  # <--- NEW IMPORT
from utilities import global_tools
from router import route_question

builder = StateGraph(State)

# 1. Add Nodes
builder.add_node("flight_agent", flight_agent_node)
builder.add_node("hotel_agent", hotel_agent_node)
builder.add_node("general_agent", general_agent_node) # <--- NEW ROOM
builder.add_node("tools", ToolNode(global_tools))

# 2. Start -> Router
builder.add_conditional_edges(
    START,
    route_question,
    {
        "flights": "flight_agent",
        "hotels": "hotel_agent",
        "general": "general_agent", # <--- NEW LOGIC (Don't hang up!)
    }
)

# 3. Agents -> Tools or End
def should_continue(state: State):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

builder.add_conditional_edges("flight_agent", should_continue, ["tools", END])
builder.add_conditional_edges("hotel_agent", should_continue, ["tools", END])
builder.add_edge("general_agent", END) # General agent just talks and finishes.

# 4. Tools -> Back to Specific Agent
def route_tool_output(state: State):
    messages = state["messages"]
    for message in reversed(messages):
        if isinstance(message, AIMessage) and message.name:
            return message.name
    return "flight_agent"

builder.add_conditional_edges(
    "tools",
    route_tool_output,
    {
        "flight_agent": "flight_agent",
        "hotel_agent": "hotel_agent"
    }
)

# 5. Compile with MEMORY
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

print("✅ The Smart Graph (with Memory & Chit-Chat) is built!")