# RAG-05 — Deep Agents RAG demo and three-way evaluation (TASK-23)

## Objective

Compare three implementations on the **same** local document and models:

| Method | What changes |
| --- | --- |
| RAG-03 | Always retrieves before answering |
| RAG-04 | LangChain \`create_agent\` decides whether to retrieve |
| RAG-05 | \`create_deep_agent\` offers a larger harness: optional task planning, virtual files and subagent delegation |

This is a teaching sandbox, not the KORA BIRD Mini-Dev Text-to-SQL implementation.

## Prerequisites and commands (Windows)

Install/start Ollama, then pull \`qwen3:1.7b\` and \`embeddinggemma-2:270m\`. Open PowerShell in \`Group Project/agent-study\`:

\`\`\`powershell
ollama list
uv sync
uv run python scripts/05_deep_agent_rag.py
uv run python scripts/05_deep_agent_rag.py --question "Explain chunking and embeddings with evidence." --output results/rag05/demo.json
uv run python scripts/05_evaluation.py --output-dir results/rag05
ollama ps
\`\`\`

The default \`--num-ctx 8192\` is larger than RAG-04 because the Deep Agents harness offers more tools and instructions. On a GTX 1060 6GB, 8192 may be too large for available VRAM; adjust \`--num-ctx\` and model selection based on measured memory. A small \`qwen3:1.7b\` may fail to select tools or delegate correctly. Do not present a missing \`task\` call as successful delegation.

## How the code works

1. \`build_retriever()\` loads the existing \`data/sample.md\`, splits at 450 characters with 80 overlap, stores numbered chunks and builds \`InMemoryVectorStore\` using EmbeddingGemma.
2. \`search_documents\` is a typed \`@tool\`. It returns chunk IDs and cosine similarity, not verified truth.
3. \`build_model()\` creates \`ChatOllama\`. \`build_deep_agent()\` provides the retrieval tool, a specialist subagent, \`TodoListMiddleware()\` and call limits.
4. \`write_todos\` is **work tracking**, not a domain-specific SQL query planner. Deep Agents v0.7+ does not automatically add that tool unless the middleware is enabled.
5. The default state-backed filesystem supports virtual notes; it **cannot** read arbitrary Windows paths. No shell execution backend or \`execute\` tool is configured.
6. \`run_agent()\` inspects returned \`AIMessage.tool_calls\`, \`ToolMessage\`, task state and optional token usage. An available tool is not proof it was used. A specialist invoked via \`task\` may isolate its internal tool calls from the top-level trace.

## Four fixed evaluation questions

- Document present: Why does RAG retrieve documents before answering?
- General knowledge: What is 2 + 2?
- Document absent: What is the admission price of the Mars Museum in 2030?
- Multi-step evidence: Explain how chunking and embeddings work together; cite both.

\`05_evaluation.py\` runs all four against RAG-03-style mandatory retrieval, RAG-04-style \`create_agent\`, and RAG-05 \`create_deep_agent\`. It creates \`comparison.csv\` and \`per_question.json\` with latency, retrieval/tool counts, to-do/delegation/filesystem usage, reported tokens (if available) and errors. **No automatic execution accuracy or faithfulness claim is made.** Inspect citations against the source and score answers manually before drawing conclusions.

## Colab

Open \`05_deep_agent_rag.ipynb\` and \`05_evaluation.ipynb\` separately, choose Runtime → Run all. Each notebook installs \`zstd\`, Python dependencies and a **Colab-local** Ollama server; it pulls both models and writes the same sample and scripts into the notebook runtime. Colab \`localhost:11434\` is not the user's Windows Ollama server.

Both notebooks include full source, no private-repository authentication and no saved execution results. They still require a real Colab Run All test to count as validated.

## Failure modes and evidence

- \`GraphRecursionError\`: bounded stop triggered; record the failure and optionally adjust budget.
- \`ModelCallLimitMiddleware\`: limits model calls; \`ToolCallLimitMiddleware\` bounds direct \`search_documents\` calls.
- No \`write_todos\`, filesystem or \`task\` call: model did not select that capability; do not count it as observed.
- Blank/missing \`usage_metadata\`: token count unavailable, not zero verified usage.
- Unsupported facts: citations alone are insufficient; check claims against retrieved evidence.
- Colab can run on CPU with a different Ollama version: record runtime, GPU and timing differences.

## Sources

- [Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview)
- [Subagents](https://docs.langchain.com/oss/python/deepagents/subagents)
- [Filesystem backends](https://docs.langchain.com/oss/python/deepagents/backends)
- [LangChain middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in)
