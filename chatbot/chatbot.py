from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph,START,END,add_messages
from typing import Annotated,TypedDict
from langgraph.checkpoint.sqlite import SqliteSaver
import uuid
import sqlite3
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode,tools_condition
from langgraph.types import Command,interrupt

load_dotenv()
llm=ChatGoogleGenerativeAI(model='gemini-3.5-flash')

@tool
def calculate(a:int,b:int):
   """"whenever calculation based anything is used or two number given"""
   decision=interrupt(f"u want {a} {b} to be multiplied??")
   if decision!="yes":
      return "no"
   
   return a*b

all_tools=[calculate]
llm=llm.bind_tools(all_tools)
class chatstate(TypedDict):
   messages:Annotated[list[str],add_messages]

def access_llm(state:chatstate):
   
   newreply=llm.invoke(state["messages"])
   return {'messages':[newreply]}

graph=StateGraph(chatstate)

graph.add_node('llm',access_llm)
graph.add_node('tools',ToolNode(all_tools))

graph.add_edge(START,'llm')

graph.add_conditional_edges('llm',tools_condition)
graph.add_edge('tools','llm')


connection=sqlite3.connect(database="chatbot.db",check_same_thread=False)
chatai=graph.compile(checkpointer=SqliteSaver(conn=connection))

config={"configurable":{"thread_id":"2"}}

while 1:  
  humanmessage=input("input please ")
  
  if humanmessage=="end":
     break

 
  for chunk,metadata in chatai.stream({"messages":[("user",humanmessage)]},config,stream_mode="messages"): 
    print(chunk.text,end="",flush=True)

  state=chatai.get_state(config)

  if state.tasks and state.tasks[0].interrupts:
     question=state.tasks[0].interrupts[0].value
     answer=input(f"{question}")
     for chunk, metadata in chatai.stream(Command(resume=answer),config,stream_mode="messages"):
         print(chunk.text,end="",flush=True)
  

  
  