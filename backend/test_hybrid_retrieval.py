from app.retrieval import Retriever


def main():

    retriever = Retriever()

    question = input(
        "Ask a question about your documents: "
    )

    print("\nRunning hybrid retrieval...\n")

    vector_results = retriever.vector_search(
        query=question,
        top_k=5
    )

    bm25_results = retriever.bm25_search(
        query=question,
        top_k=5
    )

    hybrid_results = retriever.hybrid_search(
        query=question,
        top_k=5,
        candidate_k=10
    )

    print("\n\nVECTOR SEARCH")
    print("=" * 70)

    for index, result in enumerate(
        vector_results,
        start=1
    ):

        print(
            f"{index}. "
            f"{result['source']} "
            f"page {result['page']}"
        )

    print("\n\nBM25 SEARCH")
    print("=" * 70)

    for index, result in enumerate(
        bm25_results,
        start=1
    ):

        print(
            f"{index}. "
            f"{result['source']} "
            f"page {result['page']}"
        )

    print("\n\nHYBRID SEARCH")
    print("=" * 70)

    for index, result in enumerate(
        hybrid_results,
        start=1
    ):

        print(
            f"{index}. "
            f"{result['source']} "
            f"page {result['page']} "
            f"RRF={result['rrf_score']:.6f}"
        )

if __name__ == "__main__":
    main()