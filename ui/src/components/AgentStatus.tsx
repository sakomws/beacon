'use client';

import { useState, useEffect } from 'react';

interface AgentStatus {
  name: string;
  status: 'healthy' | 'unhealthy' | 'checking';
  port: number;
  lastChecked: string;
  responseTime?: number;
}

export default function AgentStatus() {
  const [agents, setAgents] = useState<AgentStatus[]>([
    { name: 'Flight Agent', status: 'checking', port: 8000, lastChecked: '' },
    { name: 'Food Agent', status: 'checking', port: 8001, lastChecked: '' },
    { name: 'Leisure Agent', status: 'checking', port: 8002, lastChecked: '' },
    { name: 'Shopping Agent', status: 'checking', port: 8003, lastChecked: '' },
    { name: 'Stay Agent', status: 'checking', port: 8004, lastChecked: '' },
    { name: 'Work Agent', status: 'checking', port: 8005, lastChecked: '' },
  ]);

  const checkAgentHealth = async (agent: AgentStatus) => {
    const startTime = Date.now();
    try {
      // Map agent names to correct proxy names
      const agentMap: { [key: string]: string } = {
        'Flight Agent': 'flights',
        'Food Agent': 'food',
        'Leisure Agent': 'leisure',
        'Shopping Agent': 'shopping',
        'Stay Agent': 'hotels',
        'Work Agent': 'work'
      };
      
      const agentName = agentMap[agent.name] || agent.name.toLowerCase().split(' ')[0];
      const response = await fetch(`/api/proxy?agent=${agentName}&action=health`);
      const responseTime = Date.now() - startTime;
      
      if (response.ok) {
        return {
          ...agent,
          status: 'healthy' as const,
          lastChecked: new Date().toLocaleTimeString(),
          responseTime
        };
      } else {
        return {
          ...agent,
          status: 'unhealthy' as const,
          lastChecked: new Date().toLocaleTimeString(),
          responseTime
        };
      }
    } catch (error) {
      return {
        ...agent,
        status: 'unhealthy' as const,
        lastChecked: new Date().toLocaleTimeString(),
        responseTime: Date.now() - startTime
      };
    }
  };

  const checkAllAgents = async () => {
    const updatedAgents = await Promise.all(
      agents.map(agent => checkAgentHealth(agent))
    );
    setAgents(updatedAgents);
  };

  useEffect(() => {
    checkAllAgents();
    // Check every 30 seconds
    const interval = setInterval(checkAllAgents, 30000);
    return () => clearInterval(interval);
  }, []);

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

  const healthyCount = agents.filter(agent => agent.status === 'healthy').length;
  const totalCount = agents.length;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div className="flex items-center">
          <img 
            src="/beacon-logo-simple.svg" 
            alt="Beacon Logo" 
            className="w-8 h-8 mr-3"
          />
          <h3 className="text-xl font-semibold text-gray-900">
            Agent Status
          </h3>
        </div>
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-600">
            {healthyCount}/{totalCount} agents healthy
          </span>
          <button
            onClick={checkAllAgents}
            className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((agent, index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">{agent.name}</h4>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(agent.status)}`}>
                {getStatusIcon(agent.status)} {agent.status}
              </span>
            </div>
            
            <div className="text-sm text-gray-600 space-y-1">
              <div>Port: {agent.port}</div>
              <div>Last checked: {agent.lastChecked || 'Never'}</div>
              {agent.responseTime && (
                <div>Response time: {agent.responseTime}ms</div>
              )}
            </div>
          </div>
        ))}
      </div>

      {healthyCount === totalCount && (
        <div className="text-center text-green-600 font-medium">
          🎉 All agents are running smoothly!
        </div>
      )}

      {healthyCount < totalCount && (
        <div className="text-center text-yellow-600 font-medium">
          ⚠️ Some agents may be experiencing issues. Check the logs for details.
        </div>
      )}
    </div>
  );
}
