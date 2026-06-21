import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

RESULTS_DIR = BASE_DIR / "results"

FINAL_DIR = RESULTS_DIR / "final_comparison"
FINAL_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = FINAL_DIR / "final_comparison.csv"


FILES = {
    "Rule-Based": RESULTS_DIR / "rule_based" / "rule_based_results.csv",
    "Embedding-Based": RESULTS_DIR / "embedding" / "embedding_results.csv",
    "Direct LLM": RESULTS_DIR / "llm" / "llm_results.csv",
    "LLM + Ontology": RESULTS_DIR / "llm_ontology" / "llm_ontology_results.csv",
}


COLUMN_MAP = {
    "Rule-Based": {
        "domain": "domain_correct",
        "intent": "intent_correct",
        "endpoint": "endpoint_correct",
        "parameter": "parameter_correct",
        "end_to_end": "full_correct",
    },
    "Embedding-Based": {
        "domain": "domain_correct",
        "intent": "intent_correct",
        "endpoint": "endpoint_correct",
        "parameter": "parameter_correct",
        "end_to_end": "full_correct",
    },
    "Direct LLM": {
        "domain": "domain_correct",
        "intent": "intent_correct",
        "endpoint": "endpoint_correct",
        "parameter": "parameter_correct",
        "end_to_end": "full_correct",
    },
    "LLM + Ontology": {
        "domain": "llm_ontology_domain_correct",
        "intent": "llm_ontology_intent_correct",
        "endpoint": "llm_ontology_endpoint_correct",
        "parameter": "llm_ontology_parameter_correct",
        "end_to_end": "llm_ontology_end_to_end_correct",
    },
}


def is_true(value):
    return str(value).strip() == "True"


def percentage(correct, total):
    return round((correct / total) * 100, 2) if total else 0


def read_rows(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def compute_metrics(method_name, file_path):
    rows = read_rows(file_path)
    total = len(rows)
    columns = COLUMN_MAP[method_name]

    domain = sum(is_true(row[columns["domain"]]) for row in rows)
    intent = sum(is_true(row[columns["intent"]]) for row in rows)
    endpoint = sum(is_true(row[columns["endpoint"]]) for row in rows)
    parameter = sum(is_true(row[columns["parameter"]]) for row in rows)
    end_to_end = sum(is_true(row[columns["end_to_end"]]) for row in rows)

    hallucination_rate = ""
    missing_parameter_rate = ""
    ontology_inconsistency_rate = ""

    if method_name == "LLM + Ontology":
        hallucination = sum(is_true(row["has_hallucination"]) for row in rows)
        missing = sum(is_true(row["has_missing_parameters"]) for row in rows)
        inconsistent = sum(is_true(row["ontology_inconsistent"]) for row in rows)

        hallucination_rate = percentage(hallucination, total)
        missing_parameter_rate = percentage(missing, total)
        ontology_inconsistency_rate = percentage(inconsistent, total)

    return {
        "method": method_name,
        "total_queries": total,
        "domain_accuracy": percentage(domain, total),
        "intent_accuracy": percentage(intent, total),
        "endpoint_accuracy": percentage(endpoint, total),
        "parameter_accuracy": percentage(parameter, total),
        "end_to_end_accuracy": percentage(end_to_end, total),
        "hallucination_rate": hallucination_rate,
        "missing_parameter_rate": missing_parameter_rate,
        "ontology_inconsistency_rate": ontology_inconsistency_rate,
    }


def main():
    results = []

    for method_name, file_path in FILES.items():
        results.append(compute_metrics(method_name, file_path))

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print()
    print("=" * 80)
    print("FINAL COMPARISON")
    print("=" * 80)

    for row in results:
        print(row)

    print()
    print("Saved to:")
    print(OUTPUT_FILE)
    print("=" * 80)


if __name__ == "__main__":
    main()