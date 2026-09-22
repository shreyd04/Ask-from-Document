from app.retrieval import Retriever
from app.answer_pipeline import answer_question


def main():

    retriever = Retriever()

    question = input(
        "Ask a question about your documents: "
    )

    print("\nRetrieving evidence...")

    retrieved_documents = retriever.retrieve(
        question,
        top_k=5
    )

    print(
        f"Retrieved {len(retrieved_documents)} "
        f"chunks."
    )

    print("\nGenerating and verifying answer...")

    result = answer_question(
        question,
        retrieved_documents
    )

    print("\n")
    print("=" * 70)

    print("ANSWER")

    print("=" * 70)

    print(result["answer"])

    print("\nVERIFIED:")

    print(result["verified"])

    print("\nSOURCES")

    for source in result["sources"]:

        print(
            f"- {source['document']}, "
            f"page {source['page']}"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()