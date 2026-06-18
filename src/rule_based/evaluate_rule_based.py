import csv
from pathlib import Path

from rule_based_mapper import rule_based_predict

# ==========================
# Paths
# ==========================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATASET_FILE = BASE_DIR / "dataset" / "service_dataset.csv"

RESULTS_DIR = BASE_DIR / "results" / "rule_based"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = RESULTS_DIR / "rule_based_results.csv"


# ==========================
# Helpers
# ==========================

def normalize(text):
    return str(text).strip().lower()


# ==========================
# Evaluation
# ==========================

total = 0

domain_correct = 0
intent_correct = 0
endpoint_correct = 0
parameter_correct = 0
ontology_correct = 0
full_correct = 0

rows = []

with open(DATASET_FILE, "r", encoding="utf-8") as f:

    reader = csv.DictReader(f)

    for row in reader:

        total += 1

        prediction = rule_based_predict(row["query"])

        domain_ok = normalize(prediction["domain"]) == normalize(row["domain"])

        intent_ok = normalize(prediction["intent"]) == normalize(row["intent"])

        endpoint_ok = normalize(prediction["endpoint"]) == normalize(row["endpoint"])

        parameter_ok = (
            normalize(prediction["parameters"])
            == normalize(row["parameters"])
        )

        ontology_ok = (
            normalize(prediction["ontology_concept"])
            == normalize(row["ontology_concept"])
        )

        full_ok = (
            domain_ok
            and intent_ok
            and endpoint_ok
            and parameter_ok
            and ontology_ok
        )

        if domain_ok:
            domain_correct += 1

        if intent_ok:
            intent_correct += 1

        if endpoint_ok:
            endpoint_correct += 1

        if parameter_ok:
            parameter_correct += 1

        if ontology_ok:
            ontology_correct += 1

        if full_ok:
            full_correct += 1

        rows.append({

            "query": row["query"],

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

# ==========================
# Save CSV
# ==========================

fieldnames = list(rows[0].keys())

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(rows)

# ==========================
# Print Results
# ==========================

print()

print("=" * 60)
print("RULE-BASED EVALUATION")
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

print(f"Detailed results saved to:")

print(OUTPUT_FILE)

print("=" * 60)