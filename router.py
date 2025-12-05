from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Literal, TypedDict
from state import State
from dotenv import load_dotenv

load_dotenv()

# 1. Define the Structure
# We force Gemini to choose EXACTLY one of these options.
class RouteQuery(TypedDict):
    """Route query to the most relevant worker."""
    destination: Literal["flights", "hotels", "general"]

# 2. The Router Brain
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
structured_llm = llm.with_structured_output(RouteQuery)

# 3. The Router Function
# This function looks at the chat history and decides where to go next.
def route_question(state: State):
    print("---ROUTING---")
    
    # Get the last message
    last_message = state["messages"][-1]
    
    # Ask Gemini: "Where does this message belong?"
    result = structured_llm.invoke(
        [
            ("system", "You are a router. Route the input to 'flights' or 'hotels'. If unsure, route to 'general'."),
            ("human", last_message.content)
        ]
    )
    
    # Return the decision (e.g., "flights")
    print(f"Decision: {result['destination']}")
    return result["destination"]

print("✅ Router is ready to direct traffic.")