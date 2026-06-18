import os
import sys
# Add current directory to path
sys.path.insert(0, os.getcwd())

import numpy as np
from rag_service import get_faq_db

db = get_faq_db()
query = "What is the baggage allowance for economy class?"

query_embedding = db.model.encode(query)

print(f"Query: {query}\n")
scores = []
for idx, doc in enumerate(db.documents):
    doc_emb = db.doc_embeddings[idx]
    dot_product = np.dot(query_embedding, doc_emb)
    norm_q = np.linalg.norm(query_embedding)
    norm_d = np.linalg.norm(doc_emb)
    similarity = dot_product / (norm_q * norm_d) if (norm_q * norm_d) > 0 else 0
    scores.append((similarity, doc))

# Sort scores in descending order
scores.sort(key=lambda x: x[0], reverse=True)

for rank, (score, doc) in enumerate(scores):
    print(f"Rank {rank + 1} (Score: {score:.4f}):")
    print(f"  {doc}\n")
