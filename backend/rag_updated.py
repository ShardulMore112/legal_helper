import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")

# Initialize the LLM and Embedding model
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-preview-05-20",
        temperature=0.3,
        max_tokens=1000,
        google_api_key=GEMINI_API_KEY
    )

def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GEMINI_API_KEY
    )

def create_vector_store(file_path):
    """
    Loads a PDF, splits it into chunks, and creates a Chroma vector store.
    """
    import tempfile
    import shutil
    
    print(f"Loading document: {file_path}")
    loader = PyPDFLoader(file_path)
    data = loader.load()
    print(f"Document loaded. Total pages: {len(data)}")

    print("Splitting document into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    docs = text_splitter.split_documents(data)
    print(f"Document split. Total chunks: {len(docs)}")

    print("Creating vector store...")
    embeddings = get_embeddings()
    
    # Create a temporary directory for ChromaDB
    temp_dir = tempfile.mkdtemp()
    
    try:
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=temp_dir  # Use temporary directory
        )
        print("Vector store created successfully.")
        return vectorstore
    except Exception as e:
        # Clean up temp directory on error
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise e


def get_rag_chain(vectorstore):
    """
    Creates and returns the RAG chain for question answering.
    """
    retriever = vectorstore.as_retriever(
        search_type="similarity", 
        search_kwargs={"k": 5}
    )

    llm = get_llm()

    system_prompt = (
        "You are an expert legal assistant for question-answering tasks on legal documents. "
        "Use the following pieces of retrieved context to answer the question thoroughly and accurately. "

        "Instructions:"
        "1. If the information is not in the document, clearly state that you don't know and cannot answer based on the provided document."
        "2. Provide detailed, comprehensive answers when the information is available."
        "3. Cite relevant sections or page numbers when possible."
        "4. Explain legal terms and concepts in simple language."
        "5. Be professional but approachable in your tone."
        "6. If the question is ambiguous, ask for clarification."

        "Context: {context}"
        "\n\n"
        "Remember: Base your answers strictly on the provided document context. "
        "If you need to make any assumptions, clearly state them."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Question: {input}"),
    ])

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    return rag_chain

def chat_with_document(rag_chain, question):
    """
    Single question-answer interaction with the document.
    """
    try:
        response = rag_chain.invoke({"input": question})
        return response["answer"]
    except Exception as e:
        return f"Error processing question: {str(e)}"
# Alternative simpler approach without ChromaDB persistence
def create_vector_store_simple(file_path):
    """
    Simple in-memory vector store creation
    """
    print(f"Loading document: {file_path}")
    loader = PyPDFLoader(file_path)
    data = loader.load()
    print(f"Document loaded. Total pages: {len(data)}")

    print("Splitting document into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    docs = text_splitter.split_documents(data)
    print(f"Document split. Total chunks: {len(docs)}")

    print("Creating vector store...")
    embeddings = get_embeddings()
    
    # Use in-memory ChromaDB without persistence
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings
        # No persist_directory = in-memory only
    )
    print("Vector store created successfully.")
    return vectorstore

# For backward compatibility and testing
def main():
    """
    Main function for command-line usage (optional)
    """
    import argparse

    parser = argparse.ArgumentParser(description="A RAG system for legal documents.")
    parser.add_argument("document_path", help="Path to the legal document (PDF file).")
    args = parser.parse_args()

    document_path = args.document_path

    # Check if the document exists
    if not os.path.exists(document_path):
        print(f"Error: The file '{document_path}' was not found.")
        return

    try:
        vectorstore = create_vector_store(document_path)
        rag_chain = get_rag_chain(vectorstore)

        print("\nRAG Chatbot is ready. You can now ask questions about the document.")
        print("Type 'exit' to quit.")

        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break

            print("Thinking...")
            answer = chat_with_document(rag_chain, user_input)
            print(f"\nBot: {answer}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
