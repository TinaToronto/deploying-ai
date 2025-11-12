from langchain_core.tools import tool
import chromadb
from sentence_transformers import SentenceTransformer
import json
import os

# Initialize ChromaDB with persistence
client = chromadb.PersistentClient(path="./chroma_db")

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_documents_from_json():
    """Load documents from JSON file"""
    try:
        with open('data/sample_documents.json', 'r') as f:
            data = json.load(f)
        return [doc['content'] for doc in data['documents']]
    except Exception as e:
        print(f"Error loading JSON documents: {e}")
        # Fallback to embedded documents
        return [
            "Artificial Intelligence (AI) refers to computer systems that can perform tasks typically requiring human intelligence.",
            "Machine learning is a subset of AI that enables computers to learn from data without explicit programming.",
            "Neural networks are computing systems inspired by the human brain that can recognize patterns.",
            "Python is a popular programming language for data science and machine learning due to its simplicity and extensive libraries.",
            "Climate change refers to long-term shifts in temperatures and weather patterns, primarily caused by human activities.",
            "Renewable energy sources include solar, wind, hydroelectric, and geothermal power.",
            "Blockchain is a decentralized digital ledger that records transactions across many computers.",
            "Quantum computing uses quantum-mechanical phenomena to perform computations much faster than classical computers.",
            "Virtual Reality (VR) creates immersive simulated environments, while Augmented Reality (AR) overlays digital information on the real world.",
            "The Internet of Things (IoT) describes physical objects with sensors and connectivity to exchange data over the internet."
        ]

def initialize_chroma_collection():
    """Initialize ChromaDB with documents from JSON file"""
    try:
        # Delete existing collection if it exists
        try:
            client.delete_collection("knowledge_base")
        except:
            pass
        
        # Create new collection
        collection = client.create_collection(
            name="knowledge_base",
            metadata={"description": "Technology and science knowledge base"}
        )
        
        # Load documents from JSON
        documents = load_documents_from_json()
        
        # Add documents to collection
        collection.add(
            documents=documents,
            ids=[f"doc_{i}" for i in range(len(documents))],
            metadatas=[{"category": "technology", "source": "sample"} for _ in documents]
        )
        
        print(f"✅ ChromaDB collection initialized with {len(documents)} documents")
        return True
    except Exception as e:
        print(f"❌ Error initializing ChromaDB: {e}")
        return False

# Initialize on import
collection_initialized = initialize_chroma_collection()

@tool
def semantic_search(query: str, n_results: int = 3) -> str:
    """Search through knowledge documents using semantic similarity to answer questions."""
    
    if not collection_initialized:
        return "🔧 My knowledge search is currently being set up. Please try again in a moment!"
    
    try:
        collection = client.get_collection("knowledge_base")
        
        # Perform semantic search
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if results['documents'] and results['documents'][0]:
            documents = results['documents'][0]
            
            response = f"🔍 **I found some relevant information about '{query}':**\n\n"
            
            for i, doc in enumerate(documents, 1):
                response += f"**{i}. {doc}**\n\n"
            
            response += "💡 *This information comes from my knowledge base. Would you like me to explain any of these concepts in more detail?*"
            return response
        else:
            return f"🤔 I couldn't find specific information about '{query}' in my knowledge base. Try asking about technology, science, or computing topics!"
            
    except Exception as e:
        return f"📚 My search function encountered a small issue. Why don't you try asking me to explain a concept directly instead?"