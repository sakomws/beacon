from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
from ai21 import AI21Client
import os
from datetime import datetime, date
import json
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Flight Booking Agent",
    description="AI-powered flight booking agent using Maestro framework",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI21 client
api_key = os.getenv("AI21_API_KEY")
if api_key:
    client = AI21Client(api_key=api_key)
else:
    print("Warning: AI21_API_KEY not found. Running in mock mode.")
    client = None

# BrightData API configuration
BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY")
if BRIGHTDATA_API_KEY:
    BRIGHTDATA_HEADERS = {
        "Authorization": f"Bearer {BRIGHTDATA_API_KEY}",
        "Content-Type": "application/json"
    }
    print("BrightData API key loaded successfully")
else:
    print("Warning: BRIGHTDATA_API_KEY not found. Web scraping will be disabled.")
    BRIGHTDATA_HEADERS = None

# Pydantic models
class FlightSearchRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    passengers: int = 1
    class_type: str = "economy"
    preferences: Optional[Dict[str, Any]] = None

class FlightOption(BaseModel):
    airline: str
    flight_number: str
    departure_time: str
    arrival_time: str
    duration: str
    price: float
    stops: int
    aircraft: str
    booking_url: str = ""
    score: float = 0.0
    price_score: float = 0.0
    time_score: float = 0.0
    risk_score: float = 0.0
    reputation_score: float = 0.0
    flexibility_score: float = 0.0

class FlightSearchResponse(BaseModel):
    search_id: str
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str]
    passengers: int
    class_type: str
    flights: List[FlightOption]
    total_results: int

class BookingRequest(BaseModel):
    flight_id: str
    passenger_details: Dict[str, Any]
    payment_info: Dict[str, Any]

class BookingResponse(BaseModel):
    booking_id: str
    status: str
    confirmation_code: str
    total_cost: float
    flight_details: FlightOption

