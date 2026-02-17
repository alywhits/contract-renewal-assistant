from enum import Enum
from typing import TypedDict
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


def classify_intent(user_query: str) -> IntentResult:
    """
    Classifies a user query into exactly one primary intent.
    Must not perform data lookup or reasoning beyond intent classification.
    """

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

def route_query(user_query: str) -> str:
    """
    Routes a user query to the appropriate engine
    based on classified intent.
    """

    result = classify_intent(user_query)
    intent = result["intent"]

    if intent == Intent.RENEWAL_STATUS:
        # Load schema for SQL generation
        schema_path = Path(__file__).resolve().parents[1] / "prompts" / "sql-schema.md"
        sql_prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "sql-generation-system.md"

        schema = schema_path.read_text()
        sql_prompt_template = sql_prompt_path.read_text()
        sql_system_prompt = sql_prompt_template.replace("{{SQL_SCHEMA}}", schema)

        sql = generate_sql(sql_system_prompt, user_query)

        if sql == "CANNOT_ANSWER":
            return "I cannot answer that question using the available data."

        try:
            columns, rows = execute_sql(sql)

            if not rows:
                return "No matching records were found."

            return synthesize_answer(user_query, sql, columns, rows)

        except Exception:
            return "An error occurred while processing the request."


    # ---------------------------------------------
    # RAG Retrieval Path (Unstructured Policy Data)
    # ---------------------------------------------
    if intent in (
        Intent.RENEWAL_RISK,
        Intent.RENEWAL_TIMING,
        Intent.ACTIONABILITY,
    ):
        results = retrieve_similar_sections(user_query)

        if not results:
            return "No relevant policy sections were found."

        return synthesize_rag_answer(user_query, results)
    
    # ---------------------------------------------
    # Fallback
    # ---------------------------------------------
    return "This intent path is not yet implemented."
 

