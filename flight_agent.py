from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from tools import fetch_user_flight_information
from state import State
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
flight_tools = [fetch_user_flight_information]
llm_with_tools = llm.bind_tools(flight_tools)

flight_system_message = SystemMessage(content="""
You are a specialized Assistant for Swiss Air. 
Your primary job is to help users look up flight information using your tools.
""")

def flight_agent_node(state: State):
    messages = state['messages']
    conversation = [flight_system_message] + messages
    response = llm_with_tools.invoke(conversation)
    
    # THE FIX: We add a name tag to the message
    response.name = "flight_agent"
    
    return {"messages": [response]}