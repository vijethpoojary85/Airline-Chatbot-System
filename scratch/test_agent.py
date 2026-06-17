import os
import sys
# Add current directory to path
sys.path.insert(0, os.getcwd())

import time
import subprocess
from dotenv import load_dotenv

load_dotenv()

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

new_message = types.Content(parts=[types.Part.from_text(text="Hello, I need to update my date of birth for booking ABC123")])
events = runner.run(user_id="test_user", session_id="test_sess", new_message=new_message)

print("--- RAW EVENTS ---")
for event in events:
    print("Event author:", event.author)
    print("Event partial:", event.partial)
    print("Event content:", event.content)
    print("Event output:", event.output)
    print("Event actions:", event.actions)
    print("-------------------")
