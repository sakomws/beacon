'use client';

import { useState } from 'react';

interface FlightOption {
  airline: string;
  flight_number: string;
  departure_time: string;
  arrival_time: string;
  duration: string;
  price: number;
  stops: number;
  aircraft: string;
  booking_url: string;
  score: number;
  price_score: number;
  time_score: number;
  risk_score: number;
  reputation_score: number;
  flexibility_score: number;
}

interface FlightSearchResponse {
  search_id: string;
  origin: string;
  destination: string;
  departure_date: string;
  return_date?: string;
  passengers: number;
  class_type: string;
  flights: FlightOption[];
  total_results: number;
}

export default function FlightSearch() {
  const [searchData, setSearchData] = useState({
    origin: 'San Francisco',
    destination: 'Hawaii',
    departure_date: '2025-10-03',
    return_date: '2025-10-24',
    passengers: 1,
    class_type: 'economy'
  });
  
  const [results, setResults] = useState<FlightSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
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
          agent: 'flights',
          action: 'search',
          ...searchData
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Search failed');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Search Form */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">✈️ Flight Search</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">From</label>
            <input
              type="text"
              value={searchData.origin}
              onChange={(e) => setSearchData({...searchData, origin: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
              placeholder="Origin city"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">To</label>
            <input
              type="text"
              value={searchData.destination}
              onChange={(e) => setSearchData({...searchData, destination: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
              placeholder="Destination city"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Departure Date</label>
            <input
              type="date"
              value={searchData.departure_date}
              onChange={(e) => setSearchData({...searchData, departure_date: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Return Date</label>
            <input
              type="date"
              value={searchData.return_date}
              onChange={(e) => setSearchData({...searchData, return_date: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Passengers</label>
            <select
              value={searchData.passengers}
              onChange={(e) => setSearchData({...searchData, passengers: parseInt(e.target.value)})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
            >
              <option value={1}>1 Passenger</option>
              <option value={2}>2 Passengers</option>
              <option value={3}>3 Passengers</option>
              <option value={4}>4 Passengers</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Class</label>
            <select
              value={searchData.class_type}
              onChange={(e) => setSearchData({...searchData, class_type: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
            >
              <option value="economy">Economy</option>
              <option value="business">Business</option>
              <option value="first">First Class</option>
            </select>
          </div>
        </div>
        
        <div className="text-center">
          <button
            onClick={handleSearch}
            disabled={loading}
            className="px-8 py-3 bg-blue-600 text-white font-bold text-lg rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
          >
            {loading ? 'Searching...' : 'Search Flights'}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-bold text-gray-900">
              ✈️ Flight Results ({results.total_results} found)
            </h3>
            <div className="text-sm text-gray-600">
              {results.origin} → {results.destination}
            </div>
          </div>
          
          <div className="space-y-6">
            {results.flights.map((flight, index) => (
              <div key={index} className="border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4 mb-2">
                      <h4 className="text-lg font-bold text-gray-900">{flight.airline}</h4>
                      <span className="text-sm text-gray-600">{flight.flight_number}</span>
                      <span className="text-sm text-gray-600">{flight.aircraft}</span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-gray-700">Departure:</span>
                        <div className="text-gray-900">{flight.departure_time}</div>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Arrival:</span>
                        <div className="text-gray-900">{flight.arrival_time}</div>
                      </div>
                      <div>
                        <span className="font-medium text-gray-700">Duration:</span>
                        <div className="text-gray-900">{flight.duration}</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="text-2xl font-bold text-blue-600 mb-2">
                      ${flight.price.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-600">
                      {flight.stops === 0 ? 'Non-stop' : `${flight.stops} stop${flight.stops > 1 ? 's' : ''}`}
                    </div>
                  </div>
                </div>
                
                {/* Score Breakdown */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4 text-sm">
                  <div className="text-center">
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${getScoreBg(flight.price_score)} ${getScoreColor(flight.price_score)}`}>
                      Price: {flight.price_score}%
                    </div>
                  </div>
                  <div className="text-center">
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${getScoreBg(flight.time_score)} ${getScoreColor(flight.time_score)}`}>
                      Time: {flight.time_score}%
                    </div>
                  </div>
                  <div className="text-center">
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${getScoreBg(flight.risk_score)} ${getScoreColor(flight.risk_score)}`}>
                      Risk: {flight.risk_score}%
                    </div>
                  </div>
                  <div className="text-center">
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${getScoreBg(flight.reputation_score)} ${getScoreColor(flight.reputation_score)}`}>
                      Rep: {flight.reputation_score}%
                    </div>
                  </div>
                  <div className="text-center">
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${getScoreBg(flight.flexibility_score)} ${getScoreColor(flight.flexibility_score)}`}>
                      Flex: {flight.flexibility_score}%
                    </div>
                  </div>
                </div>
                
                {/* Overall Score */}
                <div className="text-center mb-4">
                  <div className={`inline-block px-4 py-2 rounded-full text-lg font-bold ${getScoreBg(flight.score)} ${getScoreColor(flight.score)}`}>
                    Overall Score: {flight.score}%
                  </div>
                </div>
                
                {/* Booking Button */}
                <div className="flex justify-center pt-4 border-t border-gray-200">
                  <a
                    href={flight.booking_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-8 py-3 bg-blue-600 text-white font-bold text-lg rounded-xl hover:bg-blue-700 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center space-x-2"
                  >
                    <span>🛫</span>
                    <span>Book This Flight</span>
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