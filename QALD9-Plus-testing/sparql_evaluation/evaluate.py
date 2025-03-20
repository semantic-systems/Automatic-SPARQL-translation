import json
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

# Define endpoints for Wikidata and DBpedia
WIKIDATA_ENDPOINT = "http://localhost:7001"
DBPEDIA_ENDPOINT = "http://localhost:7012"

# Define SPARQL prefixes for Wikidata
WIKIDATA_PREFIXES = """
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
"""

# Define SPARQL prefixes for DBpedia
DBPEDIA_PREFIXES = """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX res: <http://dbpedia.org/resource/>
PREFIX yago: <http://dbpedia.org/class/yago/>
PREFIX onto: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dbc: <http://dbpedia.org/resource/Category:>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
"""

def ensure_prefixes(query, kg):
    """Ensure SPARQL query contains the necessary prefixes for the given knowledge graph (KG)."""
    if kg == "wikidata":
        if not query.strip().startswith("PREFIX"):
            return WIKIDATA_PREFIXES + query
        return query
    elif kg == "dbpedia":
        required_prefixes = [
            "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>",
            "PREFIX dbo: <http://dbpedia.org/ontology/>",
            "PREFIX dbr: <http://dbpedia.org/resource/>",
        ]
        missing_prefixes = [p for p in required_prefixes if p not in query]
        if missing_prefixes:
            query = "\n".join(missing_prefixes) + "\n" + query
        return query
    else:
        raise ValueError("Invalid KG. Choose either 'wikidata' or 'dbpedia'.")

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

def evaluate_sparql_queries(input_file, output_excel, query_key="sparql_query", solution_file="../../../data/100_complete_entries_solution.json", kg="wikidata"):
    """Evaluates SPARQL queries for Wikidata or DBpedia, compares them to gold labels, and saves results to Excel."""
    
    # Select endpoint based on KG
    if kg == "wikidata":
        endpoint = WIKIDATA_ENDPOINT
        result_key = "wikidata_results"
    elif kg == "dbpedia":
        endpoint = DBPEDIA_ENDPOINT
        result_key = "dbpedia_results"
    else:
        raise ValueError("Invalid KG. Choose either 'wikidata' or 'dbpedia'.")

    # Load input dataset
    with open(input_file, "r") as f:
        data = json.load(f)

    # Load gold label solutions
    with open(solution_file, "r") as f:
        solution_data = json.load(f)

    # Create a mapping of questions to gold label answers and queries
    solution_mapping = {
        entry['question']: {
            "answers": entry[result_key], 
            "query": entry.get(f"{kg}_query", '')  # Adapt key based on KG
        } 
        for entry in solution_data
    }

    # Store results
    comparison_results = []

    # Process each query
    for entry in data:
        question = entry.get("natural_language_question", "")
        sparql_query = entry.get(query_key, "")

        if not sparql_query:
            continue

        # Ensure correct prefixes for the KG
        sparql_query_with_prefixes = ensure_prefixes(sparql_query, kg)

        # Execute query
        results = query_sparql(endpoint, sparql_query_with_prefixes)
        extracted_answers, error_message = extract_answer(results)

        # Get gold label answers and query
        expected_answers = solution_mapping.get(question, {}).get("answers", [])
        gold_label_query = solution_mapping.get(question, {}).get("query", "")

        # Determine correctness
        is_correct = set(expected_answers) == set(extracted_answers) if expected_answers else False

        # Append results
        comparison_results.append({
            "Question": question,
            "SPARQL Query (Generated)": sparql_query_with_prefixes,
            "Gold Label Query": gold_label_query,
            "Gold Label Answers": expected_answers,
            "Query Answers": extracted_answers,
            "Error Message": error_message if error_message else "None",
            "Correct": is_correct
        })

    # Save results to Excel
    df = pd.DataFrame(comparison_results)
    df.to_excel(output_excel, index=False)

    # Calculate accuracy metrics
    total_queries = len(comparison_results)
    correct_queries = sum(1 for result in comparison_results if result["Correct"])
    incorrect_queries = sum(1 for result in comparison_results if not result["Correct"] and "Query failed" not in result["Query Answers"] and "No answer" not in result["Query Answers"])
    failed_queries = sum(1 for result in comparison_results if "Query failed" in result["Query Answers"])
    no_answer_queries = sum(1 for result in comparison_results if "No answer" in result["Query Answers"])

    accuracy = (correct_queries / total_queries) * 100 if total_queries > 0 else 0

    # Print summary
    print(f"Total Queries: {total_queries}")
    print(f"Correct Queries: {correct_queries}")
    print(f"Incorrect Queries: {incorrect_queries}")
    print(f"Query Failed to Execute: {failed_queries}")
    print(f"No Answer Queries: {no_answer_queries}")
    print(f"Accuracy: {accuracy:.2f}%")
