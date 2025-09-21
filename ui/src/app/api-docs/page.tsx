'use client';

import { useState, useEffect } from 'react';

interface AgentInfo {
  name: string;
  port: number;
  agentName: string;
  searchEndpoint: string;
  status?: 'healthy' | 'unhealthy' | 'checking';
}

export default function ApiDocs() {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch('/api/proxy');
      const data = await response.json();
      setAgents(data.availableAgents || []);
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkAgentHealth = async (agentName: string) => {
    try {
      const response = await fetch(`/api/proxy?agent=${agentName}&action=health`);
      return response.ok;
    } catch (error) {
      return false;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-100';
      case 'unhealthy':
        return 'text-red-600 bg-red-100';
      case 'checking':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return '✅';
      case 'unhealthy':
        return '❌';
      case 'checking':
        return '⏳';
      default:
        return '❓';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            📚 API Documentation
          </h1>
          <p className="text-lg text-gray-600">
            Unified API Gateway for Beacon Travel Agents
          </p>
        </div>

        {/* API Overview */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">🌐 API Overview</h2>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-800">Base URL</h3>
              <code className="bg-gray-100 px-3 py-1 rounded text-sm">
                http://localhost:3000/api/proxy
              </code>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800">Supported Methods</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                <li><code className="bg-gray-100 px-2 py-1 rounded text-sm">POST</code> - Search and booking operations</li>
                <li><code className="bg-gray-100 px-2 py-1 rounded text-sm">GET</code> - Health checks and agent information</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Agent Status */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">🤖 Agent Status</h2>
          {loading ? (
            <div className="text-center py-4">Loading agent status...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agents.map((agent, index) => (
                <div
                  key={index}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-900">{agent.agentName}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(agent.status || 'checking')}`}>
                      {getStatusIcon(agent.status || 'checking')} {agent.status || 'checking'}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 space-y-1">
                    <div>Name: {agent.name}</div>
                    <div>Port: {agent.port}</div>
                    <div>Endpoint: {agent.searchEndpoint}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* API Examples */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">💡 API Examples</h2>
          
          <div className="space-y-6">
            {/* Search Example */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Search Flights</h3>
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto">
                <pre>{`curl -X POST http://localhost:3000/api/proxy \\
  -H "Content-Type: application/json" \\
  -d '{
    "agent": "flights",
    "action": "search",
    "origin": "San Francisco",
    "destination": "Hawaii",
    "departure_date": "2025-10-03",
    "return_date": "2025-10-24",
    "passengers": 1,
    "class_type": "economy"
  }'`}</pre>
              </div>
            </div>

            {/* Restaurant Search */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Search Restaurants</h3>
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto">
                <pre>{`curl -X POST http://localhost:3000/api/proxy \\
  -H "Content-Type: application/json" \\
  -d '{
    "agent": "food",
    "action": "search",
    "location": "Hawaii",
    "cuisine": "italian",
    "price_range": "$$",
    "rating": 4.0
  }'`}</pre>
              </div>
            </div>

            {/* Health Check */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Check Agent Health</h3>
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto">
                <pre>{`curl http://localhost:3000/api/proxy?agent=flights&action=health`}</pre>
              </div>
            </div>

            {/* Booking Example */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Book a Flight</h3>
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto">
                <pre>{`curl -X POST http://localhost:3000/api/proxy \\
  -H "Content-Type: application/json" \\
  -d '{
    "agent": "flights",
    "action": "book",
    "flight_id": "FL001",
    "passenger_info": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }'`}</pre>
              </div>
            </div>
          </div>
        </div>

        {/* Response Format */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">📋 Response Format</h2>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Success Response</h3>
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto">
                <pre>{`{
  "search_id": "search_20250920_184003",
  "origin": "San Francisco",
  "destination": "Hawaii",
  "flights": [...],
  "total_results": 5,
  "_metadata": {
    "agent": "flights",
    "action": "search",
    "timestamp": "2025-09-21T01:40:03.383Z",
    "agentName": "Flight Agent"
  }
}`}</pre>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Error Response</h3>
              <div className="bg-gray-900 text-red-400 p-4 rounded-lg overflow-x-auto">
                <pre>{`{
  "error": "Flight Agent error: 500",
  "details": "Internal server error",
  "agent": "flights",
  "action": "search"
}`}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
