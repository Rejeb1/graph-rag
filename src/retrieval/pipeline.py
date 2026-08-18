"""End-to-end retrieval: NL->Cypher (with a keyword-seed fallback) fused
with vector search. `use_graph=False` isolates the vector-only path, which
the Bloc 3 benchmark uses as the baseline to measure the graph's lift.
"""

from groq import Groq

from src.retrieval.fusion import fuse
from src.retrieval.graph_retriever import keyword_seed_triples, run_cypher
from src.retrieval.nl_to_cypher import question_to_cypher
from src.retrieval.vector_retriever import search as vector_search


def retrieve(client: Groq, question: str, use_graph: bool = True) -> dict:
    graph_rows: list[dict] = []
    cypher: str | None = None

    if use_graph:
        cypher = question_to_cypher(client, question)
        if cypher:
            try:
                graph_rows = run_cypher(cypher)
            except Exception:
                graph_rows = []
        if not graph_rows:
            graph_rows = keyword_seed_triples(question)

    vector_chunks = vector_search(question)
    context = fuse(graph_rows, vector_chunks)
    return {"context": context, "cypher": cypher, "graph_rows": graph_rows, "vector_chunks": vector_chunks}
