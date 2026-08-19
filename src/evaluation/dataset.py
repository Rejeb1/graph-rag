"""Evaluation set matched to data/documents/mcp_*.txt (Model Context Protocol docs).

The last three questions are deliberately cross-document / multi-hop: their
answer requires connecting facts that live in separate documents, which is
where graph retrieval should meaningfully outperform plain vector similarity
search — a top-k chunk retrieval can easily miss combining all of them.
"""

EVAL_SET = [
    {
        "question": "What does the stdio transport use to communicate between processes?",
        "reference": "Standard input and standard output streams, between two processes on the same machine.",
    },
    {
        "question": "What is the MCP Inspector used for?",
        "reference": "Interactively developing and testing MCP servers and clients during development.",
    },
    {
        "question": "What are the three core primitives that MCP servers can expose?",
        "reference": "Tools, resources, and prompts.",
    },
    {
        "question": "What are the two modes of elicitation, and when is each one used?",
        "reference": (
            "Form mode, for schema-driven structured data collection, and URL mode, used for "
            "sensitive flows like OAuth or credential entry where data must stay out of band."
        ),
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
            "Compare how a local stdio server and a remote Streamable HTTP server typically differ "
            "in how many clients they serve and why."
        ),
        "reference": (
            "A stdio server runs as a local subprocess over a private pipe and typically serves a single "
            "client for its lifetime. A Streamable HTTP server runs remotely over the network and is "
            "typically built to serve many clients concurrently."
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
