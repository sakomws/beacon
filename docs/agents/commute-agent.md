# 🚌 Commute Agent Documentation

## Overview
The Commute Agent provides real-time transportation and commute options search with multi-mode transport support, including public transit, rideshare, driving, walking, and cycling options. It offers intelligent recommendations based on duration, cost, distance, and real-time availability.

## Current Status
- **Status**: ✅ Healthy and operational
- **Port**: 8006
- **Data Source**: BrightData API (real-time data only)
- **Booking Integration**: Direct booking links for each transport mode
- **UI Integration**: Fully functional with CommuteSearch component

## API Endpoints

### Base URL
```
http://localhost:8006
```

### Endpoints

#### Search Commute Options
```http
POST /search
Content-Type: application/json

{
  "origin": "San Francisco",
  "destination": "Hawaii",
  "transport_mode": "all",
  "departure_time": "2025-10-03T09:00:00Z"
}
```

#### Health Check
```http
GET /health
```

## Request Models

### CommuteRequest
```json
{
  "origin": "string",
  "destination": "string", 
  "departure_time": "string (optional)",
  "transport_mode": "string (all|public_transit|rideshare|driving|walking|cycling)"
}
```

### CommuteOption
```json
{
  "mode": "string",
  "duration": "string",
  "cost": "string",
  "distance": "string",
  "description": "string",
  "booking_url": "string",
  "provider": "string",
  "real_time_info": "string (optional)"
}
```

### CommuteResponse
```json
{
  "origin": "string",
  "destination": "string",
  "options": [CommuteOption],
  "total_options": "number",
  "search_time": "string"
}
```

## Transport Modes

### Supported Modes
- **All Modes**: Search across all transportation options
- **Public Transit**: Buses, metro, subway, trains
- **Rideshare**: Uber, Lyft, taxi services
- **Driving**: Personal vehicle, car rental
- **Walking**: Pedestrian routes
- **Cycling**: Bicycle, bike sharing

### Mode Detection
The agent automatically detects transport modes from search results using keyword matching:
- Public Transit: "bus", "metro", "subway", "train", "transit"
- Rideshare: "uber", "lyft", "taxi", "rideshare"
- Driving: "drive", "car", "vehicle", "automobile"
- Walking: "walk", "walking", "pedestrian"
- Cycling: "bike", "cycling", "bicycle", "cycle"

## Data Processing

### Information Extraction
The agent extracts key information from search results:

#### Duration Extraction
- Pattern matching for time formats
- Support for minutes, hours, and mixed formats
- Examples: "25 minutes", "1h 30m", "2 hours"

#### Cost Extraction
- Dollar amount detection
- Price range identification
- Examples: "$12.50", "from $8", "starting at $15"

#### Distance Extraction
- Mile and kilometer support
- Decimal precision handling
- Examples: "8.2 miles", "12.5 km"

### Booking URL Generation
Dynamic booking URLs based on transport mode:
- **Public Transit**: Google Maps transit directions
- **Rideshare**: Uber/Lyft booking links
- **Driving**: Google Maps driving directions
- **Walking**: Google Maps walking directions
- **Cycling**: Google Maps cycling directions

## Scoring System

### Scoring Factors
The agent uses a comprehensive scoring system (0-100 scale):

#### Duration Score (30%)
- Shorter durations receive higher scores
- Time-based efficiency calculation
- Real-time traffic consideration

#### Cost Score (25%)
- Cost-effectiveness evaluation
- Price range appropriateness
- Value for money assessment

#### Convenience Score (20%)
- Ease of access and booking
- Provider reliability
- User experience factors

#### Real-time Score (15%)
- Live availability information
- Current conditions accuracy
- Update frequency

#### Safety Score (10%)
- Transport mode safety ratings
- Provider safety records
- Route safety considerations

### Score Calculation
```python
total_score = (
    duration_score * 0.30 +
    cost_score * 0.25 +
    convenience_score * 0.20 +
    real_time_score * 0.15 +
    safety_score * 0.10
)
```

## Response Examples

### Successful Search Response
```json
{
  "origin": "San Francisco",
  "destination": "Hawaii",
  "options": [
    {
      "mode": "Public Transit",
      "duration": "25 minutes",
      "cost": "$3.50",
      "distance": "8.2 miles",
      "description": "Take the metro from San Francisco to Hawaii. Includes 1 transfer at Central Station. Real-time updates available.",
      "booking_url": "https://www.google.com/maps/dir/San+Francisco/Hawaii/@transit",
      "provider": "Transit Authority",
      "real_time_info": "Next train in 3 minutes"
    },
    {
      "mode": "Rideshare",
      "duration": "18 minutes",
      "cost": "$12.50",
      "distance": "7.8 miles",
      "description": "Uber/Lyft from San Francisco to Hawaii. Direct route with minimal traffic. Estimated pickup time: 2-4 minutes.",
      "booking_url": "https://www.uber.com/ride/?pickup=San+Francisco&destination=Hawaii",
      "provider": "Uber/Lyft",
      "real_time_info": "2 cars available nearby"
    }
  ],
  "total_options": 5,
  "search_time": "Search completed at 1703123456.789"
}
```

