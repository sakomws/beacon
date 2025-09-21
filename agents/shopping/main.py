#!/usr/bin/env python3
"""
Shopping Agent - Product and store recommendations
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
class ProductSearchRequest(BaseModel):
    location: str
    category: str = "all"
    price_range: str = "all"
    brand: str = "all"
    max_results: int = 10

class ProductOption(BaseModel):
    name: str
    category: str
    brand: str
    price: float
    original_price: float
    rating: float
    store: str
    address: str
    website: str
    description: str
    availability: str
    booking_url: str = ""
    score: float = 0.0
    price_score: float = 0.0
    quality_score: float = 0.0
    value_score: float = 0.0
    reputation_score: float = 0.0
    availability_score: float = 0.0

class ProductSearchResponse(BaseModel):
    search_id: str
    location: str
    category: str
    options: List[ProductOption]
    total_results: int

class PurchaseRequest(BaseModel):
    product_id: str
    quantity: int
    payment_info: Dict[str, Any]
    shipping_address: Dict[str, Any]

class PurchaseResponse(BaseModel):
    purchase_id: str
    status: str
    confirmation_code: str
    product_details: ProductOption
    total_cost: float

# Web scraping function for product search
async def search_products_web(location: str, category: str = "all", price_range: str = "all", brand: str = "all") -> List[ProductOption]:
    """Search for products using web scraping via BrightData API"""
    
    if not BRIGHTDATA_HEADERS:
        print("BrightData API not configured, skipping web scraping")
        return []
    
    # Construct Google Search URL for products
    location_encoded = quote_plus(location)
    category_query = f"{category} products" if category != "all" else "products"
    brand_query = f" {brand}" if brand != "all" else ""
    full_query = f"{category_query}{brand_query} in {location_encoded}"
    search_url = f"https://www.google.com/search?q={quote_plus(full_query)}&brd_json=1"
    
    data = {
        "zone": "serp_api1",
        "url": search_url,
        "format": "raw"
    }
    
    try:
        print(f"Searching for products: {location} - {category} - {brand}")
        print(f"Search URL: {search_url}")
        
        response = requests.post(
            "https://api.brightdata.com/request",
            json=data,
            headers=BRIGHTDATA_HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            # Save response for debugging
            with open("brightdata_products_response.json", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Response saved ({len(response.text)} characters)")
            
            # Parse the JSON response for product data
            try:
                json_data = response.json()
                products = parse_json_product_data(json_data, location, category, brand)
                return products
            except json.JSONDecodeError:
                # Fallback to HTML parsing if JSON parsing fails
                products = parse_product_data(response.text, location, category, brand)
                return products
        else:
            print(f"BrightData API error: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"Web scraping error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def calculate_product_scores(products: List[ProductOption]) -> List[ProductOption]:
    """Calculate comprehensive scores for product options"""
    
    if not products:
        return products
    
    # Brand reputation scores (0-100, higher is better)
    brand_reputation = {
        "apple": 95, "samsung": 90, "sony": 85, "lg": 80, "nike": 90,
        "adidas": 85, "puma": 75, "zara": 80, "h&m": 70, "uniqlo": 75,
        "amazon": 85, "google": 90, "microsoft": 88, "dell": 80, "hp": 75,
        "all": 75
    }
    
    # Extract prices for normalization
    prices = [p.price for p in products if p.price > 0]
    if prices:
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price if max_price > min_price else 1
    else:
        min_price = max_price = 100.0
        price_range = 1
    
    # Extract ratings for normalization
    ratings = [p.rating for p in products if p.rating > 0]
    if ratings:
        min_rating = min(ratings)
        max_rating = max(ratings)
        rating_range = max_rating - min_rating if max_rating > min_rating else 1
    else:
        min_rating = max_rating = 4.0
        rating_range = 1
    
    for product in products:
        # 1. PRICE SCORE (0-100, higher is better for lower prices)
        if product.price > 0 and price_range > 0:
            product.price_score = max(0, 100 - ((product.price - min_price) / price_range) * 100)
        else:
            product.price_score = 70  # Default
        
        # 2. QUALITY SCORE (0-100, higher is better for higher ratings)
        if product.rating > 0:
            if rating_range > 0:
                product.quality_score = max(0, 100 - ((product.rating - min_rating) / rating_range) * 100)
            else:
                product.quality_score = 100
        else:
            product.quality_score = 50  # Default
        
        # 3. VALUE SCORE (0-100, higher is better for better value)
        if product.original_price > product.price:
            discount_percent = ((product.original_price - product.price) / product.original_price) * 100
            product.value_score = min(100, 70 + discount_percent * 0.5)
        else:
            product.value_score = 70  # Default
        
        # 4. REPUTATION SCORE (0-100, higher is better)
        product.reputation_score = brand_reputation.get(product.brand.lower(), 70)
        
        # 5. AVAILABILITY SCORE (0-100, higher is better)
        if "in stock" in product.availability.lower():
            product.availability_score = 90
        elif "limited" in product.availability.lower():
            product.availability_score = 60
        else:
            product.availability_score = 30
        
        # 6. OVERALL SCORE (weighted average)
        # Weights: Quality 30%, Price 25%, Value 20%, Reputation 15%, Availability 10%
        product.score = (
            product.quality_score * 0.30 +
            product.price_score * 0.25 +
            product.value_score * 0.20 +
            product.reputation_score * 0.15 +
            product.availability_score * 0.10
        )
    
    # Sort products by overall score (highest first)
    products.sort(key=lambda x: x.score, reverse=True)
    
    return products

def parse_json_product_data(json_data: dict, location: str, category: str, brand: str) -> List[ProductOption]:
    """Parse product data from BrightData JSON response"""
    
    products = []
    
    print(f"Parsing JSON product data from BrightData response")
    
    try:
        # Extract product data from the JSON structure
        if "organic" in json_data:
            organic_results = json_data["organic"]
            print(f"Found {len(organic_results)} organic search results")
            
            for i, result in enumerate(organic_results[:10]):  # Limit to 10 products
                try:
                    # Extract product information
                    name = result.get("title", f"Product {i+1}")
                    description = result.get("description", "")
                    link = result.get("link", "")
                    
                    # Extract price from description or extensions
                    price = 50.0  # Default
                    original_price = 50.0
                    if "extensions" in result:
                        for ext in result["extensions"]:
                            ext_text = ext.get("text", "")
                            price_match = re.search(r'\$(\d+)', ext_text)
                            if price_match:
                                price = float(price_match.group(1))
                                break
                    
                    # Extract rating from description
                    rating = 4.0  # Default
                    rating_match = re.search(r'(\d+\.?\d*)\s*stars?', description.lower())
                    if rating_match:
                        rating = float(rating_match.group(1))
                    
                    # Generate booking URL
                    booking_url = f"https://www.google.com/search?q={quote_plus(f'{name} {location} buy')}"
                    
                    # Create product object
                    product = ProductOption(
                        name=name,
                        category=category if category != "all" else "General",
                        brand=brand if brand != "all" else "Various",
                        price=price,
                        original_price=original_price,
                        rating=rating,
                        store="Local Store",
                        address=f"Store in {location}",
                        website=link,
                        description=description,
                        availability="In Stock",
                        booking_url=booking_url
                    )
                    products.append(product)
                    print(f"Created product {i+1}: {product.name} - ${product.price}")
                    
                except Exception as e:
                    print(f"Error parsing product item {i}: {e}")
                    continue
        
        if not products:
            print("No products found in JSON data")
        else:
            # Calculate scores for all products
            products = calculate_product_scores(products)
            print(f"Calculated scores for {len(products)} products")
        
    except Exception as e:
        print(f"Error parsing JSON product data: {e}")
        import traceback
        traceback.print_exc()
    
    return products

def parse_product_data(html_content: str, location: str, category: str, brand: str) -> List[ProductOption]:
    """Parse product data from scraped HTML content using BeautifulSoup"""
    
    products = []
    
    print(f"Parsing product data from HTML content ({len(html_content)} characters)")
    
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for product data in the HTML
        product_elements = soup.find_all(['div', 'article'], class_=re.compile(r'product|item|listing'))
        
        for i, element in enumerate(product_elements[:10]):
            try:
                name = element.get_text(strip=True)[:50] or f"Product {i+1}"
                
                # Generate booking URL
                booking_url = f"https://www.google.com/search?q={quote_plus(f'{name} {location} buy')}"
                
                product = ProductOption(
                    name=name,
                    category=category if category != "all" else "General",
                    brand=brand if brand != "all" else "Various",
                    price=50.0,
                    original_price=60.0,
                    rating=4.0,
                    store="Local Store",
                    address=f"Store in {location}",
                    website="",
                    description="Product found via web scraping",
                    availability="In Stock",
                    booking_url=booking_url
                )
                products.append(product)
                
            except Exception as e:
                print(f"Error parsing product element {i}: {e}")
                continue
        
        if not products:
            print("No products found in HTML content")
        else:
            products = calculate_product_scores(products)
            print(f"Calculated scores for {len(products)} products")
        
    except Exception as e:
        print(f"Error parsing HTML content: {e}")
    
    return products

# Product search agent
async def search_products_agent(search_request: ProductSearchRequest) -> ProductSearchResponse:
    """Use AI agent to search for products"""
    
    search_id = f"product_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"Processing product search for {search_request.location}")
    
    # Get real data from web scraping
    products = await search_products_web(
        search_request.location,
        search_request.category,
        search_request.price_range,
        search_request.brand
    )
    
    # If no products found, return empty results
    if not products:
        print("No products found via web scraping")
        return ProductSearchResponse(
            search_id=search_id,
            location=search_request.location,
            category=search_request.category,
            options=[],
            total_results=0
        )
    
    return ProductSearchResponse(
        search_id=search_id,
        location=search_request.location,
        category=search_request.category,
        options=products,
        total_results=len(products)
    )

def create_mock_products(search_request: ProductSearchRequest) -> List[ProductOption]:
    """Create mock product data for testing"""
    
    mock_products = [
        ProductOption(
            name="Wireless Headphones",
            category="electronics",
            brand="Sony",
            price=89.99,
            original_price=119.99,
            rating=4.5,
            store="Electronics Store",
            address=f"Main St, {search_request.location}",
            description="High-quality wireless headphones with noise cancellation",
            website="https://electronics.com",
            availability="In Stock",
            booking_url=f"https://www.google.com/search?q={quote_plus(f'Wireless Headphones Sony {search_request.location} buy')}"
        ),
        ProductOption(
            name="Running Shoes",
            category="sports",
            brand="Nike",
            price=129.99,
            original_price=129.99,
            rating=4.3,
            store="Sports Store",
            address=f"Sports Ave, {search_request.location}",
            description="Comfortable running shoes for all terrains",
            website="https://sports.com",
            availability="In Stock",
            booking_url=f"https://www.google.com/search?q={quote_plus(f'Running Shoes Nike {search_request.location} buy')}"
        ),
        ProductOption(
            name="Coffee Maker",
            category="home",
            brand="Breville",
            price=199.99,
            original_price=249.99,
            rating=4.7,
            store="Home Store",
            address=f"Home Blvd, {search_request.location}",
            description="Professional-grade coffee maker for home use",
            website="https://home.com",
            availability="Limited Stock",
            booking_url=f"https://www.google.com/search?q={quote_plus(f'Coffee Maker Breville {search_request.location} buy')}"
        )
    ]
    
    # Calculate scores for mock products
    return calculate_product_scores(mock_products)

# FastAPI app
app = FastAPI(title="Shopping Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/search-products", response_model=ProductSearchResponse)
async def search_products(search_request: ProductSearchRequest):
    """Search for products"""
    try:
        result = await search_products_agent(search_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/purchase-product", response_model=PurchaseResponse)
async def purchase_product(purchase_request: PurchaseRequest):
    """Purchase a product"""
    try:
        # This would integrate with payment systems in a real implementation
        purchase_id = f"purchase_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return PurchaseResponse(
            purchase_id=purchase_id,
            status="confirmed",
            confirmation_code=f"PUR{purchase_id[-6:].upper()}",
            product_details=ProductOption(
                name="Sample Product",
                category="General",
                brand="Sample",
                price=50.0,
                original_price=60.0,
                rating=4.0,
                store="Sample Store",
                address="123 Sample St",
                description="Sample product for purchase",
                website="https://sample.com",
                availability="In Stock"
            ),
            total_cost=purchase_request.quantity * 50.0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "shopping-agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
