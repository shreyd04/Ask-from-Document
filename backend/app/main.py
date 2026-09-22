from fastapi import FastAPI, HTTPException
from app.answer_pipeline import answer_question
from app.retrieval import Retriever
from app.generation import generate_answer
from app.schemas import (
    QuestionRequest,
    AnswerResponse
)


app = FastAPI(
    title="Production RAG API",
    description="Document question-answering API",
    version="1.0.0"
)


retriever = Retriever()


@app.get("/")
def root():

    return {
        "message": "Production RAG API is running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


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