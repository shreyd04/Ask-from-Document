from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(self):

        print("Loading cross-encoder reranker...")

        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

        print("Cross-encoder loaded.")

    def rerank(
        self,
        query: str,
        documents: list[dict],
        top_k: int = 5
    ) -> list[dict]:

        if not documents:
            return []

        pairs = []

        for document in documents:

            pairs.append(
                (
                    query,
                    document["text"]
                )
            )

        scores = self.model.predict(
            pairs
        )

        reranked_documents = []

        for document, score in zip(
            documents,
            scores
        ):

            reranked_documents.append(
                {
                    **document,
                    "reranker_score": float(score)
                }
            )

        reranked_documents.sort(
            key=lambda document:
            document["reranker_score"],
            reverse=True
        )

        return reranked_documents[:top_k]