# 🌐 Frontend Documentation

## Overview
The Beacon Travel Agent frontend is built with Next.js 15, TypeScript, and Tailwind CSS, providing a modern, responsive interface for all travel services.

## Current Status
- **Status**: ✅ Fully functional and operational
- **Port**: 3000
- **All Tabs Working**: Flight, Food, Leisure, Shopping, Stay, Work, Commute
- **Real Data Integration**: All components display live data
- **Booking Links**: Direct booking integration for all services
- **UI Fixes**: Food agent now properly displays search results

## Technology Stack

- **Framework**: Next.js 15.5.3
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Hooks
- **API Integration**: Fetch API with proxy routing

## Project Structure

```
ui/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   ├── proxy/
│   │   │   │   └── route.ts          # Unified API proxy
│   │   │   ├── flights/search/
│   │   │   ├── food/search/
│   │   │   ├── leisure/search/
│   │   │   ├── shopping/search/
│   │   │   ├── hotels/search/
│   │   │   ├── work/search/
│   │   │   └── commute/
│   │   ├── api-docs/
│   │   │   └── page.tsx              # API documentation
│   │   ├── globals.css               # Global styles
│   │   ├── layout.tsx                # Root layout
│   │   └── page.tsx                  # Main page
│   └── components/
│       ├── AgentStatus.tsx           # Agent monitoring
│       ├── FlightSearch.tsx          # Flight search component
│       ├── StaySearch.tsx            # Stay search component (renamed from HotelSearch)
│       ├── RestaurantSearch.tsx      # Restaurant search component
│       ├── ActivitySearch.tsx        # Activity search component
│       ├── ShoppingSearch.tsx        # Shopping search component
│       ├── WorkSearch.tsx            # Work search component
│       └── CommuteSearch.tsx         # Commute search component
├── public/                           # Static assets
├── package.json                      # Dependencies
├── tailwind.config.ts               # Tailwind configuration
└── tsconfig.json                    # TypeScript configuration
```

## Key Features

### 🎯 Unified Interface
- Single-page application with tabbed navigation
- Consistent design across all services
- Real-time agent status monitoring
- Responsive design for all devices

### 🔄 API Integration
- Unified API proxy for all backend services
- Intelligent error handling and retry logic
- Loading states and user feedback
- Consistent data formatting

### 📊 Real-time Monitoring
- Live agent health status
- Response time tracking
- Error rate monitoring
- Auto-refresh capabilities

## Components

### Main Page (`page.tsx`)
The main application component that orchestrates all services.

**Features:**
- Tabbed navigation between services
- Agent status dashboard
- Service-specific search components
- Error handling and loading states

**Props:** None (root component)

**State:**
- `activeTab`: Currently selected service tab
- Component-specific state managed by individual components

### Agent Status (`AgentStatus.tsx`)
Real-time monitoring component for all backend agents.

**Features:**
- Health check for all agents
- Response time tracking
- Visual status indicators
- Auto-refresh every 30 seconds

**Props:** None

**State:**
- `agents`: Array of agent status objects
- `loading`: Loading state for health checks

**API Calls:**
- `GET /api/proxy?agent={agent}&action=health`

### Search Components
Each service has its own search component with consistent patterns:

#### FlightSearch.tsx
- Flight search form with origin, destination, dates
- Passenger and class selection
- Real-time flight results with scoring
- Booking integration

#### HotelSearch.tsx
- Hotel search with location, dates, guests
- Room configuration
- Amenity filtering
- Booking capabilities

#### RestaurantSearch.tsx
- Restaurant search by location and cuisine
- Price range and rating filters
- Reservation system integration

#### ActivitySearch.tsx
- Activity search by type and duration
- Price range filtering
- Booking system integration

#### ShoppingSearch.tsx
- Product search by category and brand
- Price range filtering
- Purchase integration

#### WorkSearch.tsx
- Job search by industry and experience
- Salary range filtering
- Application system integration

#### CommuteSearch.tsx
- Transportation search with origin and destination
- Multi-mode transport filtering (public transit, rideshare, driving, walking, cycling)
- Real-time duration, cost, and distance information
- Booking integration for each transport mode

