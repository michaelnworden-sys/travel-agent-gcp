from typing import Annotated, Optional
# CHANGE: Import TypedDict from typing_extensions to fix Pydantic V2 cloud error
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_info: Optional[str]