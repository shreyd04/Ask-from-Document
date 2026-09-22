from app.config import DOCUMENTS_DIR
from app.ingestion import load_all_pdfs
from app.chunking import create_chunks
from app.embeddings import EmbeddingModel
from app.vector_store import VectorStore


def main():

    print("Loading documents...")

    pages = load_all_pdfs(DOCUMENTS_DIR)

    print(f"Loaded {len(pages)} pages.")

    if not pages:
        print("No PDF documents found.")
        return

    print("Creating chunks...")

    chunks = create_chunks(pages)

    print(f"Created {len(chunks)} chunks.")

    print("Loading embedding model...")

    embedding_model = EmbeddingModel()

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    print("Creating embeddings...")

    embeddings = embedding_model.encode(texts)

    print("Saving to ChromaDB...")

    vector_store = VectorStore()

    vector_store.add_documents(
        chunks,
        embeddings
    )

    print("Ingestion complete.")


if __name__ == "__main__":
    main()