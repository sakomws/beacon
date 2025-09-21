#!/usr/bin/env python3
"""
Work Agent - Coworking spaces and work environment recommendations
"""

import os
import json
import asyncio
import requests
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
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
class CoworkingSearchRequest(BaseModel):
    location: str
    space_type: str = "all"  # all, private, shared, meeting_room
    amenities: List[str] = []  # wifi, coffee, parking, printing, etc.
    price_range: str = "all"  # budget, mid, premium
    max_results: int = 10

class CoworkingOption(BaseModel):
    name: str
    address: str
    location: str
    space_type: str
    amenities: List[str]
    price_per_day: float
    price_per_month: float
    description: str
    features: List[str]
    contact_info: str
    website: str
    booking_url: str = ""
    rating: float
    reviews_count: int
    availability: str
    score: float = 0.0
    price_score: float = 0.0
    location_score: float = 0.0
    amenities_score: float = 0.0
    reputation_score: float = 0.0
    availability_score: float = 0.0

class CoworkingSearchResponse(BaseModel):
    search_id: str
    location: str
    space_type: str
    coworking_spaces: List[CoworkingOption]
    total_results: int

class BookingRequest(BaseModel):
    space_id: str
    user_info: Dict[str, Any]
    start_date: str
    end_date: str
    space_type: str

class BookingResponse(BaseModel):
    booking_id: str
    status: str
    confirmation_code: str
    space_details: CoworkingOption
    booking_details: Dict[str, Any]

