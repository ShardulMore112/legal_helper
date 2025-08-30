import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional
import json
import asyncio
from uuid import uuid4

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# Import our custom modules
from enhanced_tools import *
from rag_updated import create_vector_store_simple, get_rag_chain

# LangChain imports
from langchain.agents import initialize_agent
from langchain.tools import Tool
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import logging

# Disable ChromaDB telemetry to avoid errors
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)



from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Legal Document AI Assistant", description="Upload documents for RAG chatbot or AI explanation")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Create directories
Path("uploads").mkdir(exist_ok=True)
Path("static").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)

# Global variables for session management
uploaded_files = {}  # Store uploaded file info
active_rag_chains = {}  # Store RAG chains for each session
llama_llm = None

# Initialize LLMs
def initialize_llms():
    global llama_llm
    try:
        llama_llm = ChatGroq(
            model="llama3-8b-8192",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.7
        )
        print("LLMs initialized successfully")
    except Exception as e:
        print(f"Error initializing LLMs: {e}")

# Initialize LLMs at startup
initialize_llms()

# Agent tools setup
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
        description="Generates a very detailed, comprehensive, and human-readable explanation of the document."
    ),
]

agent_instructions = """
You are a formal, research-focused AI assistant specializing in legal documents.
Available tools:
1. ConvertToText — converts input data to plain text.
2. ClassifyDocument — classifies the type of the provided document.
3. SummarizeText — summarizes the given text.
4. ExplainDocument — generates a very detailed, comprehensive, yet human-readable explanation of the document.

Rules:
- If the user asks to convert data to text, use ConvertToText.
- If the user asks for a summary, use SummarizeText.
- If the user asks for a detailed explanation, use ExplainDocument.
- Always provide thorough, detailed explanations in accessible language.
- Explain all legal jargon and technical terms clearly.
"""

# Initialize agent
try:
    agent = initialize_agent(
        tools,
        llama_llm,
        agent="zero-shot-react-description",
        verbose=True,
        handle_parsing_errors=True,
        agent_kwargs={"system_message": agent_instructions}
    )
except Exception as e:
    print(f"Error initializing agent: {e}")
    agent = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_personal_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)

manager = ConnectionManager()

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a document file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")

    # Validate file type
    allowed_extensions = ['.pdf', '.txt', '.jpg', '.jpeg']
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="File type not supported. Please upload PDF, TXT, JPG, or JPEG files.")

    # Generate session ID and save file
    session_id = str(uuid4())
    file_path = f"uploads/{session_id}_{file.filename}"

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Store file info
        uploaded_files[session_id] = {
            "filename": file.filename,
            "file_path": file_path,
            "content_type": file.content_type,
            "size": file.size
        }

        return JSONResponse({
            "message": "File uploaded successfully",
            "session_id": session_id,
            "filename": file.filename,
            "file_size": file.size
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.post("/explain/{session_id}")
async def explain_document(session_id: str):
    """Generate detailed explanation of the uploaded document"""
    if session_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[session_id]
    file_path = file_info["file_path"]

    try:
        # Convert to text
        document_text = convert_to_text(file_path)

        if "Error" in document_text:
            raise HTTPException(status_code=500, detail=document_text)

        # Classify document
        doc_type = document_classifier_tool(document_text)

        # Generate detailed explanation using enhanced agent
        if agent and llama_llm:
            explanation = document_explanation_tool(document_text, doc_type, llama_llm)
        else:
            explanation = "Agent not available. Please check your API keys."

        return JSONResponse({
            "session_id": session_id,
            "filename": file_info["filename"],
            "document_type": doc_type,
            "explanation": explanation
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/create-rag/{session_id}")
async def create_rag_session(session_id: str):
    """Create RAG chatbot session for the uploaded document"""
    if session_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = uploaded_files[session_id]
    file_path = file_info["file_path"]
    
    try:
        # Only process PDF files for RAG
        if not file_path.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="RAG chatbot only supports PDF files")
        
        print(f"Creating RAG session for: {file_path}")
        
        # Use the simpler in-memory vector store
        from rag_updated import create_vector_store_simple, get_rag_chain
        vectorstore = create_vector_store_simple(file_path)  # Use the simpler version
        
        # Create RAG chain
        rag_chain = get_rag_chain(vectorstore)
        
        # Store RAG chain for this session
        active_rag_chains[session_id] = rag_chain
        
        print(f"RAG session created successfully for session: {session_id}")
        
        return JSONResponse({
            "message": "RAG chatbot session created successfully",
            "session_id": session_id,
            "filename": file_info["filename"]
        })
        
    except Exception as e:
        print(f"Error creating RAG session: {str(e)}")
        import traceback
        traceback.print_exc()  # This will print the full error trace to console
        raise HTTPException(status_code=500, detail=f"Error creating RAG session: {str(e)}")


@app.post("/create-rag/{session_id}")
async def create_rag_session(session_id: str):
    """Create RAG chatbot session for the uploaded document"""
    if session_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = uploaded_files[session_id]
    file_path = file_info["file_path"]
    
    try:
        # Only process PDF files for RAG
        if not file_path.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="RAG chatbot only supports PDF files")
        
        print(f"Creating RAG session for: {file_path}")
        
        # Create vector store with error handling
        vectorstore = create_vector_store(file_path)
        
        # Create RAG chain
        rag_chain = get_rag_chain(vectorstore)
        
        # Store RAG chain for this session
        active_rag_chains[session_id] = rag_chain
        
        print(f"RAG session created successfully for session: {session_id}")
        
        return JSONResponse({
            "message": "RAG chatbot session created successfully",
            "session_id": session_id,
            "filename": file_info["filename"]
        })
        
    except Exception as e:
        print(f"Error creating RAG session: {str(e)}")
        import traceback
        traceback.print_exc()  # This will print the full error trace to console
        raise HTTPException(status_code=500, detail=f"Error creating RAG session: {str(e)}")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for RAG chatbot"""
    await manager.connect(websocket, session_id)

    if session_id not in active_rag_chains:
        await manager.send_personal_message("Error: No RAG session found. Please upload a document first.", session_id)
        return

    rag_chain = active_rag_chains[session_id]

    try:
        await manager.send_personal_message("RAG Chatbot is ready! Ask me anything about your document.", session_id)

        while True:
            # Receive message from client
            data = await websocket.receive_text()

            # Process with RAG
            try:
                response = rag_chain.invoke({"input": data})
                answer = response.get("answer", "I couldn't generate an answer.")
                await manager.send_personal_message(f"Bot: {answer}", session_id)
            except Exception as e:
                await manager.send_personal_message(f"Error: {str(e)}", session_id)

    except WebSocketDisconnect:
        manager.disconnect(session_id)

@app.get("/sessions")
async def list_sessions():
    """List all active sessions"""
    return JSONResponse({
        "uploaded_files": len(uploaded_files),
        "active_rag_sessions": len(active_rag_chains),
        "sessions": list(uploaded_files.keys())
    })

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and cleanup files"""
    if session_id in uploaded_files:
        file_path = uploaded_files[session_id]["file_path"]
        if os.path.exists(file_path):
            os.remove(file_path)
        del uploaded_files[session_id]

    if session_id in active_rag_chains:
        del active_rag_chains[session_id]

    return JSONResponse({"message": "Session deleted successfully"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
