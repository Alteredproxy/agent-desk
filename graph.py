from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel
from langgraph.checkpoint.memory import MemorySaver

from agents import llm, triage_prompt, billing_prompt
from tools import get_order, process_refund

# The Memory of our graph!
class State(TypedDict):
    messages: Annotated[list, add_messages]
    next_department: str

class RouteDecision(BaseModel):
    """Model for routing decisions"""
    destination: str
    response: str


triage_llm = llm.with_structured_output(RouteDecision)

def triage_node(state: State):
    """Routes the user to the correct department"""
    messages = [SystemMessage(content=triage_prompt)] + state["messages"]
    decision = triage_llm.invoke(messages)
    return {"messages": [AIMessage(content=decision.response)], "next_department": decision.destination}


# Bind the tools to the LLM
billing_tools = [get_order, process_refund]
billing_llm = llm.bind_tools(billing_tools)

def billing_node(state: State):
    # Add the persona prompt to the start of the messages
    messages = [SystemMessage(content=billing_prompt)] + state["messages"]
    
    # Call the LLM
    response = billing_llm.invoke(messages)
    
    # Return the new message to be appended to the state
    return {"messages": [response]}

# This node executes the actual Python functions
tool_node = ToolNode(billing_tools)



# 1. Initialize the Memory Checkpointer
memory = MemorySaver()

# 2. Build the Graph
builder = StateGraph(State)
builder.add_node("triage", triage_node)
builder.add_node("billing", billing_node)
builder.add_node("tools", tool_node)

# 3. Routing from Triage
def route_triage(state: State):
    # Read the invisible routing decision from the state
    if state["next_department"].lower() == "billing":
        return "billing"
    # Otherwise, the Triage agent handled it, so we end!
    return END


builder.add_edge(START, "triage")
builder.add_conditional_edges("triage", route_triage)

# 4. Routing for Billing (The Tool Loop)
builder.add_conditional_edges("billing", tools_condition)
builder.add_edge("tools", "billing")

# 5. Compile with Memory AND Human-in-the-Loop!
graph = builder.compile(
    checkpointer=memory, 
    interrupt_before=["tools"]  # <-- THIS is the magic line!
)