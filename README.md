# Contract & Renewal Assistant
A controlled AI reference tool for answering contract and renewal questions using approved enterprise data sources.

This project demonstrates how to safely integrate LLMs with:

- Structured relational data (PostgreSQL)
- Policy documents stored and retrieved using vector similarity (pgvector)

This is intentionally **not** a chatbot.  
It is a constrained system designed for traceable, auditable answers.

---
## What This Project Solves

In many organizations:

- Contract data lives in structured tables.
- Renewal rules and risk factors live in policy documents.
- Users ask questions in plain language, not SQL.

Plugging an unrestricted LLM directly into that environment introduces risk.

This project shows how to:

- Accept natural language questions
- Route each question to the correct data source
- Generate answers only from approved database records or stored policy content
- Prevent hallucination outside controlled sources

---

## System Overview

The system supports two paths:

### 1. Structured Query Path (NL → SQL)

Used for:
- Contract status
- Renewal dates
- Contract counts
- Employee-linked contract data

Flow:

1. Intent is classified
2. SQL is generated using a schema-constrained prompt
3. Query is executed against PostgreSQL (SELECT-only)
4. Returned rows are used to generate the final answer

The model never connects directly to the database.

---

### 2. Policy Retrieval Path (NL → RAG)

Used for:

- Renewal risk questions
- Policy-based guidance
- Timing or approval logic

Flow:

1. Policy sections are embedded and stored in PostgreSQL
2. Query is embedded at runtime
3. pgvector similarity search retrieves top matching sections
4. The model generates an answer using only retrieved content

No external knowledge is used.

---

## Confidence Layer

Similarity is computed using L2 distance:

embedding <-> query_embedding

Confidence thresholds:

- HIGH: distance < 0.90
- MEDIUM: 0.90 ≤ distance < 1.10
- LOW: distance ≥ 1.10

Low-confidence matches trigger clarification instead of blind answers.

This prevents weak semantic matches from producing misleading output.

---

## Technology Stack

Frontend:

- Streamlit

Application Layer:

- Python 3.12
- Custom intent router (fixed categories)

LLM:

- OpenAI API (classification + constrained generation)
- `text-embedding-3-small` for policy embeddings

Database:

- PostgreSQL 16
- pgvector extension

Environment:

- Docker Compose (database)
- Python virtual environment (application)

---

## Project Structure

`contract-renewal-assistant/`  
`│`  
`├── app/`  
`│   ├── router.py`  
`│   ├── policy_ingestion.py`  
`│   ├── llm_client.py`  
`│`  
`├── prompts/`  
`├── streamlit_app.py`  
`├── docker-compose.yml`  
`├── requirements.txt`  
`└── README.md`

---

## Design Principles

- No conversational memory
- No open-ended generation
- Schema-constrained SQL
- SELECT-only database access
- Retrieval-bound policy responses
- Source transparency in every answer

---

# How to run locally

### 1. Clone the repository

`git clone https://github.com/alywhits/contract-renewal-assistant.git' 
cd contract-renewal-assistant`

### 2. Start PostgreSQL (Docker)

`docker compose up -d`

This will start:

- PostgreSQL 16
- pgvector extension enabled
- Preconfigured database schema

### 3. Create and activate Python virtual environment

`python3 -m venv venv` 
`source venv/bin/activate`

### 4. Install dependencies

`pip install -r requirements.txt`

### 5. Configure environment variables

Create a `.env` file in the root directory:

`OPENAI_API_KEY=your_api_key_here` 
`POSTGRES_PASSWORD=your_db_password`

### 6. Run the application

`streamlit run streamlit_app.py`

The app will launch in your browser at:

http://localhost:8501

---

## Production Considerations

This implementation is intentionally simplified for demonstration purposes.  
Before deploying in a production environment, the following enhancements would be required:

### 1. Role-Based Access Control (RBAC)

- Restrict access to contracts and policy documents by user role
- Enforce row-level security in PostgreSQL

### 2. Secure Document Ingestion Pipeline

- Controlled upload process for new contracts and policy documents
- Automated schema validation
- Automated embedding and indexing for new policy content

### 3. Observability and Logging

- Query logging and audit trails
- Response confidence monitoring
- Alerting for low-confidence responses

### 4. Confidence Threshold Enforcement

- Hard-block responses below defined similarity thresholds
- Escalate uncertain queries for manual review

### 5. API Layer (Optional)

- Expose functionality via secured REST API
- Separate UI layer from application services
