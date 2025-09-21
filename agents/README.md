# Beacon Travel Agents

This directory contains individual AI agents for different aspects of travel and lifestyle services. Each agent is a standalone FastAPI service that can be run independently.

## Agent Structure

Each agent follows the same architectural pattern:

- **main.py**: Core agent logic with FastAPI endpoints
- **requirements.txt**: Python dependencies
- **Port**: Each agent runs on a different port to avoid conflicts

## Available Agents

### 1. Flight Agent (Port 8000)
- **Location**: `flight/main.py`
- **Endpoints**: 
  - `POST /search-flights` - Search for flights
  - `POST /book-flight` - Book a flight
  - `GET /health` - Health check
- **Features**: Web scraping via BrightData API, flight scoring system

### 2. Food Agent (Port 8001)
- **Location**: `food/main.py`
- **Endpoints**:
  - `POST /search-restaurants` - Search for restaurants
  - `POST /make-reservation` - Make a reservation
  - `GET /health` - Health check
- **Features**: Restaurant recommendations with scoring based on cuisine, price, ratings

### 3. Leisure Agent (Port 8002)
- **Location**: `leisure/main.py`
- **Endpoints**:
  - `POST /search-activities` - Search for activities
  - `POST /book-activity` - Book an activity
  - `GET /health` - Health check
- **Features**: Activity recommendations with scoring based on type, duration, price

### 4. Shopping Agent (Port 8003)
- **Location**: `shopping/main.py`
- **Endpoints**:
  - `POST /search-products` - Search for products
  - `POST /purchase-product` - Purchase a product
  - `GET /health` - Health check
- **Features**: Product recommendations with scoring based on price, quality, brand reputation

### 5. Stay Agent (Port 8004)
- **Location**: `stay/main.py`
- **Endpoints**:
  - `POST /search-hotels` - Search for hotels
  - `POST /book-hotel` - Book a hotel
  - `GET /health` - Health check
- **Features**: Hotel recommendations with scoring based on amenities, location, price

### 6. Work Agent (Port 8005)
- **Location**: `work/main.py`
- **Endpoints**:
  - `POST /search-jobs` - Search for jobs
  - `POST /apply-job` - Apply for a job
  - `GET /health` - Health check
- **Features**: Job recommendations with scoring based on salary, company reputation, growth potential

## Running the Agents

### Prerequisites
1. Install Python 3.8+
2. Set up environment variables (see individual agent directories)
3. Install dependencies for each agent

### Starting Individual Agents

```bash
# Flight Agent
cd flight
pip install -r requirements.txt
python main.py

# Food Agent
cd ../food
pip install -r requirements.txt
python main.py

# Leisure Agent
cd ../leisure
pip install -r requirements.txt
python main.py

# Shopping Agent
cd ../shopping
pip install -r requirements.txt
python main.py

# Stay Agent
cd ../stay
pip install -r requirements.txt
python main.py

# Work Agent
cd ../work
pip install -r requirements.txt
python main.py
```

### Starting All Agents

You can run all agents simultaneously by opening multiple terminal windows or using a process manager like PM2.

## Environment Variables

Each agent requires the following environment variables:

```bash
# AI21 API Key (optional - for AI features)
AI21_API_KEY=your_ai21_api_key

# BrightData API Key (optional - for web scraping)
BRIGHTDATA_API_KEY=your_brightdata_api_key
```

## API Integration

The Next.js UI in the `ui/` directory integrates with these agents through their respective API endpoints. Each agent provides:

1. **Search endpoints** for finding relevant options
2. **Booking/Purchase endpoints** for completing transactions
3. **Health check endpoints** for monitoring
4. **Comprehensive scoring systems** for ranking results

## Scoring Systems

Each agent implements a sophisticated scoring system that considers multiple factors:

- **Price/Value**: Cost-effectiveness of options
- **Quality**: Ratings, reviews, and reputation
- **Location**: Geographic convenience and accessibility
- **Availability**: Current availability and booking options
- **Reputation**: Brand/company reputation and reliability

The scoring systems use weighted averages to provide overall scores (0-100) for easy comparison and ranking.

## Development

To add new agents or modify existing ones:

1. Follow the established pattern in existing agents
2. Use the same Pydantic models for consistency
3. Implement similar scoring systems
4. Add appropriate error handling and logging
5. Update this README with new agent information

## Testing

Each agent can be tested independently using:

```bash
# Health check
curl http://localhost:PORT/health

# Search example
curl -X POST http://localhost:PORT/search-endpoint \
  -H "Content-Type: application/json" \
  -d '{"search_params": "example"}'
```
