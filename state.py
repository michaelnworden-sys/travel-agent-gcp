from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class FerryState(TypedDict):
    # Standard chat history
    messages: Annotated[list, add_messages]
    
    # --- THIS WAS MISSING ---
    # The agent uses this to track how many "turns" it has left so it doesn't loop forever.
    remaining_steps: int 
    
    # Our custom slots
    departure_terminal: str
    arrival_terminal: str
    date_time_query: str