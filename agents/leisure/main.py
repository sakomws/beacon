#!/usr/bin/env python3
"""
Leisure Agent - Activities and entertainment recommendations
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
class ActivitySearchRequest(BaseModel):
    location: str
    activity_type: str = "all"
    duration: str = "all"
    price_range: str = "all"
    max_results: int = 10

class ActivityOption(BaseModel):
    name: str
    activity_type: str
    duration: str
    price: float
    rating: float
    address: str
    description: str
    website: str
    availability: str
    booking_url: str = ""
    score: float = 0.0
    price_score: float = 0.0
    quality_score: float = 0.0
    location_score: float = 0.0
    popularity_score: float = 0.0
    accessibility_score: float = 0.0

class ActivitySearchResponse(BaseModel):
    search_id: str
    location: str
    activity_type: str
    options: List[ActivityOption]
    total_results: int

class BookingRequest(BaseModel):
    activity_id: str
    date: str
    time: str
    participants: int
    contact_info: Dict[str, Any]

class BookingResponse(BaseModel):
    booking_id: str
    status: str
    confirmation_code: str
    activity_details: ActivityOption

# Web scraping function for activity search
async def search_activities_web(location: str, activity_type: str = "all", duration: str = "all", price_range: str = "all") -> List[ActivityOption]:
    """Search for activities using web scraping via BrightData API"""
    
    if not BRIGHTDATA_HEADERS:
        print("BrightData API not configured, skipping web scraping")
        return []
    
    # Construct Google Search URL for activities
    location_encoded = quote_plus(location)
    activity_query = f"{activity_type} activities" if activity_type != "all" else "activities"
    full_query = f"{activity_query} in {location_encoded}"
    search_url = f"https://www.google.com/search?q={quote_plus(full_query)}&brd_json=1"
    
    data = {
        "zone": "serp_api1",
        "url": search_url,
        "format": "raw"
    }
    
    try:
        print(f"Searching for activities: {location} - {activity_type}")
        print(f"Search URL: {search_url}")
        
        response = requests.post(
            "https://api.brightdata.com/request",
            json=data,
            headers=BRIGHTDATA_HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            # Save response for debugging
            with open("brightdata_activities_response.json", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Response saved ({len(response.text)} characters)")
            
            # Parse the JSON response for activity data
            try:
                json_data = response.json()
                activities = parse_json_activity_data(json_data, location, activity_type)
                return activities
            except json.JSONDecodeError:
                # Fallback to HTML parsing if JSON parsing fails
                activities = parse_activity_data(response.text, location, activity_type)
                return activities
        else:
            print(f"BrightData API error: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"Web scraping error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def calculate_activity_scores(activities: List[ActivityOption]) -> List[ActivityOption]:
    """Calculate comprehensive scores for activity options"""
    
    if not activities:
        return activities
    
    # Activity type popularity scores (0-100, higher is better)
    activity_popularity = {
        "outdoor": 85, "cultural": 80, "entertainment": 75, "sports": 70,
        "tours": 90, "nightlife": 65, "shopping": 60, "wellness": 75,
        "all": 75
    }
    
    # Extract prices for normalization
    prices = [a.price for a in activities if a.price > 0]
    if prices:
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price if max_price > min_price else 1
    else:
        min_price = max_price = 50.0
        price_range = 1
    
    # Extract ratings for normalization
    ratings = [a.rating for a in activities if a.rating > 0]
    if ratings:
        min_rating = min(ratings)
        max_rating = max(ratings)
        rating_range = max_rating - min_rating if max_rating > min_rating else 1
    else:
        min_rating = max_rating = 4.0
        rating_range = 1
    
    for activity in activities:
        # 1. PRICE SCORE (0-100, higher is better for lower prices)
        if activity.price > 0 and price_range > 0:
            activity.price_score = max(0, 100 - ((activity.price - min_price) / price_range) * 100)
        else:
            activity.price_score = 70  # Default
        
        # 2. QUALITY SCORE (0-100, higher is better for higher ratings)
        if activity.rating > 0:
            if rating_range > 0:
                activity.quality_score = max(0, 100 - ((activity.rating - min_rating) / rating_range) * 100)
            else:
                activity.quality_score = 100
        else:
            activity.quality_score = 50  # Default
        
        # 3. LOCATION SCORE (0-100, higher is better for central locations)
        activity.location_score = 80  # Default
        
        # 4. POPULARITY SCORE (0-100, higher is better)
        activity.popularity_score = activity_popularity.get(activity.activity_type.lower(), 70)
        
        # 5. ACCESSIBILITY SCORE (0-100, higher is better)
        # This would be based on actual accessibility features in a real implementation
        activity.accessibility_score = 85  # Default
        
        # 6. OVERALL SCORE (weighted average)
        # Weights: Quality 30%, Price 25%, Popularity 20%, Location 15%, Accessibility 10%
        activity.score = (
            activity.quality_score * 0.30 +
            activity.price_score * 0.25 +
            activity.popularity_score * 0.20 +
            activity.location_score * 0.15 +
            activity.accessibility_score * 0.10
        )
    
    # Sort activities by overall score (highest first)
    activities.sort(key=lambda x: x.score, reverse=True)
    
    return activities

def parse_json_activity_data(json_data: dict, location: str, activity_type: str) -> List[ActivityOption]:
    """Parse activity data from BrightData JSON response"""
    
    activities = []
    
    print(f"Parsing JSON activity data from BrightData response")
    
    try:
        # Extract activity data from the JSON structure
        if "organic" in json_data:
            organic_results = json_data["organic"]
            print(f"Found {len(organic_results)} organic search results")
            
            for i, result in enumerate(organic_results[:10]):  # Limit to 10 activities
                try:
                    # Extract activity information
                    name = result.get("title", f"Activity {i+1}")
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
                    price = 50.0  # Default
                    price_match = re.search(r'\$(\d+)', description)
                    if price_match:
                        price = float(price_match.group(1))
                    
                    # Generate booking URL
                    booking_url = f"https://www.google.com/search?q={quote_plus(f'{name} {location} booking')}"
                    
                    # Create activity object
                    activity = ActivityOption(
                        name=name,
                        activity_type=activity_type if activity_type != "all" else "Entertainment",
                        duration="2-3 hours",
                        price=price,
                        rating=rating,
                        address=f"Location in {location}",
                        description=description,
                        website=link,
                        availability="Available",
                        booking_url=booking_url
                    )
                    activities.append(activity)
                    print(f"Created activity {i+1}: {activity.name} - ${activity.price}")
                    
                except Exception as e:
                    print(f"Error parsing activity item {i}: {e}")
                    continue
        
        if not activities:
            print("No activities found in JSON data")
        else:
            # Calculate scores for all activities
            activities = calculate_activity_scores(activities)
            print(f"Calculated scores for {len(activities)} activities")
        
    except Exception as e:
        print(f"Error parsing JSON activity data: {e}")
        import traceback
        traceback.print_exc()
    
    return activities

def parse_activity_data(html_content: str, location: str, activity_type: str) -> List[ActivityOption]:
    """Parse activity data from scraped HTML content using BeautifulSoup"""
    
    activities = []
    
    print(f"Parsing activity data from HTML content ({len(html_content)} characters)")
    
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for activity data in the HTML
        activity_elements = soup.find_all(['div', 'article'], class_=re.compile(r'activity|entertainment|tour'))
        
        for i, element in enumerate(activity_elements[:10]):
            try:
                name = element.get_text(strip=True)[:50] or f"Activity {i+1}"
                
                # Generate booking URL
                booking_url = f"https://www.google.com/search?q={quote_plus(f'{name} {location} booking')}"
                
                activity = ActivityOption(
                    name=name,
                    activity_type=activity_type if activity_type != "all" else "Entertainment",
                    duration="2-3 hours",
                    price=50.0,
                    rating=4.0,
                    address=f"Location in {location}",
                    description="Activity found via web scraping",
                    website="",
                    availability="Available",
                    booking_url=booking_url
                )
                activities.append(activity)
                
            except Exception as e:
                print(f"Error parsing activity element {i}: {e}")
                continue
        
        if not activities:
            print("No activities found in HTML content")
        else:
            activities = calculate_activity_scores(activities)
            print(f"Calculated scores for {len(activities)} activities")
        
    except Exception as e:
        print(f"Error parsing HTML content: {e}")
    
    return activities

# Activity search agent
async def search_activities_agent(search_request: ActivitySearchRequest) -> ActivitySearchResponse:
    """Use AI agent to search for activities"""
    
    search_id = f"activity_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"Processing activity search for {search_request.location}")
    
    # Get real data from web scraping
    activities = await search_activities_web(
        search_request.location,
        search_request.activity_type,
        search_request.duration,
        search_request.price_range
    )
    
    # If no activities found, return empty results
    if not activities:
        print("No activities found via web scraping")
        return ActivitySearchResponse(
            search_id=search_id,
            location=search_request.location,
            activity_type=search_request.activity_type,
            options=[],
            total_results=0
        )
    
    return ActivitySearchResponse(
        search_id=search_id,
        location=search_request.location,
        activity_type=search_request.activity_type,
        options=activities,
        total_results=len(activities)
    )

def create_mock_activities(search_request: ActivitySearchRequest) -> List[ActivityOption]:
    """Create mock activity data for testing"""
    
    mock_activities = [
        ActivityOption(
            name="City Walking Tour",
            activity_type="tours",
            duration="2-3 hours",
            price=25.0,
            rating=4.5,
            address=f"Downtown {search_request.location}",
            description="Explore the city's historic landmarks and hidden gems",
            website="https://citytours.com",
            availability="Daily at 10 AM and 2 PM",
            booking_url=f"https://www.google.com/search?q={quote_plus(f'City Walking Tour {search_request.location} booking')}"
        ),
        ActivityOption(
            name="Art Gallery Visit",
            activity_type="cultural",
            duration="1-2 hours",
            price=15.0,
            rating=4.3,
            address=f"Arts District, {search_request.location}",
            description="Contemporary art exhibitions and local artists",
            website="https://artgallery.com",
            availability="Tuesday-Sunday, 10 AM - 6 PM",
            booking_url=f"https://www.google.com/search?q={quote_plus(f'Art Gallery Visit {search_request.location} booking')}"
        ),
        ActivityOption(
            name="Hiking Adventure",
            activity_type="outdoor",
            duration="4-6 hours",
            price=40.0,
            rating=4.7,
            address=f"Mountain Trail, {search_request.location}",
            description="Scenic hiking trails with breathtaking views",
            website="https://hikingadventures.com",
            availability="Weekends, 8 AM start",
            booking_url=f"https://www.google.com/search?q={quote_plus(f'Hiking Adventure {search_request.location} booking')}"
        )
    ]
    
    # Calculate scores for mock activities
    return calculate_activity_scores(mock_activities)

# FastAPI app
app = FastAPI(title="Leisure Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/search-activities", response_model=ActivitySearchResponse)
async def search_activities(search_request: ActivitySearchRequest):
    """Search for activities"""
    try:
        result = await search_activities_agent(search_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/book-activity", response_model=BookingResponse)
async def book_activity(booking_request: BookingRequest):
    """Book an activity"""
    try:
        # This would integrate with booking systems in a real implementation
        booking_id = f"book_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return BookingResponse(
            booking_id=booking_id,
            status="confirmed",
            confirmation_code=f"BOOK{booking_id[-6:].upper()}",
            activity_details=ActivityOption(
                name="Sample Activity",
                activity_type="Entertainment",
                duration="2 hours",
                price=30.0,
                rating=4.0,
                address="123 Sample St",
                description="Sample activity for booking",
                website="https://sample.com",
                availability="Available"
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "leisure-agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
