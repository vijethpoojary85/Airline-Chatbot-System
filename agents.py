import requests
from google.adk.agents.context import Context as ToolContext
from google.adk.agents import LlmAgent
from rag_service import get_faq_db

API_BASE = "http://127.0.0.1:8000"

# --- Tools Definition ---

def get_booking_details(pnr: str) -> dict:
    """Fetch passenger booking details from the mock database using PNR."""
    try:
        r = requests.get(f"{API_BASE}/api/passenger/{pnr.upper()}")
        if r.status_code == 200:
            return r.json()
        return {"error": f"Booking PNR '{pnr}' not found."}
    except Exception as e:
        return {"error": f"API request failed: {str(e)}"}

def update_passenger_dob(pnr: str, passenger_name: str, new_dob: str) -> dict:
    """Update passenger's DOB in the mock database."""
    try:
        payload = {"passenger_name": passenger_name, "dob": new_dob}
        r = requests.put(f"{API_BASE}/api/passenger/{pnr.upper()}/dob", json=payload)
        if r.status_code == 200:
            return r.json()
        return {"error": r.json().get("detail", "Failed to update DOB.")}
    except Exception as e:
        return {"error": f"API request failed: {str(e)}"}

def search_flights(departure: str, destination: str, date: str = None) -> list:
    """Search for available flights on a given route."""
    try:
        params = {"departure": departure.upper(), "destination": destination.upper()}
        if date:
            params["date"] = date
        r = requests.get(f"{API_BASE}/api/flight/search", params=params)
        if r.status_code == 200:
            return r.json()
        return []
    except Exception as e:
        return []

def update_flight_details(pnr: str, flight_number: str, departure: str, destination: str, date: str, time: str) -> dict:
    """Update flight information in passenger booking."""
    try:
        payload = {
            "number": flight_number.upper(),
            "departure": departure.upper(),
            "destination": destination.upper(),
            "date": date,
            "time": time
        }
        r = requests.put(f"{API_BASE}/api/flight/{pnr.upper()}/details", json=payload)
        if r.status_code == 200:
            return r.json()
        return {"error": r.json().get("detail", "Failed to update flight details.")}
    except Exception as e:
        return {"error": f"API request failed: {str(e)}"}

def query_faq(query: str) -> str:
    """Retrieve airline policy chunks relevant to the user query."""
    try:
        results = get_faq_db().search(query, k=1)
        if results:
            return results[0]
        return "No policy found matching the query."
    except Exception as e:
        return f"Error retrieving policy: {str(e)}"

# --- State / Context Management Tools ---

def save_pnr_to_session(pnr: str, tool_context: ToolContext) -> str:
    """Save the booking PNR to the session state so other agents can access it."""
    tool_context.state['pnr'] = pnr.upper()
    return f"PNR '{pnr.upper()}' saved in session."

def get_pnr_from_session(tool_context: ToolContext) -> str:
    """Retrieve the booking PNR from the session state if it was already provided."""
    pnr = tool_context.state.get('pnr')
    if pnr:
        return f"Current session PNR: {pnr}"
    return "No PNR saved in session. Please ask the passenger for their booking PNR."

def save_passenger_name_to_session(name: str, tool_context: ToolContext) -> str:
    """Save the passenger name to the session state."""
    tool_context.state['passenger_name'] = name
    return f"Passenger name '{name}' saved in session."

def get_passenger_name_from_session(tool_context: ToolContext) -> str:
    """Retrieve the passenger name from the session state."""
    name = tool_context.state.get('passenger_name')
    if name:
        return f"Current session passenger name: {name}"
    return "No passenger name saved in session."


# --- Agents Setup ---

# Default model used by the agents
DEFAULT_MODEL = "gemini-2.5-flash"

# 1. DOB Agent
dob_agent = LlmAgent(
    name="dob_agent",
    model=DEFAULT_MODEL,
    description="Specialized agent to update a passenger's date of birth (DOB) in a booking.",
    instruction=(
        "You are the Date of Birth (DOB) Agent.\n"
        "Your task is to help the passenger update their date of birth in their booking.\n"
        "Please follow these strict steps:\n"
        "1. Check if the booking PNR is saved in the session context using get_pnr_from_session. If not, ask the passenger for their PNR.\n"
        "2. Once you have the PNR, fetch the booking details using get_booking_details.\n"
        "3. Check if passenger_name is saved using get_passenger_name_from_session. If not, identify the passenger name from booking details, ask the user to confirm their name (e.g. 'I see that the booking ABC123 is for John Doe. Is that you?'), and save it using save_passenger_name_to_session.\n"
        "4. Ask the user for their new Date of Birth (if not already provided).\n"
        "5. Validate that the new Date of Birth is formatted correctly (YYYY-MM-DD). If they give a date in another format (like '15th January 1990'), convert it to '1990-01-15'.\n"
        "6. If validation fails (invalid DOB format, non-existent passenger, or invalid PNR), explain the error clearly to the user.\n"
        "7. Before making the update, you MUST explicitly ask the passenger to confirm. E.g.: 'Please confirm: Update DOB to 1990-01-15 for passenger John Doe in booking ABC123?'.\n"
        "8. Once the user confirms (e.g. they say 'Yes' or confirm), call update_passenger_dob.\n"
        "9. After a successful update, inform the passenger that the DOB has been successfully updated, and transfer control back to the coordinator_agent."
    ),
    tools=[
        get_pnr_from_session, 
        save_pnr_to_session, 
        get_passenger_name_from_session, 
        save_passenger_name_to_session, 
        get_booking_details, 
        update_passenger_dob
    ]
)

