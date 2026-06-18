import os
import sys
# Add current directory to path
sys.path.insert(0, os.getcwd())

import time
import subprocess
from dotenv import load_dotenv

load_dotenv()

# Verify GEMINI_API_KEY
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY is not set.")
    sys.exit(1)

# Start Mock API in background
api_process = subprocess.Popen(
    [sys.executable, "mock_api.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

# Ensure backend stops on exit
import atexit
atexit.register(lambda: api_process.terminate() if api_process.poll() is None else None)

time.sleep(2.0)

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents import coordinator_agent

session_service = InMemorySessionService()
runner = Runner(app_name="airline_assistant", agent=coordinator_agent, session_service=session_service, auto_create_session=True)

# Query with unrelated prompt
print("Sending: 'what is React'")
new_message = types.Content(parts=[types.Part.from_text(text="what is React")])
events = runner.run(user_id="test_user", session_id="test_sess", new_message=new_message)

print("\n--- RESPONSE ---")
for event in events:
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.text:
                print(part.text)
print("----------------")
