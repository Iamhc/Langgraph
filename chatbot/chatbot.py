from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph,START,END,add_messages
from typing import Annotated,TypedDict

load_dotenv()

class chatstate(TypedDict):
   messages:Annotated[list[str],add_messages]

def access_llm(state:chatstate):
   llm=ChatGoogleGenerativeAI(model='gemini-3.5-flash')
   newreply=llm.invoke(state["messages"])
   return {'messages':newreply}

graph=StateGraph(chatstate)

graph.add_node('llm',access_llm)

graph.add_edge(START,'llm')
graph.add_edge('llm',END)

chatai=graph.compile()

while 1:  
  humanmessage=input("input please ")
  
  if humanmessage=="end":
     break
  
  result=chatai.invoke({"messages":[("user",humanmessage)]})
  print(result["messages"][-1].text)