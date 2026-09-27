import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

from ragas.llms import llm_factory
from ragas.metrics.collections import (
    Faithfulness,
    ContextPrecisionWithoutReference,
)


# ============================================================
# PATH CONFIGURATION
# ============================================================

# This file:
# Ask_from_Document/backend/evaluate_ragas.py

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

# Golden dataset:
# Ask_from_Document/backend/evaluation/golden_dataset.json

DATASET_PATH = (
    BACKEND_DIR
    / "evaluation"
    / "golden_dataset.json"
)


# ============================================================
# MAKE BACKEND IMPORTABLE
# ============================================================

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# ============================================================
# IMPORT YOUR EXISTING RAG PIPELINE
# ============================================================

from app.retrieval import Retriever
from app.answer_pipeline import answer_question


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

# Project root .env
load_dotenv(PROJECT_ROOT / ".env")

# Backend .env, if present
load_dotenv(BACKEND_DIR / ".env")


# ============================================================
# CONFIGURATION
# ============================================================

GROQ_MODEL = "openai/gpt-oss-120b"

GROQ_API_KEY = os.getenv("GROQ_APIKEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_APIKEY was not found.\n"
        "Make sure your .env contains:\n"
        "GROQ_APIKEY=your_api_key"
    )


# ============================================================
# EVALUATION THRESHOLDS
# ============================================================

FAITHFULNESS_THRESHOLD = 0.80

CONTEXT_PRECISION_THRESHOLD = 0.70


# ============================================================
# CREATE ASYNC GROQ CLIENT
# ============================================================

# Groq exposes an OpenAI-compatible API.
#
# IMPORTANT:
# We use AsyncOpenAI because Ragas collection metrics
# call the asynchronous LLM generation path.

groq_client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)


# ============================================================
# CREATE RAGAS EVALUATOR LLM
# ============================================================

evaluator_llm = llm_factory(
    GROQ_MODEL,
    provider="openai",
    client=groq_client,
)


# ============================================================
# CREATE RAGAS METRICS
# ============================================================

faithfulness_metric = Faithfulness(
    llm=evaluator_llm
)

context_precision_metric = ContextPrecisionWithoutReference(
    llm=evaluator_llm
)


# ============================================================
# LOAD GOLDEN DATASET
# ============================================================

def load_dataset():

    if not DATASET_PATH.exists():

        raise FileNotFoundError(
            f"\nGolden dataset was not found at:\n"
            f"{DATASET_PATH}\n\n"
            f"Expected structure:\n"
            f"backend/\n"
            f"├── evaluate_ragas.py\n"
            f"└── evaluation/\n"
            f"    └── golden_dataset.json"
        )

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        dataset = json.load(file)

    if not isinstance(dataset, list):

        raise ValueError(
            "golden_dataset.json must contain a JSON list."
        )

    return dataset


# ============================================================
# EVALUATE ONE QUESTION
# ============================================================

async def evaluate_question(
    retriever,
    item,
    index
):

    question = item["question"]

    item_id = item.get(
        "id",
        index + 1
    )

    print()
    print("-" * 70)

    print(
        f"Evaluating {item_id}: "
        f"{question}"
    )


    # --------------------------------------------------------
    # RETRIEVE DOCUMENTS
    # --------------------------------------------------------

    retrieved_documents = retriever.retrieve(
        question,
        top_k=5
    )

    if retrieved_documents is None:

        print(
            "Retriever returned None."
        )

        return {
            "id": item_id,
            "faithfulness": 0.0,
            "context_precision": 0.0
        }


    if len(retrieved_documents) == 0:

        print(
            "No documents were retrieved."
        )

        return {
            "id": item_id,
            "faithfulness": 0.0,
            "context_precision": 0.0
        }


    print(
        f"Retrieved "
        f"{len(retrieved_documents)} "
        f"documents."
    )


    # --------------------------------------------------------
    # GENERATE ANSWER USING YOUR EXISTING PIPELINE
    # --------------------------------------------------------

    result = answer_question(
        question,
        retrieved_documents
    )


    # --------------------------------------------------------
    # HANDLE ANSWER PIPELINE RESULT
    # --------------------------------------------------------

    if isinstance(result, dict):

        generated_answer = result.get(
            "answer",
            ""
        )

    else:

        generated_answer = str(result)


    if not generated_answer:

        print(
            "Answer pipeline returned an empty answer."
        )

        return {
            "id": item_id,
            "faithfulness": 0.0,
            "context_precision": 0.0
        }


    print()
    print("Generated answer:")
    print(generated_answer)


    # --------------------------------------------------------
    # CONVERT RETRIEVED DOCUMENTS TO RAGAS CONTEXTS
    # --------------------------------------------------------

    retrieved_contexts = []

    for document in retrieved_documents:

        if isinstance(document, dict):

            text = document.get(
                "text",
                ""
            )

        else:

            # Handles LangChain-style Document objects
            text = getattr(
                document,
                "page_content",
                str(document)
            )

        if text:

            retrieved_contexts.append(
                text
            )


    if not retrieved_contexts:

        print(
            "No usable retrieved contexts found."
        )

        return {
            "id": item_id,
            "faithfulness": 0.0,
            "context_precision": 0.0
        }


    # --------------------------------------------------------
    # FAITHFULNESS
    # --------------------------------------------------------

    print()
    print("Calculating faithfulness...")

    faithfulness_result = (
        await faithfulness_metric.ascore(
            user_input=question,
            response=generated_answer,
            retrieved_contexts=retrieved_contexts,
        )
    )


    # --------------------------------------------------------
    # CONTEXT PRECISION
    # --------------------------------------------------------

    print(
        "Calculating context precision..."
    )

    context_precision_result = (
        await context_precision_metric.ascore(
            user_input=question,
            response=generated_answer,
            retrieved_contexts=retrieved_contexts,
        )
    )


    # --------------------------------------------------------
    # EXTRACT SCORES
    # --------------------------------------------------------

    faithfulness_score = float(
        faithfulness_result.value
    )

    context_precision_score = float(
        context_precision_result.value
    )


    # --------------------------------------------------------
    # DISPLAY SCORES
    # --------------------------------------------------------

    print()

    print(
        f"Faithfulness: "
        f"{faithfulness_score:.3f}"
    )

    print(
        f"Context precision: "
        f"{context_precision_score:.3f}"
    )


    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return {
        "id": item_id,
        "faithfulness": faithfulness_score,
        "context_precision": context_precision_score,
    }