# Web scraping function for flight search using BrightData API
async def search_flights_web(origin: str, destination: str, departure_date: str, passengers: int = 1) -> List[FlightOption]:
    """Search for flights using web scraping via BrightData API"""
    
    if not BRIGHTDATA_HEADERS:
        print("BrightData API not configured, skipping web scraping")
        return []
    
    # Construct Google Search URL for flights (like in your 1.py)
    from urllib.parse import quote_plus
    origin_encoded = quote_plus(origin)
    destination_encoded = quote_plus(destination)
    search_url = f"https://www.google.com/search?q=Flights%20from%20{origin_encoded}%20to%20{destination_encoded}%20on%20{departure_date}&brd_json=1"
    
    data = {
        "zone": "serp_api1",
        "url": search_url,
        "format": "raw"
    }
    
    try:
        print(f"Searching for flights: {origin} to {destination} on {departure_date}")
        print(f"Search URL: {search_url}")
        
        response = requests.post(
            "https://api.brightdata.com/request",
            json=data,
            headers=BRIGHTDATA_HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            # Save response for debugging
            with open("brightdata_response.json", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Response saved ({len(response.text)} characters)")
            
            # Parse the JSON response for flight data
            try:
                json_data = response.json()
                flights = parse_json_flight_data(json_data, origin, destination, departure_date, passengers)
                return flights
            except json.JSONDecodeError:
                # Fallback to HTML parsing if JSON parsing fails
                flights = parse_flight_data(response.text, origin, destination, departure_date, passengers)
                return flights
        else:
            print(f"BrightData API error: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"Web scraping error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def calculate_flight_scores(flights: List[FlightOption]) -> List[FlightOption]:
    """Calculate comprehensive scores for flight options"""
    
    if not flights:
        return flights
    
    # Airline reputation scores (0-100, higher is better)
    airline_reputation = {
        "United": 85, "United Airlines": 85,
        "American": 80, "American Airlines": 80,
        "Delta": 88, "Delta Air Lines": 88,
        "Southwest": 75, "Southwest Airlines": 75,
        "JetBlue": 82, "JetBlue Airways": 82,
        "Alaska": 90, "Alaska Airlines": 90,
        "Hawaiian": 85, "Hawaiian Airlines": 85,
        "Spirit": 60, "Spirit Airlines": 60,
        "Frontier": 55, "Frontier Airlines": 55,
        "Multiple Airlines": 70, "Multiple airlines": 70
    }
    
    # Extract prices for normalization
    prices = [f.price for f in flights]
    min_price = min(prices)
    max_price = max(prices)
    price_range = max_price - min_price if max_price > min_price else 1
    
    # Extract durations for normalization
    durations = []
    for f in flights:
        # Extract hours from duration string like "5h 20m+" or "1 stop · 7h 30m+"
        duration_str = f.duration.lower()
        if "h" in duration_str:
            try:
                hours = float(duration_str.split("h")[0].split()[-1])
                durations.append(hours)
            except:
                durations.append(6.0)  # Default
        else:
            durations.append(6.0)  # Default
    
    min_duration = min(durations)
    max_duration = max(durations)
    duration_range = max_duration - min_duration if max_duration > min_duration else 1
    
    for flight in flights:
        # 1. PRICE SCORE (0-100, higher is better for lower prices)
        if price_range > 0:
            flight.price_score = max(0, 100 - ((flight.price - min_price) / price_range) * 100)
        else:
            flight.price_score = 100
        
        # 2. TIME SCORE (0-100, higher is better for shorter flights)
        duration_str = flight.duration.lower()
        if "h" in duration_str:
            try:
                hours = float(duration_str.split("h")[0].split()[-1])
                if duration_range > 0:
                    flight.time_score = max(0, 100 - ((hours - min_duration) / duration_range) * 100)
                else:
                    flight.time_score = 100
            except:
                flight.time_score = 50  # Default for parsing errors
        else:
            flight.time_score = 50
        
        # 3. RISK SCORE (0-100, higher is better for lower risk)
        # Nonstop flights are lower risk
        if flight.stops == 0:
            flight.risk_score = 90
        elif flight.stops == 1:
            flight.risk_score = 70
        else:
            flight.risk_score = 50
        
        # 4. REPUTATION SCORE (0-100, higher is better)
        flight.reputation_score = airline_reputation.get(flight.airline, 60)  # Default for unknown airlines
        
        # 5. FLEXIBILITY SCORE (0-100, higher is better)
        # Based on departure time (morning/afternoon flights are more flexible)
        try:
            departure_hour = int(flight.departure_time.split(":")[0])
            if 6 <= departure_hour <= 10:  # Morning flights
                flight.flexibility_score = 90
            elif 11 <= departure_hour <= 15:  # Afternoon flights
                flight.flexibility_score = 85
            elif 16 <= departure_hour <= 20:  # Evening flights
                flight.flexibility_score = 80
            else:  # Late night/early morning
                flight.flexibility_score = 60
        except:
            flight.flexibility_score = 70  # Default
        
        # 6. OVERALL SCORE (weighted average)
        # Weights: Price 30%, Time 25%, Risk 20%, Reputation 15%, Flexibility 10%
        flight.score = (
            flight.price_score * 0.30 +
            flight.time_score * 0.25 +
            flight.risk_score * 0.20 +
            flight.reputation_score * 0.15 +
            flight.flexibility_score * 0.10
        )
    
    # Sort flights by overall score (highest first)
    flights.sort(key=lambda x: x.score, reverse=True)
    
    return flights

def parse_json_flight_data(json_data: dict, origin: str, destination: str, departure_date: str, passengers: int) -> List[FlightOption]:
    """Parse flight data from BrightData JSON response"""
    
    flights = []
    
    print(f"Parsing JSON flight data from BrightData response")
    
    try:
        # Extract flight data from the JSON structure
        if "flights" in json_data and "items" in json_data["flights"]:
            flight_items = json_data["flights"]["items"]
            print(f"Found {len(flight_items)} flight items in JSON")
            
            for i, item in enumerate(flight_items[:6]):  # Limit to 6 flights
                try:
                    # Extract price from the item - check both 'price' and 'stops' fields
                    price_text = item.get("price", item.get("stops", "from $0"))
                    price_match = re.search(r'[\$₹](\d+)', price_text)
                    if price_match:
                        price = float(price_match.group(1)) * passengers
                    else:
                        price = 200.0 * passengers  # Default price
                    
                    # Extract airline
                    airline = item.get("title", f"Airline {i+1}")
                    
                    # Extract travel time
                    travel_time = item.get("travel_time", "5h 30m")
                    
                    # Extract stops info
                    stops_text = item.get("stops", "Nonstop")
                    stops = 0 if "Nonstop" in stops_text else 1
                    
                    # Create booking URL based on airline
                    booking_url = f"https://www.google.com/search?q={airline.replace(' ', '+')}+flights+{origin.replace(' ', '+')}+to+{destination.replace(' ', '+')}+{departure_date}"
                    print(f"Created booking URL: {booking_url}")
                    
                    # Create flight object
                    flight = FlightOption(
                        airline=airline,
                        flight_number=f"FL{i+1:03d}",
                        departure_time=f"{8 + i}:00",
                        arrival_time=f"{13 + i}:00",
                        duration=travel_time,
                        price=price,
                        stops=stops,
                        aircraft="Boeing 737",
                        booking_url=booking_url
                    )
                    print(f"Flight booking_url: {flight.booking_url}")
                    flights.append(flight)
                    print(f"Created flight {i+1}: {flight.airline} - ${flight.price:.2f}")
                    
                except Exception as e:
                    print(f"Error parsing flight item {i}: {e}")
                    continue
        
        # Also check for date_price_items for additional flight data
        if "flights" in json_data and "date_price_items" in json_data["flights"]:
            date_items = json_data["flights"]["date_price_items"]
            print(f"Found {len(date_items)} date price items")
            
            # Look for flights on the specific departure date
            target_date = departure_date
            for item in date_items:
                if item.get("departure_date") == target_date:
                    price_text = item.get("price", "$0")
                    price_match = re.search(r'\$(\d+)', price_text)
                    if price_match:
                        price = float(price_match.group(1)) * passengers
                        
                        booking_url = f"https://www.google.com/search?q=flights+{origin.replace(' ', '+')}+to+{destination.replace(' ', '+')}+{departure_date}"
                        
                        flight = FlightOption(
                            airline="Multiple Airlines",
                            flight_number=f"FL{len(flights)+1:03d}",
                            departure_time="08:00",
                            arrival_time="13:00",
                            duration="5h 00m",
                            price=price,
                            stops=0,
                            aircraft="Boeing 737",
                            booking_url=booking_url
                        )
                        flights.append(flight)
                        print(f"Created date-specific flight: ${flight.price:.2f}")
                    break
        
        if not flights:
            print("No flights found in JSON data")
        else:
            # Calculate scores for all flights
            flights = calculate_flight_scores(flights)
            print(f"Calculated scores for {len(flights)} flights")
        
    except Exception as e:
        print(f"Error parsing JSON flight data: {e}")
        import traceback
        traceback.print_exc()
    
    return flights

def parse_flight_data(html_content: str, origin: str, destination: str, departure_date: str, passengers: int) -> List[FlightOption]:
    """Parse flight data from scraped HTML content using BeautifulSoup"""
    
    flights = []
    
    print(f"Parsing flight data from HTML content ({len(html_content)} characters)")
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for flight data in various possible structures
        # Google Flights uses different class names, so we'll try multiple selectors
        
        # Look for flight data in script tags containing JSON data
        script_tags = soup.find_all('script')
        flight_data_found = False
        
        for script in script_tags:
            if script.string and ('AF_initDataCallback' in script.string or 'flight' in script.string.lower()):
                print(f"Found potential flight data in script tag ({len(script.string)} chars)")
                
                # Look for price patterns in the script content
                price_matches = re.findall(r'\$(\d+)', script.string)
                if price_matches:
                    print(f"Found {len(price_matches)} price references in script")
                    flight_data_found = True
                    
                    # Extract flight information from the script data
                    # Look for patterns like "United", "Alaska", "Hawaiian" in the script
                    airline_matches = re.findall(r'"(United|Alaska|Hawaiian|Delta|American|Southwest|JetBlue|Spirit|Frontier)"', script.string)
                    
                    # Create flights based on found prices
                    for i, price_str in enumerate(price_matches[:6]):  # Limit to 6 flights
                        try:
                            price = float(price_str) * passengers
                            
                            # Use found airline or default
                            airline = airline_matches[i] if i < len(airline_matches) else f"Airline {i+1}"
                            
                            # Create flight times based on index
                            departure_hour = 8 + (i * 2) % 12
                            arrival_hour = departure_hour + 5
                            
                            booking_url = f"https://www.google.com/search?q={airline.replace(' ', '+')}+flights+{origin.replace(' ', '+')}+to+{destination.replace(' ', '+')}+{departure_date}"
                            
                            flight = FlightOption(
                                airline=airline,
                                flight_number=f"FL{i+1:03d}",
                                departure_time=f"{departure_hour:02d}:00",
                                arrival_time=f"{arrival_hour:02d}:00",
                                duration="5h 15m",
                                price=price,
                                stops=0,
                                aircraft="Boeing 737",
                                booking_url=booking_url
                            )
                            flights.append(flight)
                            print(f"Created flight {i+1}: {flight.airline} {flight.flight_number} - ${flight.price:.2f}")
                            
                        except Exception as e:
                            print(f"Error parsing price {price_str}: {e}")
                            continue
                    break
        
        # Fallback: Look for price elements in the visible HTML
        if not flight_data_found:
            price_elements = soup.find_all(text=re.compile(r'\$[\d,]+'))
            print(f"Found {len(price_elements)} price elements in HTML")
            
            if price_elements:
                for i, price_text in enumerate(price_elements[:6]):
                    try:
                        price_match = re.search(r'\$(\d+)', price_text)
                        if price_match:
                            price = float(price_match.group(1)) * passengers
                            
                            booking_url = f"https://www.google.com/search?q=flights+{origin.replace(' ', '+')}+to+{destination.replace(' ', '+')}+{departure_date}"
                            
                            flight = FlightOption(
                                airline=f"Airline {i+1}",
                                flight_number=f"FL{i+1:03d}",
                                departure_time=f"{8 + i}:00",
                                arrival_time=f"{13 + i}:00",
                                duration="5h 15m",
                                price=price,
                                stops=0,
                                aircraft="Boeing 737",
                                booking_url=booking_url
                            )
                            flights.append(flight)
                            print(f"Created flight {i+1}: {flight.airline} {flight.flight_number} - ${flight.price:.2f}")
                    except Exception as e:
                        print(f"Error parsing price {price_text}: {e}")
                        continue
        
        if not flights:
            print("No flights found in HTML content")
            print("Note: Google Flights uses dynamic content. Consider using Selenium/Playwright for full parsing.")
        
    except Exception as e:
        print(f"Error parsing HTML content: {e}")
    
    return flights

# Flight search agent using Maestro
async def search_flights_agent(search_request: FlightSearchRequest) -> FlightSearchResponse:
    """Use Maestro agent to search for flights"""
    
    # Create requirements for the flight search
    requirements = [
        {
            "name": "origin_validation",
            "description": f"Validate that {search_request.origin} is a valid airport code or city name"
        },
        {
            "name": "destination_validation", 
            "description": f"Validate that {search_request.destination} is a valid airport code or city name"
        },
        {
            "name": "date_validation",
            "description": f"Validate that {search_request.departure_date} is a valid future date"
        },
        {
            "name": "flight_search",
            "description": f"Search for flights from {search_request.origin} to {search_request.destination} on {search_request.departure_date} for {search_request.passengers} passengers in {search_request.class_type} class"
        },
        {
            "name": "price_optimization",
            "description": "Find the best price options within reasonable range"
        },
        {
            "name": "schedule_optimization",
            "description": "Prioritize convenient departure and arrival times"
        }
    ]
    
    # Create the search prompt
    search_prompt = f"""
    Search for flights with the following criteria:
    - Origin: {search_request.origin}
    - Destination: {search_request.destination}
    - Departure Date: {search_request.departure_date}
    - Return Date: {search_request.return_date if search_request.return_date else 'One-way'}
    - Passengers: {search_request.passengers}
    - Class: {search_request.class_type}
    - Preferences: {search_request.preferences if search_request.preferences else 'None specified'}
    
    Please provide a comprehensive search result with multiple flight options including:
    - Airline name
    - Flight number
    - Departure and arrival times
    - Flight duration
    - Price
    - Number of stops
    - Aircraft type
    
    Return the results in a structured JSON format.
    """
    
    try:
        # Mock mode - simulate Maestro response
        print(f"Processing flight search for {search_request.origin} to {search_request.destination}")
        
        # Use web scraping to get real flight data
        flights = await search_flights_web(
            search_request.origin,
            search_request.destination,
            search_request.departure_date,
            search_request.passengers
        )
        
        # If web scraping fails, return empty results
        if not flights:
            print("Web scraping failed, no flights found")
            flights = []
        
        return FlightSearchResponse(
            search_id=f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            origin=search_request.origin,
            destination=search_request.destination,
            departure_date=search_request.departure_date,
            return_date=search_request.return_date,
            passengers=search_request.passengers,
            class_type=search_request.class_type,
            flights=flights,
            total_results=len(flights)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flight search failed: {str(e)}")

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Flight Booking Agent API", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/search", response_model=FlightSearchResponse)
async def search_flights(search_request: FlightSearchRequest):
    """Search for flights using AI agent"""
    try:
        result = await search_flights_agent(search_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/book", response_model=BookingResponse)
async def book_flight(booking_request: BookingRequest):
    """Book a flight using AI agent"""
    
    # Create requirements for booking
    requirements = [
        {
            "name": "flight_validation",
            "description": f"Validate that flight {booking_request.flight_id} is available for booking"
        },
        {
            "name": "passenger_validation",
            "description": "Validate passenger details are complete and correct"
        },
        {
            "name": "payment_processing",
            "description": "Process payment information securely"
        },
        {
            "name": "booking_confirmation",
            "description": "Generate booking confirmation and confirmation code"
        }
    ]
    
    booking_prompt = f"""
    Process a flight booking with the following details:
    - Flight ID: {booking_request.flight_id}
    - Passenger Details: {json.dumps(booking_request.passenger_details, indent=2)}
    - Payment Information: {json.dumps(booking_request.payment_info, indent=2)}
    
    Please process the booking and provide confirmation details.
    """
    
    try:
        # Mock mode - simulate Maestro response
        print(f"Processing booking for flight {booking_request.flight_id}")
        
        # Mock booking response
        booking_response = BookingResponse(
            booking_id=f"booking_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            status="confirmed",
            confirmation_code="ABC123",
            total_cost=299.99,
            flight_details=FlightOption(
                airline="American Airlines",
                flight_number="AA1234",
                departure_time="08:30",
                arrival_time="11:45",
                duration="3h 15m",
                price=299.99,
                stops=0,
                aircraft="Boeing 737"
            )
        )
        
        return booking_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Booking failed: {str(e)}")

@app.get("/flights/{flight_id}")
async def get_flight_details(flight_id: str):
    """Get detailed information about a specific flight"""
    # Mock flight details
    return {
        "flight_id": flight_id,
        "airline": "American Airlines",
        "flight_number": "AA1234",
        "departure": {
            "airport": "LAX",
            "time": "08:30",
            "terminal": "2"
        },
        "arrival": {
            "airport": "JFK",
            "time": "11:45",
            "terminal": "4"
        },
        "duration": "3h 15m",
        "aircraft": "Boeing 737",
        "seats_available": 15
    }

@app.get("/airports/search")
async def search_airports(query: str):
    """Search for airports by name or code"""
    # Mock airport search
    airports = [
        {"code": "LAX", "name": "Los Angeles International Airport", "city": "Los Angeles"},
        {"code": "JFK", "name": "John F. Kennedy International Airport", "city": "New York"},
        {"code": "LHR", "name": "London Heathrow Airport", "city": "London"},
        {"code": "CDG", "name": "Charles de Gaulle Airport", "city": "Paris"},
        {"code": "NRT", "name": "Narita International Airport", "city": "Tokyo"}
    ]
    
    filtered_airports = [airport for airport in airports 
                        if query.lower() in airport["name"].lower() 
                        or query.lower() in airport["city"].lower()
                        or query.upper() in airport["code"]]
    
    return {"airports": filtered_airports}

@app.get("/test-scraping")
async def test_scraping(origin: str = "LAX", destination: str = "JFK", date: str = "2024-02-15"):
    """Test the web scraping functionality"""
    try:
        flights = await search_flights_web(origin, destination, date, 1)
        return {
            "status": "success" if flights else "no_data",
            "origin": origin,
            "destination": destination,
            "date": date,
            "flights_found": len(flights),
            "flights": flights,
            "message": "Real web scraping data" if flights else "No flights found - implement HTML parser for real data"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
