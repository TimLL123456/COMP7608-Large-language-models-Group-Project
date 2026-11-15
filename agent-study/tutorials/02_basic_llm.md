# TASK-20 Tutorial — Ollama, LangChain, Parameters and Embeddings

## 1. The three layers

- **Ollama server** runs local models and exposes `http://localhost:11434`.
- **Native `ollama` Python SDK** calls server endpoints directly, e.g. `Client.chat()` and `Client.embed()`.
- **`langchain-ollama`** wraps those endpoints as `ChatOllama` and `OllamaEmbeddings`, preparing us for LangChain RAG tools and LangGraph.

The scripts use a small local `qwen3:1.7b` for chat and `embeddinggemma-2:270m` for vectors. These were verified on GTX 1060 6GB (NVIDIA driver 582.78) with Ollama 0.40.11.

## 2. Setup & execution

From the `agent-study/` folder:

```powershell
ollama list
uv sync
uv run python scripts/02_basic_llm.py
uv run python scripts/02_basic_llm.py --experiment
uv run python scripts/02_embeddings.py
uv run python scripts/02_ollama_native.py

# Optional: use downloaded models other than the defaults
uv run python scripts/02_basic_llm.py --model qwen3:4b --experiment
uv run python scripts/02_embeddings.py --model embeddinggemma-2:270m
uv run python scripts/02_ollama_native.py --chat-model qwen3:4b --embed-model embeddinggemma-2:270m
```

Model names are chosen with optional `argparse` CLI flags rather than `os.getenv()`. Without a flag, defaults remain `qwen3:1.7b` (chat) and `embeddinggemma-2:270m` (embeddings); `--experiment` still works with `--model`. The local Ollama address is `http://localhost:11434`. Pull an alternate model before using it, and use the right kind of model for chat versus embeddings.

`uv sync` reads `pyproject.toml`, resolves dependencies, creates `.venv` and generates `uv.lock` locally. Only do this on a trusted machine with Ollama running. Colab installation is explained in `01_colab_setup.ipynb`.

## 3. ChatOllama parameters

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen3:1.7b",
    base_url="http://localhost:11434",
    temperature=0.3,
    top_p=0.9,
    top_k=40,
    num_ctx=4096,
    num_predict=128,
    repeat_penalty=1.1,
    seed=42,
    keep_alive="10m",
    reasoning=False,
    validate_model_on_init=True,
)
print(llm.invoke("What is RAG?").content)
```

| Parameter | What it does | Try |
| --- | --- | --- |
| `model` | Locally downloaded Ollama model ID | `qwen3:1.7b` |
| `base_url` | Address of **this runtime's** Ollama server | `http://localhost:11434` |
| `temperature` | Sampling randomness, not factual accuracy | `0.1` vs `0.7` |
| `top_p` | Probability mass of candidate tokens | `0.5` vs `0.9` |
| `top_k` | Number of next-token candidates | `10` vs `40` |
| `num_ctx` | Token budget for context incl. input/history/output | `2048` vs `4096` |
| `num_predict` | Upper bound on output tokens, not context size | `64` vs `128` |
| `repeat_penalty` | Discourages repeated token patterns | `1.0` vs `1.2` |
| `seed` | Attempts more repeatable sampling | `42` |
| `keep_alive` | Keep model in RAM/VRAM after response | `"10m"` |
| `reasoning` | Controls thinking for supported models | `False` for simple lessons |
| `validate_model_on_init` | Verify that model was pulled | `True` |

**Important:** `num_ctx` is how much information fits in a model request; increasing it may use more VRAM. `num_predict` caps how many tokens the model can produce. These are not the same setting. A seed does **not** guarantee identical replies on different machines.

A model's reasoning setting may behave differently depending on Ollama and the model; do not assume `False` works identically for every model.

## 4. Messages, invoke, stream and response metadata

```python
from langchain_core.messages import SystemMessage, HumanMessage

messages = [
    SystemMessage(content="You are an AI tutor."),
    HumanMessage(content="Explain RAG in three sentences."),
]
response = llm.invoke(messages)
print(response.content)           # The answer text
print(response.usage_metadata)    # Input/output token counts, if supplied
print(response.response_metadata) # Model, duration, completion metadata
```

