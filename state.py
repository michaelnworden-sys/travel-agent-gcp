from typing import Annotated, TypedDict, Optional
from langgraph.graph.message import AnyMessage, add_messages

# We remove "user_info" for now so the Chat Interface works automatically.
class State(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    # user_info: str  <--- COMMENT THIS OUT