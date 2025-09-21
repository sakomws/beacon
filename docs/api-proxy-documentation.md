# 🌐 API Proxy Documentation

## Overview
The API Proxy serves as a unified gateway for all Beacon Travel Agent services, providing intelligent routing, consistent error handling, and real-time monitoring capabilities.

## Base URL
```
http://localhost:3000/api/proxy
```

## Features

### 🎯 Intelligent Routing
- Automatic request routing based on agent and action
- Support for all 6 travel agents
- Consistent request/response format
- Metadata injection for tracking

### 🔄 Error Handling
- Standardized error responses
- Detailed error information
- Agent-specific error mapping
- Graceful fallback mechanisms

### 📊 Monitoring
- Real-time agent health checks
- Response time tracking
- Error rate monitoring
- Performance metrics

## API Endpoints

### POST /api/proxy
Main endpoint for all agent operations.

#### Request Format
```json
{
  "agent": "flights|food|leisure|shopping|hotels|work",
  "action": "search|book|reserve|purchase|apply",
  ...agentSpecificData
}
```

#### Response Format
```json
{
  ...agentResponse,
  "_metadata": {
    "agent": "flights",
    "action": "search",
    "timestamp": "2025-09-21T01:40:03.383Z",
    "agentName": "Flight Agent"
  }
}
```

### GET /api/proxy
List all available agents and usage information.

#### Response Format
```json
{
  "availableAgents": [
    {
      "name": "flights",
      "port": 8000,
      "agentName": "Flight Agent",
      "searchEndpoint": "/search"
    }
  ],
  "usage": {
    "search": "POST /api/proxy with {\"agent\": \"flights\", \"action\": \"search\", ...searchData}",
    "book": "POST /api/proxy with {\"agent\": \"flights\", \"action\": \"book\", ...bookingData}",
    "health": "GET /api/proxy?agent=flights&action=health"
  }
}
```

### GET /api/proxy?agent={agent}&action=health
Check health status of specific agent.

#### Parameters
- `agent`: Agent name (flights, food, leisure, shopping, hotels, work)
- `action`: Action type (health, docs, openapi)

#### Response Format
```json
{
  "status": "healthy",
  "service": "flight-agent",
  "_metadata": {
    "agent": "flights",
    "action": "health",
    "timestamp": "2025-09-21T01:40:03.383Z",
    "agentName": "Flight Agent"
  }
}
```

## Agent Configuration

### Supported Agents

| Agent | Port | Search Action | Booking Action | Agent Name |
|-------|------|---------------|----------------|------------|
| `flights` | 8000 | `search` | `book` | Flight Agent |
| `food` | 8001 | `search` | `reserve` | Food Agent |
| `leisure` | 8002 | `search` | `book` | Leisure Agent |
| `shopping` | 8003 | `search` | `purchase` | Shopping Agent |
| `hotels` | 8004 | `search` | `book` | Stay Agent |
| `work` | 8005 | `search` | `apply` | Work Agent |

### Action Mapping

#### Search Actions
- `search`: Search for items (flights, restaurants, activities, etc.)

#### Booking Actions
- `book`: Book flights, hotels, activities
- `reserve`: Make restaurant reservations
- `purchase`: Buy products
- `apply`: Apply for jobs

#### Utility Actions
- `health`: Check agent health
- `docs`: Get API documentation
- `openapi`: Get OpenAPI specification

## Usage Examples

### Search Flights
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

### Search Restaurants
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

### Book a Hotel
```bash
curl -X POST http://localhost:3000/api/proxy \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "hotels",
    "action": "book",
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
curl "http://localhost:3000/api/proxy?agent=flights&action=health"
```

### List All Agents
```bash
curl http://localhost:3000/api/proxy
```

## Error Handling

### Error Response Format
```json
{
  "error": "Agent error description",
  "details": "Detailed error information",
  "agent": "flights",
  "action": "search"
}
```

### Common Error Codes

