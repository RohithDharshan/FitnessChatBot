import os
import re
import time
from dotenv import load_dotenv
from typing import TypedDict, List

# --- Core LangChain Imports ---
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- Vector Store and Local Embeddings Imports ---
from qdrant_client import QdrantClient, models
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# --- Document Loader Imports ---
from langchain_community.document_loaders import PyPDFLoader

# --- LangGraph Imports ---
from langgraph.graph import StateGraph, START, END

# --- Environment and API Key Setup ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not all([GOOGLE_API_KEY, QDRANT_URL, QDRANT_API_KEY]):
    raise ValueError("API keys and URL for Google and Qdrant must be set in the .env file.")

# --- LLM Initialization ---
# This is the correct version
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.7)
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# --- Global Vectorizer for TF-IDF ---
VECTOR_SIZE = 384
vectorizer = TfidfVectorizer(max_features=VECTOR_SIZE)

# --- GENERAL CHATBOT (LANGGRAPH) ---
class MessageState(TypedDict):
    messages: List[BaseMessage]

# Define the REVLINE persona with a prompt template
general_chat_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are REVLINE, an encouraging and knowledgeable AI fitness assistant specializing ONLY in fitness, exercise, nutrition, and wellness topics.

IMPORTANT RULES:
1. You MUST only respond to questions related to:
   - Physical fitness and exercise routines
   - Nutrition and healthy eating
   - Wellness and mental health as it relates to fitness
   - Sports and athletic performance
   - Weight management and body composition
   - Injury prevention and recovery
   - Equipment and workout gear

2. If someone asks about topics NOT related to fitness (like technology, programming, electronics, general knowledge, etc.), you MUST respond with:
   "I'm REVLINE, a specialized fitness assistant. I can only help with fitness, exercise, nutrition, and wellness topics. Please ask me something related to your health and fitness journey!"

3. Always provide safe, helpful, and motivating advice within your specialty area.

4. ALWAYS include this disclaimer at the end of fitness-related responses: 
   'Disclaimer: I am an AI assistant. Please consult with a healthcare professional or certified trainer before starting any new fitness program.'"""),
    ("placeholder", "{messages}")
])

# Chain the prompt with the LLM
general_chat_chain = general_chat_prompt | llm

def chatbot_node(state: MessageState) -> MessageState:
    # Use the new chain instead of calling llm.invoke directly
    response = general_chat_chain.invoke({"messages": state["messages"]})
    return {"messages": state["messages"] + [response]}

graph_builder_chat = StateGraph(MessageState)
graph_builder_chat.add_node("chatbot", chatbot_node)
graph_builder_chat.add_edge(START, "chatbot")
graph_builder_chat.add_edge("chatbot", END)
graph_base_chat = graph_builder_chat.compile()


# --- RAG PIPELINE with LOCAL TF-IDF EMBEDDINGS ---

def process_pdf_and_upsert_to_qdrant(pdf_bytes: bytes, collection_name: str):
    """
    Processes a PDF using local TF-IDF embeddings, pads vectors to the correct
    size, and upserts them to Qdrant.
    """
    import tempfile
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_bytes)
        tmp_file_path = tmp_file.name

    try:
        loader = PyPDFLoader(tmp_file_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = text_splitter.split_documents(docs)
        
        texts = [doc.page_content for doc in split_docs]
        tfidf_vectors = vectorizer.fit_transform(texts).toarray()
        
        # --- VECTOR PADDING LOGIC ---
        actual_dim = tfidf_vectors.shape[1]
        
        if actual_dim < VECTOR_SIZE:
            padded_vectors = np.zeros((len(tfidf_vectors), VECTOR_SIZE))
            padded_vectors[:, :actual_dim] = tfidf_vectors
            tfidf_vectors = padded_vectors

        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE),
        )

        points_to_upsert = [
            models.PointStruct(
                id=i + 1, 
                vector=vec.tolist(), 
                payload={"content": doc.page_content, "metadata": doc.metadata}
            )
            for i, (doc, vec) in enumerate(zip(split_docs, tfidf_vectors))
        ]
        
        qdrant_client.upsert(collection_name=collection_name, points=points_to_upsert, wait=True)
        print(f"Successfully processed and uploaded {len(split_docs)} chunks to Qdrant collection '{collection_name}'.")

    finally:
        os.remove(tmp_file_path)


def get_rag_chain(collection_name: str) -> Runnable:
    """
    Creates and returns a RAG chain that uses local TF-IDF for querying.
    """
    class TfidfRetriever:
        def __init__(self, vectorizer, qdrant_client, collection_name):
            self.vectorizer = vectorizer
            self.qdrant_client = qdrant_client
            self.collection_name = collection_name

        def get_relevant_documents(self, query: str):
            query_vector_sparse = self.vectorizer.transform([query]).toarray()
            
            actual_dim = query_vector_sparse.shape[1]
            if actual_dim < VECTOR_SIZE:
                padded_vector = np.zeros((1, VECTOR_SIZE))
                padded_vector[:, :actual_dim] = query_vector_sparse
                query_vector = padded_vector[0].tolist()
            else:
                query_vector = query_vector_sparse[0].tolist()

            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=3
            )
            return [HumanMessage(content=hit.payload.get("content", "")) for hit in search_results]

    retriever = TfidfRetriever(vectorizer, qdrant_client, collection_name)

    template = """You are REVLINE, a specialized fitness assistant analyzing fitness and wellness documents ONLY.

IMPORTANT RULES:
1. You MUST only answer questions related to fitness, exercise, nutrition, wellness, and health topics.
2. If the user asks about non-fitness topics (like electronics, programming, general technology, etc.) OR if the document doesn't contain fitness-related content, respond with:
   "I'm REVLINE, a specialized fitness assistant. I can only help analyze fitness, exercise, nutrition, and wellness content. This document or your question appears to be about non-fitness topics, which is outside my expertise."

3. If the question is fitness-related but the answer isn't in the fitness document context, say:
   "I cannot find that specific fitness information in the uploaded document. Please ask about the fitness content that's actually in the document, or switch to general chat for broader fitness questions."

4. Keep fitness-related answers concise and focused on the provided text.
    
Question: {question} 
Context: {context} 
Answer:"""
    prompt = ChatPromptTemplate.from_template(template)

    rag_chain = (
        {"context": retriever.get_relevant_documents, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain