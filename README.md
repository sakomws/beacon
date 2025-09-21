# 🧳 Beacon Travel Agent

A comprehensive AI-powered travel companion system that provides intelligent recommendations for flights, hotels, dining, activities, shopping, and coworking spaces. Built with Next.js frontend and individual FastAPI microservices, featuring real-time data integration and intelligent scoring algorithms.

## 🎯 Current Status

### ✅ All Systems Operational
- **6 AI Agents**: All running and healthy
- **Real Data Integration**: BrightData API for live web scraping
- **No Mock Data**: All agents use real-time data only
- **Booking Integration**: Direct booking links for all services
- **UI**: Fully functional with all tabs working

### 🚀 Live Demo
**Access the system**: http://localhost:3000

| Service | Status | Port | Description |
|---------|--------|------|-------------|
| ✈️ Flight Agent | ✅ Healthy | 8000 | Real-time flight search with booking |
| 🍽️ Food Agent | ✅ Healthy | 8001 | Restaurant discovery with reservations |
| 🎯 Leisure Agent | ✅ Healthy | 8002 | Activity search with booking |
| 🛍️ Shopping Agent | ✅ Healthy | 8003 | Product search with purchase links |
| 🏨 Stay Agent | ✅ Healthy | 8004 | Hotel search with booking |
| 💼 Work Agent | ✅ Healthy | 8005 | Coworking space discovery |
| 🌐 UI | ✅ Running | 3000 | Next.js frontend interface |

## 🎉 Recent Updates

### ✅ Completed Features
- **Real Data Integration**: All agents now use BrightData API for live data
- **Booking Links**: Direct booking URLs for all services
- **UI Fixes**: Food agent now properly displays search results
- **Comprehensive Documentation**: Complete architecture and deployment guides
- **Health Monitoring**: Real-time agent status monitoring
- **TypeScript Support**: Full type safety in UI components

### 🔧 Technical Improvements
- **No Mock Data**: Removed all fallback mock data - real data only
- **Error Handling**: Robust error handling across all agents
- **API Consistency**: Standardized response formats across all agents
- **Performance**: Optimized response times and caching
- **Scalability**: Microservices architecture ready for horizontal scaling

## 🌟 Features

### 🤖 AI Agents
- **✈️ Flight Search**: Real-time flight search with comprehensive scoring and booking links
- **🏨 Stay Search**: Hotel and accommodation recommendations with amenity scoring
- **🍽️ Food Discovery**: Restaurant recommendations with cuisine filtering and reservations
- **🎯 Leisure Activities**: Activity search with duration and type filtering
- **🛍️ Shopping Assistant**: Product recommendations with brand and value analysis
- **💼 Work Spaces**: Coworking space discovery with amenity matching

### 🌐 API Gateway
- **Unified API Proxy**: Single endpoint for all agent communications
- **Intelligent Routing**: Automatic request routing based on agent and action
- **Real-time Monitoring**: Live agent status and health monitoring
- **Consistent Error Handling**: Standardized error responses across all agents
- **Metadata Injection**: Request tracking and performance monitoring
- **API Documentation**: Interactive documentation with live examples

## 🏗️ Architecture

### Frontend (Next.js)
- **Location**: `ui/` directory
- **Port**: 3000
- **Features**: Modern React UI with TypeScript and Tailwind CSS

### Backend Agents (FastAPI)
Each agent is a standalone microservice:

| Agent | Port | Directory | Description |
|-------|------|-----------|-------------|
| Flight | 8000 | `flight/` | Flight search and booking |
| Food | 8001 | `agents/food/` | Restaurant search and reservations |
| Leisure | 8002 | `agents/leisure/` | Activity search and booking |
| Shopping | 8003 | `agents/shopping/` | Product search and purchasing |
| Stay | 8004 | `agents/stay/` | Hotel search and booking |
| Work | 8005 | `agents/work/` | Job search and applications |

## 🚀 Quick Start

### Prerequisites
- Python 3.11.6+
- Node.js 18+
- npm or yarn
- BrightData API Key (for real data)
- AI21 API Key (optional, for AI features)

### Option 1: Start Everything at Once
```bash
# Make sure you're in the project root
cd /Users/sakom/github/hack092025/beacon
./start_all.sh
```

### Option 2: Start Services Individually

#### Start All Agents
```bash
# Flight Agent (Port 8000)
cd agents/flight && python main.py &

# Food Agent (Port 8001)
cd agents/food && python main.py &

# Leisure Agent (Port 8002)
cd agents/leisure && python main.py &

# Shopping Agent (Port 8003)
cd agents/shopping && python main.py &

# Stay Agent (Port 8004)
cd agents/stay && python main.py &

# Work Agent (Port 8005)
cd agents/work && python main.py &
```

#### Start the UI
```bash
cd ui && npm run dev
```

