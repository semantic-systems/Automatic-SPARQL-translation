import json
import pandas as pd
import re
from SPARQLWrapper import SPARQLWrapper, JSON

# Define endpoint for Wikidata
WIKIDATA_ENDPOINT = "http://localhost:7001"

# Define standard SPARQL prefixes for removal
STANDARD_PREFIXES = [
    """\nPREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>""",

    """PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>"""
]

def remove_standard_prefixes(query):
    """Removes predefined standard prefixes after executing a query."""
    for prefix in STANDARD_PREFIXES:
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
        return (["True"] if results['boolean'] else ["False"]), None

    answers = []
    bindings = results.get('results', {}).get('bindings', [])
    for binding in bindings:
        for var_name in binding:
            answers.append(binding[var_name]['value'])
    
    return (answers if answers else ["No answer"]), None

def detect_dataset_mismatch(query):
    """Detects dataset mismatches (e.g., DBpedia patterns in a Wikidata query)."""
    dbpedia_elements = ["dbo:", "dbp:", "dbr:", "dbc:", "dct:", "rdf:"]
    wikidata_elements = ["wd:", "wdt:", "p:", "ps:", "pq:"]

    contains_dbpedia = any(ele in query for ele in dbpedia_elements)
    contains_wikidata = any(ele in query for ele in wikidata_elements)

    return contains_dbpedia and not contains_wikidata

def classify_error(row):
    """Classifies errors while skipping correctly answered questions."""
    query_failed = "Query failed" in row["Query_Answers_Generated"]
    no_answer = "No answer" in row["Query_Answers_Generated"]
    error_message = row["Error_Message"]
    generated_query = row["SPARQL_Query_Generated"]
    gold_query = row["Gold_Label_Query"]

    if row["Correct"] is True:
        return "Correct"

    if detect_dataset_mismatch(generated_query):
        return "Unadapted Dataset Patterns"

    if query_failed and isinstance(error_message, str) and "QueryBadFormed" in error_message:
        return "Query Bad Formed"

    gold_props = set(re.findall(r'wdt:P\d+', gold_query))
    generated_props = set(re.findall(r'wdt:P\d+', generated_query))
    gold_entities = set(re.findall(r'wd:Q\d+', gold_query))
    generated_entities = set(re.findall(r'wd:Q\d+', generated_query))

    # Property treated as Entity
    if "wd:" in generated_query and "wdt:" not in generated_query:
        if ("wdt:" in gold_query and "wd:" in gold_query) or (
            "http://www.wikidata.org/prop/direct/" in gold_query and "http://www.wikidata.org/entity/" in gold_query
        ):
            return "Property treated as Entity"

    # Entity treated as Property
    if "wdt:" in generated_query and "wd:" not in generated_query:
        if ("wdt:" in gold_query and "wd:" in gold_query) or (
            "http://www.wikidata.org/prop/direct/" in gold_query and "http://www.wikidata.org/entity/" in gold_query
        ):
            return "Entity treated as Property"

    # Missing P31 detection
    if "wdt:P31" in gold_query and "wdt:P31" not in generated_query:
        return "Missing P31"

    if no_answer and gold_props and generated_props and gold_props != generated_props:
        return "Wrong Property"

    if gold_props - generated_props:
        return "Wrong Property"

    if no_answer and gold_entities and generated_entities and gold_entities != generated_entities:
        return "Wrong Entity"
    
    if gold_entities - generated_entities:
        return "Wrong Entity"
    
    if no_answer and "None" in error_message:
        return "Structural Error"

    return "Other"

def evaluate_wikidata_queries(
    input_file, 
    output_excel, 
    query_key="sparql_query", 
    solution_file="../../../data/100_complete_entries_solution.json"
):
    """
    Executes SPARQL queries for Wikidata, compares with gold labels, classifies errors,
    and saves results. Now also includes the gold label answer in the DataFrame.
    """
    endpoint = WIKIDATA_ENDPOINT
    result_key = "wikidata_results"

    with open(input_file, "r") as f:
        data = json.load(f)

    with open(solution_file, "r") as f:
        solution_data = json.load(f)

    # Map each question to its gold label answers and query
    solution_mapping = {
        entry['question']: {
            "answers": entry.get(result_key, []),
            "query": entry.get("wikidata_query", '')
        }
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

        # Get the gold label answers and query
        gold_answers = solution_mapping.get(question, {}).get("answers", [])
        gold_query = solution_mapping.get(question, {}).get("query", "")

        # Compare extracted answers vs. gold label answers for correctness
        is_correct = (set(gold_answers) == set(extracted_answers))

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