from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Airline Mock API Backend")

# In-memory mock database
# Stores bookings keyed by PNR
bookings = {
    "ABC123": {
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
}

# Available flights for search
available_flights = [
    {
        "number": "AK456",
        "departure": "KUL",
        "destination": "BKK",
        "date": "2024-03-15",
        "time": "14:30"
    },
    {
        "number": "AK123",
        "departure": "KUL",
        "destination": "SIN",
        "date": "2024-03-15",
        "time": "10:30"
    },
    {
        "number": "AK789",
        "departure": "SIN",
        "destination": "KUL",
        "date": "2024-03-16",
        "time": "08:15"
    }
]

# Request schemas
class UpdateDobRequest(BaseModel):
    passenger_name: Optional[str] = None
    passenger_id: Optional[str] = None
    dob: str

class UpdateFlightRequest(BaseModel):
    number: Optional[str] = None
    departure: Optional[str] = None
    destination: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None

@app.get("/api/passenger/{pnr}")
def get_passenger(pnr: str):
    """Retrieve booking details by PNR."""
    pnr_upper = pnr.upper()
    if pnr_upper not in bookings:
        raise HTTPException(status_code=404, detail=f"Booking PNR {pnr} not found.")
    return bookings[pnr_upper]

@app.put("/api/passenger/{pnr}/dob")
def update_passenger_dob(pnr: str, request: UpdateDobRequest):
    """Update passenger's date of birth."""
    pnr_upper = pnr.upper()
    if pnr_upper not in bookings:
        raise HTTPException(status_code=404, detail=f"Booking PNR {pnr} not found.")
    
    booking = bookings[pnr_upper]
    target_passenger = None
    
    # Identify passenger by ID or name
    for passenger in booking["passengers"]:
        if request.passenger_id and passenger["id"] == request.passenger_id:
            target_passenger = passenger
            break
        elif request.passenger_name and passenger["name"].lower() == request.passenger_name.lower():
            target_passenger = passenger
            break
            
    if not target_passenger:
        # If no identification provided and only one passenger, default to them
        if not request.passenger_id and not request.passenger_name and len(booking["passengers"]) == 1:
            target_passenger = booking["passengers"][0]
        else:
            ident = request.passenger_id or request.passenger_name or "unknown"
            raise HTTPException(status_code=404, detail=f"Passenger '{ident}' not found in booking {pnr}.")
            
    # Simple validation on date format (YYYY-MM-DD)
    dob_parts = request.dob.split("-")
    if len(dob_parts) != 3 or not all(part.isdigit() for part in dob_parts) or len(dob_parts[0]) != 4:
         raise HTTPException(status_code=400, detail="Invalid DOB format. Must be YYYY-MM-DD.")
         
    target_passenger["dob"] = request.dob
    return {
        "status": "success",
        "message": f"Updated DOB to {request.dob} for passenger {target_passenger['name']}",
        "passenger": target_passenger
    }

@app.put("/api/flight/{pnr}/details")
def update_flight_details(pnr: str, request: UpdateFlightRequest):
    """Update flight information in the passenger booking."""
    pnr_upper = pnr.upper()
    if pnr_upper not in bookings:
        raise HTTPException(status_code=404, detail=f"Booking PNR {pnr} not found.")
        
    booking = bookings[pnr_upper]
    
    # We update the flight for all passengers in this booking
    for passenger in booking["passengers"]:
        flight = passenger["flight"]
        if request.number:
            flight["number"] = request.number
        if request.departure:
            flight["departure"] = request.departure
        if request.destination:
            flight["destination"] = request.destination
        if request.date:
            flight["date"] = request.date
        if request.time:
            flight["time"] = request.time
            
    return {
        "status": "success",
        "message": "Flight details updated successfully.",
        "booking": booking
    }

@app.get("/api/flight/search")
def search_flights(
    departure: str = Query(..., description="Departure city code"),
    destination: str = Query(..., description="Destination city code"),
    date: Optional[str] = Query(None, description="Flight date YYYY-MM-DD")
):
    """Search for available flights based on route and date."""
    results = []
    for flight in available_flights:
        if (flight["departure"].upper() == departure.upper() and
            flight["destination"].upper() == destination.upper()):
            if not date or flight["date"] == date:
                results.append(flight)
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
