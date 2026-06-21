def normalize_text(value):
    return str(value).strip().lower()


def parse_parameters(parameter_string):
    """
    Convert:
    city=Istanbul;date=tomorrow

    into:
    {
        "city": "istanbul",
        "date": "tomorrow"
    }
    """
    parameters = {}

    if not parameter_string:
        return parameters

    for part in str(parameter_string).split(";"):
        if "=" in part:
            key, value = part.split("=", 1)
            parameters[key.strip()] = normalize_text(value)

    return parameters


OPTIONAL_PARAMETERS = {
    "GetCurrentWeather": {"unit"},
    "GetForecast": {"unit"},
    "GetTemperature": {"unit"},
    "SearchProduct": {"category", "maxPrice"},
}


def parameters_match(true_parameters, pred_parameters, intent):
    true_params = parse_parameters(true_parameters)
    pred_params = parse_parameters(pred_parameters)

    optional = OPTIONAL_PARAMETERS.get(intent, set())

    required_true_params = {
        key: value
        for key, value in true_params.items()
        if key not in optional
    }

    filtered_pred_params = {
        key: value
        for key, value in pred_params.items()
        if key in true_params
    }

    for key, true_value in required_true_params.items():
        if key not in filtered_pred_params:
            return False

        pred_value = filtered_pred_params[key]

        if true_value != "unknown" and pred_value != true_value:
            return False

    return True