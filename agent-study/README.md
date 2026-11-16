# RAG Agent Study — TASK-20 to TASK-23: Ollama, Traditional & Agentic RAG

Part of the publicly available COMP7608 [KORA Group Project](../README.md). This is a **learning sandbox**, not the KORA Text-to-SQL implementation. KORA's submitted proposal remains authoritative.

## Current scope

Learn Ollama in two interchangeable environments: local Windows + GTX 1060 (6GB) and hosted Google Colab. Use the **same** `qwen3:1.7b` chat model and `embeddinggemma-2:270m` embedding model.

| Module | Windows Python | Google Colab |
| --- | --- | --- |
| Environment | Existing Ollama 0.40.11 + uv | [01_colab_setup.ipynb](notebooks/colab/01_colab_setup.ipynb) |
| Chat + sampling parameters + streaming | [02_basic_llm.py](scripts/02_basic_llm.py) | [02_basic_llm.ipynb](notebooks/colab/02_basic_llm.ipynb) |
| Embeddings + semantic similarity | [02_embeddings.py](scripts/02_embeddings.py) | [02_embeddings.ipynb](notebooks/colab/02_embeddings.ipynb) |
| Native Ollama SDK versus LangChain | [02_ollama_native.py](scripts/02_ollama_native.py) | [02_ollama_native.ipynb](notebooks/colab/02_ollama_native.ipynb) |
| Traditional RAG: loading, chunks, search, answer | [03_traditional_rag.py](scripts/03_traditional_rag.py) | [03_traditional_rag.ipynb](notebooks/colab/03_traditional_rag.ipynb) |
| RAG-04: LangChain tool-calling agent with observable retrieval | [04_langchain_rag_agent.py](scripts/04_langchain_rag_agent.py) | [04_langchain_rag_agent.ipynb](notebooks/colab/04_langchain_rag_agent.ipynb) |
| RAG-05: Deep Agents demo and three-method evaluation | [05_deep_agent_rag.py](scripts/05_deep_agent_rag.py) · [05_evaluation.py](scripts/05_evaluation.py) | [05_deep_agent_rag.ipynb](notebooks/colab/05_deep_agent_rag.ipynb) · [05_evaluation.ipynb](notebooks/colab/05_evaluation.ipynb) |

Read the [RAG-02 parameter tutorial](tutorials/02_basic_llm.md), [RAG-03 Traditional RAG tutorial](tutorials/03_traditional_rag.md), and [RAG-04 tool-calling tutorial](tutorials/04_langchain_agent.md). Shared source: [`data/sample.md`](data/sample.md).

## Local Windows: start here

Historical Windows environment used during local checks (26 October 2026): Ollama 0.40.11, GTX 1060 6GB, driver 582.78, Python 3.14.3, uv 0.11.2. Both models were observed at **100% GPU** and the embedding model returned 768 dimensions in PowerShell tests.

Open **PowerShell**, then `cd` to this `agent-study` directory:

```powershell
ollama list
uv sync
uv run python scripts/02_basic_llm.py
uv run python scripts/02_basic_llm.py --experiment
uv run python scripts/02_embeddings.py
uv run python scripts/02_ollama_native.py
uv run python scripts/03_traditional_rag.py
uv run python scripts/04_langchain_rag_agent.py
uv run python scripts/05_deep_agent_rag.py
uv run python scripts/05_evaluation.py

# Optional model overrides
uv run python scripts/02_basic_llm.py --model qwen3:4b --experiment
uv run python scripts/02_embeddings.py --model embeddinggemma-2:270m
uv run python scripts/02_ollama_native.py --chat-model qwen3:4b --embed-model embeddinggemma-2:270m
uv run python scripts/03_traditional_rag.py --top-k 3 --chunk-size 450 --chunk-overlap 80
ollama ps
```

The early Ollama exercise scripts expose model names through CLI arguments (not environment variables); consult each script's `--help` for its accepted options. Omit the flags to keep `qwen3:1.7b` for chat and `embeddinggemma-2:270m` for embeddings. The Ollama URL stays fixed at `http://localhost:11434`; other models must be downloaded and compatible with the selected task.

`uv sync` creates a local virtual environment and generates `uv.lock`; we do not invent a lockfile without actually resolving dependencies. See `pyproject.toml` for declared dependencies.