- `SystemMessage` tells the model its task/style.
- `HumanMessage` supplies the actual question.
- `invoke()` waits for one complete response.
- `stream()` yields partial chunks: `for chunk in llm.stream("Question"): print(chunk.content, end="")`.
- `batch()` submits multiple independent inputs (can raise concurrent load on a 6GB GPU); optional exercise.
- `temperature` experiment changes **only** temperature; outputs may still be similar.

For timing, native Ollama API metadata may report nanosecond durations. Different Colab GPUs, CPU/GPU offloading and caching make wall-time comparisons imperfect.

## 5. OllamaEmbeddings and similarity

```python
from langchain_ollama import OllamaEmbeddings

embedder = OllamaEmbeddings(
    model="embeddinggemma-2:270m",
    base_url="http://localhost:11434",
    num_ctx=4096,
    keep_alive=600,
    validate_model_on_init=True,
)
query_vec = embedder.embed_query("What is RAG?")
document_vecs = embedder.embed_documents(["RAG retrieves documents.", "A cat naps."])
print(len(query_vec), len(document_vecs))
```

- `embed_query()` encodes **one** search query.
- `embed_documents()` encodes **a list** of document texts.
- A vector is a list of numeric features, **not** human-readable words. EmbeddingGemma 270M returned **768 dimensions** in the verified setup; always inspect the actual length.
- **Cosine similarity** is `dot(a,b)/(norm(a)*norm(b))`. Larger similarities suggest closer directions in embedding space; they do not prove factual correctness.
- `keep_alive=600` in this LangChain embeddings class is a duration in seconds. This is an inference/runtime setting, not a quality knob.
- Advanced `dimensions` exists in current embedding APIs, but not all embedding models support arbitrary output dimensions. Do **not** request a different size until support is verified.
- Generation sampling settings (`top_p`, `temperature`) are not useful levers for improving semantic embeddings.

## 6. Native Ollama SDK: parameter location differences

```python
from ollama import Client
client = Client(host="http://localhost:11434")
reply = client.chat(
    model="qwen3:1.7b",
    messages=[{"role": "user", "content": "Explain RAG."}],
    think=False,
    stream=False,
    keep_alive="10m",
    options={"temperature": 0.3, "num_ctx": 4096, "num_predict": 128},
)
print(reply.message.content)

vectors = client.embed(
    model="embeddinggemma-2:270m",
    input=["What is RAG?", "RAG retrieves information."],
)
print(len(vectors.embeddings), len(vectors.embeddings[0]))
```

| Concept | LangChain integration | Native SDK |
| --- | --- | --- |
| Chat initialization | `ChatOllama(model=..., temperature=...)` | `Client(host=...)` |
| Call | `llm.invoke(messages)` | `client.chat(model=..., messages=...)` |
| Sampling settings | Constructor args | `options={...}` |
| Thinking | `reasoning=False` | `think=False` |
| Text result | `response.content` | `response.message.content` |
| Embedding call | `embed_query()`, `embed_documents()` | `client.embed(input=...)` |
| Streaming | `llm.stream()` | `client.chat(stream=True)` |

Not all advanced options are supported equally by every model and library version. Match the documented library and installed versions before copying unfamiliar arguments.

## 7. Experiments & expected checks

1. Run `02_basic_llm.py`. Expect readable text plus optional usage/response metadata.
2. Run `02_basic_llm.py --experiment`. Record `temperature=0.1` and `temperature=0.7` outputs without promising they differ.
3. Run `02_embeddings.py`. Expect one 768-dimensional query vector, three document vectors, and similarity rankings; the RAG document should usually rank above Bitcoin.
4. Run `02_ollama_native.py`. Expect text, token usage and two non-empty vectors.
5. In Colab, open `01_colab_setup.ipynb`, then run each lesson notebook **independently** via Runtime → Run all. Model downloads and GPU allocation vary per session.
6. Compare actual outputs, failures and GPU/CPU modes. Never label an unrun notebook as tested.

## 8. Official references

- [LangChain ChatOllama API](https://reference.langchain.com/python/langchain-ollama/chat_models/ChatOllama)
- [LangChain OllamaEmbeddings API](https://reference.langchain.com/python/langchain-ollama/embeddings/OllamaEmbeddings)
- [Ollama native Python SDK](https://github.com/ollama/ollama-python)
- [Ollama Linux installation](https://ollama.com/download/linux)

Next module: TASK-21 introduces documents, chunking, indexing and retrieval. This module deliberately **does not yet build an agent**.
