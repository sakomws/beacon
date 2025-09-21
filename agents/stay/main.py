#!/usr/bin/env python3
"""
Stay Agent - Hotel and accommodation recommendations
"""

import os
import json
import asyncio
import requests
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AI21 API configuration
AI21_API_KEY = os.getenv("AI21_API_KEY")
if AI21_API_KEY:
    from ai21 import AI21Client
    client = AI21Client(api_key=AI21_API_KEY)
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
class HotelSearchRequest(BaseModel):
    location: str
    check_in: str
    check_out: str
    guests: int = 2
    rooms: int = 1
    hotel_type: str = "all"
    price_range: str = "all"
    max_results: int = 10

class HotelOption(BaseModel):
    name: str
    hotel_type: str
    price_per_night: float
    total_price: float
    rating: float
    address: str
    phone: str
    website: str
    amenities: List[str]
    description: str
    availability: str
    booking_url: str = ""
    score: float = 0.0
    price_score: float = 0.0
    quality_score: float = 0.0
    location_score: float = 0.0
    amenity_score: float = 0.0
    reputation_score: float = 0.0

class HotelSearchResponse(BaseModel):
    search_id: str
    location: str
    check_in: str
    check_out: str
    options: List[HotelOption]
    total_results: int

class BookingRequest(BaseModel):
    hotel_id: str
    check_in: str
    check_out: str
    guests: int
    rooms: int
    contact_info: Dict[str, Any]

class BookingResponse(BaseModel):
    booking_id: str
    status: str
    confirmation_code: str
    hotel_details: HotelOption
    total_cost: float

