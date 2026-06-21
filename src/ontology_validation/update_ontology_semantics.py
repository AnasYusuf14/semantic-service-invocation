from pathlib import Path
from owlready2 import get_ontology, DataProperty

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ONTOLOGY_FILE = BASE_DIR / "ontology" / "service_ontology.owl"

onto = get_ontology(ONTOLOGY_FILE.as_uri()).load()

with onto:
    if not hasattr(onto, "parameterAlias"):
        class parameterAlias(DataProperty):
            domain = [onto.Parameter]
            range = [str]

    if not hasattr(onto, "isRequired"):
        class isRequired(DataProperty):
            domain = [onto.Parameter]
            range = [bool]


OPTIONAL_PARAMS = {
    "GetCurrentWeather": {"unit"},
    "GetForecast": {"unit"},
    "GetTemperature": {"unit"},
    "SearchProduct": {"category", "maxPrice"},
    "CreateMeeting": {"title"},
    "CheckAvailability": {"time"},
}


ALIASES = {
    "city": ["location", "place"],
    "from": ["origin", "departure", "departureCity"],
    "to": ["destination", "arrival", "destinationCity"],
    "date": ["day", "travelDate"],
    "checkIn": ["checkInDate"],
    "unit": ["temperatureUnit"],

    "productId": ["product", "product_id", "itemId", "item"],
    "orderId": ["order", "order_id", "packageId", "package_id", "package", "shipmentId"],
    "bookingId": ["booking", "booking_id", "reservation", "reservationId"],
    "meetingId": ["meeting", "meeting_id", "eventId"],

    "guestName": ["guest", "guest_name"],
    "passengerName": ["passenger", "passenger_name"],
    "maxPrice": ["price", "budget"],
    "keyword": ["query", "productName"],
    "nights": ["duration"],
    "reason": ["returnReason"],
    "title": ["subject"],
    "participant": ["person", "attendee"],
}


updated_required = 0
updated_aliases = 0

for operation in onto.individuals():
    if not operation.is_a or operation.is_a[0].name != "Operation":
        continue

    operation_name = operation.name
    optional_for_operation = OPTIONAL_PARAMS.get(operation_name, set())

    if hasattr(operation, "hasParameter"):
        for param in operation.hasParameter:
            if hasattr(param, "parameterName") and param.parameterName:
                param_name = str(param.parameterName[0])

                param.isRequired = [param_name not in optional_for_operation]
                updated_required += 1

                alias_list = ALIASES.get(param_name, [])
                param.parameterAlias = alias_list
                updated_aliases += len(alias_list)

onto.save(file=str(ONTOLOGY_FILE), format="rdfxml")

print("Ontology updated successfully.")
print(f"Updated required/optional flags: {updated_required}")
print(f"Added aliases: {updated_aliases}")
print(f"Saved to: {ONTOLOGY_FILE}")