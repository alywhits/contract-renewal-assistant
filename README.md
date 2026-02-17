# Contract Renewal Assistant

A hybrid AI system that combines structured SQL querying and semantic policy retrieval (RAG) to support contract renewal analysis and decision support.

This project demonstrates deterministic routing, vector similarity search using pgvector, and confidence-aware response behavior.

---

## Overview

The Contract Renewal Assistant is designed to answer two types of questions:

- Structured questions about contract and employee data
- Policy-based questions about renewal rules, risk indicators, and approval requirements

The system routes queries to the appropriate engine:

- **NL → SQL** for structured database queries  
- **NL → RAG (pgvector)** for unstructured policy retrieval  

A confidence layer evaluates semantic similarity scores and adjusts system behavior when confidence is low.

---

## Architecture

### Core Components

- PostgreSQL 16
- pgvector extension
- Python 3.12
- OpenAI Embeddings API (`text-embedding-3-small`)
- Deterministic confidence scoring based on vector distance

### Data Layers

#### Structured Data
- Employees
- Contracts
- Renewal dates
- Contract value
- Status indicators

#### Unstructured Data
- Markdown-based policy documents
- Chunked by section headers
- Embedded and stored in the `policy_embeddings` table

---

## Confidence Model

Similarity is computed using L2 distance:

```sql
embedding <-> query_embedding
```

Confidence thresholds:

- **HIGH**: distance < 0.90  
- **MEDIUM**: 0.90 ≤ distance < 1.10  
- **LOW**: distance ≥ 1.10  

Behavior:

- HIGH → Return answer normally  
- MEDIUM → Return answer with moderate confidence  
- LOW → Ask a clarifying question instead of answering  

This prevents low-signal semantic matches from producing misleading responses.

---

## Project Structure

```
contract-renewal-assistant/
│
├── app/
│   ├── router.py
│   ├── policy_ingestion.py
│   ├── llm_client.py

