"""
Vector Database Module for GARCH Trading Bot
Stores reports in ChromaDB with Gemini embeddings for semantic search and meta-analysis
"""

import chromadb
from chromadb.config import Settings
import google.generativeai as genai
import os
from datetime import datetime
import json


# Initialize ChromaDB client
# For Cloud Functions, use persistent directory
CHROMA_PERSIST_DIR = "/tmp/chroma_db"

def get_chroma_client():
    """Get or create ChromaDB client"""
    client = chromadb.Client(Settings(
        persist_directory=CHROMA_PERSIST_DIR,
        anonymized_telemetry=False
    ))
    return client


def get_or_create_collection():
    """Get or create the reports collection"""
    client = get_chroma_client()
    
    # Create collection for GARCH reports
    collection = client.get_or_create_collection(
        name="garch_reports",
        metadata={"description": "GARCH Trading Bot AI Reports"}
    )
    
    return collection


def generate_embeddings(text):
    """
    Generate embeddings using Gemini API
    
    Args:
        text (str): Text to generate embeddings for
    
    Returns:
        list: Embedding vector
    """
    try:
        # Configure Gemini
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        genai.configure(api_key=api_key)
        
        # Generate embedding using Gemini embedding model
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        
        return result['embedding']
    
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        # Return None to use ChromaDB's default embedding
        return None


def store_report(report_text, metadata, pdf_url=None):
    """
    Store a report in the vector database
    
    Args:
        report_text (str): Full text of the AI report
        metadata (dict): Report metadata (timestamp, price, volatility, signal, etc.)
        pdf_url (str): URL to the PDF file in Cloud Storage
    
    Returns:
        str: Document ID
    """
    try:
        collection = get_or_create_collection()
        
        # Generate unique ID
        doc_id = f"report_{metadata.get('timestamp', datetime.now().isoformat())}"
        doc_id = doc_id.replace(':', '-').replace(' ', '_')
        
        # Prepare metadata (ChromaDB requires string or numeric values)
        chroma_metadata = {
            'timestamp': str(metadata.get('timestamp', '')),
            'price': float(metadata.get('price', 0)),
            'volatility': float(metadata.get('volatility', 0)),
            'signal': str(metadata.get('signal', '')),
            'pdf_url': str(pdf_url) if pdf_url else ''
        }
        
        # Add optional fields
        if 'avg_volatility' in metadata:
            chroma_metadata['avg_volatility'] = float(metadata['avg_volatility'])
        if 'persistence' in metadata:
            chroma_metadata['persistence'] = float(metadata['persistence'])
        
        # Generate embeddings
        embeddings = generate_embeddings(report_text)
        
        # Store in collection
        if embeddings:
            collection.add(
                documents=[report_text],
                embeddings=[embeddings],
                metadatas=[chroma_metadata],
                ids=[doc_id]
            )
        else:
            # Use ChromaDB's default embedding function
            collection.add(
                documents=[report_text],
                metadatas=[chroma_metadata],
                ids=[doc_id]
            )
        
        print(f"✅ Report stored in vector DB: {doc_id}")
        return doc_id
    
    except Exception as e:
        print(f"❌ Error storing report: {e}")
        return None


def search_similar_reports(query, n_results=5):
    """
    Search for similar reports using semantic search
    
    Args:
        query (str): Search query  
        n_results (int): Number of results to return
    
    Returns:
        dict: Search results with documents, metadata, and distances
    """
    try:
        collection = get_or_create_collection()
        
        # Generate query embeddings
        query_embedding = generate_embeddings(query)
        
        # Search 
        if query_embedding:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
        else:
            # Use default embedding
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
        
        return results
    
    except Exception as e:
        print(f"❌ Error searching reports: {e}")
        return {'documents': [], 'metadatas': [], 'distances': []}


def get_report_stats():
    """Get statistics about stored reports"""
    try:
        collection = get_or_create_collection()
        count = collection.count()
        
        return {
            'total_reports': count,
            'collection_name': collection.name
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {'total_reports': 0}


def delete_report(doc_id):
    """Delete a report by ID"""
    try:
        collection = get_or_create_collection()
        collection.delete(ids=[doc_id])
        print(f"✅ Report deleted: {doc_id}")
        return True
    except Exception as e:
        print(f"❌ Error deleting report: {e}")
        return False


if __name__ == "__main__":
    # Test vector DB functionality
    print("🧪 Testing Vector Database Module")
    
    # Test data
    test_report = """
    📊 REPORTE HORARIO - GARCH Trading Bot
    ⏰ 2025-11-26 01:10 UTC
    
    Resumen Ejecutivo:
    El mercado de Bitcoin muestra volatilidad moderada en las últimas 24 horas.
    El modelo GARCH(1,3) predice una volatilidad de 0.45%, indicando un mercado estable.
    
    Interpretación Económica:
    La persistencia del modelo (α+β = 0.92) sugiere que los shocks de volatilidad
    tienden a mantenerse en el tiempo, lo que es característico de activos financieros.
    
    Evaluación de Riesgos:
    - Riesgo: MEDIO
    - Volatilidad en rango normal
    - Sin eventos extraordinarios detectados
    
    Outlook:
    Se espera continuidad en la tendencia actual para las próximas horas.
    """
    
    test_metadata = {
        'timestamp': '2025-11-26 01:10:00',
        'price': 87500.0,
        'volatility': 0.45,
        'signal': 'BUY',
        'avg_volatility': 0.47,
        'persistence': 0.92
    }
    
    # Store report
    doc_id = store_report(test_report, test_metadata, 'gs://test-bucket/report.pdf')
    
    if doc_id:
        print(f"✅ Test report stored: {doc_id}")
        
        # Search for similar reports
        results = search_similar_reports("volatilidad bitcoin", n_results=2)
        
        if results['documents']:
            print(f"\n🔍 Found {len(results['documents'][0])} similar reports")
            for i, doc in enumerate(results['documents'][0]):
                print(f"\n--- Result {i+1} ---")
                print(f"Text: {doc[:100]}...")
                print(f"Metadata: {results['metadatas'][0][i]}")
        
        # Get stats
        stats = get_report_stats()
        print(f"\n📊 DB Stats: {stats}")
