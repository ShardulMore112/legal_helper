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

# ------------------ Enhanced Document Explanation ------------------ #
def document_explanation_tool(document_content: str, document_type: str, llama_llm) -> str:
    """
    Generates a very detailed, comprehensive, yet human-understandable explanation of any document.
    Uses LLaMA (Groq) for reasoning and Gemini for extra refinement.

    Args:
        document_content: Full text of the document.
        document_type: Type of document (from classifier).
        llama_llm: Groq LLaMA instance for reasoning.

    Returns:
        Very detailed but human-readable explanation of the document.
    """
    # Step 1: Enhanced LLaMA reasoning for detailed explanation
    llama_prompt = f"""
    You are an expert legal document analyst and communication specialist. Your task is to provide a very detailed, comprehensive, yet human-understandable explanation of the given document.

    Document Type: {document_type}
    Document Content:
    {document_content}

    Please provide a VERY DETAILED explanation following these guidelines:

    1. **Structure**: Organize your explanation in clear sections with headings:
       - Document Overview
       - Key Parties Involved
       - Main Legal Issues/Subject Matter
       - Important Terms and Conditions
       - Legal Implications
       - Timeline and Deadlines (if any)
       - Action Items or Next Steps

    2. **Content Requirements**:
       - Explain ALL legal jargon and technical terms in simple language
       - Include all important names, dates, locations, amounts, and legal authorities mentioned
       - Describe the purpose and significance of the document
       - Explain potential consequences or implications
       - Highlight any deadlines, obligations, or rights
       - Include background context where helpful

    3. **Writing Style**:
       - Use simple, clear language that anyone can understand
       - Avoid legal jargon unless you immediately explain it
       - Use examples or analogies to clarify complex concepts
       - Write in a conversational but professional tone
       - Include relevant details but organize them logically

    4. **Length**: This should be a comprehensive explanation - aim for detailed coverage of all important aspects. Don't rush through important points.

    Make sure to cover every significant aspect of this document in detail while keeping it accessible to non-lawyers.
    """

    try:
        llama_response = llama_llm.predict(llama_prompt)
    except Exception as e:
        llama_response = f"Error generating explanation with LLaMA: {e}"

    # Step 2: Enhanced Gemini refinement for clarity and detail
    gemini_prompt = f"""
    You are an expert editor specializing in making legal and technical content accessible to general audiences. 

    Your task is to enhance and refine the following document explanation to make it even more detailed, clear, and human-readable:

    Original Explanation:
    {llama_response}

    Enhancement Requirements:
    1. **Expand on any areas that seem brief or unclear**
    2. **Add more context and background information where helpful**
    3. **Ensure all legal terms are fully explained with examples**
    4. **Improve the flow and organization of information**
    5. **Add more detailed explanations of implications and consequences**
    6. **Include practical advice or insights where appropriate**
    7. **Maintain a warm, approachable tone while being thorough**

    The final explanation should be comprehensive enough that someone with no legal background can fully understand:
    - What this document is about
    - Who is involved and their roles
    - What are the main legal issues or agreements
    - What happens next or what actions are required
    - Why this document matters

    Please provide the enhanced, very detailed explanation that maintains accuracy while being highly accessible.
    """

    gemini_response = _call_gemini_api(gemini_prompt)

    # Step 3: Return enhanced detailed explanation
    return gemini_response.strip()
