# 🏨 Stay Agent Documentation

## Overview
The Stay Agent provides hotel search and booking capabilities with comprehensive scoring based on amenities, location, price, quality, and reputation.

## Current Status
- **Status**: ✅ Healthy and operational
- **Port**: 8004
- **Data Source**: BrightData API (real-time data only)
- **Booking Integration**: Direct booking links included
- **UI Integration**: Fully functional with frontend

## API Endpoints

### Base URL
```
http://localhost:8004
```

### Endpoints

#### Search Hotels
```http
POST /search-hotels
Content-Type: application/json

{
  "location": "Hawaii",
  "check_in": "2025-10-03",
  "check_out": "2025-10-10",
  "guests": 2,
  "rooms": 1,
  "hotel_type": "luxury",
  "price_range": "200-500"
}
```

#### Book Hotel
```http
POST /book-hotel
Content-Type: application/json

{
  "hotel_id": "HOT001",
  "check_in": "2025-10-03",
  "check_out": "2025-10-10",
  "guests": 2,
  "rooms": 1,
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

### HotelSearchRequest
```typescript
interface HotelSearchRequest {
  location: string;
  check_in: string;
  check_out: string;
  guests: number;
  rooms: number;
  hotel_type: string;
  price_range: string;
  max_results?: number;
}
```

### HotelOption
```typescript
interface HotelOption {
  name: string;
  hotel_type: string;
  price_per_night: number;
  total_price: number;
  rating: number;
  address: string;
  phone: string;
  website: string;
  amenities: string[];
  description: string;
  availability: string;
  score: number;
  price_score: number;
  quality_score: number;
  location_score: number;
  amenity_score: number;
  reputation_score: number;
}
```

### HotelSearchResponse
```typescript
interface HotelSearchResponse {
  search_id: string;
  location: string;
  check_in: string;
  check_out: string;
  hotels: HotelOption[];
  total_results: number;
}
```

## Scoring System

The Stay Agent uses a comprehensive scoring system (0-100 scale) with the following weights:

- **Quality Score (30%)**: Hotel ratings and reviews
- **Price Score (25%)**: Cost per night
- **Amenity Score (20%)**: Available amenities
- **Location Score (15%)**: Geographic convenience
- **Reputation Score (10%)**: Hotel type reputation

### Hotel Type Reputation Scores
- Luxury: 95
- Resort: 90
- Boutique: 85
- Business: 80
- Apartment: 75
- Budget: 60
- Hostel: 50

### Common Amenities
- WiFi: Standard amenity
- Pool: Recreational amenity
- Spa: Wellness amenity
- Restaurant: Dining amenity
- Gym: Fitness amenity
- Concierge: Service amenity
- Room Service: Convenience amenity
- Bar: Entertainment amenity

### Price Categories
- Budget: Under $100/night
- Moderate: $100-$200/night
- Upscale: $200-$400/night
- Luxury: $400+/night

## Data Sources

### Real Data
- **BrightData API**: Web scraping from hotel booking platforms
- **Response Format**: JSON with hotel details and pricing
- **Update Frequency**: Real-time during search

### Mock Data Fallback
- Used when web scraping fails
- Provides realistic sample hotels
- Maintains consistent data structure

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

### Search for Hotels
```bash
curl -X POST http://localhost:8004/search-hotels \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Hawaii",
    "check_in": "2025-10-03",
    "check_out": "2025-10-10",
    "guests": 2,
    "rooms": 1,
    "hotel_type": "luxury"
  }'
```

### Book a Hotel
```bash
curl -X POST http://localhost:8004/book-hotel \
  -H "Content-Type: application/json" \
  -d '{
    "hotel_id": "HOT001",
    "check_in": "2025-10-03",
    "check_out": "2025-10-10",
    "guests": 2,
    "rooms": 1,
    "contact_info": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }'
```

### Check Agent Health
```bash
curl http://localhost:8004/health
```

## Error Handling

### Common Error Codes
- `400`: Bad Request - Invalid input parameters
- `422`: Unprocessable Entity - Validation errors
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
cd agents/stay
python main.py
```

### Testing
```bash
# Test search functionality
python -c "
import requests
response = requests.post('http://localhost:8004/search-hotels', json={
    'location': 'Hawaii',
    'check_in': '2025-10-03',
    'check_out': '2025-10-10',
    'guests': 2,
    'rooms': 1
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
    "agent": "hotels",
    "action": "search",
    "location": "Hawaii",
    "check_in": "2025-10-03",
    "check_out": "2025-10-10",
    "guests": 2,
    "rooms": 1
  }'
```

### Direct Integration
```javascript
const response = await fetch('http://localhost:8004/search-hotels', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    location: 'Hawaii',
    check_in: '2025-10-03',
    check_out: '2025-10-10',
    guests: 2,
    rooms: 1
  })
});

const data = await response.json();
console.log(data.hotels);
```

## Search Parameters

### Hotel Types
- `all`: All hotel types
- `luxury`: Luxury hotels
- `boutique`: Boutique hotels
- `business`: Business hotels
- `resort`: Resort hotels
- `budget`: Budget hotels
- `hostel`: Hostels
- `apartment`: Apartment rentals

### Price Ranges
- `all`: All prices
- `under-100`: Under $100/night
- `100-200`: $100-$200/night
- `200-400`: $200-$400/night
- `400-600`: $400-$600/night
- `over-600`: Over $600/night

### Guest Configuration
- Adults: 1-10 guests
- Children: 0-10 children
- Rooms: 1-5 rooms
- Age restrictions may apply

## Amenity Scoring

### Standard Amenities (5 points each)
- WiFi
- Parking
- Air Conditioning
- TV
- Coffee Maker

### Premium Amenities (10 points each)
- Pool
- Gym
- Restaurant
- Bar
- Room Service

### Luxury Amenities (15 points each)
- Spa
- Concierge
- Valet Parking
- Business Center
- Conference Facilities

### Location Scoring
- City Center: 90 points
- Near Airport: 80 points
- Beachfront: 95 points
- Business District: 85 points
- Residential Area: 70 points
- Remote Location: 60 points
