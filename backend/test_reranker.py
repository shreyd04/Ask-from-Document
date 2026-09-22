from app.retrieval import Retriever


def main():

    retriever = Retriever()

    question = input(
        "Ask a question about your documents: "
    )

    print("\nRunning hybrid retrieval...")

    hybrid_results = retriever.hybrid_search(
        query=question,
        top_k=10,
        candidate_k=10
    )

    print(
        f"Retrieved {len(hybrid_results)} "
        f"hybrid candidates."
    )

    print("\nRunning cross-encoder reranking...")

    reranked_results = retriever.reranker.rerank(
        query=question,
        documents=hybrid_results,
        top_k=5
    )

    print("\n")
    print("=" * 70)
    print("RERANKED RESULTS")
    print("=" * 70)

    for index, result in enumerate(
        reranked_results,
        start=1
    ):

        print(f"\nResult {index}")

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