### Troubleshooting

- `ollama` is not recognized: reopen PowerShell and verify installation/PATH.
- Cannot connect to `localhost:11434`: start the Ollama desktop app.
- Model not found: run `ollama pull qwen3:1.7b` and `ollama pull embeddinggemma-2:270m`.
- CUDA PTX error: the old NVIDIA driver 560.94 caused failures. Driver 582.78 passed two GPU smoke tests; inspect `nvidia-smi` and `ollama ps` if it happens again.
- Do not expect byte-for-byte identical output across model versions, sampling settings or different GPUs.

## Google Colab

Open **each notebook separately** in Colab, choose a GPU runtime if available, and select **Runtime → Run all**. Every exercise notebook includes its own setup and model pulls so it can run after a fresh runtime reset. `01_colab_setup.ipynb` teaches the installation process separately.

A Colab `localhost:11434` is the server **inside the hosted Colab VM**, not the Ollama running on your Windows computer. Colab may assign a CPU runtime and remove downloaded models when a session ends. These notebooks are designed for `Run all` but **have not been executed in a live Colab session yet**.

## RAG-03 Traditional RAG baseline

The new `scripts/03_traditional_rag.py` loads [`data/sample.md`](data/sample.md), creates overlapping chunks, indexes them in `InMemoryVectorStore`, prints top-k cosine retrieval with chunk metadata, and generates answers with Qwen3. It runs both a supported question and a missing-evidence question. CLI flags include `--chat-model`, `--embed-model`, `--top-k`, `--chunk-size`, `--chunk-overlap`, `--question` and `--missing-question`. The [Colab notebook](notebooks/colab/03_traditional_rag.ipynb) embeds identical sample text and installs `zstd` first. See the [Traditional RAG tutorial](tutorials/03_traditional_rag.md). **Static validation does not establish a live successful Ollama or Colab run.**

## RAG-04 LangChain tool-calling agent

**RAG-04** extends the fixed RAG-03 baseline with a `@tool` retrieval function and LangChain `create_agent()`. It uses the **same** `data/sample.md`, embeddings and chunking, but the small chat model can choose whether to search. The script prints **actual** tool calls, arguments, returned chunks/scores, and final answers for a document question, arithmetic, and a missing fact.

From this directory run `uv sync` followed by `uv run python scripts/04_langchain_rag_agent.py`. Try `--question "Why does RAG retrieve documents before answering?"` and optionally `--chat-model qwen3:4b` after pulling that model. See [the tutorial](tutorials/04_langchain_agent.md) for CLI parameters and evaluation.

The [Colab notebook](notebooks/colab/04_langchain_rag_agent.ipynb) independently sets up Ollama and models; it has no saved outputs. It is stored as actual JSON using a notebook-specific Git attributes override, because the repository's broad `*.ipynb` Git LFS rule otherwise converts new notebooks to pointers. **No live Windows or fresh Colab test is claimed by the commit.**

## Verification status

- **Verified:** Python script content reviewed for expected API usage; JSON notebooks structurally validated before GitHub commit.
- **User-reported (26 Oct 2026):** Chat and embedding inference work with local Windows Ollama. It is not yet confirmed that all three Python scripts ran successfully.
- **Still to verify:** Full execution of all three modified Python scripts on Windows and Colab notebooks in a real Colab runtime.
- **Pending verification:** Keep these checks explicitly open until the scripts and Colab notebooks run successfully; no private Notion task is required to follow this public guide.

Next: verify RAG-04 tool-choice traces on Windows and fresh Colab; retain open acceptance checks for RAG-03 separately.

## RAG-05 Deep Agents demo (TASK-23)

The [Deep Agents tutorial](tutorials/05_deep_agent.md) explains optional `TodoListMiddleware`, virtual-filesystem context handling and model-selected specialist delegation. The demo uses the same source and embeddings as RAG-03/04; the evaluator writes per-question JSON/CSV for **Traditional RAG vs create_agent vs create_deep_agent**. Run `uv sync`, `uv run python scripts/05_deep_agent_rag.py` and `uv run python scripts/05_evaluation.py`. The standalone [Colab demo](notebooks/colab/05_deep_agent_rag.ipynb) and [Colab comparison](notebooks/colab/05_evaluation.ipynb) require live Run All validation. No accuracy or successful runtime result is claimed here.
