'use client';

import { useState } from 'react';
import FlightSearch from '@/components/FlightSearch';
import StaySearch from '@/components/StaySearch';
import RestaurantSearch from '@/components/RestaurantSearch';
import ActivitySearch from '@/components/ActivitySearch';
import ShoppingSearch from '@/components/ShoppingSearch';
import WorkSearch from '@/components/WorkSearch';
import AgentStatus from '@/components/AgentStatus';

export default function TravelAgent() {
  const [activeTab, setActiveTab] = useState('flights');

  const tabs = [
    { id: 'flights', name: 'Flights', icon: '✈️' },
    { id: 'hotels', name: 'Stay', icon: '🏨' },
    { id: 'restaurants', name: 'Food', icon: '🍽️' },
    { id: 'activities', name: 'Leisure', icon: '🎯' },
    { id: 'shopping', name: 'Shopping', icon: '🛍️' },
    { id: 'work', name: 'Work', icon: '💼' },
  ];

  const renderActiveComponent = () => {
    switch (activeTab) {
      case 'flights':
        return <FlightSearch />;
      case 'hotels':
        return <StaySearch />;
      case 'restaurants':
        return <RestaurantSearch />;
      case 'activities':
        return <ActivitySearch />;
      case 'shopping':
        return <ShoppingSearch />;
      case 'work':
        return <WorkSearch />;
      default:
        return <FlightSearch />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🧳 Beacon Travel Agent
          </h1>
          <p className="text-lg text-gray-600 mb-4">
            Your AI-powered travel companion for flights, hotels, dining, and more
          </p>
          <div className="flex justify-center space-x-4">
            <a
              href="/api-docs"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              📚 API Documentation
            </a>
            <a
              href="/api/proxy"
              target="_blank"
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              🔗 API Endpoint
            </a>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="flex flex-wrap justify-center gap-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </div>
        </div>

        {/* Agent Status */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <AgentStatus />
        </div>

        {/* Active Component */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          {renderActiveComponent()}
        </div>
      </div>
    </div>
  );
}
