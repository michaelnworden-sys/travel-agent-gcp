from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from state import State
from dotenv import load_dotenv

load_dotenv()

# A simple brain for chit-chat
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

system_message = SystemMessage(content="""
You are a helpful customer support assistant for Swiss Air.
You handle general questions and greetings. 
You do NOT have access to tools. 
If someone asks about flights or hotels, tell them you will transfer them to the right department.
""")

def general_agent_node(state: State):
    messages = state['messages']
    conversation = [system_message] + messages
    
    # Call Gemini
    response = llm.invoke(conversation)
    
    # Sign the message so the graph knows who spoke
    response.name = "general_agent"
    
    return {"messages": [response]}