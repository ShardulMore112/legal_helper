import os
import argparse
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")

# Initialize the LLM and Embedding model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-05-20",
    temperature=0.3,
    max_tokens=500,
    google_api_key=GEMINI_API_KEY
)
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GEMINI_API_KEY
)

def create_vector_store(file_path):
    """
    Loads a PDF, splits it into chunks, and creates a Chroma vector store.
    """
    print("Loading document...")
    loader = PyPDFLoader(file_path)
    data = loader.load()
    print(f"Document loaded. Total pages: {len(data)}")

    print("Splitting document into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(data)
    print(f"Document split. Total chunks: {len(docs)}")

    print("Creating vector store...")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings
    )
    print("Vector store created successfully.")
    return vectorstore

def get_rag_chain(vectorstore):
    """
    Creates and returns the RAG chain for question answering.
    """
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

    system_prompt = (
        "You are an assistant for question-answering tasks on legal documents. "
        "Use the following pieces of retrieved context to answer the question. "
        "If the information is not in the document, state that you don't know "
        "and cannot answer the question based on the provided document. "
        "Provide a concise and accurate answer based on the context. "
        "Answer in a professional and clear tone, as you are a legal assistant."
        "\n\n"
        "Context: {context}"
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "Question: {input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    return rag_chain

def main():
    """
    Main function to run the RAG system.
    """
    parser = argparse.ArgumentParser(description="A RAG system for legal documents.")
    parser.add_argument("document_path", help="Path to the legal document (PDF file).")
    args = parser.parse_args()

    document_path = args.document_path

    # Check if the document exists
    if not os.path.exists(document_path):
        print(f"Error: The file '{document_path}' was not found.")
        return

    vectorstore = create_vector_store(document_path)
    rag_chain = get_rag_chain(vectorstore)

    print("\nChatbot is ready. You can now ask questions about the document.")
    print("Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        print("Thinking...")
        try:
            response = rag_chain.invoke({"input": user_input})
            print("\nBot:", response["answer"])
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
