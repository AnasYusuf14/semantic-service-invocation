import csv
import re
from pathlib import Path
from collections import defaultdict


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASET_FILE = BASE_DIR / "dataset" / "service_dataset.csv"


def normalize_text(text: str) -> str:
    return str(text).lower().strip()


def load_service_catalog():
    """
    Build a service catalog dynamically from the dataset.
    It maps each intent to its domain and endpoint.
    """
    catalog = {}

    with open(DATASET_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            intent = row["intent"]
            catalog[intent] = {
                "domain": row["domain"],
                "intent": row["intent"],
                "endpoint": row["endpoint"],
                "ontology_concept": row["ontology_concept"],
            }

    return catalog


SERVICE_CATALOG = load_service_catalog()


KEYWORDS = {
    "GetCurrentWeather": [
        "current weather", "weather now", "right now", "today's weather",
        "weather conditions", "outside now", "how is it outside"
    ],
    "GetForecast": [
        "forecast", "tomorrow", "next monday", "next friday", "next week",
        "will it rain", "will it snow", "umbrella", "rainy", "expected weather"
    ],
    "GetAirQuality": [
        "air quality", "aqi", "pollution", "clean air", "breathable",
        "air safe", "polluted"
    ],
    "GetTemperature": [
        "temperature", "hot", "cold", "degrees", "celsius", "fahrenheit",
        "how warm", "how cold"
    ],
    "GetWindSpeed": [
        "wind", "windy", "wind speed", "breeze", "gust"
    ],

    "SearchFlight": [
        "find flights", "search flights", "available flights", "fly from",
        "get from", "travel from", "flight from", "trip to"
    ],
    "BookFlight": [
        "book flight", "reserve flight", "book ticket", "reserve ticket",
        "flight fl"
    ],
    "CancelFlight": [
        "cancel flight", "cancel booking", "cancel reservation",
        "no longer want reservation", "stop my reservation"
    ],
    "SearchHotel": [
        "find hotel", "search hotel", "place to stay", "hotels in",
        "room in", "stay in"
    ],
    "BookHotel": [
        "book hotel", "reserve hotel", "book room", "reserve room",
        "hotel h"
    ],

    "SearchProduct": [
        "search for", "find", "show me options", "looking for",
        "products", "laptop", "headphones", "shoes", "chair", "backpack"
    ],
    "GetProductDetails": [
        "product details", "details for product", "information about product",
        "full information", "specifications"
    ],
    "CompareProducts": [
        "compare", "difference between", "which is better", "versus", "vs"
    ],
    "CheckProductAvailability": [
        "available", "availability", "in stock", "still in stock",
        "can i buy"
    ],
    "GetProductReviews": [
        "reviews", "customer reviews", "what do customers say",
        "ratings", "feedback"
    ],

    "CreateOrder": [
        "create order", "place order", "buy", "purchase", "new order"
    ],
    "CancelOrder": [
        "cancel order", "stop my purchase", "cancel my purchase"
    ],
    "TrackOrder": [
        "track order", "where is my order", "where is my package",
        "delivery status", "shipment", "package"
    ],
    "ReturnOrder": [
        "return order", "send back", "return", "damaged", "arrived damaged"
    ],
    "GetOrderDetails": [
        "order details", "information about order", "what i bought",
        "show my order"
    ],

    "CreateMeeting": [
        "create meeting", "schedule meeting", "schedule", "set up",
        "put a call", "arrange a call", "meeting with"
    ],
    "CancelMeeting": [
        "cancel meeting", "delete meeting", "remove meeting"
    ],
    "UpdateMeeting": [
        "update meeting", "change meeting", "move meeting", "reschedule"
    ],
    "CheckAvailability": [
        "available", "availability", "am i free", "free on", "free at"
    ],
    "ListEvents": [
        "list events", "show events", "calendar events", "what is on my calendar"
    ],
}


def score_intents(query: str):
    """
    Score intents based on keyword matches.
    """
    q = normalize_text(query)
    scores = defaultdict(int)

    for intent, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword in q:
                scores[intent] += len(keyword.split())

    return scores


def choose_best_intent(query: str):
    scores = score_intents(query)

    if not scores:
        return None

    best_intent = max(scores, key=scores.get)

    if scores[best_intent] == 0:
        return None

    return best_intent


def rule_based_predict(query: str) -> dict:
    """
    Predict domain, intent, endpoint, and parameters using rule-based matching.
    """

    intent = choose_best_intent(query)

    if intent is None or intent not in SERVICE_CATALOG:
        return {
            "domain": "Unknown",
            "intent": "Unknown",
            "endpoint": "Unknown",
            "parameters": "",
            "ontology_concept": "Unknown"
        }

    service_info = SERVICE_CATALOG[intent]

    return {
        "domain": service_info["domain"],
        "intent": service_info["intent"],
        "endpoint": service_info["endpoint"],
        "parameters": extract_parameters(query, intent),
        "ontology_concept": service_info["ontology_concept"]
    }


def extract_parameters(query: str, intent: str) -> str:
    """
    Extract parameters using simple regex and keyword rules.
    This is intentionally limited because Rule-Based is a baseline.
    """

    if intent in [
        "GetCurrentWeather",
        "GetAirQuality",
        "GetTemperature",
        "GetWindSpeed"
    ]:
        city = extract_city(query)
        unit = extract_unit(query)

        if intent in ["GetCurrentWeather", "GetTemperature"] and unit:
            return f"city={city};unit={unit}"

        return f"city={city}"

    if intent == "GetForecast":
        city = extract_city(query)
        date = extract_date(query)
        unit = extract_unit(query)

        if unit:
            return f"city={city};date={date};unit={unit}"

        return f"city={city};date={date}"

    if intent == "SearchFlight":
        origin = extract_origin(query)
        destination = extract_destination(query)
        date = extract_date(query)
        return f"from={origin};to={destination};date={date}"

    if intent == "BookFlight":
        flight_id = extract_pattern(query, r"\bFL\d+\b", "UNKNOWN")
        passenger = extract_passenger_name(query)
        return f"flightId={flight_id};passengerName={passenger}"

    if intent == "CancelFlight":
        booking_id = extract_pattern(query, r"\bBKG\d+\b", "UNKNOWN")
        return f"bookingId={booking_id}"

    if intent == "SearchHotel":
        city = extract_city(query)
        check_in = extract_date(query)
        nights = extract_number_before_word(query, "night")
        return f"city={city};checkIn={check_in};nights={nights}"

    if intent == "BookHotel":
        hotel_id = extract_pattern(query, r"\bH\d+\b", "UNKNOWN")
        guest = extract_guest_name(query)
        nights = extract_number_before_word(query, "night")
        return f"hotelId={hotel_id};guestName={guest};nights={nights}"

    if intent == "SearchProduct":
        keyword = extract_product_keyword(query)
        category = extract_category(query)
        max_price = extract_price(query)

        params = [f"keyword={keyword}"]
        if category != "UNKNOWN":
            params.append(f"category={category}")
        if max_price != "UNKNOWN":
            params.append(f"maxPrice={max_price}")

        return ";".join(params)

    if intent in [
        "GetProductDetails",
        "CheckProductAvailability",
        "GetProductReviews"
    ]:
        product_id = extract_pattern(query, r"\bP\d+\b", "UNKNOWN")
        return f"productId={product_id}"

    if intent == "CompareProducts":
        ids = re.findall(r"\bP\d+\b", query)
        product1 = ids[0] if len(ids) > 0 else "UNKNOWN"
        product2 = ids[1] if len(ids) > 1 else "UNKNOWN"
        return f"productId1={product1};productId2={product2}"

    if intent == "CreateOrder":
        user_id = extract_pattern(query, r"\bU\d+\b", "UNKNOWN")
        product_id = extract_pattern(query, r"\bP\d+\b", "UNKNOWN")
        quantity = extract_quantity(query)
        return f"userId={user_id};productId={product_id};quantity={quantity}"

    if intent in [
        "CancelOrder",
        "TrackOrder",
        "GetOrderDetails"
    ]:
        order_id = extract_pattern(query, r"\bO\d+\b", "UNKNOWN")
        return f"orderId={order_id}"

    if intent == "ReturnOrder":
        order_id = extract_pattern(query, r"\bO\d+\b", "UNKNOWN")
        reason = "damaged" if "damaged" in query.lower() else "UNKNOWN"
        if reason != "UNKNOWN":
            return f"orderId={order_id};reason={reason}"
        return f"orderId={order_id}"

    if intent == "CreateMeeting":
        title = extract_meeting_title(query)
        date = extract_date(query)
        time = extract_time(query)
        participant = extract_participant(query)

        params = [f"title={title}", f"date={date}", f"time={time}"]
        if participant != "UNKNOWN":
            params.append(f"participant={participant}")

        return ";".join(params)

    if intent == "CancelMeeting":
        meeting_id = extract_pattern(query, r"\bM\d+\b", "UNKNOWN")
        return f"meetingId={meeting_id}"

    if intent == "UpdateMeeting":
        meeting_id = extract_pattern(query, r"\bM\d+\b", "UNKNOWN")
        date = extract_date(query)
        time = extract_time(query)

        params = [f"meetingId={meeting_id}"]
        if date != "UNKNOWN":
            params.append(f"date={date}")
        if time != "UNKNOWN":
            params.append(f"time={time}")

        return ";".join(params)

    if intent == "CheckAvailability":
        date = extract_date(query)
        time = extract_time(query)

        if time != "UNKNOWN":
            return f"date={date};time={time}"

        return f"date={date}"

    if intent == "ListEvents":
        date = extract_date(query)
        return f"date={date}"

    return ""


def extract_pattern(query: str, pattern: str, default: str):
    match = re.search(pattern, query)
    return match.group() if match else default


def extract_city(query: str) -> str:
    cities = [
        "Istanbul", "Ankara", "Izmir", "Bursa", "Antalya",
        "Tokyo", "London", "Paris", "New York", "Dubai",
        "Berlin", "Sydney", "Moscow", "Toronto", "Singapore",
        "Amsterdam", "Barcelona", "Vienna", "Rome", "Miami",
        "Lisbon", "Beijing", "Delhi", "Zurich", "Shanghai",
        "Los Angeles", "Seoul", "Cairo", "Mexico City",
        "Sao Paulo", "Jakarta", "Karachi", "Bangkok",
        "Phoenix", "Reykjavik", "Helsinki", "Mumbai",
        "Buenos Aires", "Nairobi", "Riyadh"
    ]

    q = normalize_text(query)

    for city in cities:
        if city.lower() in q:
            return city

    return "UNKNOWN"


def extract_date(query: str) -> str:
    q = normalize_text(query)

    date_patterns = [
        "tomorrow", "today", "next monday", "next tuesday",
        "next wednesday", "next thursday", "next friday",
        "next saturday", "next sunday", "monday", "tuesday",
        "wednesday", "thursday", "friday", "saturday", "sunday",
        "next week", "this weekend", "weekend"
    ]

    for date in date_patterns:
        if date in q:
            return format_date_label(date)

    iso_match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", query)
    if iso_match:
        return iso_match.group()

    return "UNKNOWN"


def format_date_label(date: str) -> str:
    mapping = {
        "next monday": "next Monday",
        "next tuesday": "next Tuesday",
        "next wednesday": "next Wednesday",
        "next thursday": "next Thursday",
        "next friday": "next Friday",
        "next saturday": "next Saturday",
        "next sunday": "next Sunday",
        "monday": "Monday",
        "tuesday": "Tuesday",
        "wednesday": "Wednesday",
        "thursday": "Thursday",
        "friday": "Friday",
        "saturday": "Saturday",
        "sunday": "Sunday",
        "tomorrow": "tomorrow",
        "today": "today",
        "next week": "next week",
        "this weekend": "this weekend",
        "weekend": "weekend",
    }

    return mapping.get(date, date)


def extract_unit(query: str) -> str:
    q = normalize_text(query)

    if "celsius" in q:
        return "celsius"
    if "fahrenheit" in q:
        return "fahrenheit"

    return ""


def extract_time(query: str) -> str:
    match = re.search(r"\b\d{1,2}\s?(AM|PM|am|pm)\b", query)
    if match:
        return match.group().replace(" ", " ")

    return "UNKNOWN"


def extract_number_before_word(query: str, word: str) -> str:
    match = re.search(rf"\b(\d+)\s+{word}s?\b", query.lower())
    if match:
        return match.group(1)

    word_numbers = {
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
    }

    for word_number, digit in word_numbers.items():
        if f"{word_number} {word}" in query.lower() or f"{word_number} {word}s" in query.lower():
            return digit

    return "UNKNOWN"


def extract_quantity(query: str) -> str:
    q = normalize_text(query)

    match = re.search(r"\bquantity\s+(\d+)\b", q)
    if match:
        return match.group(1)

    match = re.search(r"\b(\d+)\s+items?\b", q)
    if match:
        return match.group(1)

    match = re.search(r"\b(\d+)\s+units?\b", q)
    if match:
        return match.group(1)

    return "UNKNOWN"


def extract_price(query: str) -> str:
    q = normalize_text(query)

    match = re.search(r"under\s+(\d+)", q)
    if match:
        return match.group(1)

    match = re.search(r"below\s+(\d+)", q)
    if match:
        return match.group(1)

    return "UNKNOWN"


def extract_origin(query: str) -> str:
    match = re.search(r"from\s+([A-Z][a-zA-Z\s]+?)\s+to\s+", query)
    if match:
        return match.group(1).strip()

    return "UNKNOWN"


def extract_destination(query: str) -> str:
    match = re.search(r"to\s+([A-Z][a-zA-Z\s]+?)(?:\s+tomorrow|\s+next|\s+on|\.|$)", query)
    if match:
        return match.group(1).strip()

    return "UNKNOWN"


def extract_passenger_name(query: str) -> str:
    match = re.search(r"passenger\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", query)
    if match:
        return match.group(1)

    return "UNKNOWN"


def extract_guest_name(query: str) -> str:
    match = re.search(r"guest\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", query)
    if match:
        return match.group(1)

    return "UNKNOWN"


def extract_participant(query: str) -> str:
    match = re.search(r"with\s+([A-Z][a-z]+)", query)
    if match:
        return match.group(1)

    return "UNKNOWN"


def extract_meeting_title(query: str) -> str:
    if "project discussion" in normalize_text(query):
        return "Project Discussion"
    if "call" in normalize_text(query):
        return "Call"
    if "meeting" in normalize_text(query):
        return "Meeting"

    return "UNKNOWN"


def extract_product_keyword(query: str) -> str:
    products = [
        "laptop", "headphones", "running shoes", "shoes",
        "office chair", "chair", "backpack", "wireless headphones"
    ]

    q = normalize_text(query)

    for product in products:
        if product in q:
            return product

    return "UNKNOWN"


def extract_category(query: str) -> str:
    categories = ["electronics", "sports", "furniture", "accessories"]

    q = normalize_text(query)

    for category in categories:
        if category in q:
            return category

    return "UNKNOWN"


if __name__ == "__main__":
    test_queries = [
        "Should I carry an umbrella in Istanbul tomorrow?",
        "I no longer want reservation BKG3.",
        "What do customers say about P2?",
        "Where is my package O5 now?",
        "Put a call with Ali tomorrow at 2 PM."
    ]

    for query in test_queries:
        print(query)
        print(rule_based_predict(query))
        print("-" * 60)