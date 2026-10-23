from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph,START,END,add_messages
from typing import Annotated,TypedDict
from langgraph.checkpoint.sqlite import SqliteSaver
import uuid
import sqlite3

load_dotenv()
llm=ChatGoogleGenerativeAI(model='gemini-3.5-flash')

class chatstate(TypedDict):
   messages:Annotated[list[str],add_messages]

def access_llm(state:chatstate):
   
   newreply=llm.invoke(state["messages"])
   return {'messages':newreply}

graph=StateGraph(chatstate)

graph.add_node('llm',access_llm)

graph.add_edge(START,'llm')
graph.add_edge('llm',END)

connection=sqlite3.connect(database="chatbot.db",check_same_thread=False)
chatai=graph.compile(checkpointer=SqliteSaver(conn=connection))

config={"configurable":{"thread_id":"1"}}

while 1:  
  humanmessage=input("input please ")
  
  if humanmessage=="end":
     break
  
  for chunk,metadata in chatai.stream({"messages":[("user",humanmessage)]},config,stream_mode="messages"): 
    print(chunk.text,end="",flush=True)

  