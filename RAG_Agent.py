import os
import streamlit as st
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama

st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    .stChatInput input {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        border: 1px solid #3A3A3A !important;
    }
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1E1E1E !important;
        border: 1px solid #3A3A3A !important;
        color: #E0E0E0 !important;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #2A2A2A !important;
        border: 1px solid #404040 !important;
        color: #F0F0F0 !important;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .stChatMessage .avatar {
        background-color: #00FFAA !important;
        color: #000000 !important;
    }
    .stChatMessage p, .stChatMessage div {
        color: #FFFFFF !important;
    }
    .stFileUploader {
        background-color: #1E1E1E;
        border: 1px solid #3A3A3A;
        border-radius: 5px;
        padding: 15px;
    }
    h1, h2, h3 {
        color: #00FFAA !important;
    }
    </style>
    """, unsafe_allow_html=True)

PDF_STORAGE_PATH = '/Users/pranesh/coding/langchain/documents_store/pdfs/'
PROMPT_TEMPLATE = """
You are an expert research assistant. Use the provided context to answer the query. 
If unsure, state that you don't know. Be concise and factual (max 3 sentences).

Query: {user_query} 
Context: {document_context} 
Answer:
"""

EMBEDDING_MODEL = OllamaEmbeddings(model="deepseek-llm:1.5b")
LANGUAGE_MODEL = Ollama(model="deepseek-llm:1.5b")
VECTOR_STORE = InMemoryVectorStore(embedding=EMBEDDING_MODEL)

def save_uploaded_file(uploaded_file):
    os.makedirs(PDF_STORAGE_PATH, exist_ok=True)
    file_path = os.path.join(PDF_STORAGE_PATH, uploaded_file.name)
    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())
    return file_path

def load_pdf_documents(file_path):
    loader = PDFPlumberLoader(file_path)
    return loader.load()

def chunk_documents(raw_documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
    return splitter.split_documents(raw_documents)

def index_documents(document_chunks):
    VECTOR_STORE.add_documents(document_chunks)

def find_related_documents(query):
    return VECTOR_STORE.similarity_search(query)

def generate_answer(user_query, context_documents):
    context_text = "\n\n".join([doc.page_content for doc in context_documents])
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    chain = prompt | LANGUAGE_MODEL
    return chain.invoke({"user_query": user_query, "document_context": context_text})

st.title("DocuMind AI")
st.markdown("### Your Intelligent Document Assistant")
st.markdown("---")

uploaded_pdf = st.file_uploader("Upload Research Document (PDF)", type="pdf", accept_multiple_files=False)

if uploaded_pdf:
    saved_path = save_uploaded_file(uploaded_pdf)
    raw_docs = load_pdf_documents(saved_path)
    processed_chunks = chunk_documents(raw_docs)
    index_documents(processed_chunks)
    st.success("Document processed successfully. Ask your questions below.")

    user_input = st.chat_input("Enter your question about the document...")

    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        with st.spinner("Analyzing document..."):
            relevant_docs = find_related_documents(user_input)
            ai_response = generate_answer(user_input, relevant_docs)
        with st.chat_message("assistant", avatar="🤖"):
            st.write(ai_response)
