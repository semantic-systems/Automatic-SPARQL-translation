import json
import pandas as pd
import re
from SPARQLWrapper import SPARQLWrapper, JSON

# DBpedia endpoint
DBPEDIA_ENDPOINT = "http://localhost:7012"

# DBpedia-specific prefixes
DBPEDIA_PREFIXES = [
    """\nPREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX res: <http://dbpedia.org/resource/>
PREFIX yago: <http://dbpedia.org/class/yago/>
PREFIX onto: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dbc: <http://dbpedia.org/resource/Category:>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>"""
]

def remove_dbpedia_prefixes(query):
    """Remove DBpedia standard prefixes from the query."""
    for prefix in DBPEDIA_PREFIXES:
        query = query.replace(prefix, "").strip()
    return query

def query_sparql(endpoint, query):
    """Execute a SPARQL query and return results."""
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setMethod('GET')
    sparql.setTimeout(60)

    try:
        return sparql.query().convert()
    except Exception as e:
        return {"error": str(e)}

def extract_answer(results):
    """Extract answers from SPARQL query results."""
    if "error" in results:
        return ["Query failed"], results["error"]

    if 'boolean' in results:
        return ["True"] if results['boolean'] else ["False"], None

    answers = []
    bindings = results.get('results', {}).get('bindings', [])
    for binding in bindings:
        for var_name in binding:
            answers.append(binding[var_name]['value'])

    return answers if answers else ["No answer"], None

def classify_error(row):
    query_failed = "Query failed" in row["Query_Answers_Generated"]
    no_answer = "No answer" in row["Query_Answers_Generated"]
    error_message = row["Error_Message"]
    generated_query = row["SPARQL_Query_Generated"]
    gold_query = row["Gold_Label_Query"]

    if row["Correct"] is True:
        return "Correct"

    # Unadapted Dataset Patterns (Wikidata patterns in DBpedia)
    if re.search(r'\b(wd:|wdt:|p:|ps:|pq:)\b', generated_query) or \
       "http://www.wikidata.org/" in generated_query:
        return "Unadapted Dataset Patterns"

    # Syntax error
    if query_failed and isinstance(error_message, str) and "QueryBadFormed" in error_message:
        return "Query Bad Formed"

    # Ontology treated as Resource
    if (
        ("dbpedia-resource:" in generated_query or "http://dbpedia.org/resource/" in generated_query)
        and not ("dbpedia-ontology:" in generated_query or "http://dbpedia.org/ontology/" in generated_query)
        and ("http://dbpedia.org/ontology/" in gold_query or "dbo:" in gold_query)
    ):
        return "Ontology treated as Resource"

    # Resource treated as Ontology
    if (
        ("dbpedia-ontology:" in generated_query or "http://dbpedia.org/ontology/" in generated_query)
        and not ("dbpedia-resource:" in generated_query or "http://dbpedia.org/resource/" in generated_query)
        and ("http://dbpedia.org/resource/" in gold_query or "dbr:" in gold_query)
    ):
        return "Resource treated as Ontology"

    # Missing rdf:type
    if "rdf:type" in gold_query and "rdf:type" not in generated_query:
        return "Missing rdf:type"

    # Incomplete Query
    if no_answer and len(generated_query) < len(gold_query) * 0.6:
        return "Incomplete Query"

    # Structural Error: no results, no error, but structure deviates
    if no_answer and "None" in error_message:
        return "Structural Error"
    
    return "Other"

def evaluate_dbpedia_queries(input_file, output_excel, query_key="sparql_query", solution_file="../../../data/100_complete_entries_solution.json"):
    """Executes SPARQL queries for DBpedia, compares with gold labels, classifies errors, and saves results."""

    endpoint = DBPEDIA_ENDPOINT
    result_key = "dbpedia_results"

    with open(input_file, "r") as f:
        data = json.load(f)

    with open(solution_file, "r") as f:
        solution_data = json.load(f)

    solution_mapping = {
        entry['question']: {"answers": entry[result_key], "query": entry.get("dbpedia_query", '')}
        for entry in solution_data
    }

    comparison_results = []

    for entry in data:
        question = entry.get("natural_language_question", "")
        sparql_query = entry.get(query_key, "")

        if not sparql_query:
            continue

        results = query_sparql(endpoint, sparql_query)
        extracted_answers, error_message = extract_answer(results)

        gold_entry = solution_mapping.get(question, {})
        gold_answers = gold_entry.get("answers", [])
        gold_query = gold_entry.get("query", "")

        is_correct = set(gold_answers) == set(extracted_answers)

        comparison_results.append({
            "Question": question,
            "SPARQL_Query_Generated": sparql_query,
            "Gold_Label_Query": gold_query,
            "Query_Answers_Generated": extracted_answers,
            "Gold_Label_Answers": gold_answers,
            "Error_Message": error_message if error_message else "None",
            "Correct": is_correct
        })

    df = pd.DataFrame(comparison_results)
    df["Error Category"] = df.apply(classify_error, axis=1)
    df.to_excel(output_excel, index=False)