## API Integration

### Unified Proxy API
All components use the unified proxy API at `/api/proxy` for consistent communication.

**Request Format:**
```typescript
{
  agent: 'flights' | 'food' | 'leisure' | 'shopping' | 'hotels' | 'work' | 'commute',
  action: 'search' | 'book' | 'reserve' | 'purchase' | 'apply',
  ...searchData
}
```

**Response Format:**
```typescript
{
  ...responseData,
  _metadata: {
    agent: string,
    action: string,
    timestamp: string,
    agentName: string
  }
}
```

### Error Handling
Consistent error handling across all components:

```typescript
try {
  const response = await fetch('/api/proxy', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ agent, action, ...data })
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Request failed');
  }

  const data = await response.json();
  setResults(data);
} catch (err) {
  setError(err instanceof Error ? err.message : 'An error occurred');
}
```

## Styling

### Tailwind CSS Configuration
The application uses Tailwind CSS for styling with a custom configuration.

**Key Design Tokens:**
- Primary colors: Blue palette
- Secondary colors: Gray palette
- Status colors: Green (success), Yellow (warning), Red (error)
- Spacing: Consistent 4px grid system
- Typography: System font stack

### Component Styling Patterns
- Consistent card-based layouts
- Hover states and transitions
- Loading spinners and states
- Form validation styling
- Responsive grid layouts

## State Management

### Local State
Each component manages its own state using React hooks:

```typescript
const [searchData, setSearchData] = useState(initialData);
const [results, setResults] = useState(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
```

### State Patterns
- Form data management
- Loading states
- Error handling
- Results caching
- User preferences

## Performance Optimizations

### Code Splitting
- Dynamic imports for heavy components
- Lazy loading of non-critical features
- Route-based code splitting

### Caching
- API response caching
- Component memoization
- Image optimization

### Bundle Optimization
- Tree shaking for unused code
- Dynamic imports for large libraries
- Optimized asset loading

## Development

### Getting Started
```bash
cd ui
npm install
npm run dev
```

### Available Scripts
- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run start`: Start production server
- `npm run lint`: Run ESLint

### Environment Variables
```bash
# No environment variables required for frontend
# All API calls use relative URLs
```

### Development Tools
- TypeScript for type safety
- ESLint for code quality
- Tailwind CSS IntelliSense
- Next.js development tools

## Deployment

### Build Process
```bash
npm run build
```

### Production Requirements
- Node.js 18+
- Static hosting or Node.js server
- Environment configuration

### Deployment Options
- Vercel (recommended for Next.js)
- Netlify
- AWS Amplify
- Docker containerization

## Testing

### Component Testing
```bash
# Install testing dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom

# Run tests
npm run test
```

### API Testing
```bash
# Test proxy API
curl -X POST http://localhost:3000/api/proxy \
  -H "Content-Type: application/json" \
  -d '{"agent": "flights", "action": "search", "origin": "SF", "destination": "Hawaii"}'

# Test commute API
curl -X POST http://localhost:3000/api/proxy \
  -H "Content-Type: application/json" \
  -d '{"agent": "commute", "action": "search", "origin": "SF", "destination": "Hawaii", "transport_mode": "all"}'
```

### E2E Testing
```bash
# Install Playwright
npm install --save-dev @playwright/test

# Run E2E tests
npx playwright test
```

## Troubleshooting

### Common Issues

#### Module Resolution Errors
```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

#### API Connection Issues
- Verify all agents are running
- Check proxy API health
- Review network requests in browser dev tools

#### Styling Issues
- Verify Tailwind CSS configuration
- Check for conflicting styles
- Use browser dev tools for debugging

### Debug Mode
```bash
# Enable debug logging
DEBUG=* npm run dev
```

## Browser Support

### Supported Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Mobile Support
- iOS Safari 14+
- Chrome Mobile 90+
- Samsung Internet 13+

### Progressive Enhancement
- Core functionality works without JavaScript
- Enhanced features with modern browsers
- Graceful degradation for older browsers
