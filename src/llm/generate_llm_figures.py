import csv
from pathlib import Path
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent.parent

RESULTS_FILE = BASE_DIR / "results" / "llm" / "llm_results.csv"
FIGURES_DIR = BASE_DIR / "figures" / "llm"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def read_results():
    with open(RESULTS_FILE, "r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def percent(correct, total):
    return (correct / total) * 100 if total else 0


def generate_metric_accuracy_chart(rows):
    total = len(rows)

    metrics = {
        "Domain": sum(row["domain_correct"] == "True" for row in rows),
        "Intent": sum(row["intent_correct"] == "True" for row in rows),
        "Endpoint": sum(row["endpoint_correct"] == "True" for row in rows),
        "Parameter": sum(row["parameter_correct"] == "True" for row in rows),
        "End-to-End": sum(row["full_correct"] == "True" for row in rows),
    }

    labels = list(metrics.keys())
    values = [percent(value, total) for value in metrics.values()]

    plt.figure(figsize=(9, 5))
    plt.bar(labels, values)
    plt.ylim(0, 100)
    plt.ylabel("Accuracy (%)")
    plt.title("Direct LLM Accuracy by Metric")

    for i, value in enumerate(values):
        plt.text(i, value + 1, f"{value:.1f}%", ha="center")

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "llm_metrics.png", dpi=300)
    plt.close()


def generate_domain_accuracy_chart(rows):
    domain_stats = {}

    for row in rows:
        domain = row["true_domain"]

        if domain not in domain_stats:
            domain_stats[domain] = {"total": 0, "correct": 0}

        domain_stats[domain]["total"] += 1

        if row["intent_correct"] == "True":
            domain_stats[domain]["correct"] += 1

    labels = list(domain_stats.keys())
    values = [
        percent(domain_stats[d]["correct"], domain_stats[d]["total"])
        for d in labels
    ]

    plt.figure(figsize=(9, 5))
    plt.bar(labels, values)
    plt.ylim(0, 100)
    plt.ylabel("Intent Accuracy (%)")
    plt.title("Direct LLM Intent Accuracy by Domain")

    for i, value in enumerate(values):
        plt.text(i, value + 1, f"{value:.1f}%", ha="center")

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "llm_domain_accuracy.png", dpi=300)
    plt.close()


def generate_success_failure_pie(rows):
    success = sum(row["full_correct"] == "True" for row in rows)
    failure = len(rows) - success

    plt.figure(figsize=(6, 6))
    plt.pie(
        [success, failure],
        labels=["End-to-End Success", "Failure"],
        autopct="%1.1f%%",
        startangle=90
    )
    plt.title("Direct LLM End-to-End Success vs Failure")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "llm_success_failure.png", dpi=300)
    plt.close()


def main():
    rows = read_results()

    generate_metric_accuracy_chart(rows)
    generate_domain_accuracy_chart(rows)
    generate_success_failure_pie(rows)

    print("Direct LLM figures generated successfully.")
    print(f"Saved in: {FIGURES_DIR}")


if __name__ == "__main__":
    main()