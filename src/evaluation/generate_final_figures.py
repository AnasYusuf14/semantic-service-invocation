import csv
from pathlib import Path
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parent.parent.parent

COMPARISON_FILE = (
    BASE_DIR
    / "results"
    / "final_comparison"
    / "final_comparison.csv"
)

FIGURES_DIR = (
    BASE_DIR
    / "figures"
    / "final_comparison"
)

FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def load_rows():
    with open(COMPARISON_FILE, "r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def to_float(value):
    if value == "" or value is None:
        return 0.0
    return float(value)


def save_bar_chart(rows, metric_key, title, ylabel, filename):
    methods = [row["method"] for row in rows]
    values = [to_float(row[metric_key]) for row in rows]

    plt.figure(figsize=(11, 6))
    plt.bar(methods, values)

    plt.ylim(0, 100)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=20, ha="right")

    for i, value in enumerate(values):
        plt.text(i, value + 1, f"{value:.2f}%", ha="center")

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=300)
    plt.close()


def save_overall_comparison(rows):
    metrics = [
        "domain_accuracy",
        "intent_accuracy",
        "endpoint_accuracy",
        "parameter_accuracy",
        "end_to_end_accuracy",
    ]

    labels = [
        "Domain",
        "Intent",
        "Endpoint",
        "Parameter",
        "End-to-End",
    ]

    methods = [row["method"] for row in rows]

    x = range(len(labels))
    width = 0.18

    plt.figure(figsize=(12, 6))

    for index, row in enumerate(rows):
        values = [to_float(row[metric]) for metric in metrics]
        positions = [pos + (index - 1.5) * width for pos in x]
        plt.bar(positions, values, width=width, label=row["method"])

    plt.ylim(0, 100)
    plt.ylabel("Accuracy (%)")
    plt.title("Final Accuracy Comparison Across Methods")
    plt.xticks(list(x), labels)
    plt.legend()

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "overall_accuracy_comparison.png", dpi=300)
    plt.close()


def main():
    rows = load_rows()

    save_bar_chart(
        rows,
        "domain_accuracy",
        "Domain Accuracy Comparison",
        "Accuracy (%)",
        "domain_accuracy_comparison.png",
    )

    save_bar_chart(
        rows,
        "intent_accuracy",
        "Intent Accuracy Comparison",
        "Accuracy (%)",
        "intent_accuracy_comparison.png",
    )

    save_bar_chart(
        rows,
        "endpoint_accuracy",
        "Endpoint Selection Accuracy Comparison",
        "Accuracy (%)",
        "endpoint_accuracy_comparison.png",
    )

    save_bar_chart(
        rows,
        "parameter_accuracy",
        "Parameter Filling Accuracy Comparison",
        "Accuracy (%)",
        "parameter_accuracy_comparison.png",
    )

    save_bar_chart(
        rows,
        "end_to_end_accuracy",
        "End-to-End Task Success Comparison",
        "Accuracy (%)",
        "end_to_end_accuracy_comparison.png",
    )

    ontology_rows = [
        row for row in rows
        if row["hallucination_rate"] != ""
    ]

    if ontology_rows:
        save_bar_chart(
            ontology_rows,
            "hallucination_rate",
            "Hallucination Rate in LLM + Ontology",
            "Rate (%)",
            "hallucination_rate.png",
        )

        save_bar_chart(
            ontology_rows,
            "missing_parameter_rate",
            "Missing Parameter Rate in LLM + Ontology",
            "Rate (%)",
            "missing_parameter_rate.png",
        )

        save_bar_chart(
            ontology_rows,
            "ontology_inconsistency_rate",
            "Ontology Inconsistency Rate in LLM + Ontology",
            "Rate (%)",
            "ontology_inconsistency_rate.png",
        )

    save_overall_comparison(rows)

    print("Final comparison figures generated successfully.")
    print(f"Saved in: {FIGURES_DIR}")


if __name__ == "__main__":
    main()