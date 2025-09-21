import { NextRequest, NextResponse } from 'next/server';

// Agent configuration
const AGENTS = {
  flights: {
    port: 8000,
    searchEndpoint: '/search',
    name: 'Flight Agent'
  },
  food: {
    port: 8001,
    searchEndpoint: '/search-restaurants',
    name: 'Food Agent'
  },
  leisure: {
    port: 8002,
    searchEndpoint: '/search-activities',
    name: 'Leisure Agent'
  },
  shopping: {
    port: 8003,
    searchEndpoint: '/search-products',
    name: 'Shopping Agent'
  },
  hotels: {
    port: 8004,
    searchEndpoint: '/search-hotels',
    name: 'Stay Agent'
  },
  work: {
    port: 8005,
    searchEndpoint: '/search-coworking',
    name: 'Work Agent'
  },
  commute: {
    port: 8006,
    searchEndpoint: '/search',
    name: 'Commute Agent'
  }
};

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { agent, action, ...searchData } = body;

    // Validate required fields
    if (!agent || !action) {
      return NextResponse.json(
        { error: 'Missing required fields: agent and action' },
        { status: 400 }
      );
    }

    // Check if agent exists
    if (!AGENTS[agent as keyof typeof AGENTS]) {
      return NextResponse.json(
        { error: `Unknown agent: ${agent}. Available agents: ${Object.keys(AGENTS).join(', ')}` },
        { status: 400 }
      );
    }

    const agentConfig = AGENTS[agent as keyof typeof AGENTS];
    const baseUrl = `http://localhost:${agentConfig.port}`;

    // Route based on action
    let endpoint = '';
    switch (action) {
      case 'search':
        endpoint = agentConfig.searchEndpoint;
        break;
      case 'book':
      case 'reserve':
      case 'purchase':
      case 'apply':
        // Map generic actions to agent-specific endpoints
        switch (agent) {
          case 'flights':
            endpoint = '/book';
            break;
          case 'food':
            endpoint = '/make-reservation';
            break;
          case 'leisure':
            endpoint = '/book-activity';
            break;
          case 'shopping':
            endpoint = '/purchase-product';
            break;
          case 'hotels':
            endpoint = '/book-hotel';
            break;
          case 'work':
            endpoint = '/book-space';
            break;
          case 'commute':
            endpoint = '/book';
            break;
          default:
            return NextResponse.json(
              { error: `Action '${action}' not supported for agent '${agent}'` },
              { status: 400 }
            );
        }
        break;
      case 'health':
        endpoint = '/health';
        break;
      default:
        return NextResponse.json(
          { error: `Unknown action: ${action}. Supported actions: search, book, reserve, purchase, apply, health` },
          { status: 400 }
        );
    }

    // Make request to the appropriate agent
    const response = await fetch(`${baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchData),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`${agentConfig.name} error:`, response.status, errorText);
      return NextResponse.json(
        { 
          error: `${agentConfig.name} error: ${response.status}`,
          details: errorText,
          agent: agent,
          action: action
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    
    // Add metadata to response
    return NextResponse.json({
      ...data,
      _metadata: {
        agent: agent,
        action: action,
        timestamp: new Date().toISOString(),
        agentName: agentConfig.name
      }
    });

  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { 
        error: 'Internal proxy error',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const agent = searchParams.get('agent');
    const action = searchParams.get('action') || 'health';

    // If no agent specified, return available agents
    if (!agent) {
      return NextResponse.json({
        availableAgents: Object.keys(AGENTS).map(key => ({
          name: key,
          port: AGENTS[key as keyof typeof AGENTS].port,
          agentName: AGENTS[key as keyof typeof AGENTS].name,
          searchEndpoint: AGENTS[key as keyof typeof AGENTS].searchEndpoint
        })),
        usage: {
          search: 'POST /api/proxy with {"agent": "flights", "action": "search", ...searchData}',
          book: 'POST /api/proxy with {"agent": "flights", "action": "book", ...bookingData}',
          health: 'GET /api/proxy?agent=flights&action=health'
        }
      });
    }

    // Check if agent exists
    if (!AGENTS[agent as keyof typeof AGENTS]) {
      return NextResponse.json(
        { error: `Unknown agent: ${agent}. Available agents: ${Object.keys(AGENTS).join(', ')}` },
        { status: 400 }
      );
    }

    const agentConfig = AGENTS[agent as keyof typeof AGENTS];
    const baseUrl = `http://localhost:${agentConfig.port}`;

    // Route based on action
    let endpoint = '';
    switch (action) {
      case 'health':
        endpoint = '/health';
        break;
      case 'docs':
        endpoint = '/docs';
        break;
      case 'openapi':
        endpoint = '/openapi.json';
        break;
      default:
        return NextResponse.json(
          { error: `Unknown action: ${action}. Supported actions: health, docs, openapi` },
          { status: 400 }
        );
    }

    // Make request to the appropriate agent
    const response = await fetch(`${baseUrl}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`${agentConfig.name} error:`, response.status, errorText);
      return NextResponse.json(
        { 
          error: `${agentConfig.name} error: ${response.status}`,
          details: errorText,
          agent: agent,
          action: action
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    
    // Add metadata to response
    return NextResponse.json({
      ...data,
      _metadata: {
        agent: agent,
        action: action,
        timestamp: new Date().toISOString(),
        agentName: agentConfig.name
      }
    });

  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { 
        error: 'Internal proxy error',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