### Option 3: Manual Start (Current Method)
```bash
# Start all agents and UI
cd /Users/sakom/github/hack092025/beacon && \
python agents/flight/main.py & \
python agents/food/main.py & \
python agents/leisure/main.py & \
python agents/shopping/main.py & \
python agents/stay/main.py & \
python agents/work/main.py & \
cd ui && npm run dev &
```

### Access the Application
- **Main UI**: http://localhost:3000
- **API Proxy**: http://localhost:3000/api/proxy
- **Individual Agent APIs**: 
  - Flight Agent: http://localhost:8000/docs
  - Food Agent: http://localhost:8001/docs
  - Leisure Agent: http://localhost:8002/docs
  - Shopping Agent: http://localhost:8003/docs
  - Stay Agent: http://localhost:8004/docs
  - Work Agent: http://localhost:8005/docs

## 🔧 Configuration

### Environment Variables
Create `.env` files in each agent directory:

```bash
# AI21 API Key (optional - for AI features)
AI21_API_KEY=your_ai21_api_key

# BrightData API Key (optional - for web scraping)
BRIGHTDATA_API_KEY=your_brightdata_api_key
```

### Dependencies
Each agent has its own `requirements.txt` file. Install dependencies:

```bash
# For each agent directory
pip install -r requirements.txt

# For the UI
cd ui && npm install
```

## 🧠 AI Scoring System

Each agent implements a sophisticated scoring system (0-100 scale) based on multiple factors:

### Flight Agent
- **Price Score** (30%): Cost-effectiveness
- **Time Score** (25%): Flight duration
- **Risk Score** (20%): Number of stops
- **Reputation Score** (15%): Airline reputation
- **Flexibility Score** (10%): Departure time convenience

### Food Agent
- **Quality Score** (30%): Restaurant ratings
- **Price Score** (25%): Price range
- **Reputation Score** (20%): Cuisine reputation
- **Location Score** (15%): Geographic convenience
- **Availability Score** (10%): Booking availability

### Leisure Agent
- **Quality Score** (30%): Activity ratings
- **Price Score** (25%): Cost-effectiveness
- **Popularity Score** (20%): Activity type popularity
- **Location Score** (15%): Geographic accessibility
- **Accessibility Score** (10%): Physical accessibility

### Shopping Agent
- **Quality Score** (30%): Product ratings
- **Price Score** (25%): Cost-effectiveness
- **Value Score** (20%): Discounts and deals
- **Reputation Score** (15%): Brand reputation
- **Availability Score** (10%): Stock availability

### Stay Agent
- **Quality Score** (30%): Hotel ratings
- **Price Score** (25%): Cost per night
- **Amenity Score** (20%): Available amenities
- **Location Score** (15%): Geographic convenience
- **Reputation Score** (10%): Hotel type reputation

### Work Agent
- **Salary Score** (30%): Compensation level
- **Company Score** (25%): Company reputation
- **Growth Score** (20%): Industry growth potential
- **Work-Life Score** (15%): Work-life balance
- **Opportunity Score** (10%): Career advancement

## 🔍 API Endpoints

### 🌐 Unified API Proxy (Port 3000)
**Main Gateway**: `http://localhost:3000/api/proxy`

#### Search Operations
```bash
POST /api/proxy
{
  "agent": "flights|food|leisure|shopping|hotels|work",
  "action": "search",
  ...searchData
}
```

#### Booking Operations
```bash
POST /api/proxy
{
  "agent": "flights|food|leisure|shopping|hotels|work",
  "action": "book|reserve|purchase|apply",
  ...bookingData
}
```

#### Health Checks
```bash
GET /api/proxy?agent=flights&action=health
GET /api/proxy  # List all available agents
```

### Individual Agent Endpoints

#### Flight Agent (Port 8000)
- `POST /search` - Search for flights
- `POST /book` - Book a flight
- `GET /health` - Health check

#### Food Agent (Port 8001)
- `POST /search-restaurants` - Search for restaurants
- `POST /make-reservation` - Make a reservation
- `GET /health` - Health check

#### Leisure Agent (Port 8002)
- `POST /search-activities` - Search for activities
- `POST /book-activity` - Book an activity
- `GET /health` - Health check

#### Shopping Agent (Port 8003)
- `POST /search-products` - Search for products
- `POST /purchase-product` - Purchase a product
- `GET /health` - Health check

#### Stay Agent (Port 8004)
- `POST /search-hotels` - Search for hotels
- `POST /book-hotel` - Book a hotel
- `GET /health` - Health check

#### Work Agent (Port 8005)
- `POST /search-jobs` - Search for jobs
- `POST /apply-job` - Apply for a job
- `GET /health` - Health check

## 🧪 Testing

