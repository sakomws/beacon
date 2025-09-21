# Beacon Travel Agent - API Documentation

## Overview

The Beacon Travel Agent provides a comprehensive REST API for travel-related services. All agents follow a consistent API pattern with standardized request/response formats.

## Current Status

### ✅ All APIs Operational
- **6 Agent APIs**: All running and healthy on ports 8000-8005
- **API Proxy**: Unified gateway on port 3000
- **Real Data**: All agents use BrightData API for live data
- **Booking Integration**: Direct booking links in all responses
- **UI Integration**: All APIs working with frontend interface

## Base URLs

| Service | Base URL | Port |
|---------|----------|------|
| UI Proxy | `http://localhost:3000/api/proxy` | 3000 |
| Flight Agent | `http://localhost:8000` | 8000 |
| Food Agent | `http://localhost:8001` | 8001 |
| Leisure Agent | `http://localhost:8002` | 8002 |
| Shopping Agent | `http://localhost:8003` | 8003 |
| Stay Agent | `http://localhost:8004` | 8004 |
| Work Agent | `http://localhost:8005` | 8005 |

## Common Endpoints

### Health Check

All agents provide a health check endpoint:

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T20:13:06Z",
  "agent": "Flight Agent",
  "version": "1.0.0"
}
```

## Flight Agent API

### Search Flights

```http
POST /search
```

**Request Body:**
```json
{
  "origin": "San Francisco",
  "destination": "Hawaii",
  "departure_date": "2025-10-03",
  "return_date": "2025-10-10",
  "passengers": 1,
  "class": "economy"
}
```

**Response:**
```json
{
  "search_id": "flight_search_20250120_201306",
  "origin": "San Francisco",
  "destination": "Hawaii",
  "departure_date": "2025-10-03",
  "flights": [
    {
      "airline": "United",
      "flight_number": "UA123",
      "departure_time": "08:00",
      "arrival_time": "12:00",
      "duration": "4h 0m",
      "price": 498.00,
      "aircraft": "Boeing 737",
      "stops": 0,
      "booking_url": "https://www.google.com/search?q=United+flights+San+Francisco+to+Hawaii+2025-10-03",
      "score": 85.5,
      "price_score": 90.0,
      "time_score": 80.0,
      "comfort_score": 85.0
    }
  ],
  "total_results": 5
}
```

## Food Agent API

### Search Restaurants

```http
POST /search-restaurants
```

**Request Body:**
```json
{
  "location": "Hawaii",
  "cuisine": "italian",
  "price_range": "all",
  "rating": 0.0
}
```

**Response:**
```json
{
  "search_id": "restaurant_search_20250120_201306",
  "location": "Hawaii",
  "cuisine": "italian",
  "options": [
    {
      "name": "Olive Garden",
      "cuisine": "Italian",
      "price_range": "$$",
      "rating": 4.2,
      "address": "Location in Hawaii",
      "phone": "Contact via website",
      "website": "https://www.olivegarden.com",
      "booking_url": "https://www.google.com/search?q=Olive+Garden+Hawaii+reservations",
      "description": "Popular Italian restaurant in Hawaii",
      "score": 78.5
    }
  ],
  "total_results": 1
}
```

## Stay Agent API

### Search Hotels

```http
POST /search-hotels
```

**Request Body:**
```json
{
  "location": "Hawaii",
  "check_in": "2025-10-03",
  "check_out": "2025-10-10",
  "guests": 2,
  "rooms": 1
}
```

**Response:**
```json
{
  "search_id": "hotel_search_20250120_201306",
  "location": "Hawaii",
  "check_in": "2025-10-03",
  "check_out": "2025-10-10",
  "options": [
    {
      "name": "THE 10 BEST Hotels in Hawaii 2025",
      "address": "Location in Hawaii",
      "price_per_night": 150.0,
      "rating": 4.5,
      "amenities": ["WiFi", "Pool", "Gym"],
      "website": "https://www.booking.com/hawaii",
      "booking_url": "https://www.google.com/search?q=hotels+in+Hawaii+2025-10-03",
      "description": "Top-rated hotels in Hawaii",
      "score": 82.3,
      "price_score": 75.0,
      "quality_score": 90.0,
      "location_score": 85.0
    }
  ],
  "total_results": 9
}
```

## Work Agent API

### Search Coworking Spaces

```http
POST /search-coworking
```

**Request Body:**
```json
{
  "location": "Boston",
  "space_type": "all",
  "amenities": [],
  "price_range": "all"
}
```

**Response:**
```json
{
  "search_id": "coworking_search_20250120_201306",
  "location": "Boston",
  "space_type": "all",
  "coworking_spaces": [
    {
      "name": "WeWork Boston",
      "address": "Location in Boston",
      "space_type": "Shared",
      "amenities": ["WiFi", "Coffee", "Meeting Rooms"],
      "price_per_day": 60.0,
      "price_per_month": 1320.0,
      "website": "https://www.wework.com/l/coworking-space/boston",
      "booking_url": "https://www.wework.com/l/coworking-space/boston",
      "description": "Modern coworking space in Boston",
      "score": 85.2
    }
  ],
  "total_results": 3
}
```

## Leisure Agent API

### Search Activities

```http
POST /search-activities
```

**Request Body:**
```json
{
  "location": "Hawaii",
  "activity_type": "all",
  "duration": "all",
  "price_range": "all"
}
```

**Response:**
```json
{
  "search_id": "activity_search_20250120_201306",
  "location": "Hawaii",
  "activity_type": "all",
  "options": [
    {
      "name": "Things You Must See and Do in Hawaii",
      "description": "Comprehensive guide to Hawaii activities",
      "price": 50.0,
      "duration": "Full day",
      "location": "Hawaii",
      "rating": 4.5,
      "website": "https://www.hawaii.com",
      "booking_url": "https://www.google.com/search?q=activities+in+Hawaii",
      "score": 88.7
    }
  ],
  "total_results": 9
}
```

## Shopping Agent API

### Search Products

```http
POST /search-products
```

**Request Body:**
```json
{
  "location": "Hawaii",
  "category": "all",
  "price_range": "all",
  "brand": "all"
}
```

**Response:**
```json
{
  "search_id": "product_search_20250120_201306",
  "location": "Hawaii",
  "category": "all",
  "options": [
    {
      "name": "Made in Hawaii",
      "description": "Authentic Hawaiian products",
      "price": 6.0,
      "store": "Local Hawaii Store",
      "rating": 4.3,
      "location": "Hawaii",
      "website": "https://www.madeinhawaii.com",
      "booking_url": "https://www.google.com/search?q=Made+in+Hawaii+products",
      "score": 76.4
    }
  ],
  "total_results": 9
}
```

## Error Responses

### Standard Error Format

```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "details": "Additional error details",
  "timestamp": "2025-01-20T20:13:06Z"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

