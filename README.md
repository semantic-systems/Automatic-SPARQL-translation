# SPARQL Query Translation with LLMs  

---

## Project Overview

This repository contains all code and resources for the master’s thesis project:  
**"Translating SPARQL Queries Between Knowledge Graphs Using Large Language Models"**

The project explores the capabilities of LLMs in translating SPARQL queries across structurally different knowledge graphs — primarily **Wikidata**, **DBpedia**, **DBLP**, and **OpenAlex** — and classifying typical translation errors.

Key components:
- SPARQL-to-SPARQL translation using modern LLMs
- Prompting strategies: *zero-shot*, *few-shot*, *chain-of-thought*, *CoT with `<think>`*
- Detailed error classification system with 8 custom categories
- Generalizability testing across domain-specific KGs

---
requirements.txt README.md


---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/SPARQL-LLM-Translation.git
cd SPARQL-LLM-Translation
```

2. Create virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
