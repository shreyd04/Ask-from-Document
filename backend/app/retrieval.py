from rank_bm25 import BM25Okapi
from app.reranker import Reranker
from app.embeddings import EmbeddingModel
from app.vector_store import VectorStore


class Retriever:

    def __init__(self):
        
        self.embedding_model = EmbeddingModel()

        self.vector_store = VectorStore()
        self.reranker = Reranker()
        # Load all indexed chunks from ChromaDB
        self.documents = (
            self.vector_store.get_all_documents()
        )

        # Build BM25 index
        tokenized_documents = [
            self.tokenize(document["text"])
            for document in self.documents
        ]

        self.bm25 = BM25Okapi(
            tokenized_documents
        )

    @staticmethod
    def tokenize(text: str) -> list[str]:

        return text.lower().split()

    def vector_search(
        self,
        query: str,
        top_k: int = 10
    ):

        query_embedding = (
            self.embedding_model.encode(
                [query]
            )[0]
        )

        results = self.vector_store.search(
            query_embedding,
            top_k=top_k
        )

        retrieved_documents = []

        documents = results["documents"][0]

        metadatas = results["metadatas"][0]

        for document, metadata in zip(
            documents,
            metadatas
        ):

            retrieved_documents.append(
                {
                    "text": document,
                    "source": metadata["source"],
                    "page": metadata["page"],
                    "chunk_id": metadata["chunk_id"],
                }
            )

        return retrieved_documents

    def bm25_search(
        self,
        query: str,
        top_k: int = 10
    ):

        tokenized_query = self.tokenize(
            query
        )

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked_indexes = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True
        )

        results = []

        for index in ranked_indexes[:top_k]:

            document = self.documents[index]

            results.append(document)

        return results

    @staticmethod
    def document_key(document: dict):

        return (
            document["source"],
            document["page"],
            document["chunk_id"]
        )

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        candidate_k: int = 10
    ):

        vector_results = self.vector_search(
            query=query,
            top_k=candidate_k
        )

        bm25_results = self.bm25_search(
            query=query,
            top_k=candidate_k
        )

        # Reciprocal Rank Fusion
        rrf_scores = {}

        documents_by_key = {}

        rrf_k = 60

        # Add vector-search rankings
        for rank, document in enumerate(
            vector_results,
            start=1
        ):

            key = self.document_key(
                document
            )

            documents_by_key[key] = document

            rrf_scores[key] = (
                rrf_scores.get(key, 0)
                + 1 / (rrf_k + rank)
            )

        # Add BM25 rankings
        for rank, document in enumerate(
            bm25_results,
            start=1
        ):

            key = self.document_key(
                document
            )

            documents_by_key[key] = document

            rrf_scores[key] = (
                rrf_scores.get(key, 0)
                + 1 / (rrf_k + rank)
            )

        # Sort by combined RRF score
        ranked_keys = sorted(
            rrf_scores,
            key=rrf_scores.get,
            reverse=True
        )

        final_results = []

        for key in ranked_keys[:top_k]:

            document = documents_by_key[key]

            document = {
                **document,
                "rrf_score": rrf_scores[key]
            }

            final_results.append(
                document
            )

        return final_results

    def retrieve(
    self,
    query: str,
    top_k: int = 5
):
      """
      Complete retrieval pipeline:
  
      1. Vector search
      2. BM25 search
      3. RRF hybrid fusion
      4. Cross-encoder reranking
      5. Return top-k documents
      """
  
      hybrid_results = self.hybrid_search(
          query=query,
          top_k=10,
          candidate_k=10
      )
  
      reranked_results = self.reranker.rerank(
          query=query,
          documents=hybrid_results,
          top_k=top_k
      )
  
      return reranked_results