# 🛍️ Shopping Agent Documentation

## Overview
The Shopping Agent provides product search and purchasing capabilities with comprehensive scoring based on price, quality, brand reputation, value, and availability.

## Current Status
- **Status**: ✅ Healthy and operational
- **Port**: 8003
- **Data Source**: BrightData API (real-time data only)
- **Booking Integration**: Direct purchase links included
- **UI Integration**: Fully functional with frontend

## API Endpoints

### Base URL
```
http://localhost:8003
```

### Endpoints

#### Search Products
```http
POST /search-products
Content-Type: application/json

{
  "location": "Hawaii",
  "category": "electronics",
  "price_range": "100-250",
  "brand": "apple",
  "max_results": 10
}
```

#### Purchase Product
```http
POST /purchase-product
Content-Type: application/json

{
  "product_id": "PROD001",
  "quantity": 1,
  "payment_info": {
    "card_number": "****-****-****-1234",
    "expiry": "12/25",
    "cvv": "123"
  },
  "shipping_address": {
    "street": "123 Main St",
    "city": "Honolulu",
    "state": "HI",
    "zip": "96801"
  }
}
```

#### Health Check
```http
GET /health
```

## Data Models

### ProductSearchRequest
```typescript
interface ProductSearchRequest {
  location: string;
  category: string;
  price_range: string;
  brand: string;
  max_results?: number;
}
```

### ProductOption
```typescript
interface ProductOption {
  name: string;
  category: string;
  brand: string;
  price: number;
  original_price: number;
  rating: number;
  store: string;
  address: string;
  website: string;
  description: string;
  availability: string;
  score: number;
  price_score: number;
  quality_score: number;
  value_score: number;
  reputation_score: number;
  availability_score: number;
}
```

### ProductSearchResponse
```typescript
interface ProductSearchResponse {
  search_id: string;
  location: string;
  category: string;
  products: ProductOption[];
  total_results: number;
}
```

## Scoring System

The Shopping Agent uses a comprehensive scoring system (0-100 scale) with the following weights:

- **Quality Score (30%)**: Product ratings and reviews
- **Price Score (25%)**: Cost-effectiveness
- **Value Score (20%)**: Discounts and deals
- **Reputation Score (15%)**: Brand reputation
- **Availability Score (10%)**: Stock availability

### Brand Reputation Scores
- Apple: 95
- Samsung: 90
- Sony: 85
- LG: 80
- Nike: 90
- Adidas: 85
- Puma: 75
- Zara: 80
- H&M: 70
- Uniqlo: 75
- Amazon: 85
- Google: 90
- Microsoft: 88
- Dell: 80
- HP: 75

### Price Range Categories
- Under $25: Budget products
- $25-$50: Affordable products
- $50-$100: Mid-range products
- $100-$250: Premium products
- $250-$500: High-end products
- Over $500: Luxury products

## Data Sources

### Real Data
- **BrightData API**: Web scraping from e-commerce platforms
- **Response Format**: JSON with product details and pricing
- **Update Frequency**: Real-time during search

### Mock Data Fallback
- Used when web scraping fails
- Provides realistic sample products
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

### Search for Products
```bash
curl -X POST http://localhost:8003/search-products \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Hawaii",
    "category": "electronics",
    "price_range": "100-250",
    "brand": "apple"
  }'
```

### Purchase a Product
```bash
curl -X POST http://localhost:8003/purchase-product \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "PROD001",
    "quantity": 1,
    "payment_info": {
      "card_number": "****-****-****-1234",
      "expiry": "12/25",
      "cvv": "123"
    },
    "shipping_address": {
      "street": "123 Main St",
      "city": "Honolulu",
      "state": "HI",
      "zip": "96801"
    }
  }'
```

### Check Agent Health
```bash
curl http://localhost:8003/health
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
cd agents/shopping
python main.py
```

### Testing
```bash
# Test search functionality
python -c "
import requests
response = requests.post('http://localhost:8003/search-products', json={
    'location': 'Hawaii',
    'category': 'electronics',
    'price_range': '100-250',
    'brand': 'apple'
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
    "agent": "shopping",
    "action": "search",
    "location": "Hawaii",
    "category": "electronics",
    "price_range": "100-250",
    "brand": "apple"
  }'
```

### Direct Integration
```javascript
const response = await fetch('http://localhost:8003/search-products', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    location: 'Hawaii',
    category: 'electronics',
    price_range: '100-250',
    brand: 'apple'
  })
});

const data = await response.json();
console.log(data.products);
```

## Search Parameters

### Product Categories
- `all`: All categories
- `fashion`: Fashion & Clothing
- `electronics`: Electronics
- `home`: Home & Garden
- `beauty`: Beauty & Health
- `sports`: Sports & Outdoors
- `books`: Books & Media
- `toys`: Toys & Games
- `automotive`: Automotive
- `jewelry`: Jewelry & Watches

### Store Types
- `all`: All stores
- `department`: Department Stores
- `boutique`: Boutiques
- `outlet`: Outlet Malls
- `local`: Local Shops
- `online`: Online Only
- `market`: Markets & Bazaars

### Price Ranges
- `all`: All prices
- `under-25`: Under $25
- `25-50`: $25 - $50
- `50-100`: $50 - $100
- `100-250`: $100 - $250
- `250-500`: $250 - $500
- `over-500`: Over $500

## Value Calculation

### Discount Scoring
- Original price vs. current price
- Percentage discount calculation
- Value score based on savings
- Limited-time offers consideration

### Quality Indicators
- Customer ratings and reviews
- Brand reputation scores
- Product specifications
- Warranty information

### Availability Status
- In Stock: 90 points
- Limited Stock: 60 points
- Out of Stock: 30 points
- Pre-order: 50 points
