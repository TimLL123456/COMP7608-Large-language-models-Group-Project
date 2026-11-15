# RAG Agent Study — Shared Knowledge Sample

## What is retrieval-augmented generation?
Retrieval-augmented generation (RAG) retrieves useful passages from external documents before a language model writes an answer. The passages become context accompanying the user's question. RAG does not require retraining the chat model.

## Why retrieve documents before answering?
Language models sometimes generate plausible but unsupported statements. Retrieval provides relevant evidence for answering a specific question. It can also bring in information absent from model training data. However, retrieved text is not automatically accurate: a user should inspect the passages and verify important claims.

## Document loading and chunking
A loader reads a source file such as sample.md. A splitter divides long text into chunks, making retrieval more focused. chunk_size is the maximum length in characters, not tokens. chunk_overlap repeats a few characters across neighboring chunks to preserve context near boundaries. Very small chunks may omit context, while very large chunks may mix unrelated facts.

## Embeddings
An embedding model represents text as a numeric vector. Semantically related passages often have similar vectors. In this tutorial embeddinggemma-2:270m embeds both questions and chunks. Cosine similarity measures how closely their vector directions align; it does not guarantee that the passage answers the question.

## In-memory vector store and top-k
InMemoryVectorStore holds vectors and source metadata in the current Python process without a separate database service. For each user question, it retrieves the top-k most similar chunks. Metadata records the file path and chunk number so the answer can cite the evidence. The store is temporary and is rebuilt when the script is run again.

## Grounded generation
Traditional RAG uses a fixed sequence: load documents, split, embed, retrieve and answer. In this tutorial qwen3:1.7b receives the retrieved text and the question. A useful grounded answer refers to source chunk numbers and uses only supporting information. If the requested fact is missing from the sample, the model should explicitly state that it does not know instead of inventing a fact.

## Evaluating retrieval and generation
First verify that a relevant passage appears among the top three chunks for the question about why RAG retrieves documents. Then check whether the generated answer actually follows that passage. Finally, ask an unsupported question such as the price of admission to the Mars Museum in 2030. The sample contains no such price, so a made-up price would be a faithfulness failure. Similarity scores alone do not certify correctness.

## Scope
This tutorial is a learning sandbox, not the KORA project's BIRD Mini-Dev Text-to-SQL implementation. RAG-04 and RAG-05 can compare agentic systems with this fixed baseline.
