# Flight Booking Agent

A Python FastAPI agent using the Maestro agent framework for intelligent flight booking and management.

## Features

- **AI-Powered Flight Search**: Uses Maestro framework for intelligent flight search with natural language processing
- **Smart Booking**: Automated flight booking with passenger validation and payment processing
- **Booking Management**: View, modify, and cancel bookings
- **Airport Search**: Search and validate airport codes and cities
- **Preference Handling**: Support for airline preferences, seat selection, and special requests
- **Real-time Validation**: Comprehensive validation of search criteria and booking details

## Architecture

The agent is built using:
- **FastAPI**: Modern, fast web framework for building APIs
- **Maestro Framework**: AI21's agent framework for intelligent task execution
- **Pydantic**: Data validation and settings management
- **AI21 API**: Language model integration for natural language processing

## Project Structure

```
flight/
├── main.py              # FastAPI application and API endpoints
├── flight_agent.py      # Core agent logic using Maestro framework
├── agent_config.py      # Data models and agent configuration
├── requirements.txt     # Python dependencies
├── env_example.txt      # Environment variables template
└── README.md           # This file
```

## Setup

### Prerequisites

- Python 3.8+
- AI21 API key

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd beacon/flight
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env_example.txt .env
   # Edit .env and add your API keys:
   # - AI21_API_KEY: Your AI21 API key for Maestro framework
   # - BRIGHTDATA_API_KEY: Your BrightData API key for web scraping
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Endpoints

### Health Check
- `GET /` - Basic API information
- `GET /health` - Health check endpoint

### Flight Search
- `POST /search` - Search for flights using AI agent
- `GET /airports/search?query={query}` - Search airports by name or code

### Flight Details
- `GET /flights/{flight_id}` - Get detailed flight information

### Booking
- `POST /book` - Book a flight using AI agent
- `GET /bookings/{booking_id}` - Get booking details
- `DELETE /bookings/{booking_id}` - Cancel a booking

## Usage Examples

### Search for Flights

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "LAX",
    "destination": "JFK", 
    "departure_date": "2024-02-15",
    "passengers": 2,
    "class_type": "economy",
    "preferences": {
      "preferred_airlines": ["AA", "DL"],
      "max_stops": 1,
      "seat_preference": "window"
    }
  }'
```

### Book a Flight

```bash
curl -X POST "http://localhost:8000/book" \
  -H "Content-Type: application/json" \
  -d '{
    "flight_id": "flight_0_0_20240101_120000",
    "passengers": [
      {
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-01-01",
        "passenger_type": "adult"
      }
    ],
    "payment": {
      "card_number": "4111111111111111",
      "expiry_date": "12/25",
      "cvv": "123",
      "cardholder_name": "John Doe",
      "billing_address": {
        "street": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip": "10001"
      }
    },
    "contact_info": {
      "email": "john.doe@example.com",
      "phone": "+1-555-123-4567"
    }
  }'
```

### Search Airports

```bash
curl "http://localhost:8000/airports/search?query=Los Angeles"
```

## Agent Framework Integration

The agent uses the Maestro framework to:

1. **Validate Input**: Ensure search criteria and booking details are valid
2. **Process Requests**: Use natural language understanding for complex queries
3. **Optimize Results**: Apply user preferences and constraints intelligently
4. **Handle Errors**: Provide meaningful error messages and suggestions
5. **Ensure Compliance**: Validate against airline policies and regulations

## Configuration

### Environment Variables

- `AI21_API_KEY`: Optional. Your AI21 API key for Maestro framework (falls back to mock mode if not provided)
- `BRIGHTDATA_API_KEY`: Optional. Your BrightData API key for web scraping (falls back to mock data if not provided)
- `DEBUG`: Optional. Enable debug mode (default: True)
- `LOG_LEVEL`: Optional. Logging level (default: INFO)

### Agent Requirements

The agent defines specific requirements for different operations:

- **Flight Search**: Origin/destination validation, date validation, price optimization
- **Booking**: Flight availability, passenger validation, payment processing
- **Cancellation**: Booking verification, refund processing, policy compliance

## Development

### Adding New Features

1. **Define Models**: Add new Pydantic models in `agent_config.py`
2. **Create Agent Logic**: Implement agent methods in `flight_agent.py`
3. **Add Endpoints**: Create new API endpoints in `main.py`
4. **Update Requirements**: Add new requirements for agent operations

### Testing

```bash
# Run the application
python main.py

# Test endpoints using curl or Postman
# Or use the interactive API docs at http://localhost:8000/docs
```

## API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
