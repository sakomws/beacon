# 🍽️ Food Agent Documentation

## Overview
The Food Agent provides restaurant search and reservation capabilities with comprehensive scoring based on cuisine quality, price range, ratings, location, and availability.

## Current Status
- **Status**: ✅ Healthy and operational
- **Port**: 8001
- **Data Source**: BrightData API (real-time data only)
- **UI Integration**: ✅ Fixed - Now properly displays search results
- **Booking Integration**: Direct booking links included

## API Endpoints

### Base URL
```
http://localhost:8001
```

### Endpoints

#### Search Restaurants
```http
POST /search-restaurants
Content-Type: application/json

{
  "location": "Hawaii",
  "cuisine": "italian",
  "price_range": "$$",
  "rating": 4.0,
  "max_results": 10
}
```

#### Make Reservation
```http
POST /make-reservation
Content-Type: application/json

{
  "restaurant_id": "REST001",
  "date": "2025-10-03",
  "time": "19:00",
  "party_size": 2,
  "contact_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  }
}
```

#### Health Check
```http
GET /health
```

## Data Models

### RestaurantSearchRequest
```typescript
interface RestaurantSearchRequest {
  location: string;
  cuisine: string;
  price_range: string;
  rating: number;
  max_results?: number;
}
```

### RestaurantOption
```typescript
interface RestaurantOption {
  name: string;
  cuisine: string;
  price_range: string;
  rating: number;
  address: string;
  phone: string;
  website: string;
  booking_url: string;  // Direct booking link
  description: string;
  score: number;
  price_score: number;
  quality_score: number;
  location_score: number;
  reputation_score: number;
  availability_score: number;
}
```

### RestaurantSearchResponse
```typescript
interface RestaurantSearchResponse {
  search_id: string;
  location: string;
  cuisine: string;
  options: RestaurantOption[];  // Changed from 'restaurants' to 'options'
  total_results: number;
}
```

## Scoring System

The Food Agent uses a comprehensive scoring system (0-100 scale) with the following weights:

- **Quality Score (30%)**: Restaurant ratings and reviews
- **Price Score (25%)**: Price range affordability
- **Reputation Score (20%)**: Cuisine type reputation
- **Location Score (15%)**: Geographic convenience
- **Availability Score (10%)**: Booking availability

### Cuisine Reputation Scores
- Italian: 85
- Chinese: 80
- Japanese: 90
- Mexican: 75
- Indian: 85
- Thai: 80
- French: 90
- American: 70
- Seafood: 85
- Steakhouse: 80
- Sushi: 90
- Pizza: 70

### Price Range Scoring
- $ (Budget): 100 points
- $$ (Moderate): 80 points
- $$$ (Expensive): 60 points
- $$$$ (Very Expensive): 40 points

## Data Sources

### Real Data Only
- **BrightData API**: Web scraping from restaurant search engines
- **Response Format**: JSON with restaurant details and ratings
- **Update Frequency**: Real-time during search
- **No Mock Data**: System uses only real-time data

### Data Processing
- **Web Scraping**: Live data from restaurant search engines via BrightData
- **JSON Parsing**: Structured data extraction
- **Booking URL Generation**: Direct links to reservation platforms
- **Score Calculation**: AI-powered recommendation scoring

## Configuration

### Environment Variables
```bash
# Required for web scraping
BRIGHTDATA_API_KEY=your_brightdata_api_key

# Optional for AI features
AI21_API_KEY=your_ai21_api_key
```

### Dependencies
```bash
pip install -r requirements.txt
```

## Usage Examples

### Search for Restaurants
```bash
curl -X POST http://localhost:8001/search-restaurants \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Hawaii",
    "cuisine": "italian",
    "price_range": "$$",
    "rating": 4.0
  }'
```

### Make a Reservation
```bash
curl -X POST http://localhost:8001/make-reservation \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": "REST001",
    "date": "2025-10-03",
    "time": "19:00",
    "party_size": 2,
    "contact_info": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }'
```

### Check Agent Health
```bash
curl http://localhost:8001/health
```

## Error Handling

### Common Error Codes
- `400`: Bad Request - Invalid input parameters
- `422`: Unprocessable Entity - Validation errors (e.g., rating must be a number)
- `500`: Internal Server Error - Agent processing error

### Error Response Format
```json
{
  "detail": "Error description",
  "error_code": "ERROR_TYPE"
}
```

## Development

### Running the Agent
```bash
cd agents/food
python main.py
```

### Testing
```bash
# Test search functionality
python -c "
import requests
response = requests.post('http://localhost:8001/search-restaurants', json={
    'location': 'Hawaii',
    'cuisine': 'italian',
    'price_range': '$$',
    'rating': 4.0
})
print(response.json())
"
```

### Logging
The agent logs all operations to stdout with the following levels:
- INFO: Normal operations
- WARNING: Non-critical issues (e.g., missing API keys)
- ERROR: Critical errors

## Integration

### Via API Proxy
```bash
curl -X POST http://localhost:3000/api/proxy \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "food",
    "action": "search",
    "location": "Hawaii",
    "cuisine": "italian",
    "price_range": "$$",
    "rating": 4.0
  }'
```

### Direct Integration
```javascript
const response = await fetch('http://localhost:8001/search-restaurants', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    location: 'Hawaii',
    cuisine: 'italian',
    price_range: '$$',
    rating: 4.0
  })
});

const data = await response.json();
console.log(data.restaurants);
```

## Search Parameters

### Location
- City name (e.g., "Hawaii", "San Francisco")
- Neighborhood or area
- Coordinates (future enhancement)

### Cuisine Types
- `all`: All cuisines
- `italian`: Italian cuisine
- `chinese`: Chinese cuisine
- `japanese`: Japanese cuisine
- `mexican`: Mexican cuisine
- `indian`: Indian cuisine
- `thai`: Thai cuisine
- `french`: French cuisine
- `american`: American cuisine
- `seafood`: Seafood restaurants

### Price Ranges
- `$`: Budget-friendly
- `$$`: Moderate pricing
- `$$$`: Expensive
- `$$$$`: Very expensive

### Rating Filter
- Minimum rating threshold (0.0 - 5.0)
- Based on user reviews and ratings