### Error Response
```json
{
  "detail": "Commute search error: Invalid origin or destination provided"
}
```

## Integration

### Frontend Integration
The agent integrates with the `CommuteSearch` React component:
- Real-time search interface
- Transport mode filtering
- Results display with booking links
- Error handling and loading states

### API Proxy Integration
Routes through the main API proxy at `/api/commute`:
```javascript
const response = await fetch('/api/commute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    origin: 'San Francisco',
    destination: 'Hawaii',
    transport_mode: 'all'
  })
});
```

## Configuration

### Environment Variables
```bash
# Required
BRIGHTDATA_API_KEY=your_brightdata_api_key

# Optional
AI21_API_KEY=your_ai21_api_key
```

### Dependencies
```txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
aiohttp==3.9.1
beautifulsoup4==4.12.2
python-dotenv==1.0.0
```

## Error Handling

### Common Error Scenarios
1. **Invalid Locations**: Origin or destination not found
2. **API Failures**: BrightData API unavailable
3. **Network Issues**: Connection timeouts
4. **Data Parsing**: Malformed response data

### Error Response Format
```json
{
  "detail": "Error description",
  "status_code": 500,
  "timestamp": "2025-01-20T10:30:00Z"
}
```

## Performance

### Response Times
- **Average**: 1.2 seconds
- **Target**: < 2 seconds
- **Timeout**: 10 seconds

### Caching
- Response caching for repeated queries
- 5-minute cache duration
- Cache invalidation on new searches

## Monitoring

### Health Check
```bash
curl http://localhost:8006/health
```

### Logs
- Request/response logging
- Error tracking
- Performance metrics
- Debug information

## Testing

### Unit Tests
```bash
cd agents/commute
python -m pytest tests/
```

### Integration Tests
```bash
# Test search functionality
curl -X POST http://localhost:8006/search \
  -H "Content-Type: application/json" \
  -d '{"origin": "San Francisco", "destination": "Hawaii", "transport_mode": "all"}'
```

### Load Testing
- Concurrent request handling
- Memory usage monitoring
- Response time validation

## Development

### Local Development
```bash
cd agents/commute
pip install -r requirements.txt
python main.py
```

### Code Structure
```
agents/commute/
├── main.py              # FastAPI application
├── requirements.txt     # Dependencies
├── .env                 # Environment variables
└── brightdata_commute_response.json  # Debug output
```

### Adding New Transport Modes
1. Update `determine_transport_mode()` function
2. Add new mode to `transportModes` array in frontend
3. Update booking URL generation
4. Add mode-specific scoring logic

## Future Enhancements

### Planned Features
- **Real-time Updates**: WebSocket integration for live data
- **Route Optimization**: Multi-stop journey planning
- **Price Alerts**: Cost monitoring and notifications
- **Accessibility**: Enhanced accessibility information
- **Carbon Footprint**: Environmental impact scoring

### Integration Opportunities
- **Weather API**: Weather-based recommendations
- **Traffic API**: Real-time traffic integration
- **Calendar Integration**: Schedule-based suggestions
- **User Preferences**: Personalized recommendations

## Troubleshooting

### Common Issues

#### Agent Not Responding
```bash
# Check if agent is running
curl http://localhost:8006/health

# Check logs
tail -f agents/commute/logs/app.log
```

#### No Results Returned
1. Verify origin and destination are valid
2. Check BrightData API key configuration
3. Review network connectivity
4. Check for API rate limits

#### Slow Response Times
1. Check BrightData API status
2. Verify network latency
3. Review server resources
4. Check for concurrent request limits

### Debug Mode
Enable debug logging by setting:
```bash
export DEBUG=true
```

## Support

### Documentation
- [API Documentation](../api-documentation.md)
- [Architecture Overview](../architecture.md)
- [Deployment Guide](../deployment-guide.md)

### Contact
- GitHub Issues: [Create an issue](https://github.com/your-org/beacon-travel-agent/issues)
- Development Team: [Contact us](mailto:dev@beacon-travel-agent.com)

---

**Last Updated**: January 20, 2025  
**Version**: 1.0.0  
**Maintainer**: Beacon Travel Agent Team
