"""A tiny evaluation set matched to data/documents/sample.txt.

Extend this (or point it at a larger, versioned file) once the corpus grows
beyond the bundled sample document.
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
]
