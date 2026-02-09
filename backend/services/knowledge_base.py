from pathlib import Path
from services.vector_store import VectorStore

# Global vector store instance
_vector_store = None

def get_vector_store() -> VectorStore:
    """Get or create vector store singleton"""
    global _vector_store
    
    if _vector_store is None:
        _vector_store = VectorStore()
        # Try to load existing index
        if not _vector_store.load():
            print("⚠️  FAISS index not found. Run 'python build_index.py' first!")
            print("   Falling back to loading full knowledge base...")
            return None
    
    return _vector_store

def load_knowledge_base() -> dict:
    """Load all knowledge base files"""
    knowledge_dir = Path(__file__).parent.parent / "knowledge"
    
    knowledge = {}
    
    # Load each knowledge file
    files = {
        "villa_leasehold": "villa_leasehold.md",
        "condo_rules": "condo_rules.md",
        "costs_fees": "costs_fees.md",
    }
    
    for key, filename in files.items():
        filepath = knowledge_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                knowledge[key] = f.read()
        else:
            knowledge[key] = ""
    
    return knowledge

def get_relevant_knowledge(property_data, question: str, use_vector_search: bool = True) -> str:
    """
    Get relevant knowledge using vector search or fallback to full knowledge
    """
    if use_vector_search:
        vector_store = get_vector_store()
        
        if vector_store:
            # Build search query
            search_query = f"""
            Property type: {property_data.type}
            Question: {question}
            """
            
            # Search for relevant chunks
            results = vector_store.search(search_query, k=3)
            
            # Combine relevant chunks
            relevant_texts = [text for text, metadata, score in results]
            return "\n\n".join(relevant_texts)
    
    # Fallback to old method
    knowledge = load_knowledge_base()
    relevant = []
    
    # Add property-specific knowledge
    if property_data.type == "villa" or property_data.has_land:
        relevant.append(knowledge.get("villa_leasehold", ""))
    elif property_data.type == "condo":
        relevant.append(knowledge.get("condo_rules", ""))
    
    # Add cost knowledge if question is about costs
    if "cost" in question.lower() or "fee" in question.lower():
        relevant.append(knowledge.get("costs_fees", ""))
    
    return "\n\n".join(relevant)
