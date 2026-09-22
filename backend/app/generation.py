import json

from groq import Groq

from app.config import GROQ_API_KEY


MODEL_NAME = "openai/gpt-oss-120b"


client = Groq(
    api_key=GROQ_API_KEY
)


SYSTEM_PROMPT = """
You are a document question-answering system.

You MUST answer using ONLY the supplied document
evidence.

You must never use outside knowledge.

You must never guess.

Every factual claim in the answer must be supported
by one or more of the supplied sources.

You must return valid JSON.

The JSON must have this structure:

{
    "answer": "short answer",
    "claims": [
        {
            "claim": "factual claim",
            "source_ids": [1]
        }
    ]
}

The source_ids refer to the SOURCE numbers supplied
in the document context.

If the evidence does not contain enough information
to answer the question, return:

{
    "answer": "INSUFFICIENT_EVIDENCE",
    "claims": []
}
"""


def build_context(
    retrieved_documents: list[dict]
) -> str:

    context_parts = []

    for index, document in enumerate(
        retrieved_documents,
        start=1
    ):

        context_parts.append(
            f"""
SOURCE {index}

Document: {document["source"]}
Page: {document["page"]}

Content:
{document["text"]}
"""
        )

    return "\n".join(context_parts)


def generate_answer(
    question: str,
    retrieved_documents: list[dict]
) -> dict:

    if not retrieved_documents:

        return {
            "answer": "INSUFFICIENT_EVIDENCE",
            "claims": [],
            "sources": []
        }

    context = build_context(
        retrieved_documents
    )

    user_prompt = f"""
DOCUMENT EVIDENCE
=================

{context}

=================

QUESTION
========

{question}

Answer the question using ONLY the evidence above.

For every factual claim, provide the SOURCE number
that supports that claim.

If the evidence is insufficient, return exactly:

{{
    "answer": "INSUFFICIENT_EVIDENCE",
    "claims": []
}}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        temperature=0,

        max_completion_tokens=1200,

        include_reasoning=False
    )

    raw_response = (
        response.choices[0]
        .message
        .content
    )

    try:

        result = json.loads(
            raw_response
        )

    except json.JSONDecodeError:

        return {
            "answer": "INSUFFICIENT_EVIDENCE",
            "claims": [],
            "sources": []
        }

    sources = []

    for document in retrieved_documents:

        source = {
            "document": document["source"],
            "page": document["page"]
        }

        if source not in sources:

            sources.append(source)

    result["sources"] = sources

    return result