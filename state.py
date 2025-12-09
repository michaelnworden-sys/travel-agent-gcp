from typing import TypedDict, Annotated, Any
from langgraph.graph.message import add_messages

class FerryState(TypedDict):
    # We changed 'list' to 'list[Any]' so the server knows what to expect
    messages: Annotated[list[Any], add_messages]
    
    remaining_steps: int 
    departure_terminal: str
    arrival_terminal: str
    date_time_query: str