from app.retrieval import Retriever


retriever = Retriever()

question = input("Ask a question: ")

results = retriever.retrieve(
    question,
    top_k=5
)

print("\nRetrieved documents:\n")

for index, result in enumerate(results, start=1):

    print("=" * 60)

    print(f"Result {index}")

    print(f"Source: {result['source']}")

    print(f"Page: {result['page']}")

    print()

    print(result["text"])