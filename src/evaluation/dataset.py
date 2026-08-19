"""A small evaluation set matched to data/documents/*.txt (the Curie family).

The last two questions are deliberately cross-document / multi-hop: their
answer requires connecting facts that live in separate documents (sample.txt,
pierre_curie.txt, joliot_curie.txt), which is where graph retrieval should
meaningfully outperform plain vector similarity search — a top-k chunk
retrieval can easily miss combining all three.
"""

EVAL_SET = [
    {
        "question": "Who did Marie Curie marry?",
        "reference": "Marie Curie married Pierre Curie in 1895.",
    },
    {
        "question": "Which elements did Marie Curie discover?",
        "reference": "Marie Curie discovered polonium and radium.",
    },
    {
        "question": "Compare Marie Curie's two Nobel Prizes: which sciences and in what years?",
        "reference": "Physics in 1903 (shared with Pierre Curie and Henri Becquerel) and Chemistry in 1911.",
    },
    {
        "question": "Where did Marie Curie study?",
        "reference": "Marie Curie studied at the University of Paris.",
    },
    {
        "question": "How is Frederic Joliot-Curie related to Marie Curie?",
        "reference": "He was her son-in-law: he married her daughter, Irene Joliot-Curie, in 1926.",
    },
    {
        "question": "How many Nobel Prizes did the Curie family win in total, and who won them?",
        "reference": (
            "Five, across three laureates: Marie Curie (Physics 1903, Chemistry 1911), "
            "Pierre Curie (Physics 1903, shared with Marie and Henri Becquerel), and "
            "Irene and Frederic Joliot-Curie (Chemistry 1935, shared)."
        ),
    },
]
