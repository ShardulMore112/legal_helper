import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
from agent import agent
from rag import chat_with_docs
from pydantic import BaseModel
from typing import Optional

# Initialize the FastAPI app
app = FastAPI()

# Configure CORS to allow communication from your local HTML file
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Pydantic models for request bodies
class Query(BaseModel):
    query: str
    
class FileQuery(BaseModel):
    query: str
    file_content: str
    file_type: str
    
# Root endpoint for a simple check
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Document Assistant API!"}

# Endpoint for RAG-based questions
@app.post("/api/rag_query")
async def rag_query(file: UploadFile, query: str):
    """
    Processes a user query on an uploaded document using the RAG model.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Save the uploaded file to a temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            contents = await file.read()
            tmp_file.write(contents)
            tmp_file_path = tmp_file.name
    except Exception:
        raise HTTPException(status_code=500, detail="Could not save file")

    try:
        # Pass the temporary file path to the RAG function
        # NOTE: Your current rag.py is not set up to take a single file path.
        # You would need to modify it to accept a file path and a query.
        # This is a placeholder call.
        
        # simulated_response = chat_with_docs(query) 
        response = {"answer": "This is a placeholder response for the RAG model."}
        
        # Placeholder for the RAG functionality.
        # Since your rag.py is set up to work with a folder, this would need to be adapted.
        # For a live application, the logic in rag.py would be moved here.
        
        return JSONResponse(content={"response": response['answer']})

    finally:
        os.remove(tmp_file_path)

# Endpoint for Agent-based document processing
@app.post("/api/agent_query")
async def agent_query(file: UploadFile, query: str):
    """
    Processes a user query on an uploaded document using the agent model.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Save the uploaded file to a temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            contents = await file.read()
            tmp_file.write(contents)
            tmp_file_path = tmp_file.name
    except Exception:
        raise HTTPException(status_code=500, detail="Could not save file")
    
    try:
        # Placeholder for the agent logic
        # You would call your agent's functions here, passing the file path.
        # The agent would handle the rest of the logic.
        # The `agent` and `tools` scripts need to be adapted to handle this API call.
        
        # For demonstration purposes, this is a placeholder response.
        response_text = "This is a placeholder response for the agent model."
        return JSONResponse(content={"response": response_text})
    finally:
        os.remove(tmp_file_path)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
