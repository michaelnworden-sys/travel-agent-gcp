from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from tools import search_hotels
from state import State
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
hotel_tools = [search_hotels]
llm_with_tools = llm.bind_tools(hotel_tools)

hotel_system_message = SystemMessage(content="""
You are a specialized Hotel Assistant.
Your primary job is to help users find accommodation.
""")

def hotel_agent_node(state: State):
    messages = state['messages']
    conversation = [hotel_system_message] + messages
    response = llm_with_tools.invoke(conversation)
    
    # THE FIX: Name tag
    response.name = "hotel_agent"
    
    return {"messages": [response]}