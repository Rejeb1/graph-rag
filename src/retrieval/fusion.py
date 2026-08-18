"""Combine graph facts and vector chunks into a single context block."""


def format_graph_facts(rows: list[dict]) -> str:
    if not rows:
        return "(no graph facts retrieved)"
    lines = []
    for row in rows:
        if {"source", "relation", "target"} <= row.keys():
            lines.append(f"- {row['source']} --[{row['relation']}]--> {row['target']}")
        else:
            lines.append(f"- {row}")
    return "\n".join(lines)


def format_vector_chunks(chunks: list[dict]) -> str:
    if not chunks:
        return "(no matching document passages retrieved)"
    return "\n\n".join(f"[{c.get('source', 'unknown')}] {c['text']}" for c in chunks)


def fuse(graph_rows: list[dict], vector_chunks: list[dict]) -> str:
    return (
        "### Knowledge graph facts\n"
        f"{format_graph_facts(graph_rows)}\n\n"
        "### Retrieved document passages\n"
        f"{format_vector_chunks(vector_chunks)}"
    )
