from app.generation import generate_answer
from app.evidence_verifier import verify_claim


INSUFFICIENT_EVIDENCE_MESSAGE = (
    "I couldn't find sufficient evidence in the "
    "provided documents to answer this question."
)


def answer_question(
    question: str,
    retrieved_documents: list[dict]
) -> dict:

    # ------------------------------------------------
    # Step 1: Generate a draft answer
    # ------------------------------------------------

    generated = generate_answer(
        question,
        retrieved_documents
    )

    if (
        generated["answer"]
        == "INSUFFICIENT_EVIDENCE"
    ):

        return {
            "answer": INSUFFICIENT_EVIDENCE_MESSAGE,
            "sources": [],
            "verified": False
        }

    claims = generated.get(
        "claims",
        []
    )

    if not claims:

        return {
            "answer": INSUFFICIENT_EVIDENCE_MESSAGE,
            "sources": [],
            "verified": False
        }

    # ------------------------------------------------
    # Step 2: Verify every claim
    # ------------------------------------------------

    verified_claims = []

    for claim_data in claims:

        claim = claim_data.get(
            "claim",
            ""
        )

        if not claim:
            continue

        source_ids = claim_data.get(
            "source_ids",
            []
        )

        claim_sources = []

        for source_id in source_ids:

            if not isinstance(
                source_id,
                int
            ):
                continue

            index = source_id - 1

            if (
                0 <= index
                < len(retrieved_documents)
            ):

                claim_sources.append(
                    retrieved_documents[index]
                )

        if not claim_sources:

            # No evidence was associated
            # with the claim.
            return {
                "answer": INSUFFICIENT_EVIDENCE_MESSAGE,
                "sources": [],
                "verified": False
            }

        verification = verify_claim(
            claim,
            claim_sources
        )

        if not verification.get(
            "supported",
            False
        ):

            return {
                "answer": INSUFFICIENT_EVIDENCE_MESSAGE,
                "sources": [],
                "verified": False
            }

        verified_claims.append(
            {
                "claim": claim,
                "source_ids": source_ids
            }
        )

    # ------------------------------------------------
    # Step 3: Build final answer
    # ------------------------------------------------

    if not verified_claims:

        return {
            "answer": INSUFFICIENT_EVIDENCE_MESSAGE,
            "sources": [],
            "verified": False
        }

    answer_text = generated["answer"]

    used_sources = []

    for claim in verified_claims:

        for source_id in claim["source_ids"]:

            index = source_id - 1

            if (
                0 <= index
                < len(retrieved_documents)
            ):

                document = (
                    retrieved_documents[index]
                )

                source = {
                    "document": document["source"],
                    "page": document["page"]
                }

                if source not in used_sources:

                    used_sources.append(
                        source
                    )

    return {
        "answer": answer_text,
        "sources": used_sources,
        "verified": True
    }