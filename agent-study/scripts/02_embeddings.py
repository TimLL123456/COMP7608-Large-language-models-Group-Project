"""TASK-20: OllamaEmbeddings, embedding dimensions and cosine similarity.

Run: uv run python scripts/02_embeddings.py
"""

import argparse
import math

from langchain_ollama import OllamaEmbeddings

HOST = "http://localhost:11434"

parser = argparse.ArgumentParser(description="Explore local Ollama text embeddings")
parser.add_argument("--model", default="embeddinggemma-2:270m", help="Embedding model (default: %(default)s)")
args = parser.parse_args()


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Return similarity between two vectors of equal length."""
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


embeddings = OllamaEmbeddings(
    model=args.model,
    base_url=HOST,
    num_ctx=4096,                # Embedding input context budget.
    keep_alive=600,              # Seconds; keeps model loaded for ten minutes.
    validate_model_on_init=True,
)

query = "What is retrieval-augmented generation?"
documents = [
    "RAG retrieves relevant documents to help a language model answer questions.",
    "Neural networks can learn patterns from examples.",
    "Bitcoin is a decentralized digital currency.",
]

query_vector = embeddings.embed_query(query)
document_vectors = embeddings.embed_documents(documents)

print("Embedding query dimensions:", len(query_vector))
print("Number of document vectors:", len(document_vectors))
print("First five vector values:", query_vector[:5])

assert len(document_vectors) == len(documents), "Missing document embedding"
assert len(query_vector) > 0, "Empty embedding vector"
assert all(len(v) == len(query_vector) for v in document_vectors)

ranked = sorted(
    ((cosine_similarity(query_vector, v), doc)
     for doc, v in zip(documents, document_vectors, strict=True)),
    reverse=True,
)
print("\nDocuments ranked by cosine similarity:")
for score, text in ranked:
    print(f"{score:.4f}  {text}")
print("\nSimilarity is a semantic signal, not proof that an answer is correct.")
