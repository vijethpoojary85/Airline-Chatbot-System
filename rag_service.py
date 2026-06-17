import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List

class FAQVectorDB:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the sentence transformer model and encode FAQ documents."""
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
        # Sample FAQ documents based on the airline service policy
        self.documents = [
            "Baggage allowance for economy class is 20kg. Additional baggage can be purchased up to 30kg for a fee. Excess baggage charges apply for weight above the allowance.",
            "Check-in counters open 3 hours before departure and close 45 minutes before flight departure.",
            "Refund requests must be submitted 24 hours before flight departure to receive a refund."
        ]
        
        print("Encoding FAQ documents...")
        self.doc_embeddings = self.model.encode(self.documents)

    def search(self, query: str, k: int = 1) -> List[str]:
        """Perform cosine similarity search between query and documents.
        Returns the top-k matching documents.
        """
        query_embedding = self.model.encode(query)
        
        # Compute cosine similarities
        scores = []
        for doc_emb in self.doc_embeddings:
            # Cosine similarity formula
            dot_product = np.dot(query_embedding, doc_emb)
            norm_q = np.linalg.norm(query_embedding)
            norm_d = np.linalg.norm(doc_emb)
            similarity = dot_product / (norm_q * norm_d) if (norm_q * norm_d) > 0 else 0
            scores.append(similarity)
            
        # Get top-k indices
        top_k_indices = np.argsort(scores)[::-1][:k]
        
        # Return corresponding documents
        return [self.documents[idx] for idx in top_k_indices]

# Singleton instance to avoid reloading model on every query
faq_db = None

def get_faq_db():
    global faq_db
    if faq_db is None:
        faq_db = FAQVectorDB()
    return faq_db
