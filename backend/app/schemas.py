from pydantic import BaseModel


class QuestionRequest(BaseModel):

    question: str


class Source(BaseModel):

    document: str

    page: int


class AnswerResponse(BaseModel):

    question: str

    answer: str

    sources: list[Source]