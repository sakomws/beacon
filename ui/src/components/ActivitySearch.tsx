'use client';

import { useState } from 'react';

export default function ActivitySearch() {
  const [searchData, setSearchData] = useState({
    location: 'Hawaii',
    activity_type: 'all',
    duration: 'all',
    price_range: 'all'
  });
  
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/proxy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent: 'leisure',
          action: 'search',
          ...searchData
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to search activities');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">🎯 Activity Search</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Location
          </label>
          <input
            type="text"
            value={searchData.location}
            onChange={(e) => setSearchData({...searchData, location: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
            placeholder="City or destination"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Activity Type
          </label>
          <select
            value={searchData.activity_type}
            onChange={(e) => setSearchData({...searchData, activity_type: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
          >
            <option value="all">All Activities</option>
            <option value="outdoor">Outdoor Adventures</option>
            <option value="cultural">Cultural Experiences</option>
            <option value="entertainment">Entertainment</option>
            <option value="sports">Sports & Recreation</option>
            <option value="tours">Tours & Sightseeing</option>
            <option value="nightlife">Nightlife</option>
            <option value="shopping">Shopping</option>
            <option value="wellness">Wellness & Spa</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Duration
          </label>
          <select
            value={searchData.duration}
            onChange={(e) => setSearchData({...searchData, duration: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
          >
            <option value="all">Any Duration</option>
            <option value="1-2">1-2 hours</option>
            <option value="half-day">Half day (3-4 hours)</option>
            <option value="full-day">Full day (6-8 hours)</option>
            <option value="multi-day">Multi-day</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Price Range
          </label>
          <select
            value={searchData.price_range}
            onChange={(e) => setSearchData({...searchData, price_range: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
          >
            <option value="all">All Prices</option>
            <option value="free">Free</option>
            <option value="under-25">Under $25</option>
            <option value="25-50">$25 - $50</option>
            <option value="50-100">$50 - $100</option>
            <option value="over-100">Over $100</option>
          </select>
        </div>
      </div>
      
      <button
        onClick={handleSearch}
        disabled={loading}
        className="w-full bg-blue-600 text-white py-3 px-6 rounded-md font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'Searching...' : 'Search Activities'}
      </button>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <strong>Error:</strong> {error}
        </div>
      )}

      {results && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            🎯 Activity Results ({results.total_results} found)
          </h3>
          <div className="grid gap-4">
            {results.options?.map((activity: any, index: number) => (
              <div key={index} className="bg-white p-4 rounded-lg shadow border">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="text-lg font-semibold text-gray-900">{activity.name}</h4>
                  <span className="text-lg font-bold text-blue-600">${activity.price}</span>
                </div>
                <p className="text-gray-600 mb-2">{activity.description}</p>
                <div className="flex justify-between items-center">
                  <div className="flex space-x-4 text-sm text-gray-500">
                    <span>📍 {activity.location}</span>
                    <span>⏱️ {activity.duration}</span>
                    <span>⭐ {activity.rating}/5</span>
                  </div>
                  <a
                    href={activity.booking_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
                  >
                    Book Now
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