# 2. Flight Details Agent
flight_agent = LlmAgent(
    name="flight_agent",
    model=DEFAULT_MODEL,
    description="Specialized agent to modify flight itineraries (dates, routes, destination/departure cities, flight numbers, timing).",
    instruction=(
        "You are the Flight Details Agent.\n"
        "Your task is to help passengers modify their flight details (change flight, departure, destination, date, or timing).\n"
        "Please follow these steps:\n"
        "1. Retrieve the current PNR from session using get_pnr_from_session. If not found, ask the passenger for it. When they provide it, call save_pnr_to_session.\n"
        "2. Fetch the passenger's current booking details using get_booking_details to see their current flight itinerary.\n"
        "3. Find out what change they want to make (e.g., changing destination from SIN to BKK).\n"
        "4. Search for available flights using search_flights on the departure date for that route.\n"
        "5. Compare the results and present the available flights. For example: 'Found your booking AK123 from KUL to SIN. Available flight to BKK is AK456 on the same day at 14:30. Would you like to change to this flight?'\n"
        "6. If the route is invalid or there are no flights, or if there's any conflict, explain it to the user.\n"
        "7. Once the passenger confirms the change (e.g. they say 'Yes'), call update_flight_details to update the booking.\n"
        "8. After a successful update, confirm the update to the passenger (listing details of passenger, new flight number, cities, and time) and transfer control back to the coordinator_agent."
    ),
    tools=[
        get_pnr_from_session, 
        save_pnr_to_session, 
        get_booking_details, 
        search_flights, 
        update_flight_details
    ]
)

# 3. FAQ Agent
faq_agent = LlmAgent(
    name="faq_agent",
    model=DEFAULT_MODEL,
    description="Specialized FAQ Agent that answers general customer questions regarding baggage policies, check-in procedures, and refund rules.",
    instruction=(
        "You are the FAQ Agent.\n"
        "Your task is to answer passenger questions about airline policies (baggage, check-in, refunds, etc.).\n"
        "1. Always search the policy database using the query_faq tool with the user's question.\n"
        "2. Use the retrieved context chunks to formulate a helpful and accurate response.\n"
        "3. Do not make up policies; only state what is found in the retrieved documents.\n"
        "4. Once you have answered the question, ask if there is anything else the passenger needs help with. If they want to perform operations like DOB or flight changes, or if they are done, transfer control back to the coordinator_agent."
    ),
    tools=[query_faq]
)

# 4. Coordinator Agent (Router/Entry point)
coordinator_agent = LlmAgent(
    name="coordinator_agent",
    model=DEFAULT_MODEL,
    description="Main customer service assistant and agent router.",
    instruction=(
        "You are the main Airline Customer Service Coordinator.\n"
        "Your job is to greet the user (if it is a simple greeting) or immediately route them to the specialized sub-agent if they have a specific request.\n"
        "Strict routing guidelines:\n"
        "- If the user expresses intent to update their date of birth (DOB) or passenger DOB info, immediately call transfer_to_agent to dob_agent. Do not ask for PNR or DOB yourself.\n"
        "- If the user expresses intent to change their flight details, route, destination, departure city, flight number, or timing, immediately call transfer_to_agent to flight_agent. Do not ask for PNR or destination details yourself.\n"
        "- If the user has a policy question (baggage allowances, check-in counter times, refund rules, power bank rules, kirpan rules), immediately call transfer_to_agent to faq_agent.\n"
        "- If the user mentions a PNR (like ABC123), call save_pnr_to_session first to preserve the context, then perform the routing.\n"
        "- If they just say 'hello', greet them, describe what you can help with (updating passenger DOB, modifying flight details, answering FAQ queries), and ask how you can help.\n"
        "- If the user's query is unrelated to the airline or its services (e.g., general knowledge questions like 'what is React', programming questions, math, general jokes), you must politely decline to answer, stating that you are an airline assistant and can only help with airline services."
    ),
    sub_agents=[dob_agent, flight_agent, faq_agent],
    tools=[save_pnr_to_session, get_pnr_from_session]
)
