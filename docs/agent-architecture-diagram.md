# Agent Architecture Diagram

## System Overview

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        Mobile[Mobile App]
        API_Client[API Client]
    end
    
    subgraph "Frontend Layer"
        NextJS[Next.js Application]
        Components[React Components]
        State[State Management]
    end
    
    subgraph "API Gateway"
        Proxy[API Proxy Router]
        Auth[Authentication]
        RateLimit[Rate Limiting]
        CORS[CORS Handler]
    end
    
    subgraph "Agent Microservices"
        subgraph "Travel Services"
            Flight[Flight Agent<br/>Port: 8000]
            Stay[Stay Agent<br/>Port: 8004]
        end
        
        subgraph "Lifestyle Services"
            Food[Food Agent<br/>Port: 8001]
            Leisure[Leisure Agent<br/>Port: 8002]
        end
        
        subgraph "Business Services"
            Work[Work Agent<br/>Port: 8005]
            Shopping[Shopping Agent<br/>Port: 8003]
        end
    end
    
    subgraph "External APIs"
        BrightData[BrightData API<br/>Web Scraping]
        AI21[AI21 API<br/>AI Processing]
        Google[Google Search<br/>Fallback]
    end
    
    subgraph "Data Layer"
        Cache[Response Cache]
        Logs[Application Logs]
        Metrics[Performance Metrics]
    end
    
    Browser --> NextJS
    Mobile --> NextJS
    API_Client --> NextJS
    
    NextJS --> Components
    Components --> State
    NextJS --> Proxy
    
    Proxy --> Auth
    Proxy --> RateLimit
    Proxy --> CORS
    
    Proxy --> Flight
    Proxy --> Food
    Proxy --> Stay
    Proxy --> Work
    Proxy --> Leisure
    Proxy --> Shopping
    
    Flight --> BrightData
    Food --> BrightData
    Stay --> BrightData
    Work --> BrightData
    Leisure --> BrightData
    Shopping --> BrightData
    
    Flight --> AI21
    Food --> AI21
    Stay --> AI21
    Work --> AI21
    Leisure --> AI21
    Shopping --> AI21
    
    BrightData --> Cache
    AI21 --> Cache
    Google --> Cache
    
    Flight --> Logs
    Food --> Logs
    Stay --> Logs
    Work --> Logs
    Leisure --> Logs
    Shopping --> Logs
    
    Flight --> Metrics
    Food --> Metrics
    Stay --> Metrics
    Work --> Metrics
    Leisure --> Metrics
    Shopping --> Metrics
```

## Agent Communication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Frontend
    participant P as API Proxy
    participant A as Agent
    participant BD as BrightData
    participant AI as AI21
    participant C as Cache
    
    U->>UI: Search Request
    UI->>P: HTTP Request
    P->>P: Validate Request
    P->>A: Forward to Agent
    
    A->>C: Check Cache
    alt Cache Hit
        C-->>A: Return Cached Data
    else Cache Miss
        A->>BD: Web Scraping Request
        BD-->>A: Raw HTML/JSON Data
        A->>A: Parse Data
        A->>AI: AI Enhancement (Optional)
        AI-->>A: Enhanced Data
        A->>A: Calculate Scores
        A->>C: Store in Cache
    end
    
    A-->>P: Structured Response
    P-->>UI: JSON Response
    UI-->>U: Display Results
```

## Data Processing Pipeline

```mermaid
flowchart TD
    A[User Search Request] --> B[Agent Receives Request]
    B --> C[Validate Parameters]
    C --> D[Check Cache]
    
    D --> E{Cache Hit?}
    E -->|Yes| F[Return Cached Data]
    E -->|No| G[BrightData API Call]
    
    G --> H[Parse Response]
    H --> I[Extract Relevant Data]
    I --> J[Generate Booking Links]
    J --> K[AI Enhancement]
    K --> L[Calculate Scores]
    L --> M[Format Response]
    M --> N[Store in Cache]
    N --> O[Return to User]
    
    F --> O
```

## Agent Internal Architecture

