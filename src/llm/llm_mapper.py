import csv
import json
import re
from pathlib import Path

from openai import OpenAI

from config import get_openai_api_key


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASET_FILE = BASE_DIR / "dataset" / "service_dataset.csv"

MODEL_NAME = "gpt-4o-mini"


def load_service_catalog():
    operations = {}

    with open(DATASET_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            intent = row["intent"]

            if intent not in operations:
                operations[intent] = {
                    "domain": row["domain"],
                    "intent": row["intent"],
                    "endpoint": row["endpoint"],
                    "ontology_concept": row["ontology_concept"],
                }

    return list(operations.values())


SERVICE_CATALOG = load_service_catalog()


def build_prompt(query: str) -> str:
    return f"""
You are a semantic API service selector.

Given a natural language user query, select the correct API operation from the allowed operations list.

Allowed operations:
{json.dumps(SERVICE_CATALOG, indent=2)}

Return ONLY a raw JSON object.
Do not use markdown.
Do not wrap the JSON in ```json.
Do not write explanations.

Required JSON format:
{{
  "domain": "Weather | Travel | Product | Order | Calendar",
  "intent": "operationId",
  "endpoint": "endpoint path",
  "parameters": "key=value;key=value",
  "ontology_concept": "same as intent"
}}

Rules:
- Use only one operation from the allowed operations list.
- Do not invent domains.
- Do not invent intents.
- Do not invent endpoints.
- ontology_concept must be exactly equal to intent.
- parameters must be a STRING, not an object.
- parameters must use this format exactly: key=value;key=value
- Use the exact parameter names from the API when possible.
- If a required parameter is missing, use UNKNOWN.
- Return JSON only.

User query:
{query}
"""


def clean_json_text(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    return text.strip()


def parameters_to_string(parameters) -> str:
    if isinstance(parameters, str):
        return parameters

    if isinstance(parameters, dict):
        return ";".join(
            f"{key}={value}"
            for key, value in parameters.items()
        )

    return ""


def llm_predict(query: str) -> dict:
    client = OpenAI(api_key=get_openai_api_key())

    response = client.responses.create(
        model=MODEL_NAME,
        input=build_prompt(query),
        temperature=0
    )

    text = clean_json_text(response.output_text)

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        return {
            "domain": "Invalid",
            "intent": "Invalid",
            "endpoint": "Invalid",
            "parameters": "",
            "ontology_concept": "Invalid",
            "raw_output": response.output_text
        }

    intent = result.get("intent", "UNKNOWN")

    return {
        "domain": result.get("domain", "UNKNOWN"),
        "intent": intent,
        "endpoint": result.get("endpoint", "UNKNOWN"),
        "parameters": parameters_to_string(result.get("parameters", "")),
        "ontology_concept": result.get("ontology_concept", intent),
    }


if __name__ == "__main__":
    test_queries = [
        "Should I carry an umbrella in Istanbul tomorrow?",
        "I need to get from Istanbul to Dubai tomorrow.",
        "What do customers say about P2?",
        "Where is my package O5 now?",
        "Put a call with Ali tomorrow at 2 PM."
    ]

    for query in test_queries:
        print(query)
        print(llm_predict(query))
        print("-" * 60)