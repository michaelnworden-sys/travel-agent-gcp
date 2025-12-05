from typing import Annotated
# We import NotRequired to tell the strict server this key can be missing
from typing_extensions import TypedDict, NotRequired
from langgraph.graph.message import AnyMessage, add_messages

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    # NotRequired means: "You don't even have to send this key if you don't want to."
    user_info: NotRequired[str]