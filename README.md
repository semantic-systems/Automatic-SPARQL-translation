# SPARQL Query Translation with LLMs 
by Malte Bartels (Master's Thesis)  

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

3. Install requirements
```bash
pip install -r requirements.txt
```

### Evaluation Strategy
The evaluation includes:
- Accuracy (based on gold-label answers from QALD-9 and DBLP-OpenAlex)
- Structured error classification across 8 error types
- Model comparisons across KG pairs and prompting strategies
- Generalization analysis between open-domain and scholarly KGs

### Knowledge Graphs Used
- Wikidata
- DBpedia
- DBLP – https://sparql.dblp.org
- OpenAlex – https://semopenalex.org/sparql

### Ethical Considerations
This project acknowledges and reflects on:
- Social and structural biases in KGs (e.g., gender representation, geographic imbalance)
- The risk of reproducing bias through LLM-driven translation
- Environmental impact of large-scale LLM usage
- Sources and discussions can be found in the Ethical Considerations section of the thesis.

### Requirements

Main libraries used:
requests
json
re
os
glob
sys
pandas
matplotlib
seaborn
SPARQLWrapper
openai
sentence-transformers
scikit-learn


Install all dependencies via:
```bash
pip install -r requirements.txt
```
