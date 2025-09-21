# 🎯 Leisure Agent Documentation

## Overview
The Leisure Agent provides activity search and booking capabilities with comprehensive scoring based on activity type, duration, price, ratings, and accessibility.

## Current Status
- **Status**: ✅ Healthy and operational
- **Port**: 8002
- **Data Source**: BrightData API (real-time data only)
- **Booking Integration**: Direct booking links included
- **UI Integration**: Fully functional with frontend

## API Endpoints

### Base URL
```
http://localhost:8002
```

### Endpoints

#### Search Activities
```http
POST /search-activities
Content-Type: application/json

{
  "location": "Hawaii",
  "activity_type": "outdoor",
  "duration": "half-day",
  "price_range": "25-50",
  "max_results": 10
}
```

#### Book Activity
```http
POST /book-activity
Content-Type: application/json

{
  "activity_id": "ACT001",
  "date": "2025-10-03",
  "time": "10:00",
  "participants": 2,
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

### ActivitySearchRequest
```typescript
interface ActivitySearchRequest {
  location: string;
  activity_type: string;
  duration: string;
  price_range: string;
  max_results?: number;
}
```

### ActivityOption
```typescript
interface ActivityOption {
  name: string;
  activity_type: string;
  duration: string;
  price: number;
  rating: number;
  address: string;
  description: string;
  website: string;
  availability: string;
  score: number;
  price_score: number;
  quality_score: number;
  location_score: number;
  popularity_score: number;
  accessibility_score: number;
}
```

### ActivitySearchResponse
```typescript
interface ActivitySearchResponse {
  search_id: string;
  location: string;
  activity_type: string;
  activities: ActivityOption[];
  total_results: number;
}
```

## Scoring System

The Leisure Agent uses a comprehensive scoring system (0-100 scale) with the following weights:

- **Quality Score (30%)**: Activity ratings and reviews
- **Price Score (25%)**: Cost-effectiveness
- **Popularity Score (20%)**: Activity type popularity
- **Location Score (15%)**: Geographic accessibility
- **Accessibility Score (10%)**: Physical accessibility features

### Activity Type Popularity Scores
- Tours: 90
- Outdoor: 85
- Cultural: 80
- Entertainment: 75
- Sports: 70
- Nightlife: 65
- Shopping: 60
- Wellness: 75

### Duration Categories
- 1-2 hours: Short activities
- Half day (3-4 hours): Medium activities
- Full day (6-8 hours): Long activities
- Multi-day: Extended experiences

### Price Ranges
- Free: $0
- Under $25: Budget activities
- $25-$50: Moderate pricing
- $50-$100: Premium activities
- Over $100: Luxury experiences

## Data Sources

### Real Data
- **BrightData API**: Web scraping from activity booking platforms
- **Response Format**: JSON with activity details and pricing
- **Update Frequency**: Real-time during search

### Mock Data Fallback
- Used when web scraping fails
- Provides realistic sample activities
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

### Search for Activities
```bash
curl -X POST http://localhost:8002/search-activities \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Hawaii",
    "activity_type": "outdoor",
    "duration": "half-day",
    "price_range": "25-50"
  }'
```

### Book an Activity
```bash
curl -X POST http://localhost:8002/book-activity \
  -H "Content-Type: application/json" \
  -d '{
    "activity_id": "ACT001",
    "date": "2025-10-03",
    "time": "10:00",
    "participants": 2,
    "contact_info": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }'
```

### Check Agent Health
```bash
curl http://localhost:8002/health
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
cd agents/leisure
python main.py
```

### Testing
```bash
# Test search functionality
python -c "
import requests
response = requests.post('http://localhost:8002/search-activities', json={
    'location': 'Hawaii',
    'activity_type': 'outdoor',
    'duration': 'half-day',
    'price_range': '25-50'
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
    "agent": "leisure",
    "action": "search",
    "location": "Hawaii",
    "activity_type": "outdoor",
    "duration": "half-day",
    "price_range": "25-50"
  }'
```

### Direct Integration
```javascript
const response = await fetch('http://localhost:8002/search-activities', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    location: 'Hawaii',
    activity_type: 'outdoor',
    duration: 'half-day',
    price_range: '25-50'
  })
});

const data = await response.json();
console.log(data.activities);
```

## Search Parameters

### Activity Types
- `all`: All activities
- `outdoor`: Outdoor adventures
- `cultural`: Cultural experiences
- `entertainment`: Entertainment venues
- `sports`: Sports and recreation
- `tours`: Tours and sightseeing
- `nightlife`: Nightlife venues
- `shopping`: Shopping experiences
- `wellness`: Wellness and spa activities

### Duration Options
- `all`: Any duration
- `1-2`: 1-2 hours
- `half-day`: Half day (3-4 hours)
- `full-day`: Full day (6-8 hours)
- `multi-day`: Multi-day experiences

### Price Ranges
- `all`: All prices
- `free`: Free activities
- `under-25`: Under $25
- `25-50`: $25 - $50
- `50-100`: $50 - $100
- `over-100`: Over $100

## Activity Categories

### Outdoor Adventures
- Hiking trails
- Water sports
- Adventure tours
- Nature experiences

### Cultural Experiences
- Museums and galleries
- Historical sites
- Cultural performances
- Local traditions

### Entertainment
- Shows and performances
- Theme parks
- Gaming venues
- Live music

### Sports & Recreation
- Fitness activities
- Team sports
- Individual sports
- Recreational facilities
