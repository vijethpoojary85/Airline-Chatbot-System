import numpy as np
# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer
from typing import List

class FAQVectorDB:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the sentence transformer model and encode FAQ documents."""
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
        self.documents = [
            "Baggage Allowance: The baggage allowance for economy class passengers is 20kg. You can purchase additional baggage allowance up to 30kg for a fee. Excess baggage charges apply for weight above the allowance.",
            
            "Domestic Check-in Baggage Allowance: Alliance Air domestic flights have a free check-in baggage allowance of 15 Kgs per passenger (except Kullu sectors). Flights between Delhi and Kullu, and Kullu and Chandigarh have a free check-in baggage allowance of 10 Kgs per passenger.",
            
            "International Check-in Baggage Allowance: Alliance Air international flights have a free check-in baggage allowance of 20 Kgs per passenger.",
            
            "Cabin / Hand Baggage weight and pieces: Only one piece of hand baggage is permitted per passenger with a maximum weight of 5 kg. Children are entitled to the same cabin baggage allowance as adults.",
            
            "Cabin / Hand Baggage Dimensions: Hand baggage dimensions must not exceed Height 40 cm (16 inches) + Length 30 cm (12 inches) + Width 15 cm (06 inches). Total linear dimensions must not exceed 85 cm. You are also permitted to carry one laptop or ladies purse in addition to this piece.",
            
            "Check-in Baggage Dimensions and Weight: Check-in baggage dimensions must not exceed Height 80 cm (32 inches) + Length 40 cm (16 inches) + Width 150 cm (60 inches). Total linear dimensions must not exceed 270 cm. No single piece of check-in baggage can exceed 32 kg.",
            
            "Permitted Personal Items (Cabin): In addition to one piece of cabin baggage, passengers can carry one personal item such as a Lady's handbag, overcoat/wrap, camera/binoculars, reasonable reading material, infant feed/basket/bottle (if infant is carried), collapsible wheelchair/crutches/braces, walking stick, folding umbrella (no pointed edges), medicines, or a Laptop/Tablet.",
            
            "Banned and Restricted items: Power banks cannot be carried in checked baggage (only allowed in hand baggage). Samsung Galaxy Note 7 is completely banned and cannot be carried in either checked or hand baggage. Liquids, gels, or aerosols exceeding 100ml are not allowed in hand baggage, except medicines, inhalers with prescriptions, and baby food.",
            
            "Kirpan Policy: Passengers on domestic flights within India can carry a Kirpan in person if total length does not exceed 9 inches (22.86 cm), including blade <= 6 inches (15.24 cm) and handle <= 3 inches (7.62 cm). Otherwise, it must be carried in checked-in baggage.",
            
            "Infant and Student Allowances: Infants are entitled to 1 collapsible stroller/carrycot/infant car seat and hand baggage up to 5kg. Students can carry an additional 10kgs of free check-in baggage on student fare tickets with a valid student ID card (except on Kullu sectors).",
            
            "Airport Excess Baggage Charges: If baggage exceeds free allowance, charges apply at the airport: Domestic excess baggage is INR 550 per kg (inclusive of GST). International excess baggage is INR 750 per kg (inclusive of GST) or LKR 2995.45 per kg.",
            
            "Prepaid Excess Baggage (Domestic): Advance purchase of excess baggage (excluding Kullu): up to 3kg is 1350 INR, 3-5kg is 2250 INR, 5-10kg is 4500 INR, 10-15kg is 6750 INR, 15-20kg is 9000 INR, and 20-30kg is 13500 INR.",
            
            "Prepaid Excess Baggage (International): Advance purchase of excess baggage: upto 5kg is 2640 INR, 5-10kg is 5280 INR, 10-15kg is 7920 INR, and 15-20kg is 10560 INR.",
            
            "Check-in Counter Times: Check-in counters open 3 hours before departure and close 45 minutes before flight departure.",
            
            "Refund Policy: Refund requests must be submitted 24 hours before flight departure to be eligible."
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

faq_db = None

def get_faq_db():
    global faq_db
    if faq_db is None:
        faq_db = FAQVectorDB()
    return faq_db
