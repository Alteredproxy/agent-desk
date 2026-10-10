import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

# 1. Initialize the LLM (We use Groq for speed!)
llm = ChatGroq(model_name="openai/gpt-oss-120b", temperature=0)

# 2. The Triage Prompt
triage_prompt = """You are a customer support triage agent. 
Your job is to greet the customer and figure out what department they need.
If they are asking about an order, a refund, or a charge, route them to Billing.
If they are asking about a bug or how to use a feature, route them to Technical.
Otherwise, just chat with them.

CRITICAL INSTRUCTION: You MUST use the provided tool to output your decision.
Put your conversational greeting inside the 'response' field of the tool.
If no department is needed yet, set the 'destination' field to 'none'.
"""

# 3. The Billing Prompt
billing_prompt = """You are a Billing Support Agent.
You have access to tools to look up orders and process refunds.
Always look up the order first before discussing it."""
