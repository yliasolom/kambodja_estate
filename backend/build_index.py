#!/usr/bin/env python3
"""
Script to build FAISS index from knowledge base files.
Run this once to create embeddings, then rerun when knowledge base is updated.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.vector_store import VectorStore, chunk_text
from services.knowledge_base import load_knowledge_base

def build_index():
    """Build FAISS index from knowledge base"""
    print("🔨 Building FAISS index from knowledge base...")
    
    # Load knowledge base
    knowledge = load_knowledge_base()
    
    # Create vector store
    vector_store = VectorStore()
    
    # Process each knowledge file
    all_texts = []
    all_metadata = []
    
    for source, content in knowledge.items():
        print(f"📄 Processing {source}...")
        
        # Split into chunks
        chunks = chunk_text(content, chunk_size=400, overlap=50)
        
        # Add metadata
        metadata = [{"source": source, "chunk_id": i} for i in range(len(chunks))]
        
        all_texts.extend(chunks)
        all_metadata.extend(metadata)
        
        print(f"   Created {len(chunks)} chunks")
    
    # Add to index
    print(f"\n🔄 Creating embeddings for {len(all_texts)} chunks...")
    print("   (This will take a minute, using OpenAI API...)")
    
    vector_store.add_texts(all_texts, all_metadata)
    
    # Save index
    print("\n💾 Saving index to disk...")
    vector_store.save()
    
    print(f"\n✅ Done! Index contains {len(all_texts)} text chunks")
    print(f"   Index saved to: backend/data/faiss_index/")
    print("\n🚀 You can now start the backend server")

if __name__ == "__main__":
    build_index()
