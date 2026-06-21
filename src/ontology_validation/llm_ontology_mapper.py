import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ONTOLOGY_VALIDATION_DIR = BASE_DIR / "src" / "ontology_validation"

sys.path.append(str(ONTOLOGY_VALIDATION_DIR))

from ontology_validator import ONTOLOGY_CATALOG, validate_prediction


def safe_correct_with_ontology(prediction: dict) -> dict:
    """
    LLM + Ontology Safe Correction.

    Important:
    - This function does NOT change the predicted intent.
    - It only corrects fields that are directly defined in the ontology:
        domain
        endpoint
        ontology_concept
    - Parameters are NOT corrected manually.
    - Parameters are only validated by ontology_validator.
    """

    intent = prediction.get("intent", "")

    corrected = {
        "domain": prediction.get("domain", ""),
        "intent": intent,
        "endpoint": prediction.get("endpoint", ""),
        "parameters": prediction.get("parameters", ""),
        "ontology_concept": prediction.get("ontology_concept", intent),
    }

    if intent not in ONTOLOGY_CATALOG:
        return corrected

    ontology_info = ONTOLOGY_CATALOG[intent]

    corrected["domain"] = ontology_info["domain"]
    corrected["endpoint"] = ontology_info["endpoint"]
    corrected["ontology_concept"] = intent

    return corrected


def llm_ontology_predict(llm_prediction: dict) -> dict:
    corrected_prediction = safe_correct_with_ontology(llm_prediction)
    validation = validate_prediction(corrected_prediction)

    # Use ontology-corrected parameters after alias mapping and optional/required validation
    corrected_prediction["parameters"] = validation["corrected_parameters"]

    return {
        **corrected_prediction,
        "ontology_validation_valid": validation["is_valid"],
        "intent_exists": validation["intent_exists"],
        "domain_valid": validation["domain_valid"],
        "endpoint_valid": validation["endpoint_valid"],
        "ontology_concept_valid": validation["ontology_concept_valid"],
        "parameters_valid": validation["parameters_valid"],
        "missing_parameters": ",".join(validation["missing_parameters"]),
        "hallucinated_parameters": ",".join(validation["hallucinated_parameters"]),
        "has_hallucination": len(validation["hallucinated_parameters"]) > 0,
        "has_missing_parameters": len(validation["missing_parameters"]) > 0,
        "ontology_inconsistent": validation["ontology_inconsistent"],
    }


if __name__ == "__main__":
    test_prediction = {
        "domain": "Weather",
        "intent": "SearchFlight",
        "endpoint": "/wrong/path",
        "parameters": "from=Istanbul;to=Dubai;date=tomorrow",
        "ontology_concept": "SearchFlight"
    }

    print("Before:")
    print(test_prediction)

    print("\nAfter:")
    print(llm_ontology_predict(test_prediction))