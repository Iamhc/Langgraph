from dotenv import load_dotenv
from langgraph.graph import StateGraph,START,END
from typing import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

essay=input("essay please")

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")


class marks(TypedDict):
    rational:int
    facts:int
    creative:int

def rational(state:marks)->marks:
   n=llm.invoke(f"only give a rate from 0 to 10 for rational pov like 7 {essay}").text
   return {'rational':int(n)}

def facts(state:marks)->marks:
    n=llm.invoke(f"only give a rate from 0 to 10 for facts pov like 7 {essay}").text
    return {'facts':int(n)}

def creative(state:marks)->marks:
    n=llm.invoke(f"only give a rate from 0 to 10 for creative pov like 7 {essay}").text
    return {'creative':int(n)}

graph=StateGraph(marks)

graph.add_node('rational',rational)

graph.add_node('facts',facts)

graph.add_node('creative',creative)

graph.add_edge(START,'rational')
graph.add_edge(START,'facts')
graph.add_edge(START,'creative')

graph.add_edge('rational',END)
graph.add_edge('facts',END)
graph.add_edge('creative',END)

app=graph.compile()
print(app.invoke({}))