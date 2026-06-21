import csv
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parent.parent.parent

RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = BASE_DIR / "figures" / "required_final"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


FILES = {
    "Rule-Based": RESULTS_DIR / "rule_based" / "rule_based_results.csv",
    "Embedding-Based": RESULTS_DIR / "embedding" / "embedding_results.csv",
    "Direct LLM": RESULTS_DIR / "llm" / "llm_results.csv",
    "LLM + Ontology": RESULTS_DIR / "llm_ontology" / "llm_ontology_results.csv",
}


def read_csv(path):
    with open(path, "r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def is_true(value):
    return str(value).strip() == "True"


def percent(value, total):
    return (value / total) * 100 if total else 0


def get_correct_column(method, metric):
    if method == "LLM + Ontology":
        return {
            "domain": "llm_ontology_domain_correct",
            "intent": "llm_ontology_intent_correct",
            "endpoint": "llm_ontology_endpoint_correct",
            "parameter": "llm_ontology_parameter_correct",
            "end_to_end": "llm_ontology_end_to_end_correct",
        }[metric]

    return {
        "domain": "domain_correct",
        "intent": "intent_correct",
        "endpoint": "endpoint_correct",
        "parameter": "parameter_correct",
        "end_to_end": "full_correct",
    }[metric]


def generate_method_accuracy_table_figure():
    rows = read_csv(RESULTS_DIR / "final_comparison" / "final_comparison.csv")

    metrics = [
        ("intent_accuracy", "Intent"),
        ("endpoint_accuracy", "Endpoint"),
        ("parameter_accuracy", "Parameter"),
        ("end_to_end_accuracy", "End-to-End"),
    ]

    methods = [row["method"] for row in rows]
    x = range(len(metrics))
    width = 0.18

    plt.figure(figsize=(12, 6))

    for index, row in enumerate(rows):
        values = [float(row[key]) for key, _ in metrics]
        positions = [pos + (index - 1.5) * width for pos in x]
        plt.bar(positions, values, width=width, label=row["method"])

    plt.ylim(0, 100)
    plt.ylabel("Accuracy (%)")
    plt.title("Method-Based Accuracy Comparison")
    plt.xticks(list(x), [label for _, label in metrics])
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "method_based_accuracy_comparison.png", dpi=300)
    plt.close()


def generate_error_type_pie_chart():
    rows = read_csv(FILES["LLM + Ontology"])

    wrong_service = 0
    correct_service_wrong_endpoint = 0
    missing_parameter = 0
    ontology_inconsistent = 0
    hallucinated_parameter = 0

    for row in rows:
        domain_ok = is_true(row["llm_ontology_domain_correct"])
        endpoint_ok = is_true(row["llm_ontology_endpoint_correct"])
        has_missing = is_true(row["has_missing_parameters"])
        has_hallucination = is_true(row["has_hallucination"])
        is_inconsistent = is_true(row["ontology_inconsistent"])

        if not domain_ok:
            wrong_service += 1

        if domain_ok and not endpoint_ok:
            correct_service_wrong_endpoint += 1

        if has_missing:
            missing_parameter += 1

        if is_inconsistent:
            ontology_inconsistent += 1

        if has_hallucination:
            hallucinated_parameter += 1

    labels = [
        "Wrong Service",
        "Correct Service / Wrong Endpoint",
        "Missing Parameter",
        "Ontology-Inconsistent Call",
        "Hallucinated Field/Parameter",
    ]

    values = [
        wrong_service,
        correct_service_wrong_endpoint,
        missing_parameter,
        ontology_inconsistent,
        hallucinated_parameter,
    ]

    filtered = [
        (label, value)
        for label, value in zip(labels, values)
        if value > 0
    ]

    labels = [item[0] for item in filtered]
    values = [item[1] for item in filtered]

    plt.figure(figsize=(8, 8))
    plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    plt.title("Error Type Distribution")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "error_type_pie_chart.png", dpi=300)
    plt.close()


def generate_domain_based_success_comparison():
    domain_scores = defaultdict(dict)

    for method, path in FILES.items():
        rows = read_csv(path)

        domain_col = get_correct_column(method, "domain")
        intent_col = get_correct_column(method, "intent")

        stats = defaultdict(lambda: {"total": 0, "correct": 0})

        for row in rows:
            domain = row["true_domain"]
            stats[domain]["total"] += 1

            if is_true(row[intent_col]):
                stats[domain]["correct"] += 1

        for domain, data in stats.items():
            domain_scores[domain][method] = percent(
                data["correct"],
                data["total"],
            )

    domains = sorted(domain_scores.keys())
    methods = list(FILES.keys())

    x = range(len(domains))
    width = 0.18

    plt.figure(figsize=(13, 6))

    for index, method in enumerate(methods):
        values = [
            domain_scores[domain].get(method, 0)
            for domain in domains
        ]
        positions = [pos + (index - 1.5) * width for pos in x]
        plt.bar(positions, values, width=width, label=method)

    plt.ylim(0, 100)
    plt.ylabel("Intent Accuracy (%)")
    plt.title("Domain-Based Success Comparison")
    plt.xticks(list(x), domains)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "domain_based_success_comparison.png", dpi=300)
    plt.close()


def main():
    generate_method_accuracy_table_figure()
    generate_error_type_pie_chart()
    generate_domain_based_success_comparison()

    print("Required final figures generated successfully.")
    print(f"Saved in: {FIGURES_DIR}")


if __name__ == "__main__":
    main() 