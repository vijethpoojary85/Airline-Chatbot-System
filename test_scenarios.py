import os
import sys
import time
import subprocess
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify GEMINI_API_KEY
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY is not set. Cannot run automated tests because the agents require Gemini model access.")
    sys.exit(1)

# Start Mock API in background
print("Starting Mock API Backend for testing...")
api_process = subprocess.Popen(
    [sys.executable, "mock_api.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

def cleanup():
    if api_process.poll() is None:
        print("Stopping Mock API Backend...")
        api_process.terminate()
        api_process.wait()

# Ensure backend stops on exit
import atexit
atexit.register(cleanup)

# Wait for server to bind to port 8000
time.sleep(2.0)

# Import ADK elements
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents import coordinator_agent

API_BASE = "http://127.0.0.1:8000"

def run_agent_turn(runner, user_id, session_id, message_text):
    """Utility to run a single user message through the runner and return accumulated text."""
    new_message = types.Content(parts=[types.Part.from_text(text=message_text)])
    events = runner.run(user_id=user_id, session_id=session_id, new_message=new_message)
    
    accumulated_text = []
    for event in events:
        if not event.partial and event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    accumulated_text.append(part.text)
                elif part.function_call:
                    name = part.function_call.name
                    args = part.function_call.args
                    if name == "transfer_to_agent":
                        print(f"    [Workflow Edge: Transferring control to {args.get('agent_name')}]")
                    else:
                        print(f"    [Tool Executing: {name}({str(args)})]")
                elif part.function_response:
                    print(f"    [Tool Response: {str(part.function_response.response)[:80]}...]")
                    
    # Sleep 12 seconds to prevent rate limit (Free tier limit is 5 RPM)
    print("    [Rate limit mitigation: sleeping 12s...]")
    time.sleep(12)
    return "\n".join(accumulated_text).strip()

def reset_mock_data():
    """Helper to reset database to initial state before each scenario."""
    # Simply update the internal state directly in the API by calling reset,
    # or recreate it. For testing, since we just start it up, the first scenario runs on fresh data.
    # We can perform updates sequentially and assert final states.
    pass

def test_scenario_1():
    print("\n--- Running Scenario 1: DOB Update ---")
    session_service = InMemorySessionService()
    runner = Runner(app_name="airline_assistant", agent=coordinator_agent, session_service=session_service, auto_create_session=True)
    
    user_id = "test_user_1"
    session_id = "test_session_1"
    
    # Step 1: User requests DOB update with PNR
    print("User > I need to update my date of birth for booking ABC123")
    resp = run_agent_turn(runner, user_id, session_id, "I need to update my date of birth for booking ABC123")
    print(f"Agent > {resp}")
    
    # Step 2: User gives DOB
    print("\nUser > 15th January 1990")
    resp = run_agent_turn(runner, user_id, session_id, "15th January 1990")
    print(f"Agent > {resp}")
    
    # Step 3: User confirms
    print("\nUser > Yes")
    resp = run_agent_turn(runner, user_id, session_id, "Yes")
    print(f"Agent > {resp}")
    
    # Assert database update
    db_res = requests.get(f"{API_BASE}/api/passenger/ABC123").json()
    dob_updated = db_res["passengers"][0]["dob"]
    print(f"\nVerification: Booking DOB in database is now: {dob_updated}")
    assert dob_updated == "1990-01-15", f"Expected DOB to be 1990-01-15, but got {dob_updated}"
    print("Scenario 1: SUCCESS")

def test_scenario_2():
    print("\n--- Running Scenario 2: Flight Details Update ---")
    session_service = InMemorySessionService()
    runner = Runner(app_name="airline_assistant", agent=coordinator_agent, session_service=session_service, auto_create_session=True)
    
    user_id = "test_user_2"
    session_id = "test_session_2"
    
    # Step 1: User requests flight change route KUL to BKK
    print("User > I need to change my flight from KUL to BKK")
    resp = run_agent_turn(runner, user_id, session_id, "I need to change my flight from KUL to BKK")
    print(f"Agent > {resp}")
    
    # Step 2: User provides PNR
    print("\nUser > ABC123")
    resp = run_agent_turn(runner, user_id, session_id, "ABC123")
    print(f"Agent > {resp}")
    
    # Step 3: User confirms change to flight AK456 at 14:30
    print("\nUser > Yes")
    resp = run_agent_turn(runner, user_id, session_id, "Yes")
    print(f"Agent > {resp}")
    
    # Assert database update
    db_res = requests.get(f"{API_BASE}/api/passenger/ABC123").json()
    flight = db_res["passengers"][0]["flight"]
    print(f"\nVerification: Updated flight details in database: {flight}")
    assert flight["number"] == "AK456", "Expected flight number AK456"
    assert flight["destination"] == "BKK", "Expected destination BKK"
    assert flight["time"] == "14:30", "Expected flight time 14:30"
    print("Scenario 2: SUCCESS")

def test_scenario_3():
    print("\n--- Running Scenario 3: FAQ Query ---")
    session_service = InMemorySessionService()
    runner = Runner(app_name="airline_assistant", agent=coordinator_agent, session_service=session_service, auto_create_session=True)
    
    user_id = "test_user_3"
    session_id = "test_session_3"
    
    # Step 1: User asks about baggage policy
    print("User > What is the baggage allowance for economy class?")
    resp = run_agent_turn(runner, user_id, session_id, "What is the baggage allowance for economy class?")
    print(f"Agent > {resp}")
    
    # Verify response contains the relevant policy limit
    assert "20kg" in resp.lower() or "20 kg" in resp.lower(), "Baggage response should mention 20kg allowance limit"
    print("Scenario 3: SUCCESS")

if __name__ == "__main__":
    try:
        test_scenario_1()
        test_scenario_2()
        test_scenario_3()
        print("\nAll Scenarios Passed Successfully!")
    except AssertionError as e:
        print(f"\nAssertion failed during testing: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        sys.exit(1)
    finally:
        cleanup()
