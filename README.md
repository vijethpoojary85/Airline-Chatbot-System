# Airline Customer Service Assistant

An AI-powered airline customer support assistant built with Python, FastAPI, and the Google Agent Development Kit (ADK). The system leverages a multi-agent orchestration pattern to route user requests to specialized sub-agents.

---

## Features

- **Multi-Agent Orchestration**: A central Coordinator Agent automatically routes user queries to the correct sub-agent depending on intent.
- **Booking Management**: Specialized agents update passenger Date of Birth (DOB) and modify flight itineraries (departure, destination, dates, timings, flight numbers).
- **RAG FAQ Agent**: A custom Retrieval-Augmented Generation agent answers airline policy questions (baggage allowance, check-in timelines, refund rules, restricted items) using vector similarity search.
- **Graceful Session Context**: Seamlessly retains PNR and passenger identity across sub-agent handoffs.

---

## Project Structure

The project code is organized into a modular, self-contained Python package:

```text
Airline Customer Service Assistant/
│
├── airline_agent/           # Core application package
│   ├── .adk/                # Google ADK configuration metadata
│   ├── __init__.py          # Marks folder as importable Python package
│   ├── agent.py             # ADK entrypoint module (exports root_agent)
│   ├── agents.py            # Definitions for coordinator and sub-agents
│   ├── mock_api.py          # FastAPI mock backend database & API server
│   └── rag_service.py       # RAG Vector DB and embedding logic (SentenceTransformers)
│
├── tests/                   # Dedicated test directory
│   └── test_scenarios.py    # Automated end-to-end integration tests
│
├── .env.example             # Template for local environment variables
├── .gitignore               # Git exclusions
├── requirements.txt         # Project dependencies
├── README.md                # Project documentation
└── main.py                  # Main orchestration driver (CLI mode)
```

---

## Setup & Installation

### Prerequisites
- Python 3.10 or higher
- A valid **Gemini API Key** (from Google AI Studio)

### 1. Install Dependencies
Ensure your virtual environment is active, and install the required libraries:
```bash
pip install fastapi uvicorn requests python-dotenv numpy sentence-transformers google-adk google-genai
```

### 2. Configure Environment
Copy the sample environment file to create a local `.env`:
```bash
copy .env.example .env
```
Open `.env` and fill in your Gemini API key:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

---

## Running the Application

### Option A: Standard Interactive Chat (All-in-One CLI)
Run the root driver script. This starts the mock API backend automatically in the background and launches the terminal chat loop:
```bash
.\venv\Scripts\python.exe main.py
```
To exit, type `/exit` or `quit`.

### Option B: Running with Google ADK Web UI

#### 1. Start the Mock API Backend (Terminal 1)
The backend API server must be running so that agents can call tools to query/update booking data:
```bash
.\venv\Scripts\python.exe airline_agent/mock_api.py
```

#### 2. Start the ADK Web UI (Terminal 2)
Launch the Google ADK web interface (bound to port `8080` to avoid conflict with the API on port `8000`):
```bash
.\venv\Scripts\adk.exe web --port 8080 airline_agent
```
Once started, visit **[http://127.0.0.1:8080/](http://127.0.0.1:8080/)** in your web browser.

#### 3. Run interactive chat in terminal via ADK (Terminal 2)
Alternatively, you can run the agent in the console using the ADK CLI:
```bash
.\venv\Scripts\adk.exe run airline_agent
```

---

## Testing

Run the automated integration tests to verify multi-agent flows (DOB update, flight changes, FAQ query retrieval):
```bash
.\venv\Scripts\python.exe tests/test_scenarios.py
```


