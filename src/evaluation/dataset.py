"""Evaluation set matched to data/documents/mcp_*.txt (Model Context Protocol docs).

Kept intentionally small (4 questions) to fit comfortably within Groq's
free-tier daily token budget across a full 4-config benchmark run. The last
two are deliberately cross-document / multi-hop: their answer requires
connecting facts that live in separate documents, which is where graph
retrieval should meaningfully outperform plain vector similarity search — a
top-k chunk retrieval can easily miss combining both.
"""

EVAL_SET = [
    {
        "question": "What is the MCP Inspector used for?",
        "reference": "Interactively developing and testing MCP servers and clients during development.",
    },
    {
        "question": "What are the three core primitives that MCP servers can expose?",
        "reference": "Tools, resources, and prompts.",
    },
    {
        "question": (
            "Which client-side features were deprecated in protocol version 2026-07-28, "
            "and what should replace each of them?"
        ),
        "reference": (
            "Roots, sampling, and logging. Roots should be replaced by passing directories via tool "
            "parameters, resource URIs, or server configuration. Sampling should be replaced by servers "
            "integrating directly with an LLM provider's API. Logging should be replaced by writing to "
            "stderr (stdio) or using OpenTelemetry."
        ),
    },
    {
        "question": (
            "How does the notification system let a client know when a server's tools change, and "
            "what does the client typically do in response?"
        ),
        "reference": (
            "The server must declare a listChanged capability for tools; a client opens a subscription "
            "via subscriptions/listen requesting tool list changes; when the tool list changes, the "
            "server sends a notifications/tools/list_changed message, and the client typically responds "
            "by re-issuing a tools/list request to refresh its view."
        ),
    },
]
