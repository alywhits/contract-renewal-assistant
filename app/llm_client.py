"""
LLM Client Module

Responsibilities:
- Intent classification
- Schema-aware SQL generation
- Safe SQL execution
- Grounded answer synthesis

This module does NOT:
- Route requests
- Apply business rules
- Perform vector retrieval
"""

import os
import psycopg2
from typing import Literal
from openai import OpenAI
from pathlib import Path

client = OpenAI()

# ============================================================
# Intent Classification
# ============================================================

IntentLabel = Literal[
    "renewal_status",
    "renewal_risk",
    "renewal_timing",
    "actionability",
    "out_of_scope",
]


def classify_intent(system_prompt: str, user_query: str) -> IntentLabel:
    """
    Uses the LLM to classify a user query into one of the allowed intent labels.
    Deterministic (temperature=0).
    """

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ],
        max_output_tokens=16,
        temperature=0,
    )

    return response.output_text.strip()


# ============================================================
# NL-to-SQL Generation
# ============================================================

def generate_sql(system_prompt: str, user_query: str) -> str:
    """
    Generates PostgreSQL SELECT statements from natural language.
    Must return:
    - Raw SQL
    - OR the string "CANNOT_ANSWER"
    """

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ],
        max_output_tokens=256,
        temperature=0,
    )

    return response.output_text.strip()


# ============================================================
# Safe SQL Execution Layer
# ============================================================

def execute_sql(query: str):
    """
    Executes SQL against PostgreSQL.
    Enforces:
    - SELECT-only restriction
    - Read-only behavior
    """

    if not query.strip().lower().startswith("select"):
        raise ValueError("Only SELECT statements are allowed.")

    conn = psycopg2.connect(
        dbname="contract_renewal_db",
        user="contract_rw",
        password=os.environ.get("POSTGRES_PASSWORD"),
        host="localhost",
        port=5432,
    )

    try:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            return columns, rows
    finally:
        conn.close()


# ============================================================
# Grounded Answer Synthesis
# ============================================================

def synthesize_answer(question: str, sql: str, columns, rows):
    """
    Converts raw SQL results into a natural language answer.
    The model is strictly grounded in returned rows.
    """

    system_prompt = Path("prompts/sql-answer-system.md").read_text()

    user_content = f"""
Question:
{question}

Executed SQL:
{sql}

Columns:
{columns}

Rows:
{rows}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0,
        max_output_tokens=300,
    )

    return response.output_text.strip()

# -------------------------------------------------
# RAG Answer Synthesis (Context-Constrained)
# -------------------------------------------------
def synthesize_rag_answer(user_query: str, retrieved_sections: list) -> str:
    """
    Generates a response using ONLY the provided policy context.
    Must not rely on outside knowledge.
    """

    context_blocks = []
    for doc, section, content, _ in retrieved_sections:
        context_blocks.append(
            f"Document: {doc}\nSection: {section}\n{content}"
        )

    context = "\n\n".join(context_blocks)

    system_prompt = """
You are a policy assistant.

Use ONLY the provided context to answer the user question.
Do not use outside knowledge.
If the answer cannot be determined from the context, say:
"I do not have enough information from the provided policy context."
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{user_query}",
            },
        ],
        temperature=0,
        max_output_tokens=300,
    )

    return response.output_text.strip()



# ============================================================
# Manual Test Harness (Development Only)
# ============================================================

if __name__ == "__main__":

    """

    Manual test harness (disabled during router integration)

    # Load schema for injection into SQL generation prompt
    schema = Path("prompts/sql-schema.md").read_text()
    sql_prompt_template = Path("prompts/sql-generation-system.md").read_text()
    sql_system_prompt = sql_prompt_template.replace("{{SQL_SCHEMA}}", schema)

#    question = "Which contracts are currently active?"
#    question = "What is the CEO's compensation package?"
    question = "Which contracts have status cancelled?"

    # 1. Generate SQL
    sql = generate_sql(sql_system_prompt, question)
    print("Generated SQL:", sql)

    # 2 & 3. Execute safely and synthesize answer with guardrails
if sql == "CANNOT_ANSWER":
    print("Final Answer: I cannot answer that question using the available data.")
else:
    try:
        columns, rows = execute_sql(sql)

        if not rows:
            print("Final Answer: No matching records were found.")
        else:
            answer = synthesize_answer(question, sql, columns, rows)
            print("Final Answer:", answer)

    except Exception as e:
        print("Final Answer: An error occurred while processing the request.")
        print("Debug Info:", str(e))
    """

