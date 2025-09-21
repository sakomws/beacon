#!/bin/bash

echo "🚀 Starting Beacon Travel Agent System"
echo "======================================"

# Function to start an agent
start_agent() {
    local agent_name=$1
    local port=$2
    local directory=$3
    
    echo "Starting $agent_name on port $port..."
    cd "$directory"
    python main.py &
    local pid=$!
    echo "$agent_name started with PID $pid on port $port"
    cd ..
}

# Start all agents
echo "📡 Starting AI Agents..."
start_agent "Flight Agent" 8000 "flight"
start_agent "Food Agent" 8001 "agents/food"
start_agent "Leisure Agent" 8002 "agents/leisure"
start_agent "Shopping Agent" 8003 "agents/shopping"
start_agent "Stay Agent" 8004 "agents/stay"
start_agent "Work Agent" 8005 "agents/work"

# Wait a moment for agents to start
echo "⏳ Waiting for agents to initialize..."
sleep 5

# Check if agents are running
echo "🔍 Checking agent health..."
for port in 8000 8001 8002 8003 8004 8005; do
    if curl -s http://localhost:$port/health > /dev/null; then
        echo "✅ Agent on port $port is healthy"
    else
        echo "❌ Agent on port $port is not responding"
    fi
done

# Start the UI
echo "🌐 Starting Next.js UI..."
cd ui
npm run dev &
ui_pid=$!
echo "UI started with PID $ui_pid on port 3000"

echo ""
echo "🎉 All services started!"
echo "========================="
echo "🌐 UI: http://localhost:3000"
echo "✈️  Flight Agent: http://localhost:8000"
echo "🍽️  Food Agent: http://localhost:8001"
echo "🎯 Leisure Agent: http://localhost:8002"
echo "🛍️  Shopping Agent: http://localhost:8003"
echo "🏨 Stay Agent: http://localhost:8004"
echo "💼 Work Agent: http://localhost:8005"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait
