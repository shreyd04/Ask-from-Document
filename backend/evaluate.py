import json
from pathlib import Path

from app.retrieval import Retriever
from app.answer_pipeline import answer_question


DATASET_PATH = (
    Path(__file__).parent
    / "evaluation"
    / "golden_dataset.json"
)
MIN_RETRIEVAL_SCORE = 0.70
MIN_CITATION_SCORE = 0.80
MIN_VERIFICATION_RATE = 0.80

def load_dataset():

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def normalize(text: str) -> str:

    return " ".join(
        text.lower().split()
    )


def source_matches(
    actual_source: dict,
    expected_source: dict
) -> bool:

    actual_document = normalize(
        actual_source["document"]
    )

    expected_document = normalize(
        expected_source["document"]
    )

    actual_page = int(
        actual_source["page"]
    )

    expected_page = int(
        expected_source["page"]
    )

    return (
        actual_document
        == expected_document
        and actual_page
        == expected_page
    )


def calculate_retrieval_score(
    retrieved_documents: list[dict],
    expected_sources: list[dict]
) -> float:

    if not expected_sources:

        return 0.0

    matched = 0

    for expected in expected_sources:

        found = False

        for retrieved in retrieved_documents:

            actual = {
                "document": retrieved["source"],
                "page": retrieved["page"]
            }

            if source_matches(
                actual,
                expected
            ):

                found = True
                break

        if found:

            matched += 1

    return matched / len(
        expected_sources
    )


def calculate_answer_match(
    generated_answer: str,
    expected_answer: str
) -> float:

    generated = normalize(
        generated_answer
    )

    expected = normalize(
        expected_answer
    )

    if not generated:
        return 0.0

    if generated == expected:
        return 1.0

    # We intentionally do not call
    # this a semantic correctness score.
    #
    # This is only an exact normalized
    # match indicator.

    return 0.0


def evaluate_question(
    retriever,
    item: dict
) -> dict:

    question = item["question"]

    expected_answer = item[
        "expected_answer"
    ]

    expected_sources = item[
        "expected_sources"
    ]

    retrieved_documents = (
        retriever.retrieve(
            question,
            top_k=5
        )
    )

    retrieval_score = (
        calculate_retrieval_score(
            retrieved_documents,
            expected_sources
        )
    )

    result = answer_question(
        question,
        retrieved_documents
    )

    generated_answer = result[
        "answer"
    ]

    answer_match = (
        calculate_answer_match(
            generated_answer,
            expected_answer
        )
    )

    generated_sources = result.get(
        "sources",
        []
    )

    citation_score = (
        calculate_retrieval_score(
            [
                {
                    "source": source[
                        "document"
                    ],
                    "page": source["page"]
                }
                for source in generated_sources
            ],
            expected_sources
        )
    )

    return {
        "id": item["id"],
        "question": question,
        "retrieval_score": retrieval_score,
        "answer_exact_match": answer_match,
        "citation_score": citation_score,
        "verified": result.get(
            "verified",
            False
        ),
        "generated_answer": generated_answer
    }


def main():

    dataset = load_dataset()

    print(
        f"Loaded {len(dataset)} "
        f"evaluation questions."
    )

    retriever = Retriever()

    results = []

    for index, item in enumerate(
        dataset,
        start=1
    ):

        print(
            f"\nEvaluating "
            f"{index}/{len(dataset)}: "
            f"{item['id']}"
        )

        result = evaluate_question(
            retriever,
            item
        )

        results.append(result)

        print(
            f"Retrieval score: "
            f"{result['retrieval_score']:.2f}"
        )

        print(
            f"Answer exact match: "
            f"{result['answer_exact_match']:.2f}"
        )

        print(
            f"Citation score: "
            f"{result['citation_score']:.2f}"
        )

        print(
            f"Verified: "
            f"{result['verified']}"
        )

    # ------------------------------------
    # Aggregate metrics
    # ------------------------------------

    question_count = len(results)

    if question_count == 0:

        print("No evaluation questions found.")

        return

    average_retrieval = (
        sum(
            result["retrieval_score"]
            for result in results
        )
        / question_count
    )

    average_exact_match = (
        sum(
            result["answer_exact_match"]
            for result in results
        )
        / question_count
    )

    average_citation = (
        sum(
            result["citation_score"]
            for result in results
        )
        / question_count
    )

    verification_rate = (
        sum(
            1
            for result in results
            if result["verified"]
        )
        / question_count
    )

    print("\n")
    print("=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    print(
        f"Questions: "
        f"{question_count}"
    )

    print(
        f"Average retrieval score: "
        f"{average_retrieval:.3f}"
    )

    print(
        f"Average exact answer match: "
        f"{average_exact_match:.3f}"
    )

    print(
        f"Average citation score: "
        f"{average_citation:.3f}"
    )

    print(
        f"Verification rate: "
        f"{verification_rate:.3f}"
    )

    print("=" * 70)
    failed = False
    if average_retrieval < MIN_RETRIEVAL_SCORE:
        print(
            "\nFAIL: Retrieval score is below "
            f"{MIN_RETRIEVAL_SCORE:.2f}"
        )
        failed = True
    if average_citation < MIN_CITATION_SCORE:
        print(
            "\nFAIL: Citation score is below "
            f"{MIN_CITATION_SCORE:.2f}"
        )
        failed = True
    if verification_rate < MIN_VERIFICATION_RATE:
        print(
            "\nFAIL: Verification rate is below "
            f"{MIN_VERIFICATION_RATE:.2f}"
        )
        failed = True
    if failed:
        print(
            "\nEvaluation FAILED."
        )
        raise SystemExit(1)
    print(
        "\nEvaluation PASSED."
    )

if __name__ == "__main__":
    main()