# ============================================================
# MAIN EVALUATION
# ============================================================

async def main():

    print()
    print("=" * 70)
    print("RAGAS RAG EVALUATION")
    print("=" * 70)


    # --------------------------------------------------------
    # DISPLAY CONFIGURATION
    # --------------------------------------------------------

    print()

    print(
        f"Dataset:\n"
        f"{DATASET_PATH}"
    )

    print()

    print(
        f"Evaluator model:\n"
        f"{GROQ_MODEL}"
    )


    # --------------------------------------------------------
    # LOAD DATASET
    # --------------------------------------------------------

    dataset = load_dataset()

    print()

    print(
        f"Loaded "
        f"{len(dataset)} "
        f"evaluation questions."
    )


    if len(dataset) == 0:

        print()

        print(
            "Golden dataset is empty."
        )

        return


    # --------------------------------------------------------
    # INITIALIZE RETRIEVER
    # --------------------------------------------------------

    print()

    print(
        "Initializing retriever..."
    )

    retriever = Retriever()


    # --------------------------------------------------------
    # RUN EVALUATION
    # --------------------------------------------------------

    results = []

    for index, item in enumerate(dataset):

        result = await evaluate_question(
            retriever,
            item,
            index
        )

        results.append(result)


    # --------------------------------------------------------
    # CHECK RESULTS
    # --------------------------------------------------------

    if not results:

        print()

        print(
            "No evaluation results."
        )

        return


    # --------------------------------------------------------
    # CALCULATE AVERAGES
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # DETERMINE PASS / FAIL
    # --------------------------------------------------------

    faithfulness_passed = (
        average_faithfulness
        >= FAITHFULNESS_THRESHOLD
    )


    context_precision_passed = (
        average_context_precision
        >= CONTEXT_PRECISION_THRESHOLD
    )


    evaluation_passed = (
        faithfulness_passed
        and context_precision_passed
    )


    # --------------------------------------------------------
    # SAVE EVALUATION RESULTS
    # --------------------------------------------------------

    RESULTS_DIR = (
        BACKEND_DIR
        / "evaluation"
        / "results"
    )

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    RESULTS_PATH = (
        RESULTS_DIR
        / "latest_results.json"
    )


    evaluation_output = {

        "model": GROQ_MODEL,

        "dataset": str(
            DATASET_PATH
        ),

        "questions": len(results),

        "average_faithfulness": (
            average_faithfulness
        ),

        "average_context_precision": (
            average_context_precision
        ),

        "thresholds": {

            "faithfulness": (
                FAITHFULNESS_THRESHOLD
            ),

            "context_precision": (
                CONTEXT_PRECISION_THRESHOLD
            )
        },

        "passed": evaluation_passed,

        "results": results
    }


    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            evaluation_output,
            file,
            indent=2
        )


    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------

    print()
    print()
    print("=" * 70)
    print("RAGAS EVALUATION SUMMARY")
    print("=" * 70)

    print()

    print(
        f"Questions: "
        f"{len(results)}"
    )

    print()

    print(
        f"Faithfulness: "
        f"{average_faithfulness:.3f} "
        f"(threshold: "
        f"{FAITHFULNESS_THRESHOLD:.3f})"
    )

    print(
        f"Context precision: "
        f"{average_context_precision:.3f} "
        f"(threshold: "
        f"{CONTEXT_PRECISION_THRESHOLD:.3f})"
    )

    print()


    if faithfulness_passed:

        print(
            "✓ Faithfulness threshold: PASSED"
        )

    else:

        print(
            "✗ Faithfulness threshold: FAILED"
        )


    if context_precision_passed:

        print(
            "✓ Context precision threshold: PASSED"
        )

    else:

        print(
            "✗ Context precision threshold: FAILED"
        )


    print()


    if evaluation_passed:

        print(
            "✓ OVERALL EVALUATION: PASSED"
        )

    else:

        print(
            "✗ OVERALL EVALUATION: FAILED"
        )


    print()

    print(
        f"Results saved to:\n"
        f"{RESULTS_PATH}"
    )

    print()

    print("=" * 70)


    # --------------------------------------------------------
    # RETURN NON-ZERO EXIT CODE ON FAILURE
    # --------------------------------------------------------

    if not evaluation_passed:

        raise SystemExit(1)


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    asyncio.run(main())