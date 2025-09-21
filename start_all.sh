#!/bin/bash

# Beacon Travel Agent Startup Script
# Usage: ./start_all.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Beacon Travel Agent System${NC}"
echo "======================================"

# Check if we're in the right directory
if [ ! -d "agents" ] || [ ! -d "ui" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    echo -e "${YELLOW}   Expected directories: agents/ and ui/${NC}"
    exit 1
fi

# Check if lsof is available
if ! command -v lsof &> /dev/null; then
    echo -e "${RED}❌ Error: lsof command not found${NC}"
    echo -e "${YELLOW}   Please install lsof or use a different method to check ports${NC}"
    exit 1
fi

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local process_name=$2
    
    echo -e "${YELLOW}🔍 Checking for existing processes on port $port...${NC}"
    
    # Find processes using the port
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}⚠️  Found existing processes on port $port: $pids${NC}"
        echo -e "${YELLOW}🔄 Killing existing $process_name processes...${NC}"
        
        # Kill the processes
        echo "$pids" | xargs kill -9 2>/dev/null
        
        # Wait a moment for processes to die
        sleep 2
        
        # Verify they're gone
        local remaining_pids=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$remaining_pids" ]; then
            echo -e "${RED}❌ Failed to kill all processes on port $port${NC}"
            return 1
        else
            echo -e "${GREEN}✅ Successfully killed processes on port $port${NC}"
        fi
    else
        echo -e "${GREEN}✅ Port $port is free${NC}"
    fi
}

# Kill existing processes on all required ports
echo -e "${BLUE}🧹 Cleaning up existing processes...${NC}"
kill_port 3000 "UI"
kill_port 8000 "Flight Agent"
kill_port 8001 "Food Agent"
kill_port 8002 "Leisure Agent"
kill_port 8003 "Shopping Agent"
kill_port 8004 "Stay Agent"
kill_port 8005 "Work Agent"

echo ""

# Function to start an agent
start_agent() {
    local agent_name=$1
    local port=$2
    local directory=$3
    
    echo -e "${BLUE}Starting $agent_name on port $port...${NC}"
    if [ -d "$directory" ]; then
        cd "$directory"
        python main.py &
        local pid=$!
        echo -e "${GREEN}✅ $agent_name started with PID $pid on port $port${NC}"
        cd - > /dev/null
    else
        echo -e "${RED}❌ Directory $directory not found for $agent_name${NC}"
        return 1
    fi
}

# Start all agents
echo -e "${BLUE}📡 Starting AI Agents...${NC}"
start_agent "Flight Agent" 8000 "agents/flight"
start_agent "Food Agent" 8001 "agents/food"
start_agent "Leisure Agent" 8002 "agents/leisure"
start_agent "Shopping Agent" 8003 "agents/shopping"
start_agent "Stay Agent" 8004 "agents/stay"
start_agent "Work Agent" 8005 "agents/work"

# Wait a moment for agents to start
echo -e "${YELLOW}⏳ Waiting for agents to initialize...${NC}"
sleep 5

# Check if agents are running
echo -e "${BLUE}🔍 Checking agent health...${NC}"
agent_names=("Flight Agent" "Food Agent" "Leisure Agent" "Shopping Agent" "Stay Agent" "Work Agent")
ports=(8000 8001 8002 8003 8004 8005)

for i in "${!ports[@]}"; do
    port=${ports[$i]}
    name=${agent_names[$i]}
    
    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name (port $port) is healthy${NC}"
    else
        echo -e "${RED}❌ $name (port $port) is not responding${NC}"
    fi
done

# Start the UI
echo -e "${BLUE}🌐 Starting Next.js UI...${NC}"
if [ -d "ui" ] && [ -f "ui/package.json" ]; then
    cd ui
    npm run dev &
    ui_pid=$!
    echo -e "${GREEN}✅ UI started with PID $ui_pid on port 3000${NC}"
    cd - > /dev/null
else
    echo -e "${RED}❌ UI directory or package.json not found${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 All services started!${NC}"
echo "========================="
echo -e "${BLUE}🌐 UI: http://localhost:3000${NC}"
echo -e "${BLUE}✈️  Flight Agent: http://localhost:8000${NC}"
echo -e "${BLUE}🍽️  Food Agent: http://localhost:8001${NC}"
echo -e "${BLUE}🎯 Leisure Agent: http://localhost:8002${NC}"
echo -e "${BLUE}🛍️  Shopping Agent: http://localhost:8003${NC}"
echo -e "${BLUE}🏨 Stay Agent: http://localhost:8004${NC}"
echo -e "${BLUE}💼 Work Agent: http://localhost:8005${NC}"
echo ""
# Function to cleanup all processes
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down all services...${NC}"
    
    # Kill all agent processes
    for port in 8000 8001 8002 8003 8004 8005; do
        local pids=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$pids" ]; then
            echo -e "${YELLOW}🔄 Stopping processes on port $port...${NC}"
            echo "$pids" | xargs kill -9 2>/dev/null
        fi
    done
    
    # Kill UI process
    local ui_pids=$(lsof -ti:3000 2>/dev/null)
    if [ ! -z "$ui_pids" ]; then
        echo -e "${YELLOW}🔄 Stopping UI process...${NC}"
        echo "$ui_pids" | xargs kill -9 2>/dev/null
    fi
    
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Set up signal handlers for cleanup
trap cleanup SIGINT SIGTERM

echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for user to stop
wait