#### 400 Bad Request
- Missing required fields (`agent`, `action`)
- Invalid agent name
- Invalid action for agent

#### 422 Unprocessable Entity
- Validation errors from agent
- Invalid data format
- Missing required parameters

#### 500 Internal Server Error
- Agent communication failure
- Proxy processing error
- Network connectivity issues

### Error Examples

#### Invalid Agent
```json
{
  "error": "Unknown agent: invalid. Available agents: flights, food, leisure, shopping, hotels, work"
}
```

#### Agent Communication Error
```json
{
  "error": "Flight Agent error: 500",
  "details": "Internal server error",
  "agent": "flights",
  "action": "search"
}
```

#### Validation Error
```json
{
  "error": "Food Agent error: 422",
  "details": "{\"detail\":[{\"type\":\"float_parsing\",\"loc\":[\"body\",\"rating\"],\"msg\":\"Input should be a valid number\"}]}",
  "agent": "food",
  "action": "search"
}
```

## Monitoring and Health Checks

### Agent Health Monitoring
The proxy automatically monitors agent health and provides status information.

#### Health Check Endpoints
- Individual agent: `GET /api/proxy?agent={agent}&action=health`
- All agents: `GET /api/proxy`

#### Health Status Indicators
- `healthy`: Agent responding normally
- `unhealthy`: Agent not responding or error
- `checking`: Health check in progress

### Response Time Tracking
- Automatic response time measurement
- Performance metrics collection
- Slow query identification

### Error Rate Monitoring
- Error count tracking per agent
- Error rate calculations
- Alert thresholds

## Integration Patterns

### Frontend Integration
```javascript
// Search flights
const searchFlights = async (searchData) => {
  const response = await fetch('/api/proxy', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      agent: 'flights',
      action: 'search',
      ...searchData
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error);
  }
  
  return response.json();
};
```

### Backend Integration
```python
import requests

def search_flights(search_data):
    response = requests.post('http://localhost:3000/api/proxy', json={
        'agent': 'flights',
        'action': 'search',
        **search_data
    })
    
    if response.status_code != 200:
        raise Exception(f"API Error: {response.json()['error']}")
    
    return response.json()
```

### Microservice Integration
```go
type SearchRequest struct {
    Agent  string      `json:"agent"`
    Action string      `json:"action"`
    Data   interface{} `json:"data"`
}

func SearchFlights(data map[string]interface{}) (*SearchResponse, error) {
    req := SearchRequest{
        Agent:  "flights",
        Action: "search",
        Data:   data,
    }
    
    resp, err := http.Post("http://localhost:3000/api/proxy", 
        "application/json", 
        json.NewEncoder(req))
    
    if err != nil {
        return nil, err
    }
    
    defer resp.Body.Close()
    
    var result SearchResponse
    return &result, json.NewDecoder(resp.Body).Decode(&result)
}
```

## Performance Considerations

### Caching
- Response caching for repeated requests
- Agent health status caching
- Metadata caching

### Load Balancing
- Round-robin agent selection
- Health-based routing
- Failover mechanisms

### Rate Limiting
- Per-agent rate limiting
- Global rate limiting
- Burst handling

## Security

### Input Validation
- Request parameter validation
- Agent name validation
- Action type validation

### Error Information
- Sanitized error messages
- No sensitive data exposure
- Proper error logging

### CORS Configuration
- Cross-origin request handling
- Proper headers
- Security policies

## Development

### Local Development
```bash
# Start all agents
./start_all.sh

# Test proxy
curl -X POST http://localhost:3000/api/proxy \
  -H "Content-Type: application/json" \
  -d '{"agent": "flights", "action": "search", "origin": "SF", "destination": "Hawaii"}'
```

### Testing
```bash
# Test all agents
for agent in flights food leisure shopping hotels work; do
  curl "http://localhost:3000/api/proxy?agent=$agent&action=health"
done
```

### Debugging
- Enable debug logging
- Monitor network requests
- Check agent logs
- Review error responses
