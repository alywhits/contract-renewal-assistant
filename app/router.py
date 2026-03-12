from enum import Enum
from typing import TypedDict, List, Tuple
from pathlib import Path
from .policy_ingestion import retrieve_similar_sections

from .llm_client import (
    classify_intent as llm_classify,
    generate_sql,
    execute_sql,
    synthesize_answer,
    synthesize_rag_answer,
)


class Intent(str, Enum):
    RENEWAL_STATUS = "renewal_status"
    RENEWAL_RISK = "renewal_risk"
    RENEWAL_TIMING = "renewal_timing"
    ACTIONABILITY = "actionability"
    OUT_OF_SCOPE = "out_of_scope"


class IntentResult(TypedDict):
    intent: Intent
    reason: str


class Response(TypedDict, total=False):
    intent: Intent
    answer: str
    source: str
    confidence: float
    needs_clarification: bool
    generated_sql: str
    retrieved_context: List[Tuple[str, str, str, float]]


def classify_intent(user_query: str) -> IntentResult:
    prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "intent-router-system.md"
    system_prompt = prompt_path.read_text()

    raw_label = llm_classify(
        system_prompt=system_prompt,
        user_query=user_query,
    )

    try:
        intent = Intent(raw_label)
    except ValueError:
        intent = Intent.OUT_OF_SCOPE

    return {
        "intent": intent,
        "reason": "classified by LLM intent router",
    }


def route_query(user_query: str) -> Response:
    result = classify_intent(user_query)
    intent = result["intent"]

    # -----------------------------
    # SQL PATH
    # -----------------------------
    if intent == Intent.RENEWAL_STATUS:
        schema_path = Path(__file__).resolve().parents[1] / "prompts" / "sql-schema.md"
        sql_prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "sql-generation-system.md"

        schema = schema_path.read_text()
        sql_prompt_template = sql_prompt_path.read_text()
        sql_system_prompt = sql_prompt_template.replace("{{SQL_SCHEMA}}", schema)

        sql = generate_sql(sql_system_prompt, user_query)

        if sql == "CANNOT_ANSWER":
            return {
                "intent": intent,
                "answer": "I cannot answer that question using the available data.",
                "source": "sql",
                "confidence": 0.2,
                "needs_clarification": False,
                "generated_sql": sql,
            }

        try:
            columns, rows = execute_sql(sql)

            if not rows:
                return {
                    "intent": intent,
                    "answer": "No matching records were found.",
                    "source": "sql",
                    "confidence": 0.6,
                    "needs_clarification": False,
                    "generated_sql": sql,
                }

            answer = synthesize_answer(user_query, sql, columns, rows)

            return {
                "intent": intent,
                "answer": answer,
                "source": "sql",
                "confidence": 0.95,
                "needs_clarification": False,
                "generated_sql": sql,
            }

        except Exception:
            return {
                "intent": intent,
                "answer": "An error occurred while processing the request.",
                "source": "sql",
                "confidence": 0.1,
                "needs_clarification": False,
                "generated_sql": sql,
            }

    # -----------------------------
    # RAG PATH
    # -----------------------------
    if intent in (
        Intent.RENEWAL_RISK,
        Intent.RENEWAL_TIMING,
        Intent.ACTIONABILITY,
    ):
        retrieved_sections, confidence_label = retrieve_similar_sections(user_query)

        if not retrieved_sections:
            return {
                "intent": intent,
                "answer": "No relevant policy sections were found.",
                "source": "rag",
                "confidence": 0.4,
                "needs_clarification": False,
            }

        answer = synthesize_rag_answer(user_query, retrieved_sections)

        return {
            "intent": intent,
            "answer": answer,
            "source": "rag",
            "confidence": 0.85,
            "needs_clarification": False,
            "retrieved_context": retrieved_sections,
        }

    # -----------------------------
    # FALLBACK
    # -----------------------------
    return {
        "intent": intent,
        "answer": "This assistant supports questions about contract status, renewal timing, and renewal risk. That request is outside its current scope.",
        "source": "fallback",
        "confidence": 0.1,
        "needs_clarification": False,
    }
