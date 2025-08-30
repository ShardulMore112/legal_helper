import os
import json
from dotenv import load_dotenv
from langchain.agents import initialize_agent
from langchain.tools import Tool
from tools import *
from langchain_groq import ChatGroq
import warnings
warnings.filterwarnings("ignore", category=UserWarning)  # suppress LangChain deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


load_dotenv()

# -------------------- Agent LLM -------------------- #
# This LLaMA/Groq instance is used for reasoning in the tools
llama_llm = ChatGroq(
    model="llama3-8b-8192",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)

# -------------------- Tools -------------------- #
tools = [
    Tool(
        name="ConvertToText",
        func=convert_to_text,
        description="Converts input data to plain text."
    ),
    Tool(
        name="ClassifyDocument",
        func=document_classifier_tool,
        description="Classifies the type of the provided document."
    ),
    Tool(
        name="SummarizeText",
        func=summarize_tool,
        description="Summarizes the given text."
    ),
    Tool(
        name="ExplainDocument",
        func=document_explanation_tool,
        description="Generates a clear, detailed, and simplified explanation of the document using LLaMA + Gemini."
    ),
]

# -------------------- Agent Instructions -------------------- #
agent_instructions = """
You are a formal, research-focused AI assistant.
Available tools:
1. ConvertToText — converts input data to plain text.
2. ClassifyDocument — classifies the type of the provided document.
3. SummarizeText — summarizes the given text.
4. ExplainDocument — generates a detailed, simplified, and readable explanation of the document using LLaMA + Gemini.

Rules:
- If the user asks to convert data to text, use ConvertToText.
- If the user asks for a summary, use SummarizeText.
- If the user asks for a detailed explanation, use ExplainDocument.
- Always answer in a formal, detailed, and readable tone use legal jargans but explain them properly.
"""

# -------------------- Initialize Agent -------------------- #
agent = initialize_agent(
    tools,
    llama_llm,  # The reasoning LLM for tool orchestration; you can still call Gemini inside tools
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True,
    agent_kwargs={"system_message": agent_instructions}
)

# -------------------- Main Execution -------------------- #
if __name__ == "__main__":
    print("Welcome to the Legal Helper Agent!")
    file_path = r"Mr_Vijay_Agarwal_Ors_vs_Harinarayan_G_Bajaj_Ors_on_27_February_2013.PDF"

    # Step 1: Convert to text
    text = convert_to_text(file_path)

    # Step 2: Classify document
    doc_type = document_classifier_tool(text)

    # Step 3: Generate detailed explanation
    explanation = document_explanation_tool(text, doc_type, llama_llm)
    
    print("\nDocument Explanation:\n", explanation)
