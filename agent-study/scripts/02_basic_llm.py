"""TASK-20: ChatOllama generation parameters, messages, streaming and experiments.

Run: uv run python scripts/02_basic_llm.py
Optional: uv run python scripts/02_basic_llm.py --model qwen3:4b --experiment
Ollama must be running with qwen3:1.7b already downloaded.
"""

import argparse

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

HOST = "http://localhost:11434"

parser = argparse.ArgumentParser(description="Explore ChatOllama chat and generation settings")
parser.add_argument("--model", default="qwen3:1.7b", help="Chat model (default: %(default)s)")
parser.add_argument("--experiment", action="store_true", help="Compare temperatures")
args = parser.parse_args()

# These are ChatOllama constructor arguments, not a native SDK 'options' dict.
settings = {
    "model": args.model,
    "base_url": HOST,
    "temperature": 0.3,       # Lower is usually more predictable.
    "top_p": 0.9,             # Cumulative probability sampling threshold.
    "top_k": 40,              # Number of candidate tokens considered.
    "num_ctx": 4096,          # Context-window token budget; affects KV cache.
    "num_predict": 128,       # Maximum generated tokens (not the input length).
    "repeat_penalty": 1.1,    # Discourages repeated text.
    "seed": 42,               # Repeatability hint, not a guarantee.
    "keep_alive": "10m",      # Keep model loaded between calls.
    "reasoning": False,       # Turn off thinking for this introductory example.
    "validate_model_on_init": True,
}
llm = ChatOllama(**settings)

messages = [
    SystemMessage(content="You are a friendly technical tutor. Be concise."),
    HumanMessage(content="Explain RAG in three simple sentences."),
]
reply = llm.invoke(messages)
print("=== ChatOllama invoke() ===")
print(reply.content)
print("Usage:", reply.usage_metadata)
print("Response metadata:", reply.response_metadata)

print("\n=== Streaming (chunks arrive as they are generated) ===")
for chunk in llm.stream("Explain an embedding in one sentence."):
    print(chunk.content, end="", flush=True)
print()

if args.experiment:
    print("\n=== Temperature experiment: change one parameter ===")
    prompt = "Give a short analogy for retrieval-augmented generation."
    for temperature in (0.1, 0.7):
        test_model = ChatOllama(**{**settings, "temperature": temperature})
        result = test_model.invoke(prompt)
        print(f"temperature={temperature}: {result.content}")
    print("Outputs might be similar even with different temperatures.")
