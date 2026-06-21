import csv
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "src" / "evaluation"))

from parameter_utils import parameters_match


FILES = [
    {
        "name": "Rule-Based",
        "path": BASE_DIR / "results" / "rule_based" / "rule_based_results.csv",
        "true_params": "true_parameters",
        "pred_params": "pred_parameters",
        "true_intent": "true_intent",
        "param_col": "parameter_correct",
        "full_col": "full_correct",
        "correct_cols": ["domain_correct", "intent_correct", "endpoint_correct", "ontology_correct"],
    },
    {
        "name": "Embedding",
        "path": BASE_DIR / "results" / "embedding" / "embedding_results.csv",
        "true_params": "true_parameters",
        "pred_params": "pred_parameters",
        "true_intent": "true_intent",
        "param_col": "parameter_correct",
        "full_col": "full_correct",
        "correct_cols": ["domain_correct", "intent_correct", "endpoint_correct", "ontology_correct"],
    },
    {
        "name": "Direct LLM",
        "path": BASE_DIR / "results" / "llm" / "llm_results.csv",
        "true_params": "true_parameters",
        "pred_params": "pred_parameters",
        "true_intent": "true_intent",
        "param_col": "parameter_correct",
        "full_col": "full_correct",
        "correct_cols": ["domain_correct", "intent_correct", "endpoint_correct", "ontology_correct"],
    },
    {
        "name": "LLM + Ontology",
        "path": BASE_DIR / "results" / "llm_ontology" / "llm_ontology_results.csv",
        "true_params": "true_parameters",
        "pred_params": "corrected_pred_parameters",
        "true_intent": "true_intent",
        "param_col": "llm_ontology_parameter_correct",
        "full_col": "llm_ontology_end_to_end_correct",
        "correct_cols": [
            "llm_ontology_domain_correct",
            "llm_ontology_intent_correct",
            "llm_ontology_endpoint_correct",
            "llm_ontology_ontology_correct",
        ],
    },
]


def is_true(value):
    return str(value).strip() == "True"


def process_file(config):
    path = config["path"]

    with open(path, "r", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    for row in rows:
        param_ok = parameters_match(
            row[config["true_params"]],
            row[config["pred_params"]],
            row[config["true_intent"]],
        )

        row[config["param_col"]] = str(param_ok)

        full_ok = param_ok and all(
            is_true(row[col])
            for col in config["correct_cols"]
        )

        row[config["full_col"]] = str(full_ok)

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)
    param_count = sum(is_true(row[config["param_col"]]) for row in rows)
    full_count = sum(is_true(row[config["full_col"]]) for row in rows)

    print(config["name"])
    print(f"Parameter Accuracy: {param_count / total:.2%}")
    print(f"End-to-End Accuracy: {full_count / total:.2%}")
    print("-" * 50)


def main():
    for config in FILES:
        process_file(config)


if __name__ == "__main__":
    main()