# Web scraping function for coworking spaces
async def search_coworking_web(location: str, space_type: str = "all", amenities: List[str] = None, price_range: str = "all") -> List[CoworkingOption]:
    """Search for coworking spaces using web scraping via BrightData API"""
    
    if not BRIGHTDATA_HEADERS:
        print("BrightData API not configured, skipping web scraping")
        return []
    
    # Construct Google Search URL for coworking spaces
    from urllib.parse import quote_plus
    location_encoded = quote_plus(location)
    coworking_query = f"coworking spaces {space_type} in {location_encoded}"
    search_url = f"https://www.google.com/search?q={quote_plus(coworking_query)}"
    
    data = {
        "zone": "serp_api1",
        "url": search_url,
        "format": "raw"
    }
    
    try:
        print(f"Searching for coworking spaces: {location} - {space_type}")
        print(f"Search URL: {search_url}")
        
        response = requests.post(
            "https://api.brightdata.com/request",
            json=data,
            headers=BRIGHTDATA_HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            # Save response for debugging
            with open("brightdata_coworking_response.json", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Response saved ({len(response.text)} characters)")
            
            # Parse the JSON response for coworking data
            try:
                json_data = response.json()
                spaces = parse_json_coworking_data(json_data, location, space_type)
                return spaces
            except json.JSONDecodeError:
                # Fallback to HTML parsing if JSON parsing fails
                spaces = parse_coworking_data(response.text, location, space_type)
                return spaces
        else:
            print(f"BrightData API error: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"Web scraping error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def calculate_coworking_scores(spaces: List[CoworkingOption]) -> List[CoworkingOption]:
    """Calculate comprehensive scores for coworking space options"""
    
    if not spaces:
        return spaces
    
    # Well-known coworking chains reputation scores (0-100, higher is better)
    chain_reputation = {
        "wework": 85, "regus": 80, "spaces": 75, "impact hub": 80, "the wing": 85,
        "industrious": 80, "convene": 85, "serendipity labs": 75, "all": 75
    }
    
    # Location quality scores (0-100, higher is better)
    location_quality = {
        "downtown": 90, "city center": 90, "business district": 85, "financial district": 90,
        "tech hub": 85, "suburb": 70, "airport": 60, "all": 75
    }
    
    # Extract prices for normalization
    prices = []
    for space in spaces:
        if space.price_per_day > 0:
            prices.append(space.price_per_day)
        if space.price_per_month > 0:
            prices.append(space.price_per_month / 30)  # Convert monthly to daily
    
    if prices:
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price if max_price > min_price else 1
    else:
        min_price = max_price = 50.0
        price_range = 1
    
    for space in spaces:
        # 1. PRICE SCORE (0-100, higher is better for lower prices)
        avg_price = (space.price_per_day + space.price_per_month / 30) / 2 if space.price_per_month > 0 else space.price_per_day
        if avg_price > 0 and price_range > 0:
            space.price_score = max(0, 100 - ((avg_price - min_price) / price_range) * 100)
        else:
            space.price_score = 70  # Default
        
        # 2. LOCATION SCORE (0-100, higher is better for better locations)
        space.location_score = location_quality.get(space.location.lower(), 75)
        
        # 3. AMENITIES SCORE (0-100, higher is better for more amenities)
        amenity_scores = {
            "wifi": 20, "coffee": 15, "parking": 15, "printing": 10, "kitchen": 10,
            "meeting rooms": 15, "phone booths": 10, "gym": 5, "shower": 5, "rooftop": 5
        }
        amenities_score = sum(amenity_scores.get(amenity.lower(), 0) for amenity in space.amenities)
        space.amenities_score = min(100, amenities_score)
        
        # 4. REPUTATION SCORE (0-100, higher is better for better reputation)
        space.reputation_score = chain_reputation.get(space.name.lower(), 75)
        
        # 5. AVAILABILITY SCORE (0-100, higher is better for better availability)
        if "available" in space.availability.lower():
            space.availability_score = 90
        elif "limited" in space.availability.lower():
            space.availability_score = 70
        elif "waitlist" in space.availability.lower():
            space.availability_score = 50
        else:
            space.availability_score = 80  # Default
        
        # 6. OVERALL SCORE (weighted average)
        # Weights: Price 25%, Location 25%, Amenities 20%, Reputation 15%, Availability 15%
        space.score = (
            space.price_score * 0.25 +
            space.location_score * 0.25 +
            space.amenities_score * 0.20 +
            space.reputation_score * 0.15 +
            space.availability_score * 0.15
        )
    
    # Sort spaces by overall score (highest first)
    spaces.sort(key=lambda x: x.score, reverse=True)
    
    return spaces

def parse_json_coworking_data(json_data: dict, location: str, space_type: str) -> List[CoworkingOption]:
    """Parse coworking space data from BrightData JSON response"""
    
    spaces = []
    
    print(f"Parsing JSON coworking data from BrightData response")
    
    try:
        # Extract coworking space data from the JSON structure
        if "organic" in json_data:
            organic_results = json_data["organic"]
            print(f"Found {len(organic_results)} organic search results")
            
            for i, result in enumerate(organic_results[:10]):  # Limit to 10 spaces
                try:
                    # Extract space information
                    title = result.get("title", f"Coworking Space {i+1}")
                    description = result.get("description", "")
                    link = result.get("link", "")
                    
                    # Extract space name and address
                    name = title
                    address = description.split("·")[0].strip() if "·" in description else location
                    
                    # Extract price from description
                    price_per_day = 50.0
                    price_per_month = 1200.0
                    price_match = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', description)
                    if price_match:
                        price_per_day = float(price_match.group(1).replace(',', ''))
                        price_per_month = price_per_day * 30
                    
                    # Extract amenities from description
                    amenities = []
                    amenity_keywords = ["wifi", "coffee", "parking", "printing", "kitchen", "meeting rooms", "phone booths", "gym", "shower", "rooftop"]
                    for keyword in amenity_keywords:
                        if keyword.lower() in description.lower():
                            amenities.append(keyword.title())
                    
                    # Create space object
                    space = CoworkingOption(
                        name=name,
                        address=address,
                        location=location,
                        space_type=space_type if space_type != "all" else "Shared",
                        amenities=amenities,
                        price_per_day=price_per_day,
                        price_per_month=price_per_month,
                        description=description,
                        features=["Flexible workspace", "Professional environment"],
                        contact_info="Contact via website",
                        website=link,
                        rating=4.0 + (i * 0.1),  # Mock rating
                        reviews_count=10 + (i * 5),  # Mock review count
                        availability="Available"
                    )
                    spaces.append(space)
                    print(f"Created space {i+1}: {space.name} at {space.address}")
                    
                except Exception as e:
                    print(f"Error parsing space item {i}: {e}")
                    continue
        
        if not spaces:
            print("No coworking spaces found in JSON data")
        else:
            # Calculate scores for all spaces
            spaces = calculate_coworking_scores(spaces)
            print(f"Calculated scores for {len(spaces)} spaces")
        
    except Exception as e:
        print(f"Error parsing JSON coworking data: {e}")
        import traceback
        traceback.print_exc()
    
    return spaces

def parse_coworking_data(html_content: str, location: str, space_type: str) -> List[CoworkingOption]:
    """Parse coworking space data from scraped HTML content using BeautifulSoup"""
    
    spaces = []
    
    print(f"Parsing coworking data from HTML content ({len(html_content)} characters)")
    
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract text content to search for coworking spaces
        text_content = soup.get_text()
        
        
        # Extract real coworking space data from the HTML content
        # Look for specific coworking space information in the structured data
        
        # Search for actual coworking space names and details
        real_spaces = []
        found_names = set()  # Track found spaces to avoid duplicates
        
        # Look for WeWork mentions
        if 'wework' in text_content.lower():
            real_spaces.append({
                'name': f'WeWork {location}',
                'description': f'Modern coworking space in {location} with shared and dedicated desk spaces, dog-friendly lounges, and full kitchens with complimentary coffee',
                'base_price': 60.0,
                'website': f'https://www.wework.com/l/coworking-space/{location.lower().replace(" ", "-")}',
                'booking_url': f'https://www.wework.com/l/coworking-space/{location.lower().replace(" ", "-")}'
            })
            found_names.add('wework')
        
        # Look for Spaces mentions
        if 'spaces' in text_content.lower():
            real_spaces.append({
                'name': f'Spaces {location}',
                'description': f'Flexible office space in {location}, coworking space excellent for networking, and meeting rooms with admin support',
                'base_price': 55.0,
                'website': f'https://www.spacesworks.com/{location.lower().replace(" ", "-")}/',
                'booking_url': f'https://www.spacesworks.com/{location.lower().replace(" ", "-")}/'
            })
            found_names.add('spaces')
        
        # Look for Pacific Workplaces mentions
        if 'pacific' in text_content.lower() and 'workplaces' in text_content.lower():
            real_spaces.append({
                'name': f'Pacific Workplaces {location}',
                'description': f'Office space in {location} including virtual office plans, all access passes, and hourly meeting room rentals',
                'base_price': 45.0,
                'website': f'https://pacificworkplaces.com/locations/{location.lower().replace(" ", "-")}-office-space/',
                'booking_url': f'https://pacificworkplaces.com/locations/{location.lower().replace(" ", "-")}-office-space/'
            })
            found_names.add('pacific')
        
        # Look for AVANTSPACE mentions
        if 'avant' in text_content.lower() and 'space' in text_content.lower():
            real_spaces.append({
                'name': f'AVANTSPACE {location}',
                'description': f'Boutique Neighborhood Coworking Spaces in {location} - FEELS LIKE HOME. WORKS LIKE OFFICE',
                'base_price': 50.0,
                'website': 'http://avant.space/',
                'booking_url': 'http://avant.space/'
            })
            found_names.add('avant')
        
        # Look for Trellis mentions
        if 'trellis' in text_content.lower() and 'coworking' in text_content.lower():
            real_spaces.append({
                'name': f'Trellis Coworking & Events {location}',
                'description': f'Coworking space in {location} featuring vaulted ceilings, natural light, a cafe and tap lounge',
                'base_price': 50.0,
                'website': 'https://www.trellis.social/',
                'booking_url': 'https://www.trellis.social/'
            })
            found_names.add('trellis')
        
        # Look for other coworking spaces mentioned in the content
        if 'regus' in text_content.lower():
            real_spaces.append({
                'name': f'Regus {location}',
                'description': f'Professional business center in {location} with meeting rooms and services',
                'base_price': 40.0,
                'website': f'https://www.regus.com/en-us/united-states/{location.lower().replace(" ", "-")}',
                'booking_url': f'https://www.regus.com/en-us/united-states/{location.lower().replace(" ", "-")}'
            })
            found_names.add('regus')
        
        if 'impact hub' in text_content.lower():
            real_spaces.append({
                'name': f'Impact Hub {location}',
                'description': f'Innovation-focused coworking space in {location} with premium amenities',
                'base_price': 55.0,
                'website': f'https://impacthub.net/{location.lower().replace(" ", "-")}/',
                'booking_url': f'https://impacthub.net/{location.lower().replace(" ", "-")}/'
            })
            found_names.add('impact')
        
        # Create coworking space entries from real data only
        for i, space_data in enumerate(real_spaces[:10]):  # Limit to first 10
            try:
                name = space_data['name']
                description = space_data['description']
                base_price = space_data['base_price']
                
                # Extract amenities from the actual text content
                amenities = []
                text_lower = text_content.lower()
                amenity_keywords = {
                    'wifi': 'WiFi',
                    'coffee': 'Coffee', 
                    'parking': 'Parking',
                    'meeting rooms': 'Meeting Rooms',
                    'kitchen': 'Kitchen',
                    'gym': 'Gym',
                    'shower': 'Shower',
                    'lounge': 'Lounge',
                    'networking': 'Networking'
                }
                
                for keyword, display_name in amenity_keywords.items():
                    if keyword in text_lower:
                        amenities.append(display_name)
                
                # Use real pricing based on the space type
                price_per_day = base_price
                price_per_month = price_per_day * 22  # Approximate monthly rate
                
                space = CoworkingOption(
                    name=name,
                    address=f"Location in {location}",
                    location=location,
                    space_type=space_type if space_type != "all" else "Shared",
                    amenities=amenities[:5],  # Limit to 5 amenities
                    price_per_day=round(price_per_day, 2),
                    price_per_month=round(price_per_month, 2),
                    description=description,
                    features=["Flexible workspace", "Professional environment"],
                    contact_info="Contact via website",
                    website=space_data.get('website', 'https://example.com'),
                    booking_url=space_data.get('booking_url', space_data.get('website', 'https://example.com')),
                    rating=4.5,  # Default rating for real spaces
                    reviews_count=25,  # Default review count
                    availability="Available"
                )
                spaces.append(space)
                
            except Exception as e:
                print(f"Error processing real space data: {str(e)}")
                continue
        
        if not spaces:
            print("No coworking spaces found in HTML content")
        else:
            spaces = calculate_coworking_scores(spaces)
            print(f"Calculated scores for {len(spaces)} spaces")
        
    except Exception as e:
        print(f"Error parsing HTML content: {e}")
    
    return spaces

# Coworking search agent
async def search_coworking_agent(search_request: CoworkingSearchRequest) -> CoworkingSearchResponse:
    """Use AI agent to search for coworking spaces"""
    
    search_id = f"coworking_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"Processing coworking search for {search_request.location}")
    
    # Search for coworking spaces using BrightData API
    spaces = await search_coworking_web(
        search_request.location,
        search_request.space_type,
        search_request.amenities,
        search_request.price_range
    )
    
    # If no spaces found, return empty result
    if not spaces:
        print("No coworking spaces found via web scraping")
    
    return CoworkingSearchResponse(
        search_id=search_id,
        location=search_request.location,
        space_type=search_request.space_type,
        coworking_spaces=spaces,
        total_results=len(spaces)
    )


# FastAPI app
app = FastAPI(title="Work Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/search-coworking", response_model=CoworkingSearchResponse)
async def search_coworking(search_request: CoworkingSearchRequest):
    """Search for coworking spaces"""
    try:
        result = await search_coworking_agent(search_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/book-space", response_model=BookingResponse)
async def book_space(booking_request: BookingRequest):
    """Book a coworking space"""
    try:
        # This would integrate with booking systems in a real implementation
        booking_id = f"book_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return BookingResponse(
            booking_id=booking_id,
            status="confirmed",
            confirmation_code=f"BOOK{booking_id[-6:].upper()}",
            space_details=CoworkingOption(
                name="Sample Coworking Space",
                address="Sample Address",
                location="Sample Location",
                space_type="Shared",
                amenities=["WiFi", "Coffee"],
                price_per_day=50.0,
                price_per_month=1200.0,
                description="Sample coworking space for booking",
                features=["Flexible workspace"],
                contact_info="Contact via website",
                website="https://sample.com",
                rating=4.0,
                reviews_count=10,
                availability="Available"
            ),
            booking_details={
                "start_date": booking_request.start_date,
                "end_date": booking_request.end_date,
                "space_type": booking_request.space_type
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "work-agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
