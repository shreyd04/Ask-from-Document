import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from ragas.llms import llm_factory
from ragas.metrics.collections import (
    Faithfulness,
    ContextPrecisionWithoutReference,
)

from app.retrieval import Retriever
from app.answer_pipeline import answer_question


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# Paths
# --------------------------------------------------

DATASET_PATH = (
    Path(__file__).parent
    / "evaluation"
    / "golden_dataset.json"
)


# --------------------------------------------------
# Configuration
# --------------------------------------------------

GROQ_MODEL = "openai/gpt-oss-120b"


# --------------------------------------------------
# Create Groq client for Ragas
# --------------------------------------------------

groq_client = Groq()


# --------------------------------------------------
# Create Ragas evaluator LLM
# --------------------------------------------------

evaluator_llm = llm_factory(
    GROQ_MODEL,
    provider="groq",
    client=groq_client,
    temperature=0,
)


# --------------------------------------------------
# Create Ragas metrics
# --------------------------------------------------

faithfulness_metric = Faithfulness(
    llm=evaluator_llm
)


context_precision_metric = (
    ContextPrecisionWithoutReference(
        llm=evaluator_llm
    )
)


# --------------------------------------------------
# Load golden dataset
# --------------------------------------------------

def load_dataset():

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# --------------------------------------------------
# Evaluate one question
# --------------------------------------------------

async def evaluate_question(
    retriever,
    item
):

    question = item["question"]

    print(
        f"\nEvaluating {item['id']}: "
        f"{question}"
    )

    # ----------------------------------------------
    # Retrieve documents using YOUR RAG pipeline
    # ----------------------------------------------

    retrieved_documents = (
        retriever.retrieve(
            question,
            top_k=5
        )
    )

    if not retrieved_documents:

        print(
            "No documents were retrieved."
        )

        return {
            "id": item["id"],
            "faithfulness": 0.0,
            "context_precision": 0.0
        }

    # ----------------------------------------------
    # Generate answer using YOUR pipeline
    # ----------------------------------------------

    result = answer_question(
        question,
        retrieved_documents
    )

    generated_answer = result[
        "answer"
    ]

    # ----------------------------------------------
    # Convert retrieved chunks into Ragas format
    # ----------------------------------------------

    retrieved_contexts = [
        document["text"]
        for document in retrieved_documents
    ]

    # ----------------------------------------------
    # Faithfulness
    # ----------------------------------------------

    faithfulness_result = (
        await faithfulness_metric.ascore(
            user_input=question,
            response=generated_answer,
            retrieved_contexts=retrieved_contexts
        )
    )

    # ----------------------------------------------
    # Context precision
    # ----------------------------------------------

    context_precision_result = (
        await context_precision_metric.ascore(
            user_input=question,
            response=generated_answer,
            retrieved_contexts=retrieved_contexts
        )
    )

    faithfulness_score = float(
        faithfulness_result.value
    )

    context_precision_score = float(
        context_precision_result.value
    )

    print(
        f"Faithfulness: "
        f"{faithfulness_score:.3f}"
    )

    print(
        f"Context precision: "
        f"{context_precision_score:.3f}"
    )

    return {
        "id": item["id"],
        "faithfulness": faithfulness_score,
        "context_precision": context_precision_score,
    }


# --------------------------------------------------
# Main
# --------------------------------------------------

async def main():

    dataset = load_dataset()

    print(
        f"Loaded {len(dataset)} "
        f"evaluation questions."
    )

    retriever = Retriever()

    results = []

    for item in dataset:

        result = await evaluate_question(
            retriever,
            item
        )

        results.append(result)

    if not results:

        print(
            "No evaluation results."
        )

        return

    # ----------------------------------------------
    # Aggregate results
    # ----------------------------------------------

    average_faithfulness = (
        sum(
            result["faithfulness"]
            for result in results
        )
        / len(results)
    )

    average_context_precision = (
        sum(
            result["context_precision"]
            for result in results
        )
        / len(results)
    )

    print("\n")
    print("=" * 70)
    print("RAGAS EVALUATION SUMMARY")
    print("=" * 70)

    print(
        f"Questions: "
        f"{len(results)}"
    )

    print(
        f"Average faithfulness: "
        f"{average_faithfulness:.3f}"
    )

    print(
        f"Average context precision: "
        f"{average_context_precision:.3f}"
    )

    print("=" * 70)


if __name__ == "__main__":

    asyncio.run(main())