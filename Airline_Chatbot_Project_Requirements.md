# Airline Chatbot System
### GenAI Developer Interview Case Study

## Table of Contents
1. [Overview](#overview)
2. [Core Requirements](#core-requirements)
3. [System Architecture](#system-architecture)
4. [Technical Implementation Requirements](#technical-implementation-requirements)
5. [Sample Test Scenarios](#sample-test-scenarios)

---

## Overview

The task is to build an intelligent airline service chatbot using the **Agent Development Kit (ADK)**. The system must handle passenger booking management through specialized agents, alongside a knowledge-based FAQ system for answering policy questions.

## Core Requirements

| # | Requirement | Description |
|---|---|---|
| 1 | Multi-Agent Architecture | Built using ADK |
| 2 | Mock API Implementation | Simulates airline backend operations |
| 3 | RAG-based FAQ Agent | Uses vector similarity search |
| 4 | Natural Language Understanding | Routes user intent to the correct agent |
| 5 | Session Management | Maintains PNR context throughout a session |

---

## System Architecture

### Agent Summary

| Agent | Purpose | Key Technology |
|---|---|---|
| DOB Agent | Update passenger date of birth | Field validation |
| Flight Details Agent | Modify flight information | Availability / conflict checks |
| FAQ Agent (RAG) | Answer policy & service questions | Vector similarity search |

### 1. DOB Agent

| Field | Details |
|---|---|
| Purpose | Update passenger date of birth |
| Input | PNR + new DOB + passenger identification |
| Validation | DOB format, passenger existence, PNR validity |
| Output | Confirmation with updated details |

### 2. Flight Details Agent

| Field | Details |
|---|---|
| Purpose | Modify flight information |
| Input | PNR + flight details to update |
| Validation | Flight availability, timing conflicts, route validity |

**Supported Updates:**
- Destination / Departure cities
- Flight number
- Flight date
- Flight timing

### 3. FAQ Agent (RAG)

| Field | Details |
|---|---|
| Purpose | Answer airline policy and service questions |
| Technology | Vector similarity search + chunk retrieval |
| Reference Document | [Baggage Policy PDF](https://plone.allianceair.in/allianceair/en/assets/policy/baggage-policy.pdf/view) |
| Knowledge Areas | Baggage policies, check-in procedures, refund rules, etc. |

**Retrieval Process:**
1. Convert query to embedding
2. Search vector database
3. Retrieve relevant chunks
4. Generate contextual answer

---

## Technical Implementation Requirements

### Phase 1: Mock API Development

Create mock APIs that simulate airline backend services.

**Required Mock Endpoints**

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/passenger/{pnr}` | Get booking details |
| PUT | `/api/passenger/{pnr}/dob` | Update DOB |
| PUT | `/api/flight/{pnr}/details` | Update flight details |
| GET | `/api/flight/search` | Search available flights |

**Sample Mock Data Structure**

```json
{
  "pnr": "ABC123",
  "passengers": [
    {
      "id": "PAX001",
      "name": "John Doe",
      "dob": "1990-01-15",
      "flight": {
        "number": "AK123",
        "departure": "KUL",
        "destination": "SIN",
        "date": "2024-03-15",
        "time": "10:30"
      }
    }
  ]
}
```

### Phase 2: Agent Development

**ADK Implementation Requirements**
- **Agent Router** — route user queries to the appropriate agent
- **Context Management** — maintain PNR context throughout the session
- **Error Handling** — graceful failure with helpful messages
- **Validation** — input validation for all agent operations

**RAG FAQ Agent Requirements**
- **Vector Database** — mock vector store with sample documents
- **Embedding Generation** — sentence transformers or similar
- **Similarity Search** — cosine similarity for document retrieval
- **Answer Generation** — LLM-based response using retrieved chunks

**Sample FAQ Documents**
- "Baggage allowance for economy class is 20kg. Additional baggage can be purchased..."
- "Check-in counters open 3 hours before departure and close 45 minutes before..."
- "Refund requests must be submitted 24 hours before flight departure..."

---

## Sample Test Scenarios

### Scenario 1: DOB Update

**User:** "I need to update my date of birth for booking ABC123"
**System:** "I can help you update your date of birth. What is your new date of birth?"
**User:** "15th January 1990"
**System:** "Please confirm: Update DOB to 1990-01-15 for passenger John Doe in booking ABC123?"
**User:** "Yes"
**System:** "DOB updated successfully for John Doe in booking ABC123"

### Scenario 2: Flight Details Update

**User:** "I need to change my flight from KUL to BKK"
**System:** "I can help you change your flight destination. Which booking are you referring to?"
**User:** "ABC123"
**System:** "Found your booking AK123 from KUL to SIN. Available flight to BKK is AK456 on the same day at 14:30. Would you like to change to this flight?"
**User:** "Yes"
**System:** "Flight changed successfully to AK456 from KUL to BKK at 14:30 for John Doe in booking ABC123"

### Scenario 3: FAQ Query

**User:** "What is the baggage allowance for economy class?"
**System:** "The baggage allowance for economy class passengers is 20kg. You can purchase additional baggage allowance up to 30kg for a fee. Excess baggage charges apply for weight above the allowance."
