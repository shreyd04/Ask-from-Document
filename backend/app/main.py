from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.answer_pipeline import answer_question
from app.retrieval import Retriever
from app.schemas import (
    QuestionRequest,
    AnswerResponse
)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://localhost:5173",
        "https://ask-from-document-9m67bbg73-shreyd04.vercel.app/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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