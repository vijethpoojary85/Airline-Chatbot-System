# Airline Customer Service Assistant

An AI-powered airline customer support assistant built with Python, FastAPI, and Google ADK. The system routes user requests to specialized agents for:

- updating passenger DOB information
- changing flight details
- answering airline policy questions

## Overview

The project combines:

- a multi-agent orchestration layer (`agents.py`)
- a mock backend API (`mock_api.py`)
- a FAQ retrieval service (`rag_service.py`)
- a CLI entrypoint (`main.py`)
- scenario-based tests (`test_scenarios.py`)

## Architecture

The flow is:

1. `main.py` loads environment variables and starts the mock API server.
2. The chat runner initializes the coordinator agent.
3. The coordinator routes requests to the correct specialist agent.
4. Specialist agents use tools to query the API or retrieve policy context.
5. The FAQ agent uses embeddings to find relevant airline policy text.

## Project Structure

- `main.py` - starts the backend and runs the chat application
- `agents.py` - defines coordinator, DOB, flight, and FAQ agents
- `mock_api.py` - FastAPI mock airline booking backend
- `rag_service.py` - FAQ embedding/search logic
- `test_scenarios.py` - sample end-to-end scenarios
- `.env.example` - environment variable template

## Features

### 1. Coordinator Agent
The main assistant receives user messages and decides whether the request belongs to:

- DOB update flow
- flight details update flow
- baggage/check-in/refund policy questions

### 2. DOB Agent
Helps users update a booking passenger's date of birth after confirming the booking details.

### 3. Flight Agent
Assists with flight changes, route updates, and timetable-related requests.

### 4. FAQ Agent
Searches airline policy documents and answers questions about:

- baggage allowance
- check-in timings
- refund rules

## Setup

### Prerequisites

- Python 3.10 or higher
- A valid Gemini API key

### Install dependencies

Use your virtual environment and install the required packages:

```bash
pip install fastapi uvicorn requests python-dotenv numpy sentence-transformers google-adk google-genai
```

### Configure environment

Copy the sample environment file and add your API key:

```bash
copy .env.example .env
```

Then update `.env` with your real Gemini key:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

## Running the Application

Start the assistant with:

```bash
python main.py
```

This command will:

- load `.env`
- launch the mock API backend on `http://127.0.0.1:8000`
- start the interactive chat session

## Mock API

The mock API simulates booking data and exposes endpoints such as:

- `GET /api/passenger/{pnr}`
- `PUT /api/passenger/{pnr}/dob`
- `PUT /api/flight/{pnr}/details`
- `GET /api/flight/search`

These endpoints are used by the agents to read and update booking information.

## Testing

Run the scenario tests with:

```bash
python test_scenarios.py
```

The script checks:

- DOB update workflow
- flight change workflow
- FAQ retrieval behavior

## Notes

- The FAQ engine downloads and loads embeddings on first use.
- The mock backend is started automatically when running `main.py`.
- The `.env` file is ignored by Git to protect secrets.
