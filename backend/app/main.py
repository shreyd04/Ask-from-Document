from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.answer_pipeline import answer_question
from app.retrieval import Retriever
from app.schemas import QuestionRequest, AnswerResponse


app = FastAPI(
    title="Ask My Doc RAG API",
    description="Domain-specific document question-answering system with grounded citations.",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Lazy-loaded retriever
# ---------------------------------------------------------

_retriever = None


def get_retriever():
    global _retriever

    if _retriever is None:
        print("Initializing retriever...")
        _retriever = Retriever()
        print("Retriever initialized.")

    return _retriever


# ---------------------------------------------------------
# Root
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Ask My Doc RAG API is running",
        "status": "ok",
    }


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ---------------------------------------------------------
# Ask endpoint
# ---------------------------------------------------------

@app.post(
    "/ask",
    response_model=AnswerResponse
)
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        retriever = get_retriever()

        retrieved_documents = retriever.retrieve(
            question,
            top_k=5
        )

        result = answer_question(
            question,
            retrieved_documents
        )

        return {
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"],
        }

    except Exception as exc:

        print(f"Error while answering question: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Unable to generate an answer from the indexed documents."
        )