from app.retrieval import Retriever


def main():

    retriever = Retriever()

    question = input(
        "Ask a question about your documents: "
    )

    results = retriever.retrieve(
        question,
        top_k=5
    )

    print("\n")
    print("=" * 70)
    print("FINAL RETRIEVAL RESULTS")
    print("=" * 70)

    print(
        f"\nRetrieved {len(results)} documents.\n"
    )

    for index, result in enumerate(
        results,
        start=1
    ):

        print(f"Result {index}")

        print(
            f"Source: {result['source']}"
        )

        print(
            f"Page: {result['page']}"
        )

        print(
            f"Chunk: {result['chunk_id']}"
        )

        print(
            f"Reranker score: "
            f"{result['reranker_score']:.4f}"
        )

        print("\nText:")

        print(result["text"])

        print("-" * 70)


if __name__ == "__main__":
    main()