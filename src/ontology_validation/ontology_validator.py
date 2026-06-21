from pathlib import Path
from owlready2 import get_ontology


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ONTOLOGY_FILE = BASE_DIR / "ontology" / "service_ontology.owl"


PARAMETER_ALIASES = {
    "location": "city",
    "place": "city",

    "product": "productId",
    "product_id": "productId",
    "item": "productId",
    "itemId": "productId",

    "order": "orderId",
    "order_id": "orderId",
    "package": "orderId",
    "packageId": "orderId",
    "package_id": "orderId",
    "shipmentId": "orderId",

    "booking": "bookingId",
    "booking_id": "bookingId",
    "reservation": "bookingId",
    "reservationId": "bookingId",

    "meeting": "meetingId",
    "meeting_id": "meetingId",
    "eventId": "meetingId",

    "guest": "guestName",
    "guest_name": "guestName",

    "passenger": "passengerName",
    "passenger_name": "passengerName",

    "origin": "from",
    "departure": "from",
    "departureCity": "from",

    "destination": "to",
    "arrival": "to",
    "destinationCity": "to",

    "day": "date",
    "travelDate": "date",

    "price": "maxPrice",
    "budget": "maxPrice",

    "query": "keyword",
    "productName": "keyword",

    "duration": "nights",

    "returnReason": "reason",

    "subject": "title",

    "person": "participant",
    "attendee": "participant",
}


def normalize(text):
    return str(text).strip().lower()


def parse_parameters(parameter_string):
    parameters = {}

    if not parameter_string:
        return parameters

    for part in str(parameter_string).split(";"):
        if "=" in part:
            key, value = part.split("=", 1)
            parameters[key.strip()] = value.strip()

    return parameters


def parameters_to_string(parameters):
    return ";".join(
        f"{key}={value}"
        for key, value in parameters.items()
    )


def load_ontology_catalog():
    onto = get_ontology(ONTOLOGY_FILE.as_uri()).load()

    catalog = {}

    for individual in onto.individuals():
        if not individual.is_a or individual.is_a[0].name != "Operation":
            continue

        intent = individual.name

        domain_name = None
        endpoint_path = None
        parameters = set()
        required_parameters = set()
        optional_parameters = set()

        for domain in onto.individuals():
            if hasattr(domain, "hasOperation"):
                if individual in list(domain.hasOperation):
                    domain_name = domain.name

        if hasattr(individual, "hasEndpoint") and individual.hasEndpoint:
            endpoint_individual = individual.hasEndpoint[0]
            if hasattr(endpoint_individual, "endpointPath") and endpoint_individual.endpointPath:
                endpoint_path = str(endpoint_individual.endpointPath[0])

        if hasattr(individual, "hasParameter"):
            for param in individual.hasParameter:
                if not hasattr(param, "parameterName") or not param.parameterName:
                    continue

                param_name = str(param.parameterName[0])
                parameters.add(param_name)

                is_required = True

                if hasattr(param, "isRequired") and param.isRequired:
                    is_required = bool(param.isRequired[0])

                if is_required:
                    required_parameters.add(param_name)
                else:
                    optional_parameters.add(param_name)

        catalog[intent] = {
            "domain": domain_name,
            "endpoint": endpoint_path,
            "ontology_concept": intent,
            "parameters": parameters,
            "required_parameters": required_parameters,
            "optional_parameters": optional_parameters,
        }

    return catalog


ONTOLOGY_CATALOG = load_ontology_catalog()


def apply_parameter_aliases(parameters, allowed_parameters):
    corrected = {}

    for key, value in parameters.items():
        if key in allowed_parameters:
            corrected[key] = value
            continue

        alias = PARAMETER_ALIASES.get(key)

        if alias and alias in allowed_parameters:
            corrected[alias] = value
        else:
            corrected[key] = value

    return corrected


def validate_prediction(prediction):
    intent = prediction.get("intent", "")
    domain = prediction.get("domain", "")
    endpoint = prediction.get("endpoint", "")
    ontology_concept = prediction.get("ontology_concept", "")
    parameters = parse_parameters(prediction.get("parameters", ""))

    result = {
        "intent_exists": False,
        "domain_valid": False,
        "endpoint_valid": False,
        "ontology_concept_valid": False,
        "parameters_valid": False,
        "missing_parameters": [],
        "hallucinated_parameters": [],
        "corrected_parameters": "",
        "ontology_inconsistent": False,
        "is_valid": False,
    }

    if intent not in ONTOLOGY_CATALOG:
        result["ontology_inconsistent"] = True
        result["hallucinated_parameters"] = list(parameters.keys())
        result["corrected_parameters"] = parameters_to_string(parameters)
        return result

    expected = ONTOLOGY_CATALOG[intent]

    corrected_parameters = apply_parameter_aliases(
        parameters,
        expected["parameters"]
    )

    expected_params = expected["parameters"]
    required_params = expected["required_parameters"]
    predicted_params = set(corrected_parameters.keys())

    result["intent_exists"] = True
    result["domain_valid"] = normalize(domain) == normalize(expected["domain"])
    result["endpoint_valid"] = normalize(endpoint) == normalize(expected["endpoint"])
    result["ontology_concept_valid"] = normalize(ontology_concept) == normalize(expected["ontology_concept"])

    result["missing_parameters"] = sorted(list(required_params - predicted_params))
    result["hallucinated_parameters"] = sorted(list(predicted_params - expected_params))
    result["corrected_parameters"] = parameters_to_string(corrected_parameters)

    result["parameters_valid"] = (
        len(result["missing_parameters"]) == 0
        and len(result["hallucinated_parameters"]) == 0
    )

    result["ontology_inconsistent"] = not (
        result["intent_exists"]
        and result["domain_valid"]
        and result["endpoint_valid"]
        and result["ontology_concept_valid"]
        and len(result["hallucinated_parameters"]) == 0
    )

    result["is_valid"] = (
        result["intent_exists"]
        and result["domain_valid"]
        and result["endpoint_valid"]
        and result["ontology_concept_valid"]
        and result["parameters_valid"]
    )

    return result


if __name__ == "__main__":
    print("Loaded operations:", len(ONTOLOGY_CATALOG))
    print("Example GetForecast:", ONTOLOGY_CATALOG.get("GetForecast"))

    test_prediction = {
        "domain": "Weather",
        "intent": "GetForecast",
        "endpoint": "/weather/forecast",
        "parameters": "location=Istanbul;date=tomorrow",
        "ontology_concept": "GetForecast"
    }

    print(validate_prediction(test_prediction))