from langgraph.prebuilt import ToolNode
from tools import fetch_user_flight_information, search_hotels

# This Node is the "Muscle".
# If an agent decides to call a tool, this node executes the Python code
# and returns the result back to the chat.
global_tools = [fetch_user_flight_information, search_hotels]
tool_node = ToolNode(global_tools)

print("✅ Tool Execution Node is ready.")