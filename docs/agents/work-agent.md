# 💼 Work Agent Documentation

## Overview
The Work Agent provides coworking space search and discovery capabilities with comprehensive scoring based on amenities, location, pricing, and space quality.

## Current Status
- **Status**: ✅ Healthy and operational
- **Port**: 8005
- **Data Source**: BrightData API (real-time data only)
- **Dynamic Locations**: ✅ Fixed - Now returns location-specific results
- **Booking Integration**: Direct booking links included

## API Endpoints

### Base URL
```
http://localhost:8005
```

### Endpoints

#### Search Coworking Spaces
```http
POST /search-coworking
Content-Type: application/json

{
  "location": "Boston",
  "space_type": "all",
  "amenities": ["WiFi", "Coffee", "Meeting Rooms"],
  "price_range": "all"
}
```

#### Book Coworking Space
```http
POST /book-coworking
Content-Type: application/json

{
  "space_id": "SPACE001",
  "date": "2025-10-03",
  "duration": "full-day",
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

### CoworkingSearchRequest
```typescript
interface CoworkingSearchRequest {
  location: string;
  space_type: string;
  amenities: string[];
  price_range: string;
  max_results?: number;
}
```

### CoworkingOption
```typescript
interface CoworkingOption {
  name: string;
  address: string;
  space_type: string;
  amenities: string[];
  price_per_day: number;
  price_per_month: number;
  website: string;
  booking_url: string;  // Direct booking link
  description: string;
  score: number;
  price_score: number;
  amenity_score: number;
  location_score: number;
  quality_score: number;
}
```

### CoworkingSearchResponse
```typescript
interface CoworkingSearchResponse {
  search_id: string;
  location: string;
  space_type: string;
  coworking_spaces: CoworkingOption[];
  total_results: number;
}
```

## Scoring System

The Work Agent uses a comprehensive scoring system (0-100 scale) with the following weights:

- **Price Score (30%)**: Cost-effectiveness
- **Amenity Score (25%)**: Available amenities
- **Location Score (20%)**: Geographic convenience
- **Quality Score (15%)**: Space quality and reputation
- **Availability Score (10%)**: Booking availability

### Coworking Space Types
- **Shared Desk**: 70 points (affordable, social)
- **Dedicated Desk**: 80 points (personal space, stability)
- **Private Office**: 90 points (privacy, professional)
- **Meeting Room**: 85 points (collaboration, presentation)
- **Event Space**: 75 points (flexibility, capacity)

### Amenity Scoring
- **WiFi**: 20 points (essential)
- **Coffee**: 15 points (comfort)
- **Meeting Rooms**: 25 points (collaboration)
- **Printing**: 10 points (convenience)
- **Kitchen**: 15 points (comfort)
- **Parking**: 10 points (accessibility)
- **24/7 Access**: 20 points (flexibility)
- **Phone Booths**: 15 points (privacy)

### Price Range Scoring
- **Under $50/day**: 100 points (budget-friendly)
- **$50-100/day**: 80 points (moderate)
- **$100-200/day**: 60 points (premium)
- **Over $200/day**: 40 points (luxury)

## Data Sources

### Real Data Only
- **BrightData API**: Web scraping from coworking space directories
- **Response Format**: JSON with space details and amenities
- **Update Frequency**: Real-time during search
- **No Mock Data**: System uses only real-time data

### Data Processing
- **Web Scraping**: Live data from coworking directories via BrightData
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

### Search for Jobs
```bash
curl -X POST http://localhost:8005/search-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Hawaii",
    "job_type": "full-time",
    "industry": "technology",
    "experience_level": "mid-level"
  }'
```

### Apply for a Job
```bash
curl -X POST http://localhost:8005/apply-job \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "JOB001",
    "candidate_info": {
      "name": "John Doe",
      "email": "john@example.com",
      "experience": "5 years"
    },
    "resume_url": "https://example.com/resume.pdf",
    "cover_letter": "I am excited to apply for this position..."
  }'
```

### Check Agent Health
```bash
curl http://localhost:8005/health
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
cd agents/work
python main.py
```

### Testing
```bash
# Test search functionality
python -c "
import requests
response = requests.post('http://localhost:8005/search-jobs', json={
    'location': 'Hawaii',
    'job_type': 'full-time',
    'industry': 'technology',
    'experience_level': 'mid-level'
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
    "agent": "work",
    "action": "search",
    "location": "Hawaii",
    "job_type": "full-time",
    "industry": "technology",
    "experience_level": "mid-level"
  }'
```

### Direct Integration
```javascript
const response = await fetch('http://localhost:8005/search-jobs', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    location: 'Hawaii',
    job_type: 'full-time',
    industry: 'technology',
    experience_level: 'mid-level'
  })
});

const data = await response.json();
console.log(data.jobs);
```

## Search Parameters

### Job Types
- `all`: All job types
- `full-time`: Full-time positions
- `part-time`: Part-time positions
- `contract`: Contract positions
- `freelance`: Freelance work
- `internship`: Internship opportunities
- `remote`: Remote positions
- `hybrid`: Hybrid positions

### Industries
- `all`: All industries
- `technology`: Technology sector
- `healthcare`: Healthcare sector
- `finance`: Finance sector
- `education`: Education sector
- `hospitality`: Hospitality & Tourism
- `retail`: Retail sector
- `manufacturing`: Manufacturing
- `consulting`: Consulting
- `nonprofit`: Non-profit sector

### Experience Levels
- `all`: All levels
- `entry`: Entry Level (0-2 years)
- `mid`: Mid Level (3-5 years)
- `senior`: Senior Level (6-10 years)
- `executive`: Executive (10+ years)

### Salary Ranges
- `all`: All salaries
- `under-50k`: Under $50,000
- `50k-75k`: $50,000 - $75,000
- `75k-100k`: $75,000 - $100,000
- `100k-150k`: $100,000 - $150,000
- `150k-200k`: $150,000 - $200,000
- `over-200k`: Over $200,000

## Work-Life Balance Scoring

### Remote Work
- Full Remote: 90 points
- Hybrid (2-3 days): 80 points
- Hybrid (1 day): 70 points
- Office Only: 60 points

### Benefits Consideration
- Health Insurance: 10 points
- 401k/Retirement: 10 points
- Flexible PTO: 15 points
- Professional Development: 10 points
- Gym Membership: 5 points
- Commuter Benefits: 5 points

### Company Culture Indicators
- Work-life balance mentions: +10 points
- Flexible hours: +15 points
- Remote work options: +20 points
- Team collaboration: +10 points
- Innovation focus: +10 points
