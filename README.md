# Contract Policy Risk Analyzer 

An intelligent document analysis system that compares employee contracts against business policies to identify compliance risks and missing terms using LLM-powered semantic analysis.

---

## Overview

This application automates the review of employment contracts by extracting clauses from PDF documents, categorizing them by policy type, and identifying potential risks when contract terms deviate from established business policies.

---

## Installations 

- required **ollama** models

```sh
ollama pull qwen3-embedding:8b
ollama pull llama3.1:8b
```

- python pip requirements

```sh
pip install -r requirements.txt
```

---

## start the application

```sh
streamlit run main.py
```

--- 

## Project Structure

```
contract-policy-risk-analyzer/
├── main.py                       # Streamlit application
├── data_cleanising.py            # PDF processing and clause extraction
├── embedding_model.py            # Vector embedding and storage
├── prompts/
│   └── policy-risk-analyser.txt
├── output_files/                 # Uploaded PDFs
├── business-policy-db/           # ChromaDB for policies
├── employee-contract-db/         # ChromaDB for contracts
└── requirements.txt
```