# Web scraping function for hotel search
async def search_hotels_web(location: str, check_in: str, check_out: str, guests: int = 2, rooms: int = 1, hotel_type: str = "all", price_range: str = "all") -> List[HotelOption]:
    """Search for hotels using web scraping via BrightData API"""
    
    if not BRIGHTDATA_HEADERS:
        print("BrightData API not configured, skipping web scraping")
        return []
    
    # Construct Google Search URL for hotels
    location_encoded = quote_plus(location)
    hotel_query = f"hotels in {location_encoded}"
    search_url = f"https://www.google.com/search?q={quote_plus(hotel_query)}&brd_json=1"
    
    data = {
        "zone": "serp_api1",
        "url": search_url,
        "format": "raw"
    }
    
    try:
        print(f"Searching for hotels: {location} - {check_in} to {check_out}")
        print(f"Search URL: {search_url}")
        
        response = requests.post(
            "https://api.brightdata.com/request",
            json=data,
            headers=BRIGHTDATA_HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            # Save response for debugging
            with open("brightdata_hotels_response.json", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Response saved ({len(response.text)} characters)")
            
            # Parse the JSON response for hotel data
            try:
                json_data = response.json()
                hotels = parse_json_hotel_data(json_data, location, check_in, check_out, guests, rooms)
                return hotels
            except json.JSONDecodeError:
                # Fallback to HTML parsing if JSON parsing fails
                hotels = parse_hotel_data(response.text, location, check_in, check_out, guests, rooms)
                return hotels
        else:
            print(f"BrightData API error: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"Web scraping error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def calculate_hotel_scores(hotels: List[HotelOption]) -> List[HotelOption]:
    """Calculate comprehensive scores for hotel options"""
    
    if not hotels:
        return hotels
    
    # Hotel type reputation scores (0-100, higher is better)
    hotel_type_reputation = {
        "luxury": 95, "boutique": 85, "business": 80, "resort": 90,
        "budget": 60, "hostel": 50, "apartment": 75, "all": 75
    }
    
    # Extract prices for normalization
    prices = [h.price_per_night for h in hotels if h.price_per_night > 0]
    if prices:
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price if max_price > min_price else 1
    else:
        min_price = max_price = 150.0
        price_range = 1
    
    # Extract ratings for normalization
    ratings = [h.rating for h in hotels if h.rating > 0]
    if ratings:
        min_rating = min(ratings)
        max_rating = max(ratings)
        rating_range = max_rating - min_rating if max_rating > min_rating else 1
    else:
        min_rating = max_rating = 4.0
        rating_range = 1
    
    for hotel in hotels:
        # 1. PRICE SCORE (0-100, higher is better for lower prices)
        if hotel.price_per_night > 0 and price_range > 0:
            hotel.price_score = max(0, 100 - ((hotel.price_per_night - min_price) / price_range) * 100)
        else:
            hotel.price_score = 70  # Default
        
        # 2. QUALITY SCORE (0-100, higher is better for higher ratings)
        if hotel.rating > 0:
            if rating_range > 0:
                hotel.quality_score = max(0, 100 - ((hotel.rating - min_rating) / rating_range) * 100)
            else:
                hotel.quality_score = 100
        else:
            hotel.quality_score = 50  # Default
        
        # 3. LOCATION SCORE (0-100, higher is better for central locations)
        # This would be based on actual location analysis in a real implementation
        hotel.location_score = 80  # Default
        
        # 4. AMENITY SCORE (0-100, higher is better for more amenities)
        amenity_count = len(hotel.amenities)
        hotel.amenity_score = min(100, 50 + amenity_count * 5)
        
        # 5. REPUTATION SCORE (0-100, higher is better)
        hotel.reputation_score = hotel_type_reputation.get(hotel.hotel_type.lower(), 75)
        
        # 6. OVERALL SCORE (weighted average)
        # Weights: Quality 30%, Price 25%, Amenities 20%, Location 15%, Reputation 10%
        hotel.score = (
            hotel.quality_score * 0.30 +
            hotel.price_score * 0.25 +
            hotel.amenity_score * 0.20 +
            hotel.location_score * 0.15 +
            hotel.reputation_score * 0.10
        )
    
    # Sort hotels by overall score (highest first)
    hotels.sort(key=lambda x: x.score, reverse=True)
    
    return hotels

def parse_json_hotel_data(json_data: dict, location: str, check_in: str, check_out: str, guests: int, rooms: int) -> List[HotelOption]:
    """Parse hotel data from BrightData JSON response"""
    
    hotels = []
    
    print(f"Parsing JSON hotel data from BrightData response")
    
    try:
        # Extract hotel data from the JSON structure
        if "organic" in json_data:
            organic_results = json_data["organic"]
            print(f"Found {len(organic_results)} organic search results")
            
            for i, result in enumerate(organic_results[:10]):  # Limit to 10 hotels
                try:
                    # Extract hotel information
                    name = result.get("title", f"Hotel {i+1}")
                    description = result.get("description", "")
                    link = result.get("link", "")
                    
                    # Extract rating from description or extensions
                    rating = 4.0  # Default
                    if "extensions" in result:
                        for ext in result["extensions"]:
                            ext_text = ext.get("text", "")
                            rating_match = re.search(r'(\d+\.?\d*)\s*stars?', ext_text.lower())
                            if rating_match:
                                rating = float(rating_match.group(1))
                                break
                    
                    # Extract price from description
                    price_per_night = 150.0  # Default
                    price_match = re.search(r'\$(\d+)', description)
                    if price_match:
                        price_per_night = float(price_match.group(1))
                    
                    # Calculate total price (simplified)
                    nights = 3  # Default
                    total_price = price_per_night * nights * rooms
                    
                    # Generate booking URL
                    booking_url = f"https://www.google.com/search?q={quote_plus(f'{name} hotel {location} booking')}"
                    
                    # Create hotel object
                    hotel = HotelOption(
                        name=name,
                        hotel_type="Hotel",
                        price_per_night=price_per_night,
                        total_price=total_price,
                        rating=rating,
                        address=f"Address in {location}",
                        phone="(555) 000-0000",
                        website=link,
                        amenities=["WiFi", "Pool", "Gym", "Restaurant"],
                        description=description,
                        availability="Available",
                        booking_url=booking_url
                    )
                    hotels.append(hotel)
                    print(f"Created hotel {i+1}: {hotel.name} - ${hotel.price_per_night}/night")
                    
                except Exception as e:
                    print(f"Error parsing hotel item {i}: {e}")
                    continue
        
        if not hotels:
            print("No hotels found in JSON data")
        else:
            # Calculate scores for all hotels
            hotels = calculate_hotel_scores(hotels)
            print(f"Calculated scores for {len(hotels)} hotels")
        
    except Exception as e:
        print(f"Error parsing JSON hotel data: {e}")
        import traceback
        traceback.print_exc()
    
    return hotels

def parse_hotel_data(html_content: str, location: str, check_in: str, check_out: str, guests: int, rooms: int) -> List[HotelOption]:
    """Parse hotel data from scraped HTML content using BeautifulSoup"""
    
    hotels = []
    
    print(f"Parsing hotel data from HTML content ({len(html_content)} characters)")
    
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for hotel data in the HTML
        hotel_elements = soup.find_all(['div', 'article'], class_=re.compile(r'hotel|accommodation|property'))
        
        for i, element in enumerate(hotel_elements[:10]):
            try:
                name = element.get_text(strip=True)[:50] or f"Hotel {i+1}"
                
                # Generate booking URL
                booking_url = f"https://www.google.com/search?q={quote_plus(f'{name} hotel {location} booking')}"
                
                hotel = HotelOption(
                    name=name,
                    hotel_type="Hotel",
                    price_per_night=150.0,
                    total_price=450.0,
                    rating=4.0,
                    address=f"Address in {location}",
                    phone="(555) 000-0000",
                    website="",
                    amenities=["WiFi", "Pool"],
                    description="Hotel found via web scraping",
                    availability="Available",
                    booking_url=booking_url
                )
                hotels.append(hotel)
                
            except Exception as e:
                print(f"Error parsing hotel element {i}: {e}")
                continue
        
        if not hotels:
            print("No hotels found in HTML content")
        else:
            hotels = calculate_hotel_scores(hotels)
            print(f"Calculated scores for {len(hotels)} hotels")
        
    except Exception as e:
        print(f"Error parsing HTML content: {e}")
    
    return hotels

# Hotel search agent
async def search_hotels_agent(search_request: HotelSearchRequest) -> HotelSearchResponse:
    """Use AI agent to search for hotels"""
    
    search_id = f"hotel_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"Processing hotel search for {search_request.location}")
    
    # Get real data from web scraping
    hotels = await search_hotels_web(
        search_request.location,
        search_request.check_in,
        search_request.check_out,
        search_request.guests,
        search_request.rooms,
        search_request.hotel_type,
        search_request.price_range
    )
    
    # If no hotels found, return empty results
    if not hotels:
        print("No hotels found via web scraping")
        return HotelSearchResponse(
            search_id=search_id,
            location=search_request.location,
            check_in=search_request.check_in,
            check_out=search_request.check_out,
            options=[],
            total_results=0
        )
    
    return HotelSearchResponse(
        search_id=search_id,
        location=search_request.location,
        check_in=search_request.check_in,
        check_out=search_request.check_out,
        options=hotels,
        total_results=len(hotels)
    )

def create_mock_hotels(search_request: HotelSearchRequest) -> List[HotelOption]:
    """Create mock hotel data for testing"""
    
    # Calculate nights
    from datetime import datetime
    check_in_date = datetime.strptime(search_request.check_in, "%Y-%m-%d")
    check_out_date = datetime.strptime(search_request.check_out, "%Y-%m-%d")
    nights = (check_out_date - check_in_date).days
    
    mock_hotels = [
        HotelOption(
            name="Grand Plaza Hotel",
            hotel_type="luxury",
            price_per_night=299.99,
            total_price=299.99 * nights * search_request.rooms,
            rating=4.5,
            address=f"123 Main Street, {search_request.location}",
            phone="(555) 123-4567",
            website="https://grandplaza.com",
            amenities=["WiFi", "Pool", "Spa", "Restaurant", "Gym", "Concierge"],
            description="Luxury hotel in the heart of the city with premium amenities",
            availability="Available",
            booking_url=f"https://www.google.com/search?q={quote_plus(f'Grand Plaza Hotel {search_request.location} booking')}"
        ),
        HotelOption(
            name="Boutique Inn",
            hotel_type="boutique",
            price_per_night=189.99,
            total_price=189.99 * nights * search_request.rooms,
            rating=4.3,
            address=f"456 Arts District, {search_request.location}",
            phone="(555) 234-5678",
            website="https://boutiqueinn.com",
            amenities=["WiFi", "Restaurant", "Bar", "Room Service"],
            description="Charming boutique hotel with unique character and style",
            availability="Available",
            booking_url=f"https://www.google.com/search?q={quote_plus(f'Boutique Inn {search_request.location} booking')}"
        ),
        HotelOption(
            name="Budget Stay",
            hotel_type="budget",
            price_per_night=89.99,
            total_price=89.99 * nights * search_request.rooms,
            rating=3.8,
            address=f"789 Business District, {search_request.location}",
            phone="(555) 345-6789",
            website="https://budgetstay.com",
            amenities=["WiFi", "Breakfast"],
            description="Affordable accommodation with essential amenities",
            availability="Available",
            booking_url=f"https://www.google.com/search?q={quote_plus(f'Budget Stay {search_request.location} booking')}"
        )
    ]
    
    # Calculate scores for mock hotels
    return calculate_hotel_scores(mock_hotels)

# FastAPI app
app = FastAPI(title="Stay Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/search-hotels", response_model=HotelSearchResponse)
async def search_hotels(search_request: HotelSearchRequest):
    """Search for hotels"""
    try:
        result = await search_hotels_agent(search_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/book-hotel", response_model=BookingResponse)
async def book_hotel(booking_request: BookingRequest):
    """Book a hotel"""
    try:
        # This would integrate with hotel booking systems in a real implementation
        booking_id = f"hotel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return BookingResponse(
            booking_id=booking_id,
            status="confirmed",
            confirmation_code=f"HOT{booking_id[-6:].upper()}",
            hotel_details=HotelOption(
                name="Sample Hotel",
                hotel_type="Hotel",
                price_per_night=150.0,
                total_price=450.0,
                rating=4.0,
                address="123 Sample St",
                phone="(555) 000-0000",
                website="https://sample.com",
                amenities=["WiFi", "Pool"],
                description="Sample hotel for booking",
                availability="Available"
            ),
            total_cost=450.0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "stay-agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
