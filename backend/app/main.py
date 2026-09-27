from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.answer_pipeline import answer_question
from app.retrieval import Retriever
from app.schemas import (
    QuestionRequest,
    AnswerResponse
)


app = FastAPI(
    title="Ask My Doc API",
    description="Domain-specific document question-answering API",
    version="1.0.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Retriever
# --------------------------------------------------

retriever = Retriever()


# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "Ask My Doc API is running"
    }


# --------------------------------------------------
# Health
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# --------------------------------------------------
# Ask
# --------------------------------------------------

@app.post(
    "/ask",
    response_model=AnswerResponse
)
def ask_question(
    request: QuestionRequest
):

    question = request.question.strip()

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

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
            "sources": result["sources"]
        }

    except Exception as exc:

        print(
            f"Error while answering question: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate an answer."
        )