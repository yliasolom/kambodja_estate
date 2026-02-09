import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple
from openai import OpenAI
from config import settings

class VectorStore:
    """FAISS-based vector store for knowledge base embeddings"""
    
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.texts = []
        self.metadata = []
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.index_path = Path(__file__).parent.parent / "data" / "faiss_index"
        self.index_path.mkdir(parents=True, exist_ok=True)
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding from OpenAI"""
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return np.array(response.data[0].embedding, dtype=np.float32)
    
    def add_texts(self, texts: List[str], metadata: List[dict] = None):
        """Add texts to the index"""
        embeddings = []
        for text in texts:
            embedding = self.get_embedding(text)
            embeddings.append(embedding)
        
        embeddings_array = np.array(embeddings, dtype=np.float32)
        self.index.add(embeddings_array)
        self.texts.extend(texts)
        
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{}] * len(texts))
    
    def search(self, query: str, k: int = 3) -> List[Tuple[str, dict, float]]:
        """Search for most similar texts"""
        query_embedding = self.get_embedding(query)
        query_embedding = np.array([query_embedding], dtype=np.float32)
        
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.texts):
                results.append((
                    self.texts[idx],
                    self.metadata[idx],
                    float(distance)
                ))
        
        return results
    
    def save(self, name: str = "knowledge_base"):
        """Save index to disk"""
        index_file = self.index_path / f"{name}.index"
        texts_file = self.index_path / f"{name}_texts.pkl"
        metadata_file = self.index_path / f"{name}_metadata.pkl"
        
        faiss.write_index(self.index, str(index_file))
        
        with open(texts_file, 'wb') as f:
            pickle.dump(self.texts, f)
        
        with open(metadata_file, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        print(f"✅ Index saved to {self.index_path}")
    
    def load(self, name: str = "knowledge_base") -> bool:
        """Load index from disk"""
        index_file = self.index_path / f"{name}.index"
        texts_file = self.index_path / f"{name}_texts.pkl"
        metadata_file = self.index_path / f"{name}_metadata.pkl"
        
        if not all([index_file.exists(), texts_file.exists(), metadata_file.exists()]):
            return False
        
        self.index = faiss.read_index(str(index_file))
        
        with open(texts_file, 'rb') as f:
            self.texts = pickle.load(f)
        
        with open(metadata_file, 'rb') as f:
            self.metadata = pickle.load(f)
        
        print(f"✅ Index loaded from {self.index_path}")
        return True


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    
    return chunks
