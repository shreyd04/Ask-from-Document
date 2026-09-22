import chromadb

from app.config import CHROMA_DIR


class VectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR)
        )

        self.collection = self.client.get_or_create_collection(
            name="documents"
        )

    def clear(self):

        try:
            self.client.delete_collection(
                name="documents"
            )
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(
            name="documents"
        )

    def add_documents(
        self,
        chunks: list[dict],
        embeddings
    ):

        ids = []

        documents = []

        metadatas = []

        vectors = []

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):

            chunk_id = (
                f"{chunk['source']}"
                f"_{chunk['page']}"
                f"_{chunk['chunk_id']}"
                f"_{index}"
            )

            ids.append(chunk_id)

            documents.append(chunk["text"])

            metadatas.append(
                {
                    "source": chunk["source"],
                    "page": chunk["page"],
                    "chunk_id": chunk["chunk_id"],
                }
            )

            vectors.append(
                embedding.tolist()
            )

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=vectors,
        )

    def search(
        self,
        query_embedding,
        top_k: int = 5
    ):

        results = self.collection.query(
            query_embeddings=[
                query_embedding.tolist()
            ],
            n_results=top_k,
        )

        return results

    def get_all_documents(self):

        """
        Return every chunk currently stored
        in ChromaDB.

        This is used to build the BM25 index.
        """

        results = self.collection.get(
            include=[
                "documents",
                "metadatas"
            ]
        )

        documents = []

        for document, metadata in zip(
            results["documents"],
            results["metadatas"]
        ):

            documents.append(
                {
                    "text": document,
                    "source": metadata["source"],
                    "page": metadata["page"],
                    "chunk_id": metadata["chunk_id"],
                }
            )

        return documents