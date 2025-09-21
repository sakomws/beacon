# ✈️ Flight Agent Documentation

## Overview
The Flight Agent provides real-time flight search and booking capabilities with comprehensive scoring based on price, time, risk, airline reputation, and flexibility.

## Current Status
- **Status**: ✅ Healthy and operational
- **Port**: 8000
- **Data Source**: BrightData API (real-time data only)
- **Booking Integration**: Direct booking links included
- **UI Integration**: Fully functional with frontend

## API Endpoints

### Base URL
```
http://localhost:8000
```

### Endpoints

#### Search Flights
```http
POST /search
Content-Type: application/json

{
  "origin": "San Francisco",
  "destination": "Hawaii", 
  "departure_date": "2025-10-03",
  "return_date": "2025-10-24",
  "passengers": 1,
  "class_type": "economy"
}
```

#### Book Flight
```http
POST /book
Content-Type: application/json

{
  "flight_id": "FL001",
  "passenger_info": {
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

### FlightSearchRequest
```typescript
interface FlightSearchRequest {
  origin: string;
  destination: string;
  departure_date: string;
  return_date?: string;
  passengers: number;
  class_type: string;
  max_results?: number;
}
```

### FlightOption
```typescript
interface FlightOption {
  airline: string;
  flight_number: string;
  departure_time: string;
  arrival_time: string;
  duration: string;
  price: number;
  stops: number;
  aircraft: string;
  booking_url: string;  // Direct booking link
  score: number;
  price_score: number;
  time_score: number;
  risk_score: number;
  reputation_score: number;
  flexibility_score: number;
}
```

### FlightSearchResponse
```typescript
interface FlightSearchResponse {
  search_id: string;
  origin: string;
  destination: string;
  departure_date: string;
  return_date?: string;
  passengers: number;
  class_type: string;
  flights: FlightOption[];
  total_results: number;
}
```

## Scoring System

The Flight Agent uses a comprehensive scoring system (0-100 scale) with the following weights:

- **Price Score (30%)**: Cost-effectiveness based on relative pricing
- **Time Score (25%)**: Flight duration optimization
- **Risk Score (20%)**: Number of stops and connection reliability
- **Reputation Score (15%)**: Airline reputation and reliability
- **Flexibility Score (10%)**: Departure time convenience

### Airline Reputation Scores
- United Airlines: 85
- American Airlines: 80
- Delta Air Lines: 88
- Southwest Airlines: 75
- JetBlue Airways: 82
- Alaska Airlines: 90
- Hawaiian Airlines: 85
- Spirit Airlines: 60
- Frontier Airlines: 55

## Data Sources

### Real Data Only
- **BrightData API**: Web scraping from Google Flights
- **Response Format**: JSON with flight pricing and details
- **Update Frequency**: Real-time during search
- **No Mock Data**: System uses only real-time data

### Data Processing
- **Web Scraping**: Live data from Google Flights via BrightData
- **JSON Parsing**: Structured data extraction
- **Booking URL Generation**: Direct links to booking platforms
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

### Search for Flights
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "San Francisco",
    "destination": "Hawaii",
    "departure_date": "2025-10-03",
    "return_date": "2025-10-24",
    "passengers": 1,
    "class_type": "economy"
  }'
```

### Check Agent Health
```bash
curl http://localhost:8000/health
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
cd flight
python main.py
```

### Testing
```bash
# Test search functionality
python -c "
import requests
response = requests.post('http://localhost:8000/search', json={
    'origin': 'San Francisco',
    'destination': 'Hawaii',
    'departure_date': '2025-10-03',
    'passengers': 1,
    'class_type': 'economy'
})
print(response.json())
"
```

### Logging
The agent logs all operations to stdout with the following levels:
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Critical errors

## Integration

### Via API Proxy
```bash
curl -X POST http://localhost:3000/api/proxy \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "flights",
    "action": "search",
    "origin": "San Francisco",
    "destination": "Hawaii",
    "departure_date": "2025-10-03",
    "return_date": "2025-10-24",
    "passengers": 1,
    "class_type": "economy"
  }'
```

### Direct Integration
```javascript
const response = await fetch('http://localhost:8000/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    origin: 'San Francisco',
    destination: 'Hawaii',
    departure_date: '2025-10-03',
    return_date: '2025-10-24',
    passengers: 1,
    class_type: 'economy'
  })
});

const data = await response.json();
console.log(data.flights);
```
