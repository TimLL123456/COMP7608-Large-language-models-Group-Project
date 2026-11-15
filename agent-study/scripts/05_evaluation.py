"""RAG-05: compare fixed RAG, LangChain create_agent and Deep Agents.

Run from agent-study: uv run python scripts/05_evaluation.py
Output is a trace table, NOT an automatically graded accuracy benchmark.
"""
import argparse
import csv
import importlib.util
import json
import time
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

SCRIPT = Path(__file__).with_name("05_deep_agent_rag.py")
spec = importlib.util.spec_from_file_location("rag05_demo", SCRIPT)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def main():
    parser = argparse.ArgumentParser(description="RAG-05 three-method evaluation")
    parser.add_argument("--chat-model", default="qwen3:1.7b")
    parser.add_argument("--embed-model", default="embeddinggemma-2:270m")
    parser.add_argument("--num-ctx", type=int, default=8192)
    parser.add_argument("--recursion-limit", type=int, default=24)
    parser.add_argument("--output-dir", type=Path, default=Path("results/rag05"))
    args = parser.parse_args()
    if args.num_ctx < 2048 or args.recursion_limit < 4:
        parser.error("Require --num-ctx >=2048 and --recursion-limit >=4")

    search, store, chunks = demo.build_retriever(args.embed_model)
    model = demo.build_model(args.chat_model, args.num_ctx)
    baseline = demo.build_basic_agent(model, search)
    deep = demo.build_deep_agent(model, search)
    records = []

    for question in demo.QUESTIONS:
        print(f"\nQuestion: {question}")
        started = time.perf_counter()
        try:
            # Fixed RAG: retrieval is mandatory, regardless of question type.
            matches = store.similarity_search_with_score(
                question, k=min(3, len(chunks))
            )
            excerpts = "\n\n".join(
                f"[chunk {c.metadata['chunk_id']} | data/sample.md]\n{c.page_content}"
                for c, _ in matches
            )
            reply = model.invoke([
                SystemMessage(content=(
                    "Answer only using document excerpts. If no evidence supports a "
                    "fact, say I don't know based on the document. Cite [chunk N]."
                )),
                HumanMessage(content=f"Excerpts:\n{excerpts}\n\nQuestion: {question}"),
            ])
            usage = reply.usage_metadata or {}
            fixed = {
                "approach": "traditional_rag", "question": question,
                "answer": str(reply.content),
                "seconds": round(time.perf_counter()-started, 3),
                "retrieval_calls": 1, "delegation_calls": 0, "todo_calls": 0,
                "filesystem_calls": 0, "invalid_tool_calls": 0,
                "citation_present": "[chunk " in str(reply.content),
                "usage_tokens": {
                    "input": usage.get("input_tokens", 0),
                    "output": usage.get("output_tokens", 0),
                },
                "error": None,
            }
        except Exception as exc:
            fixed = {
                "approach": "traditional_rag", "question": question,
                "answer": "", "seconds": round(time.perf_counter()-started, 3),
                "retrieval_calls": 0, "delegation_calls": 0, "todo_calls": 0,
                "filesystem_calls": 0, "invalid_tool_calls": 0,
                "citation_present": False,
                "usage_tokens": {"input": 0, "output": 0},
                "error": f"{type(exc).__name__}: {exc}",
            }
        records.append(fixed)
        records.append(demo.run_agent(
            baseline, question, "create_agent", args.recursion_limit, verbose=False
        ))
        records.append(demo.run_agent(
            deep, question, "create_deep_agent", args.recursion_limit, verbose=False
        ))
        for record in records[-3:]:
            print(f"  {record['approach']}: {record['seconds']}s, "
                  f"retrievals={record['retrieval_calls']}, "
                  f"error={record['error'] or 'none'}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "per_question.json"
    csv_path = args.output_dir / "comparison.csv"
    json_path.write_text(
        json.dumps({
            "config": {
                "chat_model": args.chat_model, "embed_model": args.embed_model,
                "num_ctx": args.num_ctx, "recursion_limit": args.recursion_limit,
                "top_k": 3, "chunk_size": 450, "chunk_overlap": 80,
                "source": "data/sample.md",
            },
            "results": records,
            "limitations": (
                "Citation presence does not prove correctness. Manually review "
                "every retrieved passage, final answer, and failure. Local and "
                "Colab runtimes differ; compare within runtime first."
            ),
        }, indent=2, ensure_ascii=False, default=str), encoding="utf-8",
    )
    cols = [
        "approach", "question", "seconds", "retrieval_calls",
        "delegation_calls", "todo_calls", "filesystem_calls",
        "invalid_tool_calls", "citation_present", "error", "answer",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    print(f"\nSaved {csv_path} and {json_path}")
    print("Inspect output manually; these results are NOT accuracy scores.")


if __name__ == "__main__":
    main()
