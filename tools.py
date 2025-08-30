import re
import requests
import json
import os
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from typing import Dict, Any

# ------------------ Convert to Text ------------------ #
def convert_to_text(file_path: str) -> str:
    """
    Converts a document (txt, pdf, jpg/jpeg) to plain text.
    """
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()
    
    if file_extension == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    elif file_extension == '.pdf':
        try:
            document_text = ""
            with fitz.open(file_path) as pdf_document:
                for page in pdf_document:
                    document_text += page.get_text()
            return document_text
        except Exception as e:
            return f"Error processing PDF: {e}"
    
    elif file_extension in ['.jpg', '.jpeg']:
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            return f"Error processing image: {e}"
    else:
        return "Unsupported file type."

# ------------------ Gemini API Helper ------------------ #
def _call_gemini_api(prompt: str, model_name: str = "gemini-2.5-flash-preview-05-20") -> str:
    """
    Calls the Gemini API to generate content based on a given prompt.
    """
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        print("Error: Gemini API key is not set. Please set the 'GEMINI_API_KEY' environment variable.")
        return "API Key Missing."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        
        result = response.json()
        candidate = result.get("candidates", [])[0]
        text = candidate.get("content", {}).get("parts", [])[0].get("text", "")
        
        return text
    
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return "An error occurred while calling the Gemini API."
    except (IndexError, KeyError) as e:
        print(f"Error parsing Gemini API response: {e}")
        return "An error occurred while parsing the API response."

# ------------------ Document Classification ------------------ #
def document_classifier_tool(document_content: str) -> str:
    """
    Classifies the document type using Gemini API.
    Returns only the category name.
    """
    system_prompt = (
        "You are a highly accurate legal document classifier. "
        "Classify the following document into one of these categories: "
        "'Non-Disclosure Agreement', 'Service Agreement', 'Lease Agreement', "
        "'Arrest Warrant', 'Power of Attorney', 'Will', 'Court Summons', 'Divorce Decree', 'Affidavit', "
        "'Partnership Agreement', 'Employment Contract', 'Memorandum of Understanding', 'Sale Deed', 'FIR', "
        "'Bail Order', 'Legal Notice', 'Court Order', 'Judgment', 'License', 'Bond', 'Complaint', "
        "'General Legal Document', 'Other Legal Document'. "
        "Respond with only the category name. If none fit, use 'General Legal Document'."
    )
    prompt = f"{system_prompt}\n\nDocument Content:\n{document_content[:4000]}"
    return _call_gemini_api(prompt).strip()

# ------------------ Summarization ------------------ #
def summarize_tool(document_content: str, document_type: str = "") -> str:
    """
    Generates a plain-language summary using Gemini API.
    """
    prompt = f"""
    You are a legal document assistant. Summarize the following document in plain language.
    Document Type: {document_type}
    Document Content:
    {document_content}
    """
    return _call_gemini_api(prompt)

# ------------------ Dynamic JSON Extraction ------------------ #
def document_explanation_tool(document_content: str, document_type: str, llama_llm) -> str:
    """
    Generates a detailed, simplified, and readable explanation of any document.
    Uses LLaMA (Groq) for reasoning and Gemini for extra refinement.
    
    Args:
        document_content: Full text of the document.
        document_type: Type of document (from classifier).
        llama_llm: Groq LLaMA instance for reasoning.
    
    Returns:
        Plain-language explanation of the document in a few moderate-length paragraphs.
    """
    # Step 1: LLaMA reasoning
    llama_prompt = f"""
    You are an intelligent assistant. Read the following document carefully and generate a clear, simplified explanation:
    
    Document Type: {document_type}
    Document Content:
    {document_content}
    
    Guidelines:
    1. Write in plain language, easy to understand.
    2. Include important names, dates, authorities, locations, and reasons.
    3. Do not make the explanation too long or too short – aim for moderate length.
    4. Organize it in 2-4 concise paragraphs.
    """
    try:
        llama_response = llama_llm.predict(llama_prompt)
    except Exception as e:
        llama_response = f"Error generating explanation with LLaMA: {e}"

    # Step 2: Gemini refinement
    gemini_prompt = f"""
    You are a smart assistant that improves clarity. 
    Refine the following explanation for readability and correctness without changing the meaning:
    
    Original Explanation:
    {llama_response}
    """
    gemini_response = _call_gemini_api(gemini_prompt)
    
    # Step 3: Return refined explanation
    return gemini_response.strip()
