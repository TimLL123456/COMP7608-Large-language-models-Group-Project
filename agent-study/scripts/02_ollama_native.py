"""TASK-20: Compare the native Ollama SDK with LangChain ChatOllama.

Run: uv run python scripts/02_ollama_native.py
Optional: uv run python scripts/02_ollama_native.py --chat-model qwen3:4b --embed-model embeddinggemma-2:270m
The native SDK sends sampling settings inside 'options'.
"""

import argparse

from ollama import Client

HOST = "http://localhost:11434"

parser = argparse.ArgumentParser(description="Explore native Ollama chat and embedding APIs")
parser.add_argument("--chat-model", default="qwen3:1.7b", help="Chat model (default: %(default)s)")
parser.add_argument("--embed-model", default="embeddinggemma-2:270m", help="Embedding model (default: %(default)s)")
args = parser.parse_args()

client = Client(host=HOST)

reply = client.chat(
    model=args.chat_model,
    messages=[
        {"role": "system", "content": "You are an AI tutor. Reply concisely."},
        {"role": "user", "content": "Explain RAG in three simple sentences."},
    ],
    stream=False,
    think=False,
    keep_alive="10m",
    options={
        "temperature": 0.3,
        "top_p": 0.9,
        "top_k": 40,
        "num_ctx": 4096,
        "num_predict": 128,
        "repeat_penalty": 1.1,
        "seed": 42,
    },
)
print("Native chat:", reply.message.content)
print("Input tokens:", reply.prompt_eval_count)
print("Output tokens:", reply.eval_count)

texts = [
    "What is retrieval-augmented generation?",
    "RAG retrieves relevant documents to support answers.",
]
result = client.embed(
    model=args.embed_model,
    input=texts,
    keep_alive="10m",
)
print("Native embedding count:", len(result.embeddings))
print("First vector dimensions:", len(result.embeddings[0]))
assert len(result.embeddings) == len(texts)
