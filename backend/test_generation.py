from app.retrieval import Retriever
from app.generation import generate_answer


def main():

    retriever = Retriever()

    question = input(
        "Ask a question about your documents: "
    )

    print("\nSearching documents...\n")

    retrieved_documents = retriever.retrieve(
        question,
        top_k=5
    )

    print(
        f"Retrieved {len(retrieved_documents)} chunks."
    )

    print("\nGenerating answer...\n")

    answer = generate_answer(
        question,
        retrieved_documents
    )

    print("=" * 70)

    print("ANSWER")

    print("=" * 70)

    print(answer["answer"])

    print("\nSOURCES")

    for source in answer["sources"]:

        print(
        f"- {source['document']}, "
        f"page {source['page']}"
      )

    print("=" * 70)


if __name__ == "__main__":
    main()