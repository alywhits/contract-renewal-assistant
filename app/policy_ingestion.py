import os
import psycopg2
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


# -------------------------------------------------
# Chunk policy documents by section headers
# -------------------------------------------------
def load_policy_chunks():
    policies_path = Path(__file__).resolve().parent / "policies"
    chunks = []

    for file_path in policies_path.glob("*.md"):
        document_name = file_path.stem
        content = file_path.read_text()

        sections = content.split("## ")

        for section in sections:
            if not section.strip():
                continue

            lines = section.splitlines()
            section_title = lines[0].strip()
            section_body = "\n".join(lines[1:]).strip()

            if section_body:
                chunks.append({
                    "document_name": document_name,
                    "section_title": section_title,
                    "content": section_body,
                })

    return chunks


# -------------------------------------------------
# Generate embedding
# -------------------------------------------------
def generate_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


# -------------------------------------------------
# Store embeddings in Postgres
# -------------------------------------------------
def store_embeddings():
    chunks = load_policy_chunks()

    conn = psycopg2.connect(
        dbname="contract_renewal_db",
        user="contract_rw",
        password=os.getenv("POSTGRES_PASSWORD"),
        host="localhost",
        port=5432,
    )

    try:
        with conn.cursor() as cur:
            for chunk in chunks:
                embedding = generate_embedding(chunk["content"])

                cur.execute(
                    """
                    INSERT INTO policy_embeddings
                    (document_name, section_title, content, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        chunk["document_name"],
                        chunk["section_title"],
                        chunk["content"],
                        embedding,
                    ),
                )

        conn.commit()

    finally:
        conn.close()


# -------------------------------------------------
# Confidence classification
# -------------------------------------------------
def classify_confidence(distance: float) -> str:
    if distance < 0.90:
        return "HIGH"
    elif distance < 1.10:
        return "MEDIUM"
    else:
        return "LOW"


# -------------------------------------------------
# Retrieve top-k similar policy sections
# -------------------------------------------------
def retrieve_similar_sections(query: str, k: int = 3):
    query_embedding = generate_embedding(query)

    conn = psycopg2.connect(
        dbname="contract_renewal_db",
        user="contract_rw",
        password=os.getenv("POSTGRES_PASSWORD"),
        host="localhost",
        port=5432,
    )

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT document_name,
                       section_title,
                       content,
                       embedding <-> %s AS distance
                FROM policy_embeddings
                ORDER BY distance
                LIMIT %s
                """,
                (str(query_embedding), k),
            )

            results = cur.fetchall()

            if not results:
                return [], "LOW"

            top_distance = results[0][3]
            confidence = classify_confidence(top_distance)

            return results, confidence

    finally:
        conn.close()


if __name__ == "__main__":
    results, confidence = retrieve_similar_sections(
        "What happens if a contract automatically renews?"
    )

    print("\nOverall Confidence:", confidence)

    for r in results:
        print("\n---")
        print("Document:", r[0])
        print("Section:", r[1])
        print("Content:", r[2])
        print("Distance:", r[3])

