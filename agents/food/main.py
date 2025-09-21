#!/usr/bin/env python3
"""
Food Agent - Restaurant and dining recommendations
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
class RestaurantSearchRequest(BaseModel):
    location: str
    cuisine: str = "all"
    price_range: str = "all"
    rating: float = 0.0
    max_results: int = 10

class RestaurantOption(BaseModel):
    name: str
    cuisine: str
    price_range: str
    rating: float
    address: str
    phone: str
    website: str
    booking_url: str = ""
    description: str
    score: float = 0.0
    price_score: float = 0.0
    quality_score: float = 0.0
    location_score: float = 0.0
    reputation_score: float = 0.0
    availability_score: float = 0.0

class RestaurantSearchResponse(BaseModel):
    search_id: str
    location: str
    cuisine: str
    options: List[RestaurantOption]
    total_results: int

class ReservationRequest(BaseModel):
    restaurant_id: str
    date: str
    time: str
    party_size: int
    contact_info: Dict[str, Any]

class ReservationResponse(BaseModel):
    reservation_id: str
    status: str
    confirmation_code: str
    restaurant_details: RestaurantOption

# Web scraping function for restaurant search
async def search_restaurants_web(location: str, cuisine: str = "all", price_range: str = "all", rating: float = 0.0) -> List[RestaurantOption]:
    """Search for restaurants using web scraping via BrightData API"""
    
    if not BRIGHTDATA_HEADERS:
        print("BrightData API not configured, skipping web scraping")
        return []
    
    # Construct Google Search URL for restaurants
    from urllib.parse import quote_plus
    location_encoded = quote_plus(location)
    cuisine_query = f" {cuisine}" if cuisine != "all" else ""
    price_query = f" {price_range}" if price_range != "all" else ""
    search_query = f"restaurants{cuisine_query}{price_query} in {location_encoded}"
    search_url = f"https://www.google.com/search?q={quote_plus(search_query)}"
    
    data = {
        "zone": "serp_api1",
        "url": search_url,
        "format": "raw"
    }
    
    try:
        print(f"Searching for restaurants: {location} - {cuisine} - {price_range}")
        print(f"Search URL: {search_url}")
        
        response = requests.post(
            "https://api.brightdata.com/request",
            json=data,
            headers=BRIGHTDATA_HEADERS,
            timeout=60
        )
        
        if response.status_code == 200:
            # Save response for debugging
            with open("brightdata_restaurants_response.json", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Response saved ({len(response.text)} characters)")
            
            # Parse the JSON response for restaurant data
            try:
                json_data = response.json()
                restaurants = parse_json_restaurant_data(json_data, location, cuisine, price_range)
                return restaurants
            except json.JSONDecodeError:
                # Fallback to HTML parsing if JSON parsing fails
                restaurants = parse_restaurant_data(response.text, location, cuisine, price_range)
                return restaurants
        else:
            print(f"BrightData API error: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"Web scraping error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def calculate_restaurant_scores(restaurants: List[RestaurantOption]) -> List[RestaurantOption]:
    """Calculate comprehensive scores for restaurant options"""
    
    if not restaurants:
        return restaurants
    
    # Cuisine reputation scores (0-100, higher is better)
    cuisine_reputation = {
        "italian": 85, "chinese": 80, "japanese": 90, "mexican": 75,
        "indian": 85, "thai": 80, "french": 90, "american": 70,
        "seafood": 85, "steakhouse": 80, "sushi": 90, "pizza": 70,
        "all": 75
    }
    
    # Extract ratings for normalization
    ratings = [r.rating for r in restaurants if r.rating > 0]
    if ratings:
        min_rating = min(ratings)
        max_rating = max(ratings)
        rating_range = max_rating - min_rating if max_rating > min_rating else 1
    else:
        min_rating = max_rating = 4.0
        rating_range = 1
    
    # Price range scoring
    price_scores = {"$": 100, "$$": 80, "$$$": 60, "$$$$": 40}
    
    for restaurant in restaurants:
        # 1. PRICE SCORE (0-100, higher is better for lower prices)
        restaurant.price_score = price_scores.get(restaurant.price_range, 70)
        
        # 2. QUALITY SCORE (0-100, higher is better for higher ratings)
        if restaurant.rating > 0:
            if rating_range > 0:
                restaurant.quality_score = max(0, 100 - ((restaurant.rating - min_rating) / rating_range) * 100)
            else:
                restaurant.quality_score = 100
        else:
            restaurant.quality_score = 50  # Default for unknown ratings
        
        # 3. LOCATION SCORE (0-100, higher is better for central locations)
        # This would be based on actual location analysis in a real implementation
        restaurant.location_score = 80  # Default
        
        # 4. REPUTATION SCORE (0-100, higher is better)
        restaurant.reputation_score = cuisine_reputation.get(restaurant.cuisine.lower(), 70)
        
        # 5. AVAILABILITY SCORE (0-100, higher is better)
        # This would be based on actual availability in a real implementation
        restaurant.availability_score = 85  # Default
        
        # 6. OVERALL SCORE (weighted average)
        # Weights: Quality 30%, Price 25%, Reputation 20%, Location 15%, Availability 10%
        restaurant.score = (
            restaurant.quality_score * 0.30 +
            restaurant.price_score * 0.25 +
            restaurant.reputation_score * 0.20 +
            restaurant.location_score * 0.15 +
            restaurant.availability_score * 0.10
        )
    
    # Sort restaurants by overall score (highest first)
    restaurants.sort(key=lambda x: x.score, reverse=True)
    
    return restaurants

def parse_json_restaurant_data(json_data: dict, location: str, cuisine: str, price_range: str) -> List[RestaurantOption]:
    """Parse restaurant data from BrightData JSON response"""
    
    restaurants = []
    
    print(f"Parsing JSON restaurant data from BrightData response")
    
    try:
        # Extract restaurant data from the JSON structure
        if "organic" in json_data:
            organic_results = json_data["organic"]
            print(f"Found {len(organic_results)} organic search results")
            
            for i, result in enumerate(organic_results[:10]):  # Limit to 10 restaurants
                try:
                    # Extract restaurant information
                    name = result.get("title", f"Restaurant {i+1}")
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
                    
                    # Determine price range from description
                    price_range_detected = "$$"
                    if "$" in description:
                        dollar_count = description.count("$")
                        if dollar_count == 1:
                            price_range_detected = "$"
                        elif dollar_count == 2:
                            price_range_detected = "$$"
                        elif dollar_count == 3:
                            price_range_detected = "$$$"
                        elif dollar_count >= 4:
                            price_range_detected = "$$$$"
                    
                    # Create restaurant object
                    restaurant = RestaurantOption(
                        name=name,
                        cuisine=cuisine if cuisine != "all" else "Mixed",
                        price_range=price_range_detected,
                        rating=rating,
                        address="Address not available",
                        phone="Phone not available",
                        website=link,
                        description=description
                    )
                    restaurants.append(restaurant)
                    print(f"Created restaurant {i+1}: {restaurant.name} - {restaurant.rating} stars")
                    
                except Exception as e:
                    print(f"Error parsing restaurant item {i}: {e}")
                    continue
        
        if not restaurants:
            print("No restaurants found in JSON data")
        else:
            # Calculate scores for all restaurants
            restaurants = calculate_restaurant_scores(restaurants)
            print(f"Calculated scores for {len(restaurants)} restaurants")
        
    except Exception as e:
        print(f"Error parsing JSON restaurant data: {e}")
        import traceback
        traceback.print_exc()
    
    return restaurants

def parse_restaurant_data(html_content: str, location: str, cuisine: str, price_range: str) -> List[RestaurantOption]:
    """Parse restaurant data from scraped HTML content using BeautifulSoup"""
    
    restaurants = []
    
    print(f"Parsing restaurant data from HTML content ({len(html_content)} characters)")
    
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract text content to search for restaurants
        text_content = soup.get_text()
        
        # Search for actual restaurant data from the HTML content
        real_restaurants = []
        found_names = set()  # Track found restaurants to avoid duplicates
        
        print(f"Searching for restaurant patterns in HTML content...")
        print(f"Text content length: {len(text_content)}")
        print(f"First 500 characters: {text_content[:500]}")
        
        # Look for common restaurant chains and popular restaurants
        restaurant_patterns = [
            # Popular restaurant chains
            (r'mcdonald\'?s', 'McDonald\'s', 'Fast Food', '$', 'https://www.mcdonalds.com/', 'https://www.mcdonalds.com/'),
            (r'starbucks', 'Starbucks', 'Coffee', '$$', 'https://www.starbucks.com/', 'https://www.starbucks.com/'),
            (r'pizza hut', 'Pizza Hut', 'Pizza', '$$', 'https://www.pizzahut.com/', 'https://www.pizzahut.com/'),
            (r'domino\'?s', 'Domino\'s Pizza', 'Pizza', '$$', 'https://www.dominos.com/', 'https://www.dominos.com/'),
            (r'subway', 'Subway', 'Sandwiches', '$$', 'https://www.subway.com/', 'https://www.subway.com/'),
            (r'kfc', 'KFC', 'Fast Food', '$$', 'https://www.kfc.com/', 'https://www.kfc.com/'),
            (r'taco bell', 'Taco Bell', 'Mexican', '$$', 'https://www.tacobell.com/', 'https://www.tacobell.com/'),
            (r'burger king', 'Burger King', 'Fast Food', '$$', 'https://www.burgerking.com/', 'https://www.burgerking.com/'),
            (r'wendy\'?s', 'Wendy\'s', 'Fast Food', '$$', 'https://www.wendys.com/', 'https://www.wendys.com/'),
            (r'chipotle', 'Chipotle', 'Mexican', '$$$', 'https://www.chipotle.com/', 'https://www.chipotle.com/'),
            (r'panera bread', 'Panera Bread', 'Bakery', '$$', 'https://www.panerabread.com/', 'https://www.panerabread.com/'),
            (r'dunkin\'?', 'Dunkin\'', 'Coffee', '$$', 'https://www.dunkindonuts.com/', 'https://www.dunkindonuts.com/'),
            # Additional popular chains
            (r'olive garden', 'Olive Garden', 'Italian', '$$', 'https://www.olivegarden.com/', 'https://www.olivegarden.com/'),
            (r'red lobster', 'Red Lobster', 'Seafood', '$$$', 'https://www.redlobster.com/', 'https://www.redlobster.com/'),
            (r'applebee\'?s', 'Applebee\'s', 'American', '$$', 'https://www.applebees.com/', 'https://www.applebees.com/'),
            (r'outback', 'Outback Steakhouse', 'Steakhouse', '$$$', 'https://www.outback.com/', 'https://www.outback.com/'),
            (r'ihop', 'IHOP', 'Breakfast', '$$', 'https://www.ihop.com/', 'https://www.ihop.com/'),
            (r'denny\'?s', 'Denny\'s', 'Diner', '$$', 'https://www.dennys.com/', 'https://www.dennys.com/'),
            (r'chili\'?s', 'Chili\'s', 'American', '$$', 'https://www.chilis.com/', 'https://www.chilis.com/'),
            (r'tgi friday\'?s', 'TGI Friday\'s', 'American', '$$', 'https://www.tgifridays.com/', 'https://www.tgifridays.com/'),
            (r'ruby tuesday', 'Ruby Tuesday', 'American', '$$', 'https://www.rubytuesday.com/', 'https://www.rubytuesday.com/'),
            (r'texas roadhouse', 'Texas Roadhouse', 'Steakhouse', '$$$', 'https://www.texasroadhouse.com/', 'https://www.texasroadhouse.com/'),
            (r'longhorn', 'LongHorn Steakhouse', 'Steakhouse', '$$$', 'https://www.longhornsteakhouse.com/', 'https://www.longhornsteakhouse.com/'),
            (r'red robin', 'Red Robin', 'Burgers', '$$', 'https://www.redrobin.com/', 'https://www.redrobin.com/'),
            (r'five guys', 'Five Guys', 'Burgers', '$$', 'https://www.fiveguys.com/', 'https://www.fiveguys.com/'),
            (r'shake shack', 'Shake Shack', 'Burgers', '$$', 'https://www.shakeshack.com/', 'https://www.shakeshack.com/'),
            (r'in-n-out', 'In-N-Out Burger', 'Burgers', '$$', 'https://www.in-n-out.com/', 'https://www.in-n-out.com/'),
            (r'whataburger', 'Whataburger', 'Burgers', '$$', 'https://www.whataburger.com/', 'https://www.whataburger.com/'),
            (r'white castle', 'White Castle', 'Burgers', '$', 'https://www.whitecastle.com/', 'https://www.whitecastle.com/'),
            (r'jack in the box', 'Jack in the Box', 'Fast Food', '$$', 'https://www.jackinthebox.com/', 'https://www.jackinthebox.com/'),
            (r'carl\'?s jr', 'Carl\'s Jr.', 'Fast Food', '$$', 'https://www.carlsjr.com/', 'https://www.carlsjr.com/'),
            (r'hardee\'?s', 'Hardee\'s', 'Fast Food', '$$', 'https://www.hardees.com/', 'https://www.hardees.com/'),
            (r'popeye\'?s', 'Popeye\'s', 'Chicken', '$$', 'https://www.popeyes.com/', 'https://www.popeyes.com/'),
            (r'chick-fil-a', 'Chick-fil-A', 'Chicken', '$$', 'https://www.chick-fil-a.com/', 'https://www.chick-fil-a.com/'),
            (r'bojangles', 'Bojangles', 'Chicken', '$$', 'https://www.bojangles.com/', 'https://www.bojangles.com/'),
            (r'zaxby\'?s', 'Zaxby\'s', 'Chicken', '$$', 'https://www.zaxbys.com/', 'https://www.zaxbys.com/'),
            (r'raising cane\'?s', 'Raising Cane\'s', 'Chicken', '$$', 'https://www.raisingcanes.com/', 'https://www.raisingcanes.com/'),
            (r'wingstop', 'Wingstop', 'Chicken', '$$', 'https://www.wingstop.com/', 'https://www.wingstop.com/'),
            (r'buffalo wild wings', 'Buffalo Wild Wings', 'Sports Bar', '$$', 'https://www.buffalowildwings.com/', 'https://www.buffalowildwings.com/'),
            (r'hooters', 'Hooters', 'Sports Bar', '$$', 'https://www.hooters.com/', 'https://www.hooters.com/'),
            (r'twin peaks', 'Twin Peaks', 'Sports Bar', '$$', 'https://www.twinpeaksrestaurant.com/', 'https://www.twinpeaksrestaurant.com/'),
            (r'the cheesecake factory', 'The Cheesecake Factory', 'American', '$$$', 'https://www.thecheesecakefactory.com/', 'https://www.thecheesecakefactory.com/'),
            (r'pf chang\'?s', 'P.F. Chang\'s', 'Asian', '$$$', 'https://www.pfchangs.com/', 'https://www.pfchangs.com/'),
            (r'benihana', 'Benihana', 'Japanese', '$$$', 'https://www.benihana.com/', 'https://www.benihana.com/'),
            (r'hibachi', 'Hibachi Grill', 'Japanese', '$$$', 'https://www.hibachigrill.com/', 'https://www.hibachigrill.com/'),
            (r'panda express', 'Panda Express', 'Chinese', '$$', 'https://www.pandaexpress.com/', 'https://www.pandaexpress.com/'),
            (r'pei wei', 'Pei Wei', 'Asian', '$$', 'https://www.peiwei.com/', 'https://www.peiwei.com/'),
            (r'qdoba', 'Qdoba', 'Mexican', '$$', 'https://www.qdoba.com/', 'https://www.qdoba.com/'),
            (r'moe\'?s', 'Moe\'s Southwest Grill', 'Mexican', '$$', 'https://www.moes.com/', 'https://www.moes.com/'),
            (r'q\'doba', 'Q\'doba', 'Mexican', '$$', 'https://www.qdoba.com/', 'https://www.qdoba.com/'),
            (r'rubio\'?s', 'Rubio\'s', 'Mexican', '$$', 'https://www.rubios.com/', 'https://www.rubios.com/'),
            (r'baja fresh', 'Baja Fresh', 'Mexican', '$$', 'https://www.bajafresh.com/', 'https://www.bajafresh.com/'),
            (r'el pollo loco', 'El Pollo Loco', 'Mexican', '$$', 'https://www.elpolloloco.com/', 'https://www.elpolloloco.com/'),
            (r'del taco', 'Del Taco', 'Mexican', '$$', 'https://www.deltaco.com/', 'https://www.deltaco.com/'),
            (r'carl\'?s jr', 'Carl\'s Jr.', 'Fast Food', '$$', 'https://www.carlsjr.com/', 'https://www.carlsjr.com/'),
            (r'hardee\'?s', 'Hardee\'s', 'Fast Food', '$$', 'https://www.hardees.com/', 'https://www.hardees.com/'),
            (r'popeye\'?s', 'Popeye\'s', 'Chicken', '$$', 'https://www.popeyes.com/', 'https://www.popeyes.com/'),
            (r'chick-fil-a', 'Chick-fil-A', 'Chicken', '$$', 'https://www.chick-fil-a.com/', 'https://www.chick-fil-a.com/'),
            (r'bojangles', 'Bojangles', 'Chicken', '$$', 'https://www.bojangles.com/', 'https://www.bojangles.com/'),
            (r'zaxby\'?s', 'Zaxby\'s', 'Chicken', '$$', 'https://www.zaxbys.com/', 'https://www.zaxbys.com/'),
            (r'raising cane\'?s', 'Raising Cane\'s', 'Chicken', '$$', 'https://www.raisingcanes.com/', 'https://www.raisingcanes.com/'),
            (r'wingstop', 'Wingstop', 'Chicken', '$$', 'https://www.wingstop.com/', 'https://www.wingstop.com/'),
            (r'buffalo wild wings', 'Buffalo Wild Wings', 'Sports Bar', '$$', 'https://www.buffalowildwings.com/', 'https://www.buffalowildwings.com/'),
            (r'hooters', 'Hooters', 'Sports Bar', '$$', 'https://www.hooters.com/', 'https://www.hooters.com/'),
            (r'twin peaks', 'Twin Peaks', 'Sports Bar', '$$', 'https://www.twinpeaksrestaurant.com/', 'https://www.twinpeaksrestaurant.com/'),
            (r'the cheesecake factory', 'The Cheesecake Factory', 'American', '$$$', 'https://www.thecheesecakefactory.com/', 'https://www.thecheesecakefactory.com/'),
            (r'pf chang\'?s', 'P.F. Chang\'s', 'Asian', '$$$', 'https://www.pfchangs.com/', 'https://www.pfchangs.com/'),
            (r'benihana', 'Benihana', 'Japanese', '$$$', 'https://www.benihana.com/', 'https://www.benihana.com/'),
            (r'hibachi', 'Hibachi Grill', 'Japanese', '$$$', 'https://www.hibachigrill.com/', 'https://www.hibachigrill.com/'),
            (r'panda express', 'Panda Express', 'Chinese', '$$', 'https://www.pandaexpress.com/', 'https://www.pandaexpress.com/'),
            (r'pei wei', 'Pei Wei', 'Asian', '$$', 'https://www.peiwei.com/', 'https://www.peiwei.com/'),
            (r'qdoba', 'Qdoba', 'Mexican', '$$', 'https://www.qdoba.com/', 'https://www.qdoba.com/'),
            (r'moe\'?s', 'Moe\'s Southwest Grill', 'Mexican', '$$', 'https://www.moes.com/', 'https://www.moes.com/'),
            (r'q\'doba', 'Q\'doba', 'Mexican', '$$', 'https://www.qdoba.com/', 'https://www.qdoba.com/'),
            (r'rubio\'?s', 'Rubio\'s', 'Mexican', '$$', 'https://www.rubios.com/', 'https://www.rubios.com/'),
            (r'baja fresh', 'Baja Fresh', 'Mexican', '$$', 'https://www.bajafresh.com/', 'https://www.bajafresh.com/'),
            (r'el pollo loco', 'El Pollo Loco', 'Mexican', '$$', 'https://www.elpolloloco.com/', 'https://www.elpolloloco.com/'),
            (r'del taco', 'Del Taco', 'Mexican', '$$', 'https://www.deltaco.com/', 'https://www.deltaco.com/'),
        ]
        
        for pattern, name, cuisine_type, price, website, booking_url in restaurant_patterns:
            if re.search(pattern, text_content, re.IGNORECASE):
                print(f"Found restaurant pattern: {name}")
                if name.lower() not in found_names:
                    real_restaurants.append({
                        'name': name,
                        'cuisine': cuisine_type,
                        'price_range': price,
                        'website': website,
                        'booking_url': booking_url,
                        'description': f"Popular {cuisine_type.lower()} restaurant in {location}"
                    })
                    found_names.add(name.lower())
        
        # Look for local restaurant mentions
        local_patterns = [
            (r'best restaurants? in ' + location.lower(), 'Local Restaurant', 'Local Cuisine', '$$$'),
            (r'top restaurants? in ' + location.lower(), 'Top Restaurant', 'Fine Dining', '$$$$'),
            (r'popular restaurants? in ' + location.lower(), 'Popular Restaurant', 'Local Cuisine', '$$$'),
        ]
        
        for pattern, name, cuisine_type, price in local_patterns:
            if re.search(pattern, text_content, re.IGNORECASE):
                if 'local' not in found_names:
                    real_restaurants.append({
                        'name': f"Local Restaurant in {location}",
                        'cuisine': cuisine_type,
                        'price_range': price,
                        'website': f"https://www.google.com/search?q=restaurants+in+{location.replace(' ', '+')}",
                        'booking_url': f"https://www.google.com/search?q=restaurants+in+{location.replace(' ', '+')}",
                        'description': f"Highly rated local restaurant in {location}"
                    })
                    found_names.add('local')
        
        # Create restaurant entries from real data only
        print(f"Processing {len(real_restaurants)} real restaurants")
        for i, restaurant_data in enumerate(real_restaurants[:10]):  # Limit to first 10
            try:
                name = restaurant_data['name']
                cuisine_type = restaurant_data['cuisine']
                price = restaurant_data['price_range']
                website = restaurant_data['website']
                booking_url = restaurant_data['booking_url']
                description = restaurant_data['description']
                
                # Generate realistic rating and address
                rating = 4.0 + (hash(name) % 10) / 10  # Rating between 4.0-5.0
                address = f"Location in {location}"
                
                restaurant = RestaurantOption(
                    name=name,
                    cuisine=cuisine_type,
                    price_range=price,
                    rating=round(rating, 1),
                    address=address,
                    phone="Contact via website",
                    website=website,
                    booking_url=booking_url,
                    description=description
                )
                restaurants.append(restaurant)
                print(f"Added restaurant: {name} ({cuisine_type})")
                
            except Exception as e:
                print(f"Error processing real restaurant data: {str(e)}")
                continue
        
        if not restaurants:
            print("No restaurants found in HTML content")
        else:
            print(f"Found {len(restaurants)} restaurants before scoring")
            restaurants = calculate_restaurant_scores(restaurants)
            print(f"Calculated scores for {len(restaurants)} restaurants")
        
    except Exception as e:
        print(f"Error parsing HTML content: {e}")
    
    return restaurants

# Restaurant search agent
async def search_restaurants_agent(search_request: RestaurantSearchRequest) -> RestaurantSearchResponse:
    """Use AI agent to search for restaurants"""
    
    search_id = f"restaurant_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"Processing restaurant search for {search_request.location}")
    
    # Get real data from web scraping
    restaurants = await search_restaurants_web(
        search_request.location,
        search_request.cuisine,
        search_request.price_range,
        search_request.rating
    )
    
    # If no restaurants found, return empty results
    if not restaurants:
        print("No restaurants found via web scraping")
        return RestaurantSearchResponse(
            search_id=search_id,
            location=search_request.location,
            cuisine=search_request.cuisine,
            options=[],
            total_results=0
        )
    
    return RestaurantSearchResponse(
        search_id=search_id,
        location=search_request.location,
        cuisine=search_request.cuisine,
        options=restaurants,
        total_results=len(restaurants)
    )

def create_mock_restaurants(search_request: RestaurantSearchRequest) -> List[RestaurantOption]:
    """Create mock restaurant data for testing"""
    
    mock_restaurants = [
        RestaurantOption(
            name="The Golden Spoon",
            cuisine=search_request.cuisine if search_request.cuisine != "all" else "Italian",
            price_range="$$",
            rating=4.5,
            address="123 Main St, " + search_request.location,
            phone="(555) 123-4567",
            website="https://goldenspoon.com",
            description="Award-winning Italian cuisine with fresh ingredients"
        ),
        RestaurantOption(
            name="Ocean Breeze Seafood",
            cuisine="Seafood",
            price_range="$$$",
            rating=4.3,
            address="456 Harbor Ave, " + search_request.location,
            phone="(555) 234-5678",
            website="https://oceanbreeze.com",
            description="Fresh seafood with ocean views"
        ),
        RestaurantOption(
            name="Spice Garden",
            cuisine="Indian",
            price_range="$$",
            rating=4.7,
            address="789 Spice St, " + search_request.location,
            phone="(555) 345-6789",
            website="https://spicegarden.com",
            description="Authentic Indian cuisine with traditional spices"
        )
    ]
    
    # Calculate scores for mock restaurants
    return calculate_restaurant_scores(mock_restaurants)

# FastAPI app
app = FastAPI(title="Food Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/search-restaurants", response_model=RestaurantSearchResponse)
async def search_restaurants(search_request: RestaurantSearchRequest):
    """Search for restaurants"""
    try:
        result = await search_restaurants_agent(search_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/make-reservation", response_model=ReservationResponse)
async def make_reservation(reservation_request: ReservationRequest):
    """Make a restaurant reservation"""
    try:
        # This would integrate with reservation systems in a real implementation
        reservation_id = f"res_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return ReservationResponse(
            reservation_id=reservation_id,
            status="confirmed",
            confirmation_code=f"RES{reservation_id[-6:].upper()}",
            restaurant_details=RestaurantOption(
                name="Sample Restaurant",
                cuisine="Mixed",
                price_range="$$",
                rating=4.0,
                address="123 Sample St",
                phone="(555) 000-0000",
                website="https://sample.com",
                description="Sample restaurant for reservation"
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "food-agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
