
# SPARQL Query Translation with LLMs 
If you use the code or datasets from this repository in your research, please cite our upcoming paper:

Bartels, M. C., Banerjee, D., & Usbeck, R. (2025, September). Automating SPARQL Query Translations between DBpedia and Wikidata. To be published in the Proceedings of the SEMANTiCS 2025 Conference.

BibTeX
For easy integration into your reference manager, you can use the following BibTeX entry:
@inproceedings{Bartels2025Automating,
  author    = {Bartels, Malte Christian and Banerjee, Debayan and Usbeck, Ricardo},
  title     = {{Automating SPARQL Query Translations between DBpedia and Wikidata}},
  booktitle = {Proceedings of the SEMANTiCS 2025 Conference},
  year      = {2025},
  month     = {september},
  note      = {To be published}
}

---

## Project Overview

This repository contains all code and resources for the master’s thesis project:  
**"Translating SPARQL Queries Between Knowledge Graphs Using Large Language Models"**

The project explores the capabilities of LLMs in translating SPARQL queries across structurally different knowledge graphs — primarily **Wikidata**, **DBpedia**, **DBLP**, and **OpenAlex** — and classifying typical translation errors.

The primary translation tasks covered are:
* **DBpedia <-> Wikidata** (bidirectional)
* **DBLP -> OpenAlex** (unidirectional)

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

Our Wikidata and DBpedia endpoints were hosted using Qlever Graph database. You may install Qlever using "pip install qlever". You can find the Qleverfiles in qlever-dbpedia/ and qlever-wikidata/ folders in this repository. 
- Wikidata - dumps as of November 2024. 
- DBpedia - download RDF dump from https://ltdata1.informatik.uni-hamburg.de/automating-sparql-translations/dbpedia.tgz, unzip to folder rdf-input/ in qlever-dbpedia/ and use the existing Qleverfile to start Qlever DB.
- DBLP – https://sparql.dblp.org (last accessed on April 18th, 2025)
- OpenAlex – https://semopenalex.org/sparql (last accessed on April 18th, 2025)

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

---

## Project Structure

Automatic-SPARQL-translation/
│
├── data/                             # Final benchmark datasets.
├── DBLP-OpenAlex-data-preparation/   # Scripts and data to prepare the DBLP->OpenAlex benchmark.
├── QALD9-Plus-data-preparation/      # Scripts and data to prepare the DBpedia<->Wikidata benchmark.
├── DBLP-OpenAlex-testing/            # Notebooks and results for DBLP->OpenAlex translation tests.
├── QALD9-Plus-testing/               # Notebooks and results for DBpedia<->Wikidata translation tests.
├── qlever-dbpedia/                   # Local QLever instance for the DBpedia KG.
├── qlever-wikidata/                  # Local QLever instance for the Wikidata KG.
├── Result-comparison/                # Analysis, categorization, and visualization of all test results.
│
├── LICENSE
├── README.md
└── requirements.txt

---

## Folder Breakdown & Purpose

Here is a detailed description of each folder's purpose and its key contents.

### `data/`
Contains the final, curated benchmark datasets used for the translation tasks. These are the "gold standard" datasets.
* `100_complete_entries.json`: The 100-query benchmark for DBpedia/Wikidata.
* `solution_dbpedia_and_wikidata.json`: The solution set for the DBpedia/Wikidata benchmark.
* `mapped_entities_relations.json`: The aligned entities and relations between DBpedia and Wikidata.

### `DBLP-OpenAlex-data-preparation/`
This folder contains the Jupyter Notebook and associated files for creating the DBLP to OpenAlex translation benchmark.
* `DBLP_OpenAlex_data_preperation.ipynb`: The main notebook for data extraction, question generation, and entity alignment between DBLP and OpenAlex.
* `DBLP_to_OpenAlex_input.json`: The generated input file for the translation models.

### `QALD9-Plus-data-preparation/`
Holds the notebook and files for creating the QALD-9+ benchmark for Wikidata and DBpedia translation.
* `QALD9-Plus-data-preparation.ipynb`: The primary notebook used to extract the 100-query benchmark and perform entity/relation alignment between Wikidata and DBpedia.
* `100_complete_entries.json`: The raw extracted benchmark queries.
* `solution_dbpedia_and_wikidata_mapped.json`: The final solution set with mapped entities.

### `DBLP-OpenAlex-testing/`
This directory contains all experiments related to the DBLP to OpenAlex translation task. It's organized by the prompting strategy used.
* `fewshot-DBLP-OpenAlex/`: Tests using a few-shot prompting strategy. Contains notebooks, model outputs (`.json`), result comparisons (`.xlsx`), and plots (`.png`).
* `zeroshot-entity-aligned-DBLP-OpenAlex/`: Tests using a zero-shot prompting strategy with pre-aligned entities.

### `QALD9-Plus-testing/`
This is the most extensive testing directory, containing all experiments for the bidirectional translation between DBpedia and Wikidata. It is organized by prompting strategy and the models tested (Llama, Mistral, DeepSeek).
* **Sub-folders** are named according to the **prompting strategy**, **translation direction**, and **model**. For example, `CoT-entity-aligned/CoT-dbpedia-wikidata/` contains the Chain-of-Thought tests for translating from DBpedia to Wikidata.
* **Key files** in each sub-folder include:
    * `*.ipynb`: The notebook to run the experiment.
    * `*_input_*.json`: The input data for the model.
    * `*_executed.json`: The raw results from the model execution.
    * `*_extracted.json`: The cleaned, extracted SPARQL queries from the model output.
    * `*_results_comparison.xlsx`: A spreadsheet comparing the model's output to the ground truth.
    * `*_results_analysis.xlsx`: Detailed error analysis for each query.

### `qlever-` folders
These folders (`qlever-dbpedia/` and `qlever-wikidata/`) contain the necessary `Qleverfile` to set up local instances of the DBpedia and Wikidata knowledge graphs using the [QLever SPARQL engine](https://github.com/ad-freiburg/qlever). This allows for local query execution and testing.

### `Result-comparison/`
This folder is dedicated to the **analysis and visualization** of all experimental results from the testing directories.
* `results_*.ipynb`: Jupyter notebooks used to aggregate data, perform comparative analysis, and generate visualizations.
* `*.png`: Various plots, heatmaps, and charts visualizing model performance, error distributions, and query correctness.
* `categorization/`: Contains spreadsheets (`.xlsx`) with the detailed, manual error categorization for each model and prompting strategy. These files are the source for the final analysis.

---

## Expected Results

The primary output of this project is the collection of analysis files and visualizations that compare the performance of different Large Language Models and prompting strategies for SPARQL translation.

After running the notebooks in the `*-testing` directories, you can expect to find:
1.  **Translated Queries**: Raw and extracted SPARQL queries in `.json` format for each experiment.
2.  **Comparison Spreadsheets**: Detailed `.xlsx` files in each testing sub-folder comparing the generated query against the solution.
3.  **Aggregated Analysis**: In the `Result-comparison/categorization/` folder, comprehensive `.xlsx` spreadsheets containing the manual error categorization across all experiments.
4.  **Visualizations**: A rich set of plots and heatmaps in the `Result-comparison/` folder that visually summarize the project's findings, such as the comparison of correct queries shown below.