## Rate Limiting

- **Default Limit**: 100 requests per minute per IP
- **Burst Limit**: 10 requests per second
- **Headers**: Rate limit information included in response headers

## Authentication

Currently, the API is open and doesn't require authentication. Future versions will include:
- API key authentication
- User-based rate limiting
- Request signing

## Data Sources

All agents use the following external data sources:
- **BrightData API**: Primary data source for web scraping
- **AI21 API**: AI-powered data enhancement
- **Google Search**: Fallback search mechanism

## Response Caching

- **Cache Duration**: 5 minutes for search results
- **Cache Key**: Based on request parameters
- **Cache Invalidation**: Automatic expiration

## SDKs and Libraries

### Python Example

```python
import requests

# Search for flights
response = requests.post(
    "http://localhost:8000/search",
    json={
        "origin": "San Francisco",
        "destination": "Hawaii",
        "departure_date": "2025-10-03",
        "passengers": 1
    }
)

flights = response.json()["flights"]
```

### JavaScript Example

```javascript
// Search for restaurants
const response = await fetch('http://localhost:8001/search-restaurants', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    location: 'Hawaii',
    cuisine: 'italian',
    price_range: 'all'
  })
});

const data = await response.json();
const restaurants = data.options;
```

## Testing

### Health Check Test

```bash
curl http://localhost:8000/health
```

### Search Test

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "San Francisco",
    "destination": "Hawaii",
    "departure_date": "2025-10-03",
    "passengers": 1
  }'
```

## Changelog

### Version 1.0.0
- Initial API release
- All six agent services
- Standardized request/response formats
- Health check endpoints
- Error handling
