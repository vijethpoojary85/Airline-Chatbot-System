import os
import sys
import time
import subprocess
import atexit
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check for GEMINI_API_KEY
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY is not set in the environment variables or a .env file.")
    print("The Google ADK relies on the Gemini API. Please make sure the key is configured.")
    # Prompt the user to enter their API key if they wish
    user_key = input("Enter GEMINI_API_KEY (press Enter to skip if already set globally): ").strip()
    if user_key:
        os.environ["GEMINI_API_KEY"] = user_key
        api_key = user_key

# Start the mock API backend server in the background
print("Starting Mock API Backend...")
api_process = subprocess.Popen(
    [sys.executable, os.path.join("airline_agent", "mock_api.py")],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

# Register atexit handler to ensure the mock API server is shut down when the script exits
def cleanup_api():
    if api_process.poll() is None:
        print("\nStopping Mock API Backend...")
        api_process.terminate()
        api_process.wait()
        print("Mock API Backend stopped.")

atexit.register(cleanup_api)

# Wait for FastAPI to start up and bind to port 8000
time.sleep(2.0)

# Import ADK modules after setting up environment
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from airline_agent.agents import coordinator_agent

def display_event(event) -> None:
    """Pretty-print runner events to the console."""
    if event.partial:
        # Skip streaming tokens to keep output clean in terminal
        return

    if not event.content or not event.content.parts:
        return

    for part in event.content.parts:
        if part.text:
            print(f"\n{event.author} > {part.text.strip()}")
        elif part.function_call:
            if part.function_call.name == "transfer_to_agent":
                target = part.function_call.args.get("agent_name")
                print(f"  [System: Transferring control to {target}]")
            else:
                args_str = str(part.function_call.args)
                if len(args_str) > 60:
                    args_str = args_str[:60] + "..."
                print(f"  [Tool Call: {part.function_call.name}({args_str})]")
        elif part.function_response:
            resp_str = str(part.function_response.response)
            if len(resp_str) > 80:
                resp_str = resp_str[:80] + "..."
            print(f"  [Tool Response: {resp_str}]")

def main():
    print("\n" + "="*50)
    print("  Airline Customer Service Assistant (ADK Multi-Agent)")
    print("="*50)
    print("Type '/exit' to quit the chat session.\n")

    # Initialize the session service and runner
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="airline_assistant",
        agent=coordinator_agent,
        session_service=session_service,
        auto_create_session=True
    )

    user_id = "user_1"
    session_id = "session_1"

    print("coordinator_agent > Hello! I am your Airline Customer Service Coordinator. How can I help you today?")

    while True:
        try:
            user_input = input("\nUser > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("/exit", "exit", "quit"):
                break

            # Create message payload
            new_message = types.Content(
                parts=[types.Part.from_text(text=user_input)]
            )

            # Run the agent workflow synchronously
            events = runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message
            )

            # Consume events and display outputs
            for event in events:
                display_event(event)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError occurred: {str(e)}")

    print("\nThank you for using Airline Customer Service Assistant!")

if __name__ == "__main__":
    main()
