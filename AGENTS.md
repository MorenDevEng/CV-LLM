# AGENTS.md - RAG-PDFs Development Guide

This document provides guidelines for agentic coding agents working on this codebase.

## Project Overview

A Flask-based RAG (Retrieval-Augmented Generation) application that processes PDF documents and provides:
- PDF upload and embedding storage via ChromaDB
- Chat interface powered by Groq LLM (Llama 3.3)
- Keyword matching against document content

## Technology Stack

- **Backend**: Flask
- **LLM**: LangChain + Groq (llama-3.3-70b-versatile)
- **Vector Store**: ChromaDB
- **PDF Processing**: PyPDFLoader, RecursiveCharacterTextSplitter
- **Environment**: Python 3.13, pip

## Build & Run Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file with GROQ_API_KEY=your_api_key

# Run Flask app
python -m flask --app src/app run --debug --host=0.0.0.0 --port=5000

# Or directly
python src/app.py
```

### Docker
```bash
# Build image
docker build -t rag-pdfs .

# Run container
docker run -p 5000:5000 --env-file .env rag-pdfs

# Or with docker-compose
docker-compose up --build
```

### Running a Single Test
This project currently has no test suite. When adding tests, use pytest:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agent.py

# Run specific test
pytest tests/test_agent.py::test_validate_question
```

## Code Style Guidelines

### General
- Follow PEP 8 style guide
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable and function names

### Imports
- Standard library imports first
- Third-party imports second
- Local imports last
- Group imports by type with blank lines between groups
- Example:
```python
import os
import re
from typing import Optional

from flask import Flask, jsonify, render_template, request
from langchain_groq import ChatGroq

from agent import RAGPipeline
```

### Types
- Use type hints for function parameters and return values
- Prefer built-in types (str, int, list, dict) over typing module when simple
- Example:
```python
def process_pdf(self, file_path: str) -> list[str]:
    ...
```

### Naming Conventions
- **Functions/Variables**: snake_case (e.g., `rag_pipeline`, `process_pdf`)
- **Classes**: PascalCase (e.g., `RAGPipeline`, `SecurityError`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_QUERY_LENGTH`)
- **Private functions/variables**: prefix with underscore (e.g., `_internal_func`)

### Error Handling
- Use custom exception classes for domain-specific errors (see `SecurityError`)
- Always catch specific exceptions, avoid bare `except:`
- Return meaningful error messages to API consumers
- Example:
```python
class SecurityError(Exception):
    pass

def chat(message: str) -> dict:
    try:
        result = rag_pipeline.chat(message)
        return {'success': True, 'response': result}
    except SecurityError as e:
        return {'success': False, 'error': str(e)}
    except Exception as e:
        return {'success': False, 'error': 'Internal server error'}
```

### Input Validation & Security
- Sanitize all user inputs before processing
- Enforce maximum length limits on queries
- Validate file types for uploads (PDF only)
- Block dangerous patterns (prompt injection, code execution)
- Use `SecurityError` for security-related validation failures

### File Structure
```
RAG-PDFs/
├── src/
│   ├── app.py          # Flask routes and app config
│   ├── agent.py        # RAG pipeline logic
│   └── templates/
│       └── index.html  # Frontend
├── pdfs/               # Uploaded PDFs
├── vectordb/           # ChromaDB storage
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env
```

### Flask Best Practices
- Use `os.path` for path operations (not hardcoded paths)
- Set `UPLOAD_FOLDER` and `MAX_CONTENT_LENGTH` config
- Validate file extensions before processing
- Use `secure_filename()` for uploaded files
- Return JSON responses with consistent structure:
```python
return jsonify({'success': True, 'data': ...})
return jsonify({'success': False, 'error': 'message'})
```

### LangChain/RAG Patterns
- Use `RunnablePassthrough` for passing question through chain
- Set appropriate `chunk_size` (1000) and `chunk_overlap` (100)
- Use similarity search with `k=5` for QA, `k=10` for keyword matching
- Include system prompt with clear rules about answering only from context

## Environment Variables

Required in `.env`:
```
GROQ_API_KEY=your_groq_api_key_here
```

## Common Tasks

### Adding a new API endpoint
1. Add route in `src/app.py`
2. Create corresponding method in `src/agent.py` if needed
3. Return consistent JSON structure with success/error

### Modifying the LLM
Change model in `src/agent.py:80`:
```python
self.llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # Change model name
    temperature=0.2
)
```

### Adding input validation
Add patterns to `BLOCKED_PATTERNS` list in `src/agent.py` and create validation functions using the existing `sanitize_input()` and `check_blocked_patterns()` utilities.
