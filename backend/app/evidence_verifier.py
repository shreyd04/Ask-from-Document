import json

from groq import Groq

from app.config import GROQ_API_KEY


MODEL_NAME = "openai/gpt-oss-120b"


client = Groq(
    api_key=GROQ_API_KEY
)


VERIFIER_PROMPT = """
You are an evidence verification system.

Your ONLY task is to determine whether a factual
claim is directly supported by the supplied evidence.

Do NOT use outside knowledge.

Do NOT infer facts that are not present.

Return valid JSON:

{
    "supported": true,
    "reason": "short explanation"
}

or:

{
    "supported": false,
    "reason": "short explanation"
}

A claim is supported only when the supplied evidence
contains enough information to justify the claim.
"""


def verify_claim(
    claim: str,
    source_documents: list[dict]
) -> dict:

    evidence_parts = []

    for index, document in enumerate(
        source_documents,
        start=1
    ):

        evidence_parts.append(
            f"""
SOURCE {index}

Document: {document["source"]}
Page: {document["page"]}

Content:
{document["text"]}
"""
        )

    evidence = "\n".join(
        evidence_parts
    )

    prompt = f"""
EVIDENCE
========

{evidence}

========

CLAIM
=====

{claim}

Is this claim supported by the supplied evidence?

Return JSON only.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,

        messages=[
            {
                "role": "system",
                "content": VERIFIER_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0,

        max_completion_tokens=300,

        include_reasoning=False
    )

    raw_response = (
        response.choices[0]
        .message
        .content
    )

    try:

        return json.loads(
            raw_response
        )

    except json.JSONDecodeError:

        return {
            "supported": False,
            "reason": "Verifier returned invalid JSON."
        }