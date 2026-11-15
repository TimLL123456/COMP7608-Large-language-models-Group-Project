# RAG-03 Traditional RAG tutorial — TASK-21

## What and why

Traditional RAG is a **fixed retrieval → answer** baseline, not an agent. Pipeline: `data/sample.md` → `Document` → overlapping chunks → `OllamaEmbeddings` → `InMemoryVectorStore` → top-k results → `ChatOllama` answer. It is a teaching exercise separate from KORA's BIRD Mini-Dev Text-to-SQL implementation.

## Local Windows setup

Run from `Group Project/agent-study/` with Ollama server available at `http://localhost:11434`:

```powershell
ollama pull qwen3:1.7b
ollama pull embeddinggemma-2:270m
uv sync
uv run python scripts/03_traditional_rag.py
uv run python scripts/03_traditional_rag.py --chat-model qwen3:1.7b --embed-model embeddinggemma-2:270m --top-k 3 --chunk-size 450 --chunk-overlap 80
uv run python scripts/03_traditional_rag.py --chunk-size 300 --chunk-overlap 50
uv run python scripts/03_traditional_rag.py --chunk-size 600 --chunk-overlap 100
```

CLI defaults: `--chat-model qwen3:1.7b`, `--embed-model embeddinggemma-2:270m`, `--top-k 3`, `--chunk-size 450`, `--chunk-overlap 80`. Optional `--question` and `--missing-question` select evaluation prompts. The script does **not** use `os.getenv()`. Other models must be pulled beforehand.

## 1. Document loading and splitting

`Document(page_content=..., metadata={'source': 'data/sample.md'})` keeps the source of each passage. `RecursiveCharacterTextSplitter(chunk_size=450, chunk_overlap=80)` breaks the document at paragraph/line boundaries when possible. `chunk_size` and `chunk_overlap` are **characters**, not tokens. After splitting, `chunk_id` identifies each fragment. Small chunks may lose context; large chunks may include irrelevant material.

## 2. Indexing and retrieving

`OllamaEmbeddings(model='embeddinggemma-2:270m', base_url='http://localhost:11434')` converts texts and queries into numeric vectors. `InMemoryVectorStore(embedding=embedder)` keeps those vectors only for the Python process; `add_documents(chunks)` builds the index. `similarity_search_with_score(question, k=3)` returns `(Document, cosine similarity)` pairs ranked from most similar to less similar. Cosine scores indicate semantic proximity, **not factual validity**. Inspect each returned `page_content`, `source` and `chunk_id`.

## 3. Grounded generation

Retrieved passages are formatted as `[chunk N | data/sample.md]` plus full text. The fixed system instruction asks Qwen3 to cite chunk numbers, use only the excerpts and say **I don't know based on the provided document.** if evidence is missing. This is a prompt-based safeguard, not a guarantee. Check each claim against its cited snippet.

## 4. Expected output — structure only

```text
Loaded sample.md: <measured characters> characters -> <measured chunks> chunks
First chunk metadata: {'source': 'data/sample.md', 'chunk_id': 1}
Indexed <measured chunks> chunks with embeddinggemma-2:270m
=== Question: Why does RAG retrieve documents before answering? ===
Top 3 retrieved chunks (cosine similarity; higher is closer):
  1. score=<measured cosine>, data/sample.md, chunk=<n>: <actual passage>
Grounded answer: <source-grounded reply with [chunk N]>
=== Question: What is the admission price of the Mars Museum in 2030? ===
Grounded answer: I don't know based on the provided document.
```

These are expected **patterns**; neither numerical similarity scores nor generated answers should be invented. Acceptance: relevant evidence appears among top 3, a cited supported answer, an explicit unknown on the unsupported question, and successful end-to-end runs in **both environments**.

## 5. Colab — independent Run All

Open [03_traditional_rag.ipynb](../notebooks/colab/03_traditional_rag.ipynb). It installs Python dependencies and `zstd` before the official Ollama Linux installer, starts Ollama on Colab's localhost, pulls the two default models, and embeds the *exact* shared `sample.md` text to avoid reliance on private GitHub access. The notebook teaches loader, splitter, vector store, similarity scores and source-grounded generation in separate cells.

Use Runtime → Change runtime type → GPU if available, then Runtime → Run all. A fresh Colab VM starts empty; model downloads recur after reset. Colab and Windows localhost refer to different machines; generated wording and processor use may differ.

## 6. Exercises and validation log

1. Run defaults and record the retrieved top-three snippets.
2. Compare `--chunk-size 300 --chunk-overlap 50` with `600/100`; identify changed source chunks.
3. Compare `--top-k 1` versus `3`; note context size and answer quality.
4. Evaluate the Mars Museum question: a fabricated price is a failure even if similarity is high.
5. Run fresh Colab Run All and record errors, observed scores, answers and `ollama ps` processor mode.

Static file validation is **not** proof of live Ollama inference. Retain RAG-03 In Progress until local and Colab behavioral checks pass.

## References

- [InMemoryVectorStore API](https://reference.langchain.com/python/langchain-core/vectorstores/in_memory/InMemoryVectorStore)
- [Recursive text splitter](https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter)
- [Ollama model library](https://ollama.com/library)