```mermaid
graph TB
    subgraph "Agent Service"
        subgraph "API Layer"
            FastAPI[FastAPI Server]
            Routes[API Routes]
            Middleware[CORS Middleware]
        end
        
        subgraph "Business Logic"
            Search[Search Logic]
            Parser[Data Parser]
            Scorer[Scoring Algorithm]
            Validator[Input Validator]
        end
        
        subgraph "Data Models"
            Request[Request Models]
            Response[Response Models]
            Options[Option Models]
        end
        
        subgraph "External Integration"
            BrightDataClient[BrightData Client]
            AI21Client[AI21 Client]
            HTTPClient[HTTP Client]
        end
        
        subgraph "Utilities"
            Logger[Logging]
            Cache[Local Cache]
            Config[Configuration]
        end
    end
    
    FastAPI --> Routes
    Routes --> Middleware
    Routes --> Search
    
    Search --> Parser
    Search --> Scorer
    Search --> Validator
    
    Parser --> Request
    Parser --> Response
    Parser --> Options
    
    Search --> BrightDataClient
    Search --> AI21Client
    Search --> HTTPClient
    
    Search --> Logger
    Search --> Cache
    Search --> Config
```

## Service Dependencies

```mermaid
graph LR
    subgraph "Core Dependencies"
        Python[Python 3.11+]
        FastAPI[FastAPI]
        Pydantic[Pydantic]
        Requests[Requests]
    end
    
    subgraph "External Dependencies"
        BrightData[BrightData API]
        AI21[AI21 API]
    end
    
    subgraph "Optional Dependencies"
        Redis[Redis Cache]
        Database[Database]
        Monitoring[Monitoring Tools]
    end
    
    Python --> FastAPI
    FastAPI --> Pydantic
    FastAPI --> Requests
    
    FastAPI --> BrightData
    FastAPI --> AI21
    
    FastAPI --> Redis
    FastAPI --> Database
    FastAPI --> Monitoring
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx/HAProxy]
    end
    
    subgraph "Application Servers"
        subgraph "Server 1"
            UI1[Next.js UI]
            Agent1[Agent Instances]
        end
        
        subgraph "Server 2"
            UI2[Next.js UI]
            Agent2[Agent Instances]
        end
        
        subgraph "Server N"
            UIN[Next.js UI]
            AgentN[Agent Instances]
        end
    end
    
    subgraph "External Services"
        BrightData[BrightData API]
        AI21[AI21 API]
    end
    
    subgraph "Infrastructure"
        Cache[Redis Cache]
        DB[Database]
        Logs[Log Storage]
        Metrics[Metrics Collection]
    end
    
    LB --> UI1
    LB --> UI2
    LB --> UIN
    
    UI1 --> Agent1
    UI2 --> Agent2
    UIN --> AgentN
    
    Agent1 --> BrightData
    Agent2 --> BrightData
    AgentN --> BrightData
    
    Agent1 --> AI21
    Agent2 --> AI21
    AgentN --> AI21
    
    Agent1 --> Cache
    Agent2 --> Cache
    AgentN --> Cache
    
    Agent1 --> DB
    Agent2 --> DB
    AgentN --> DB
    
    Agent1 --> Logs
    Agent2 --> Logs
    AgentN --> Logs
    
    Agent1 --> Metrics
    Agent2 --> Metrics
    AgentN --> Metrics
```

## Error Handling Flow

```mermaid
flowchart TD
    A[Request Received] --> B[Validate Input]
    B --> C{Valid?}
    C -->|No| D[Return 422 Error]
    C -->|Yes| E[Process Request]
    
    E --> F[Call External API]
    F --> G{API Success?}
    G -->|No| H[Log Error]
    H --> I[Return 503 Error]
    
    G -->|Yes| J[Parse Response]
    J --> K{Parse Success?}
    K -->|No| L[Log Parse Error]
    L --> M[Return 500 Error]
    
    K -->|Yes| N[Process Data]
    N --> O[Calculate Scores]
    O --> P[Format Response]
    P --> Q[Return 200 Success]
    
    D --> R[Log Error]
    I --> R
    M --> R
    Q --> S[Log Success]
    R --> T[Update Metrics]
    S --> T
```

This architecture diagram provides a comprehensive view of the Beacon Travel Agent system, showing the relationships between components, data flow, and deployment structure.
