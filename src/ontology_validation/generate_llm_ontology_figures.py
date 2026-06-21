import csv
from pathlib import Path
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent.parent

RESULTS_FILE = (
    BASE_DIR
    / "results"
    / "llm_ontology"
    / "llm_ontology_results.csv"
)

FIGURES_DIR = (
    BASE_DIR
    / "figures"
    / "llm_ontology"
)

FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def load_rows():
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def percentage(correct, total):
    return (correct / total) * 100


def metrics_chart(rows):
    total = len(rows)

    domain = sum(r["llm_ontology_domain_correct"] == "True" for r in rows)
    intent = sum(r["llm_ontology_intent_correct"] == "True" for r in rows)
    endpoint = sum(r["llm_ontology_endpoint_correct"] == "True" for r in rows)
    parameter = sum(r["llm_ontology_parameter_correct"] == "True" for r in rows)
    end_to_end = sum(r["llm_ontology_end_to_end_correct"] == "True" for r in rows)

    labels = [
        "Domain",
        "Intent",
        "Endpoint",
        "Parameter",
        "End-to-End",
    ]

    values = [
        percentage(domain, total),
        percentage(intent, total),
        percentage(endpoint, total),
        percentage(parameter, total),
        percentage(end_to_end, total),
    ]

    plt.figure(figsize=(9, 5))
    plt.bar(labels, values)

    plt.ylim(0, 100)
    plt.ylabel("Accuracy (%)")
    plt.title("LLM + Ontology Standard Metrics")

    for i, v in enumerate(values):
        plt.text(i, v + 1, f"{v:.1f}%", ha="center")

    plt.tight_layout()

    plt.savefig(
        FIGURES_DIR / "llm_ontology_metrics.png",
        dpi=300,
    )

    plt.close()


def validation_chart(rows):
    total = len(rows)

    valid = sum(
        r["ontology_validation_valid"] == "True"
        for r in rows
    )

    hallucination = sum(
        r["has_hallucination"] == "True"
        for r in rows
    )

    missing = sum(
        r["has_missing_parameters"] == "True"
        for r in rows
    )

    inconsistent = sum(
        r["ontology_inconsistent"] == "True"
        for r in rows
    )

    labels = [
        "Valid",
        "Hallucination",
        "Missing Params",
        "Ontology Inconsistent",
    ]

    values = [
        percentage(valid, total),
        percentage(hallucination, total),
        percentage(missing, total),
        percentage(inconsistent, total),
    ]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, values)

    plt.ylim(0, 100)
    plt.ylabel("Percentage (%)")
    plt.title("Ontology Validation Statistics")

    for i, v in enumerate(values):
        plt.text(i, v + 1, f"{v:.1f}%", ha="center")

    plt.tight_layout()

    plt.savefig(
        FIGURES_DIR / "ontology_validation_metrics.png",
        dpi=300,
    )

    plt.close()


def success_failure(rows):
    success = sum(
        r["llm_ontology_end_to_end_correct"] == "True"
        for r in rows
    )

    failure = len(rows) - success

    plt.figure(figsize=(6, 6))

    plt.pie(
        [success, failure],
        labels=[
            "Success",
            "Failure",
        ],
        autopct="%1.1f%%",
        startangle=90,
    )

    plt.title(
        "LLM + Ontology End-to-End Success"
    )

    plt.tight_layout()

    plt.savefig(
        FIGURES_DIR / "llm_ontology_success_failure.png",
        dpi=300,
    )

    plt.close()


def main():
    rows = load_rows()

    metrics_chart(rows)
    validation_chart(rows)
    success_failure(rows)

    print()
    print("Figures generated successfully.")
    print(FIGURES_DIR)


if __name__ == "__main__":
    main()