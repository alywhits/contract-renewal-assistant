Contract Renewal Assistant

A hybrid AI system that combines structured SQL querying and semantic policy retrieval (RAG) to support contract renewal analysis and decision support.

This project demonstrates deterministic routing, vector similarity search using pgvector, and confidence-aware response behavior.

Overview

The Contract Renewal Assistant is designed to answer two types of questions:

Structured questions about contract and employee data

Policy-based questions about renewal rules, risk indicators, and approval requirements

The system routes queries to the appropriate engine:

NL → SQL for structured database queries

NL → RAG (pgvector) for unstructured policy retrieval

A confidence layer evaluates semantic similarity scores and adjusts system behavior when confidence is low.

Architecture

Core components:

PostgreSQL 16

pgvector extension

Python 3.12

OpenAI Embeddings API (text-embedding-3-small)

Deterministic confidence scoring based on vector distance

Data Layers

Structured Data

Employees

Contracts

Renewal dates

Contract value

Status indicators

Unstructured Data

Markdown-based policy documents

Chunked by section headers

Embedded and stored in policy_embeddings table

Confidence Model

Similarity is computed using L2 distance:

embedding <-> query_embedding


Confidence thresholds:

HIGH: distance < 0.90

MEDIUM: 0.90 ≤ distance < 1.10

LOW: distance ≥ 1.10

Behavior:

HIGH → Return answer normally

MEDIUM → Return answer with moderate confidence

LOW → Ask clarifying question instead of answering

This prevents low-signal semantic matches from producing misleading answers.

Project Structure
contract-renewal-assistant/
│
├── app/
│   ├── router.py
│   ├── policy_ingestion.py
│   ├── llm_client.py
│   └── policies/
│
├── prompts/
│   ├── intent-router-system.md
│   ├── sql-generation-system.md
│   ├── sql-answer-system.md
│   └── sql-schema.md
│
├── docker-compose.yml
└── README.md

Running the System
1. Start Postgres with pgvector
docker compose up -d

2. Load policy embeddings
python3 app/policy_ingestion.py

3. Query retrieval test

Edit the query inside policy_ingestion.py main block and run:

python3 app/policy_ingestion.py

Design Principles

Deterministic routing

Measured semantic thresholds

No LLM self-reported confidence

Clear separation of structured vs unstructured logic

Safety-aware behavior for low-confidence responses

Future Enhancements

Dynamic clarification generation

Hybrid SQL + RAG synthesis

Confidence calibration across larger policy corpus

API layer for external integration

Front-end UI for business users

Demo Focus

This system demonstrates:

NL → SQL routing

NL → pgvector retrieval

Empirical threshold-based confidence scoring

Controlled behavior when semantic signal is weak