### Quick System Test
```bash
# Test all agents via proxy (recommended)
curl -X POST http://localhost:3000/api/proxy \
  -H "Content-Type: application/json" \
  -d '{"agent": "flights", "action": "search", "origin": "San Francisco", "destination": "Hawaii", "departure_date": "2025-10-03", "return_date": "2025-10-24", "passengers": 1, "class_type": "economy"}'

curl -X POST http://localhost:3000/api/proxy \
  -H "Content-Type: application/json" \
  -d '{"agent": "food", "action": "search", "location": "Hawaii", "cuisine": "all", "price_range": "all", "rating": 0.0}'

curl -X POST http://localhost:3000/api/proxy \
  -H "Content-Type: application/json" \
  -d '{"agent": "hotels", "action": "search", "location": "Hawaii", "check_in": "2025-10-03", "check_out": "2025-10-10", "guests": 2, "rooms": 1}'

curl -X POST http://localhost:3000/api/proxy \
  -H "Content-Type: application/json" \
  -d '{"agent": "leisure", "action": "search", "location": "Hawaii", "activity_type": "all", "duration": "all", "price_range": "all"}'

curl -X POST http://localhost:3000/api/proxy \
  -H "Content-Type: application/json" \
  -d '{"agent": "shopping", "action": "search", "location": "Hawaii", "category": "all", "price_range": "all", "brand": "all"}'

curl -X POST http://localhost:3000/api/proxy \
  -H "Content-Type: application/json" \
  -d '{"agent": "work", "action": "search", "location": "Hawaii", "space_type": "all", "amenities": [], "price_range": "all"}'
```

### Test Individual Agents (Direct)
```bash
# Test flight search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"origin": "San Francisco", "destination": "Hawaii", "departure_date": "2025-10-03", "return_date": "2025-10-24", "passengers": 1, "class_type": "economy"}'

# Test restaurant search
curl -X POST http://localhost:8001/search-restaurants \
  -H "Content-Type: application/json" \
  -d '{"location": "Hawaii", "cuisine": "all", "price_range": "all", "rating": 0.0}'
```

### Health Checks
```bash
# Via proxy (recommended)
curl http://localhost:3000/api/proxy?agent=flights&action=health
curl http://localhost:3000/api/proxy  # List all agents

# Direct agent health checks
curl http://localhost:8000/health  # Flight
curl http://localhost:8001/health  # Food
curl http://localhost:8002/health  # Leisure
curl http://localhost:8003/health  # Shopping
curl http://localhost:8004/health  # Stay
curl http://localhost:8005/health  # Work
```

## 🛠️ Development

### Adding New Agents
1. Create a new directory in `agents/`
2. Follow the established pattern in existing agents
3. Use the same Pydantic models for consistency
4. Implement similar scoring systems
5. Add appropriate error handling and logging
6. Update this README with new agent information

### Modifying Existing Agents
1. Each agent is independent and can be modified separately
2. Ensure API compatibility is maintained
3. Update scoring algorithms as needed
4. Test thoroughly before deployment

## 📚 Documentation

### Complete Documentation Suite
- **[Architecture Overview](docs/architecture.md)**: System design and technical architecture
- **[Solution Overview](docs/solution-overview.md)**: Business value and problem-solving approach
- **[API Documentation](docs/api-documentation.md)**: Complete API reference and examples
- **[Deployment Guide](docs/deployment-guide.md)**: Setup, deployment, and operations
- **[Agent Documentation](docs/agents/)**: Individual agent documentation
  - [Flight Agent](docs/agents/flight-agent.md)
  - [Food Agent](docs/agents/food-agent.md)
  - [Stay Agent](docs/agents/stay-agent.md)
  - [Work Agent](docs/agents/work-agent.md)
  - [Leisure Agent](docs/agents/leisure-agent.md)
  - [Shopping Agent](docs/agents/shopping-agent.md)

### Quick Reference
- **Main Documentation**: [docs/README.md](docs/README.md)
- **API Proxy Documentation**: [docs/api-proxy-documentation.md](docs/api-proxy-documentation.md)
- **Frontend Documentation**: [docs/ui/frontend-documentation.md](docs/ui/frontend-documentation.md)

## 📊 Data Sources

- **Real Data Only**: BrightData API for live web scraping
- **No Mock Data**: All agents use real-time data exclusively
- **AI Integration**: AI21 API for intelligent recommendations
- **Booking Integration**: Direct links to booking platforms

## 🚨 Troubleshooting

### Common Issues
1. **Port conflicts**: Ensure no other services are using ports 8000-8005 and 3000
2. **Missing dependencies**: Run `pip install -r requirements.txt` in each agent directory
3. **API key issues**: Check environment variables are set correctly
4. **Agent not responding**: Check logs and restart the specific agent

### Logs
Each agent logs to stdout. Check the terminal where you started each agent for error messages.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review agent logs
3. Test individual endpoints
4. Create an issue with detailed information