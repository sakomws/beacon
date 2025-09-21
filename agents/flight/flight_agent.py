"""
Flight-specific agent logic using Maestro framework
"""
import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from ai21 import AI21Client
from agent_config import (
    FlightSearchCriteria, 
    BookingRequest, 
    FlightOption, 
    BookingResponse,
    AgentRequirements,
    AgentPrompts
)

class FlightAgent:
    """Flight booking agent using Maestro framework"""
    
    def __init__(self, api_key: str):
        self.client = AI21Client(api_key=api_key)
    
    async def search_flights(self, criteria: FlightSearchCriteria) -> List[FlightOption]:
        """Search for flights using Maestro agent"""
        
        requirements = AgentRequirements.flight_search_requirements(criteria)
        prompt = AgentPrompts.flight_search_prompt(criteria)
        
        try:
            # Use Maestro to run the flight search
            run_result = self.client.beta.maestro.runs.create_and_poll(
                input=prompt,
                requirements=requirements,
                include=["requirements_result"]
            )
            
            # Parse the Maestro result and create flight options
            # In a real implementation, you would parse the actual API response
            # For now, we'll create mock data based on the search criteria
            return self._create_mock_flights(criteria)
            
        except Exception as e:
            raise Exception(f"Flight search failed: {str(e)}")
    
    async def book_flight(self, booking_request: BookingRequest) -> BookingResponse:
        """Book a flight using Maestro agent"""
        
        requirements = AgentRequirements.booking_requirements(booking_request)
        prompt = AgentPrompts.booking_prompt(booking_request)
        
        try:
            # Use Maestro to process the booking
            run_result = self.client.beta.maestro.runs.create_and_poll(
                input=prompt,
                requirements=requirements,
                include=["requirements_result"]
            )
            
            # Parse the Maestro result and create booking response
            # In a real implementation, you would parse the actual API response
            return self._create_mock_booking(booking_request)
            
        except Exception as e:
            raise Exception(f"Booking failed: {str(e)}")
    
    async def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        """Cancel a booking using Maestro agent"""
        
        requirements = AgentRequirements.cancellation_requirements(booking_id)
        prompt = f"""
        Cancel booking {booking_id} and process refund according to airline policy.
        Provide cancellation confirmation and refund details.
        """
        
        try:
            # Use Maestro to process the cancellation
            run_result = self.client.beta.maestro.runs.create_and_poll(
                input=prompt,
                requirements=requirements,
                include=["requirements_result"]
            )
            
            # Mock cancellation response
            return {
                "booking_id": booking_id,
                "status": "cancelled",
                "refund_amount": 250.00,
                "refund_method": "original_payment_method",
                "cancellation_fee": 25.00,
                "cancellation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Cancellation failed: {str(e)}")
    
    async def get_booking_details(self, booking_id: str) -> Dict[str, Any]:
        """Get booking details using Maestro agent"""
        
        prompt = f"""
        Retrieve detailed information for booking {booking_id} including:
        - Flight details
        - Passenger information
        - Booking status
        - Payment information
        - Cancellation policy
        - Check-in information
        """
        
        try:
            # Use Maestro to retrieve booking details
            run_result = self.client.beta.maestro.runs.create_and_poll(
                input=prompt,
                requirements=[
                    {
                        "name": "booking_verification",
                        "description": f"Verify booking {booking_id} exists and is accessible"
                    },
                    {
                        "name": "data_retrieval",
                        "description": "Retrieve all relevant booking information"
                    }
                ],
                include=["requirements_result"]
            )
            
            # Mock booking details
            return {
                "booking_id": booking_id,
                "status": "confirmed",
                "confirmation_code": "ABC123",
                "flight_details": {
                    "airline": "American Airlines",
                    "flight_number": "AA1234",
                    "departure": {
                        "airport": "LAX",
                        "time": "08:30",
                        "date": "2024-01-15"
                    },
                    "arrival": {
                        "airport": "JFK",
                        "time": "11:45",
                        "date": "2024-01-15"
                    }
                },
                "passengers": [
                    {
                        "name": "John Doe",
                        "seat": "12A",
                        "passenger_type": "adult"
                    }
                ],
                "total_cost": 299.99,
                "booking_date": "2024-01-01T10:00:00Z"
            }
            
        except Exception as e:
            raise Exception(f"Failed to retrieve booking details: {str(e)}")
    
    def _create_mock_flights(self, criteria: FlightSearchCriteria) -> List[FlightOption]:
        """Create mock flight options based on search criteria"""
        
        # Mock flight data - in a real implementation, this would come from airline APIs
        base_flights = [
            {
                "airline": "American Airlines",
                "flight_number": "AA1234",
                "aircraft": "Boeing 737",
                "base_price": 299.99,
                "departure_times": ["08:30", "14:20", "19:45"],
                "stops": [0, 0, 1]
            },
            {
                "airline": "Delta Airlines", 
                "flight_number": "DL5678",
                "aircraft": "Airbus A320",
                "base_price": 325.50,
                "departure_times": ["09:15", "15:30", "20:10"],
                "stops": [0, 1, 0]
            },
            {
                "airline": "United Airlines",
                "flight_number": "UA9012", 
                "aircraft": "Boeing 737",
                "base_price": 275.00,
                "departure_times": ["07:45", "13:20", "18:30"],
                "stops": [1, 0, 1]
            }
        ]
        
        flights = []
        for i, flight_data in enumerate(base_flights):
            for j, dep_time in enumerate(flight_data["departure_times"]):
                # Calculate arrival time (simplified)
                dep_hour = int(dep_time.split(":")[0])
                arr_hour = (dep_hour + 3) % 24
                arr_time = f"{arr_hour:02d}:{int(dep_time.split(':')[1]) + 15:02d}"
                
                # Adjust price based on class and preferences
                price = flight_data["base_price"]
                if criteria.class_type.value == "business":
                    price *= 2.5
                elif criteria.class_type.value == "first":
                    price *= 4.0
                elif criteria.class_type.value == "premium_economy":
                    price *= 1.5
                
                # Apply passenger multiplier
                price *= criteria.passengers
                
                flight_option = FlightOption(
                    flight_id=f"flight_{i}_{j}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    price=round(price, 2),
                    currency="USD",
                    segments=[{
                        "airline": flight_data["airline"],
                        "flight_number": flight_data["flight_number"],
                        "aircraft": flight_data["aircraft"],
                        "departure": {
                            "airport": criteria.origin,
                            "time": dep_time,
                            "terminal": "2"
                        },
                        "arrival": {
                            "airport": criteria.destination,
                            "time": arr_time,
                            "terminal": "4"
                        },
                        "duration": "3h 15m",
                        "stops": flight_data["stops"][j],
                        "cabin_class": criteria.class_type.value
                    }],
                    baggage_allowance={
                        "carry_on": "1 bag",
                        "checked": "1 bag" if criteria.class_type.value in ["economy", "premium_economy"] else "2 bags"
                    },
                    cancellation_policy={
                        "free_cancellation": "24 hours",
                        "refund_policy": "Full refund within 24 hours"
                    },
                    booking_class="Y" if criteria.class_type.value == "economy" else "C"
                )
                flights.append(flight_option)
        
        return flights[:6]  # Return top 6 results
    
    def _create_mock_booking(self, booking_request: BookingRequest) -> BookingResponse:
        """Create mock booking response"""
        
        # Mock flight details
        flight_details = FlightOption(
            flight_id=booking_request.flight_id,
            price=299.99,
            currency="USD",
            segments=[{
                "airline": "American Airlines",
                "flight_number": "AA1234",
                "aircraft": "Boeing 737",
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
                "stops": 0,
                "cabin_class": "economy"
            }],
            baggage_allowance={
                "carry_on": "1 bag",
                "checked": "1 bag"
            },
            cancellation_policy={
                "free_cancellation": "24 hours",
                "refund_policy": "Full refund within 24 hours"
            },
            booking_class="Y"
        )
        
        return BookingResponse(
            booking_id=f"booking_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            confirmation_code="ABC123",
            status="confirmed",
            total_cost=299.99,
            currency="USD",
            flight_details=flight_details,
            passengers=booking_request.passengers,
            booking_date=datetime.now(),
            cancellation_deadline=datetime.now().replace(hour=23, minute=59, second=59)
        )
