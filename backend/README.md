# Legal Document AI Assistant

A comprehensive FastAPI web application that provides two powerful ways to analyze legal documents:

1. **AI Document Explanation**: Get detailed, human-readable explanations of your documents
2. **RAG Chatbot**: Interactive Q&A with your documents using Retrieval-Augmented Generation

## Features

- **Drag & Drop File Upload**: Easy file upload with support for PDF, TXT, JPG, and JPEG files
- **Document Classification**: Automatically classify document types
- **Detailed Explanations**: Generate comprehensive, yet accessible explanations of legal documents
- **Interactive Chatbot**: Ask specific questions about your documents using RAG technology
- **Real-time Chat**: WebSocket-powered chat interface for seamless interaction
- **Responsive Design**: Modern, mobile-friendly web interface
- **Session Management**: Handle multiple document sessions

## Tech Stack

- **Backend**: FastAPI, Python 3.8+
- **AI/ML**: LangChain, Google Gemini, Groq LLaMA, ChromaDB
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **WebSockets**: Real-time chat communication
- **Document Processing**: PyMuPDF, pytesseract, Pillow

## Prerequisites

1. **Python 3.8 or higher**
2. **API Keys** (free tier available):
   - [Groq API Key](https://console.groq.com/) - For LLaMA model access
   - [Google Gemini API Key](https://aistudio.google.com/app/apikey) - For document processing

## Installation & Setup

### 1. Clone or Download the Project

Save all the provided files in a project directory:

```
legal-document-ai/
├── main.py
├── enhanced_tools.py
├── rag_updated.py
├── requirements_updated.txt
├── .env.template
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv legal_ai_env

# Activate virtual environment
# On Windows:
legal_ai_env\Scripts\activate
# On macOS/Linux:
source legal_ai_env/bin/activate
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements_updated.txt
```

### 4. Set up Environment Variables

```bash
# Copy the template
cp .env.template .env

# Edit .env file and add your API keys
# Use any text editor to edit the .env file
```

**Required API Keys:**
- **GROQ_API_KEY**: Get from [Groq Console](https://console.groq.com/)
- **GEMINI_API_KEY**: Get from [Google AI Studio](https://aistudio.google.com/app/apikey)

### 5. Update Import Statements

In `main.py`, update the imports to use the correct filenames:

```python
# Change this line:
from enhanced_tools import *
# And this line:
from rag import create_vector_store, get_rag_chain

# To:
from enhanced_tools import *
from rag_updated import create_vector_store, get_rag_chain
```

## Running the Application

### 1. Start the Server

```bash
# Make sure your virtual environment is activated
python main.py

# Or alternatively:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Access the Application

Open your web browser and navigate to:
```
http://localhost:8000
```

## Usage Guide

### Document Explanation Feature

1. **Upload Document**: Drag and drop or browse to select your document (PDF, TXT, JPG, JPEG)
2. **Choose "Get Detailed Explanation"**: Click the explanation button
3. **Review Results**: Get a comprehensive, human-readable explanation of your document

### RAG Chatbot Feature

1. **Upload PDF Document**: Only PDF files are supported for RAG
2. **Choose "Start RAG Chatbot"**: Click the chatbot button
3. **Wait for Processing**: The system will create a vector database from your document
4. **Start Chatting**: Ask any questions about your document
5. **Interactive Q&A**: Get specific answers based on document content

### Sample Questions for RAG Chatbot

- "What are the main terms of this agreement?"
- "Who are the parties involved?"
- "What are the key dates and deadlines?"
- "What are the payment terms?"
- "What happens if someone breaches this contract?"

## File Structure

```
legal-document-ai/
├── main.py                     # FastAPI application
├── enhanced_tools.py           # Enhanced AI tools with detailed explanations
├── rag_updated.py             # RAG functionality for chatbot
├── requirements_updated.txt    # Python dependencies
├── .env                       # Environment variables (create from template)
├── .env.template              # Environment template
├── uploads/                   # Uploaded files storage (auto-created)
├── templates/
│   └── index.html            # Main web interface
└── static/
    ├── style.css             # Styling
    └── script.js             # Frontend functionality
```

## API Endpoints

- `GET /` - Main web interface
- `POST /upload` - Upload document
- `POST /explain/{session_id}` - Get document explanation
- `POST /create-rag/{session_id}` - Create RAG session
- `WebSocket /ws/{session_id}` - Chat with document
- `GET /sessions` - List active sessions
- `DELETE /session/{session_id}` - Delete session

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure to update import statements in main.py to use correct filenames
2. **API Key Errors**: Verify your API keys are correctly set in .env file
3. **File Upload Issues**: Check file size (max 50MB) and type (PDF, TXT, JPG, JPEG)
4. **Port Already in Use**: Change the port in main.py or kill existing process

### Getting API Keys

**Groq API Key (Free):**
1. Go to [Groq Console](https://console.groq.com/)
2. Sign up/login
3. Navigate to API Keys section
4. Create new API key

**Google Gemini API Key (Free):**
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the generated key

## Customization

### Modify Document Explanation Detail Level

Edit the prompts in `enhanced_tools.py` in the `document_explanation_tool` function to adjust the level of detail or specific focus areas.

### Change RAG Settings

Modify parameters in `rag_updated.py`:
- `chunk_size` and `chunk_overlap` for document splitting
- `k` parameter for number of retrieved chunks
- Temperature and max_tokens for LLM responses

### Styling Customization

Edit `static/style.css` to change colors, fonts, layout, or add new visual elements.

## Security Notes

- Never commit your `.env` file to version control
- Use environment variables for all sensitive information
- Consider adding authentication for production use
- Regularly update dependencies for security patches

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all API keys are correctly configured
3. Ensure all dependencies are properly installed
4. Check the console logs for detailed error messages

## License

This project is for educational and demonstration purposes. Please ensure compliance with all API providers' terms of service.
