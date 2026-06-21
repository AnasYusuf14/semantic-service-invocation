import csv
import sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASET_FILE = BASE_DIR / "dataset" / "service_dataset.csv"

RESULTS_DIR = BASE_DIR / "results" / "embedding"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = RESULTS_DIR / "embedding_results.csv"

RULE_BASED_DIR = BASE_DIR / "src" / "rule_based"
sys.path.append(str(RULE_BASED_DIR))

from rule_based_mapper import extract_parameters

MODEL_NAME = "all-MiniLM-L6-v2"


def normalize(text):
    return str(text).strip().lower()


def load_dataset():
    with open(DATASET_FILE, "r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def main():
    rows = load_dataset()

    model = SentenceTransformer(MODEL_NAME)

    queries = [row["query"] for row in rows]

    embeddings = model.encode(
        queries,
        normalize_embeddings=True
    )

    total = 0

    domain_correct = 0
    intent_correct = 0
    endpoint_correct = 0
    parameter_correct = 0
    ontology_correct = 0
    full_correct = 0

    result_rows = []

    for i, row in enumerate(rows):
        total += 1

        query_embedding = embeddings[i]

        similarities = np.dot(embeddings, query_embedding)

        # Leave-one-out: do not allow matching the same exact row
        similarities[i] = -1

        best_index = int(np.argmax(similarities))
        matched_row = rows[best_index]

        predicted_intent = matched_row["intent"]

        prediction = {
            "domain": matched_row["domain"],
            "intent": matched_row["intent"],
            "endpoint": matched_row["endpoint"],
            "parameters": extract_parameters(row["query"], predicted_intent),
            "ontology_concept": matched_row["ontology_concept"],
            "similarity_score": float(similarities[best_index]),
            "matched_query": matched_row["query"]
        }

        domain_ok = normalize(prediction["domain"]) == normalize(row["domain"])
        intent_ok = normalize(prediction["intent"]) == normalize(row["intent"])
        endpoint_ok = normalize(prediction["endpoint"]) == normalize(row["endpoint"])
        parameter_ok = normalize(prediction["parameters"]) == normalize(row["parameters"])
        ontology_ok = normalize(prediction["ontology_concept"]) == normalize(row["ontology_concept"])

        full_ok = (
            domain_ok
            and intent_ok
            and endpoint_ok
            and parameter_ok
            and ontology_ok
        )

        domain_correct += domain_ok
        intent_correct += intent_ok
        endpoint_correct += endpoint_ok
        parameter_correct += parameter_ok
        ontology_correct += ontology_ok
        full_correct += full_ok

        result_rows.append({
            "query": row["query"],
            "matched_query": prediction["matched_query"],
            "similarity_score": prediction["similarity_score"],

            "true_domain": row["domain"],
            "pred_domain": prediction["domain"],

            "true_intent": row["intent"],
            "pred_intent": prediction["intent"],

            "true_endpoint": row["endpoint"],
            "pred_endpoint": prediction["endpoint"],

            "true_parameters": row["parameters"],
            "pred_parameters": prediction["parameters"],

            "true_ontology": row["ontology_concept"],
            "pred_ontology": prediction["ontology_concept"],

            "domain_correct": domain_ok,
            "intent_correct": intent_ok,
            "endpoint_correct": endpoint_ok,
            "parameter_correct": parameter_ok,
            "ontology_correct": ontology_ok,
            "full_correct": full_ok
        })

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=result_rows[0].keys())
        writer.writeheader()
        writer.writerows(result_rows)

    print()
    print("=" * 60)
    print("EMBEDDING-BASED EVALUATION")
    print("=" * 60)
    print(f"Total Queries           : {total}")
    print()
    print(f"Domain Accuracy         : {domain_correct / total:.2%}")
    print(f"Intent Accuracy         : {intent_correct / total:.2%}")
    print(f"Endpoint Accuracy       : {endpoint_correct / total:.2%}")
    print(f"Parameter Accuracy      : {parameter_correct / total:.2%}")
    print(f"Ontology Accuracy       : {ontology_correct / total:.2%}")
    print()
    print(f"End-to-End Accuracy     : {full_correct / total:.2%}")
    print()
    print("Detailed results saved to:")
    print(OUTPUT_FILE)
    print("=" * 60)


if __name__ == "__main__":
    main()