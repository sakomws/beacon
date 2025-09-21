"""
Agent configuration and models for the Flight Booking Agent
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime, date

class ClassType(str, Enum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"

class TripType(str, Enum):
    ONE_WAY = "one_way"
    ROUND_TRIP = "round_trip"
    MULTI_CITY = "multi_city"

class PassengerType(str, Enum):
    ADULT = "adult"
    CHILD = "child"
    INFANT = "infant"

class PassengerDetails(BaseModel):
    first_name: str = Field(..., description="Passenger's first name")
    last_name: str = Field(..., description="Passenger's last name")
    date_of_birth: date = Field(..., description="Passenger's date of birth")
    passport_number: Optional[str] = Field(None, description="Passport number if international")
    nationality: Optional[str] = Field(None, description="Passenger's nationality")
    passenger_type: PassengerType = Field(PassengerType.ADULT, description="Type of passenger")
    special_requests: Optional[str] = Field(None, description="Special requests or needs")

class PaymentDetails(BaseModel):
    card_number: str = Field(..., description="Credit card number")
    expiry_date: str = Field(..., description="Card expiry date (MM/YY)")
    cvv: str = Field(..., description="Card CVV")
    cardholder_name: str = Field(..., description="Name on the card")
    billing_address: Dict[str, str] = Field(..., description="Billing address")

class FlightPreferences(BaseModel):
    preferred_airlines: Optional[List[str]] = Field(None, description="Preferred airline codes")
    max_stops: int = Field(0, description="Maximum number of stops allowed")
    preferred_departure_times: Optional[List[str]] = Field(None, description="Preferred departure time ranges")
    seat_preference: Optional[str] = Field(None, description="Seat preference (window, aisle, middle)")
    meal_preference: Optional[str] = Field(None, description="Meal preference")
    special_assistance: Optional[List[str]] = Field(None, description="Special assistance requirements")

class FlightSearchCriteria(BaseModel):
    origin: str = Field(..., description="Origin airport code or city")
    destination: str = Field(..., description="Destination airport code or city")
    departure_date: date = Field(..., description="Departure date")
    return_date: Optional[date] = Field(None, description="Return date for round trip")
    passengers: int = Field(1, ge=1, le=9, description="Number of passengers")
    class_type: ClassType = Field(ClassType.ECONOMY, description="Class of service")
    trip_type: TripType = Field(TripType.ONE_WAY, description="Type of trip")
    preferences: Optional[FlightPreferences] = Field(None, description="Flight preferences")

class Airport(BaseModel):
    code: str = Field(..., description="Airport IATA code")
    name: str = Field(..., description="Airport name")
    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country name")
    timezone: str = Field(..., description="Airport timezone")

class FlightSegment(BaseModel):
    airline: str = Field(..., description="Airline name")
    flight_number: str = Field(..., description="Flight number")
    aircraft: str = Field(..., description="Aircraft type")
    departure: Dict[str, Any] = Field(..., description="Departure details")
    arrival: Dict[str, Any] = Field(..., description="Arrival details")
    duration: str = Field(..., description="Flight duration")
    stops: int = Field(0, description="Number of stops")
    cabin_class: str = Field(..., description="Cabin class")

class FlightOption(BaseModel):
    flight_id: str = Field(..., description="Unique flight identifier")
    price: float = Field(..., description="Total price for all passengers")
    currency: str = Field("USD", description="Currency code")
    segments: List[FlightSegment] = Field(..., description="Flight segments")
    baggage_allowance: Dict[str, Any] = Field(..., description="Baggage allowance details")
    cancellation_policy: Dict[str, Any] = Field(..., description="Cancellation policy")
    booking_class: str = Field(..., description="Booking class code")

class BookingRequest(BaseModel):
    flight_id: str = Field(..., description="Selected flight ID")
    passengers: List[PassengerDetails] = Field(..., description="Passenger details")
    payment: PaymentDetails = Field(..., description="Payment information")
    contact_info: Dict[str, str] = Field(..., description="Contact information")
    special_requests: Optional[str] = Field(None, description="Special requests")

class BookingResponse(BaseModel):
    booking_id: str = Field(..., description="Unique booking identifier")
    confirmation_code: str = Field(..., description="Booking confirmation code")
    status: str = Field(..., description="Booking status")
    total_cost: float = Field(..., description="Total booking cost")
    currency: str = Field("USD", description="Currency code")
    flight_details: FlightOption = Field(..., description="Booked flight details")
    passengers: List[PassengerDetails] = Field(..., description="Passenger details")
    booking_date: datetime = Field(default_factory=datetime.now, description="Booking date")
    cancellation_deadline: Optional[datetime] = Field(None, description="Cancellation deadline")

class AgentRequirements:
    """Predefined requirements for different agent operations"""
    
    @staticmethod
    def flight_search_requirements(criteria: FlightSearchCriteria) -> List[Dict[str, str]]:
        """Get requirements for flight search operation"""
        return [
            {
                "name": "origin_validation",
                "description": f"Validate that '{criteria.origin}' is a valid airport code or city name and resolve to proper airport code"
            },
            {
                "name": "destination_validation",
                "description": f"Validate that '{criteria.destination}' is a valid airport code or city name and resolve to proper airport code"
            },
            {
                "name": "date_validation",
                "description": f"Validate that departure date '{criteria.departure_date}' is valid and in the future"
            },
            {
                "name": "route_validation",
                "description": f"Verify that flights are available between {criteria.origin} and {criteria.destination}"
            },
            {
                "name": "price_optimization",
                "description": "Find the best price options within reasonable range and consider user preferences"
            },
            {
                "name": "schedule_optimization",
                "description": "Prioritize convenient departure and arrival times based on user preferences"
            },
            {
                "name": "airline_preferences",
                "description": f"Consider preferred airlines: {criteria.preferences.preferred_airlines if criteria.preferences and criteria.preferences.preferred_airlines else 'No preferences'}"
            },
            {
                "name": "stop_requirements",
                "description": f"Respect maximum stops requirement: {criteria.preferences.max_stops if criteria.preferences else 0} stops maximum"
            }
        ]
    
    @staticmethod
    def booking_requirements(booking_request: BookingRequest) -> List[Dict[str, str]]:
        """Get requirements for booking operation"""
        return [
            {
                "name": "flight_availability",
                "description": f"Verify that flight {booking_request.flight_id} is still available for booking"
            },
            {
                "name": "passenger_validation",
                "description": "Validate all passenger details are complete, correct, and meet airline requirements"
            },
            {
                "name": "payment_processing",
                "description": "Process payment information securely and validate payment method"
            },
            {
                "name": "seat_assignment",
                "description": "Assign seats based on passenger preferences and availability"
            },
            {
                "name": "booking_confirmation",
                "description": "Generate booking confirmation with unique confirmation code"
            },
            {
                "name": "email_notification",
                "description": "Send booking confirmation email to passenger contact information"
            }
        ]
    
    @staticmethod
    def cancellation_requirements(booking_id: str) -> List[Dict[str, str]]:
        """Get requirements for cancellation operation"""
        return [
            {
                "name": "booking_verification",
                "description": f"Verify booking {booking_id} exists and belongs to the requesting user"
            },
            {
                "name": "cancellation_policy",
                "description": "Check cancellation policy and determine refund eligibility"
            },
            {
                "name": "refund_processing",
                "description": "Process refund according to airline policy and booking terms"
            },
            {
                "name": "confirmation_notification",
                "description": "Send cancellation confirmation to passenger"
            }
        ]

class AgentPrompts:
    """Predefined prompts for different agent operations"""
    
    @staticmethod
    def flight_search_prompt(criteria: FlightSearchCriteria) -> str:
        """Generate flight search prompt"""
        preferences_text = ""
        if criteria.preferences:
            prefs = []
            if criteria.preferences.preferred_airlines:
                prefs.append(f"Preferred airlines: {', '.join(criteria.preferences.preferred_airlines)}")
            if criteria.preferences.max_stops is not None:
                prefs.append(f"Maximum stops: {criteria.preferences.max_stops}")
            if criteria.preferences.preferred_departure_times:
                prefs.append(f"Preferred departure times: {', '.join(criteria.preferences.preferred_departure_times)}")
            if criteria.preferences.seat_preference:
                prefs.append(f"Seat preference: {criteria.preferences.seat_preference}")
            if prefs:
                preferences_text = f"\nPreferences: {', '.join(prefs)}"
        
        return f"""
        Search for flights with the following criteria:
        - Origin: {criteria.origin}
        - Destination: {criteria.destination}
        - Departure Date: {criteria.departure_date}
        - Return Date: {criteria.return_date if criteria.return_date else 'One-way trip'}
        - Passengers: {criteria.passengers}
        - Class: {criteria.class_type.value}
        - Trip Type: {criteria.trip_type.value}{preferences_text}
        
        Please provide a comprehensive search result with multiple flight options including:
        - Airline name and flight number
        - Departure and arrival times (local times)
        - Flight duration
        - Price breakdown (base fare, taxes, fees)
        - Number of stops and layover information
        - Aircraft type
        - Baggage allowance
        - Cancellation policy
        
        Return the results in a structured JSON format suitable for API consumption.
        """
    
    @staticmethod
    def booking_prompt(booking_request: BookingRequest) -> str:
        """Generate booking prompt"""
        return f"""
        Process a flight booking with the following details:
        - Flight ID: {booking_request.flight_id}
        - Number of Passengers: {len(booking_request.passengers)}
        - Passenger Details: {[f"{p.first_name} {p.last_name} ({p.passenger_type.value})" for p in booking_request.passengers]}
        - Contact Information: {booking_request.contact_info}
        - Special Requests: {booking_request.special_requests or 'None'}
        
        Please process the booking and provide:
        - Booking confirmation details
        - Confirmation code
        - Total cost breakdown
        - Seat assignments
        - Booking terms and conditions
        - Cancellation policy
        """
