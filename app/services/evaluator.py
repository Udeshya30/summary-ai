from rouge import Rouge
from sentence_transformers import SentenceTransformer, util

# Load once (enterprise performance optimization)
model = SentenceTransformer('all-MiniLM-L6-v2')

def evaluate_summary(generated: str, reference: str):
    rouge = Rouge()
    scores = rouge.get_scores(generated, reference)[0]
    return scores  # Dict with all ROUGE values

def semantic_similarity(generated, reference):
    emb1 = model.encode(generated, convert_to_tensor=True)
    emb2 = model.encode(reference, convert_to_tensor=True)
    return float(util.cos_sim(emb1, emb2))
