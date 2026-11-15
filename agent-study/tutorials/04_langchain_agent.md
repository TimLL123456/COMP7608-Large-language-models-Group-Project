# RAG-04 — LangChain tool-calling RAG agent (TASK-22)

## Goal and differences from RAG-03

RAG-03 always retrieves before generating. RAG-04 **offers** the model a tool: it can call `search_documents(query: str)` if the question needs `data/sample.md`, otherwise it can answer directly. The LLM (not Python branching) chooses its actions. This remains a beginner study project, **not** the KORA BIRD Mini-Dev Text-to-SQL implementation.

```text
Traditional RAG: Question -> retrieve top-k -> Qwen3 -> answer
Agentic RAG:  Question -> Qwen3 -> choose tool? -> tool result -> Qwen3 -> answer
                                  \------ direct answer when no tool needed
```

Use the same Qwen3 1.7B chat model, EmbeddingGemma 270M, chunk size 450, overlap 80, and top-k 3 for a fair comparison. The behavior is **not guaranteed**: small models can skip needed tools, call unnecessary tools, emit invalid tool arguments or hallucinate unsupported facts.

## Files

- `scripts/04_langchain_rag_agent.py` — Windows/PowerShell runnable example.
- `notebooks/colab/04_langchain_rag_agent.ipynb` — independent fresh Colab Run All lesson.
- `data/sample.md` — exactly the same learning evidence used in RAG-03.
- `pyproject.toml` — adds the `langchain` dependency.

## Local Windows setup

Start Windows Ollama, then run these commands **from `Group Project/agent-study`**:

```powershell
ollama list
ollama pull qwen3:1.7b
ollama pull embeddinggemma-2:270m
uv sync
uv run python scripts/04_langchain_rag_agent.py
uv run python scripts/04_langchain_rag_agent.py --top-k 3 --chunk-size 450 --chunk-overlap 80
uv run python scripts/04_langchain_rag_agent.py --question "Why does RAG retrieve documents before answering?"
# Optional: only when GPU/RAM permits
ollama pull qwen3:4b
uv run python scripts/04_langchain_rag_agent.py --chat-model qwen3:4b
ollama ps
```

Keep the default models on a GTX 1060 6GB first; switching to 4B is optional and may cause CPU offload or memory pressure.

### Command-line parameters

| Option | Default | Meaning |
| --- | --- | --- |
| `--chat-model` | `qwen3:1.7b` | Ollama model making tool decisions |
| `--embed-model` | `embeddinggemma-2:270m` | Embeds document chunks and search queries |
| `--top-k` | `3` | Maximum passages returned per tool invocation |
| `--chunk-size` | `450` | Maximum characters per chunk, not tokens |
| `--chunk-overlap` | `80` | Characters repeated between chunks |
| `--recursion-limit` | `8` | LangGraph maximum supersteps per question (bounds looping) |
| `--question` | three benchmark questions | Repeat flag to replace the defaults with custom questions |

## Walkthrough: what each component does

1. `Document` records the source path; `RecursiveCharacterTextSplitter` makes chunks and assigns `chunk_id`.
2. `OllamaEmbeddings` converts chunks and searches to vectors. `InMemoryVectorStore` holds them only for this run.
3. `@tool` turns a typed Python function and its docstring into a tool schema available to the chat model. `query: str` is the expected argument. The function searches top-k and returns actual passage text, source, chunk number and cosine score.
4. `ChatOllama` with `reasoning=False` and `temperature=0` makes the tool decision; even temperature zero does not ensure deterministic tool selection.
5. `create_agent(model=llm, tools=[search_documents], system_prompt=...)` creates a model/tool loop. Its `invoke` returns `result["messages"]`, including model outputs, tool call metadata, `ToolMessage` results, and the final answer.
6. The script prints every `AIMessage.tool_calls` (tool name/arguments) and every `ToolMessage` (returned search evidence). It also prints `invalid_tool_calls` if the model produces malformed calls, and counts calls/results.
7. `config={"recursion_limit": 8}` bounds graph supersteps **per question**; it is not a token or exact tool-call limit. A `GraphRecursionError` is reported as a bounded-loop failure instead of a success.

The tool is for *retrieving facts*, not executing arbitrary shell commands or changing files.

## Matching questions and interpretation

| Test | Question | Desired trace | Failure examples |
| --- | --- | --- | --- |
| Document fact | Why does RAG retrieve documents before answering? | `search_documents` called; citations match returned chunks | No call; invented explanation attributed to document |
| General knowledge | What is 2 + 2? | Prefer **zero** tool calls; answer 4 | Unnecessary search; wrong answer |
| Missing evidence | What is the admission price of the Mars Museum in 2030? | Do not invent a price; ideally search, then say not in document | Fabricated price or fake citation |

```text
=== Question: <actual question> ===
TOOL CALL 1: search_documents args={'query': '...'}  # only if selected
TOOL RESULT 1: name=search_documents id=...
[chunk N | data/sample.md | cosine_similarity=<actual>]
<retrieved passage>
TRACE: tool_calls=<measured>, tool_results=<measured>
FINAL ANSWER: <actual model answer>
```

The display above is a **format illustration**, not collected inference results. Similarity measures relatedness, not correctness. Inspect the answer against source chunks before scoring.

## Colab Run All

Open [04_langchain_rag_agent.ipynb](../notebooks/colab/04_langchain_rag_agent.ipynb). Each notebook is self-contained: check the assigned GPU, install Python libraries, install `zstd` before the official Ollama Linux installer, start an Ollama server inside Colab, wait for its API, download both models, index the same embedded `sample.md` text, then run the three questions with traces.

Colab `localhost:11434` refers to that hosted runtime, not Windows. Choose GPU when available, but record whether `ollama ps` reports CPU or GPU. New Colab sessions may need model downloads again. Installation invokes the official remote Ollama installer; review source/host if your environment has execution restrictions.

## Validation log — fill with real outputs

- [ ] Windows: exact command and Ollama/model versions recorded.
- [ ] Document question: actual tool arguments, retrieved chunks and supported answer captured.
- [ ] Arithmetic: actual tool-routing decision and answer captured.
- [ ] Missing fact: no fabricated admission price; capture any unexpected call/answer.
- [ ] Confirm `ollama ps` and note resource limits; compare 1.7B with 4B only if feasible.
- [ ] Fresh Colab Run All: setup and three test traces executed; record CPU/GPU and failures.
- [ ] Compare the measured tool-call counts/grounding with RAG-03 always-retrieve baseline.

**Validation distinction:** Source-code review, JSON notebook validation and a GitHub commit are not proof of live inference. Leave unverified boxes unchecked.

## References

- [LangChain create_agent()](https://reference.langchain.com/python/langchain/agents/factory/create_agent)
- [LangChain tool calling](https://docs.langchain.com/oss/python/langchain/tools)
- [LangGraph recursion limit](https://docs.langchain.com/oss/python/langgraph/graph-api#recursion-limit)
- [Ollama LangChain integration](https://docs.langchain.com/oss/python/integrations/chat/ollama)
