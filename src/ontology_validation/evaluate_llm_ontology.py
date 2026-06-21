import csv
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

LLM_RESULTS_FILE = BASE_DIR / "results" / "llm" / "llm_results.csv"

RESULTS_DIR = BASE_DIR / "results" / "llm_ontology"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = RESULTS_DIR / "llm_ontology_results.csv"

sys.path.append(str(BASE_DIR / "src" / "ontology_validation"))

from llm_ontology_mapper import llm_ontology_predict


def normalize(text):
    return str(text).strip().lower()


def main():
    total = 0

    domain_correct = 0
    intent_correct = 0
    endpoint_correct = 0
    parameter_correct = 0
    ontology_correct = 0
    end_to_end_correct = 0

    hallucination_count = 0
    missing_parameter_count = 0
    ontology_inconsistent_count = 0
    ontology_valid_count = 0

    output_rows = []

    with open(LLM_RESULTS_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            total += 1

            llm_prediction = {
                "domain": row["pred_domain"],
                "intent": row["pred_intent"],
                "endpoint": row["pred_endpoint"],
                "parameters": row["pred_parameters"],
                "ontology_concept": row["pred_ontology"],
            }

            prediction = llm_ontology_predict(llm_prediction)

            domain_ok = normalize(prediction["domain"]) == normalize(row["true_domain"])
            intent_ok = normalize(prediction["intent"]) == normalize(row["true_intent"])
            endpoint_ok = normalize(prediction["endpoint"]) == normalize(row["true_endpoint"])
            parameter_ok = normalize(prediction["parameters"]) == normalize(row["true_parameters"])
            ontology_ok = normalize(prediction["ontology_concept"]) == normalize(row["true_ontology"])

            end_to_end_ok = (
                domain_ok
                and intent_ok
                and endpoint_ok
                and parameter_ok
                and ontology_ok
            )

            has_hallucination = prediction["has_hallucination"]
            has_missing_parameters = prediction["has_missing_parameters"]
            ontology_inconsistent = prediction["ontology_inconsistent"]
            ontology_valid = prediction["ontology_validation_valid"]

            domain_correct += domain_ok
            intent_correct += intent_ok
            endpoint_correct += endpoint_ok
            parameter_correct += parameter_ok
            ontology_correct += ontology_ok
            end_to_end_correct += end_to_end_ok

            hallucination_count += has_hallucination
            missing_parameter_count += has_missing_parameters
            ontology_inconsistent_count += ontology_inconsistent
            ontology_valid_count += ontology_valid

            output_rows.append({
                "query": row["query"],

                "true_domain": row["true_domain"],
                "original_pred_domain": row["pred_domain"],
                "corrected_pred_domain": prediction["domain"],

                "true_intent": row["true_intent"],
                "original_pred_intent": row["pred_intent"],
                "corrected_pred_intent": prediction["intent"],

                "true_endpoint": row["true_endpoint"],
                "original_pred_endpoint": row["pred_endpoint"],
                "corrected_pred_endpoint": prediction["endpoint"],

                "true_parameters": row["true_parameters"],
                "original_pred_parameters": row["pred_parameters"],
                "corrected_pred_parameters": prediction["parameters"],

                "true_ontology": row["true_ontology"],
                "original_pred_ontology": row["pred_ontology"],
                "corrected_pred_ontology": prediction["ontology_concept"],

                "llm_ontology_domain_correct": domain_ok,
                "llm_ontology_intent_correct": intent_ok,
                "llm_ontology_endpoint_correct": endpoint_ok,
                "llm_ontology_parameter_correct": parameter_ok,
                "llm_ontology_ontology_correct": ontology_ok,
                "llm_ontology_end_to_end_correct": end_to_end_ok,

                "ontology_validation_valid": ontology_valid,
                "has_hallucination": has_hallucination,
                "has_missing_parameters": has_missing_parameters,
                "ontology_inconsistent": ontology_inconsistent,
                "missing_parameters": prediction["missing_parameters"],
                "hallucinated_parameters": prediction["hallucinated_parameters"],
            })

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=output_rows[0].keys())
        writer.writeheader()
        writer.writerows(output_rows)

    print()
    print("=" * 60)
    print("LLM + ONTOLOGY SAFE CORRECTION EVALUATION")
    print("=" * 60)
    print(f"Total Queries                 : {total}")
    print()
    print("Standard Metrics")
    print("-" * 60)
    print(f"Domain Accuracy               : {domain_correct / total:.2%}")
    print(f"Intent Accuracy               : {intent_correct / total:.2%}")
    print(f"Endpoint Accuracy             : {endpoint_correct / total:.2%}")
    print(f"Parameter Accuracy            : {parameter_correct / total:.2%}")
    print(f"Ontology Accuracy             : {ontology_correct / total:.2%}")
    print(f"End-to-End Accuracy           : {end_to_end_correct / total:.2%}")
    print()
    print("Ontology Validation Metrics")
    print("-" * 60)
    print(f"Ontology Valid Call Rate      : {ontology_valid_count / total:.2%}")
    print(f"Hallucination Rate            : {hallucination_count / total:.2%}")
    print(f"Missing Parameter Rate        : {missing_parameter_count / total:.2%}")
    print(f"Ontology Inconsistency Rate   : {ontology_inconsistent_count / total:.2%}")
    print()
    print("Detailed results saved to:")
    print(OUTPUT_FILE)
    print("=" * 60)


if __name__ == "__main__":
    main()