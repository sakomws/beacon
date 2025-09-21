'use client';

import { useState } from 'react';

interface StayOption {
  name: string;
  hotel_type: string;
  price_per_night: number;
  total_price: number;
  rating: number;
  address: string;
  phone: string;
  website: string;
  amenities: string[];
  description: string;
  availability: string;
  booking_url: string;
  score: number;
  price_score: number;
  quality_score: number;
  location_score: number;
  amenity_score: number;
  reputation_score: number;
}

export default function StaySearch() {
  const [searchData, setSearchData] = useState({
    location: 'Hawaii',
    check_in: '2025-10-03',
    check_out: '2025-10-10',
    guests: 2,
    rooms: 1
  });
  
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<StayOption[]>([]);
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
          agent: 'hotels',
          action: 'search',
          ...searchData
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Stay search error:', response.status, errorText);
        try {
          const errorData = JSON.parse(errorText);
          throw new Error(errorData.error || 'Failed to search hotels');
        } catch (parseError) {
          throw new Error(`Stay Agent error: ${response.status} - ${errorText}`);
        }
      }

      const data = await response.json();
      console.log('Stay search response:', data);
      setResults(data.options || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 8) return 'bg-green-100';
    if (score >= 6) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
          🏨 Stay Search
        </h2>
        <p className="text-gray-600 text-lg">Find the perfect accommodation for your trip</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-bold text-gray-800 mb-2">
            Location
          </label>
          <input
            type="text"
            value={searchData.location}
            onChange={(e) => setSearchData({...searchData, location: e.target.value})}
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black font-medium shadow-sm hover:border-blue-400 transition-colors"
            placeholder="City or destination"
          />
        </div>
        
        <div>
          <label className="block text-sm font-bold text-gray-800 mb-2">
            Check-in
          </label>
          <input
            type="date"
            value={searchData.check_in}
            onChange={(e) => setSearchData({...searchData, check_in: e.target.value})}
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black font-medium shadow-sm hover:border-blue-400 transition-colors"
          />
        </div>
        
        <div>
          <label className="block text-sm font-bold text-gray-800 mb-2">
            Check-out
          </label>
          <input
            type="date"
            value={searchData.check_out}
            onChange={(e) => setSearchData({...searchData, check_out: e.target.value})}
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black font-medium shadow-sm hover:border-blue-400 transition-colors"
          />
        </div>
        
        <div>
          <label className="block text-sm font-bold text-gray-800 mb-2">
            Guests
          </label>
          <select
            value={searchData.guests}
            onChange={(e) => setSearchData({...searchData, guests: parseInt(e.target.value)})}
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black font-medium shadow-sm hover:border-blue-400 transition-colors"
          >
            {[1,2,3,4,5,6].map(num => (
              <option key={num} value={num}>{num}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-bold text-gray-800 mb-2">
            Rooms
          </label>
          <select
            value={searchData.rooms}
            onChange={(e) => setSearchData({...searchData, rooms: parseInt(e.target.value)})}
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black font-medium shadow-sm hover:border-blue-400 transition-colors"
          >
            {[1,2,3,4,5].map(num => (
              <option key={num} value={num}>{num}</option>
            ))}
          </select>
        </div>
      </div>
      
      <button
        onClick={handleSearch}
        disabled={loading}
        className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-8 rounded-lg font-bold text-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
      >
        {loading ? '🔍 Searching...' : '🏨 Search Hotels'}
      </button>

      {error && (
        <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
          <p className="text-red-800 font-semibold">❌ Error: {error}</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-6">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-gray-800 mb-2">
              🎯 Found {results.length} Hotel Options
            </h3>
            <p className="text-gray-600">Sorted by AI-powered scoring</p>
          </div>
          
          <div className="grid gap-6">
            {results.map((hotel, index) => (
              <div key={index} className="bg-white rounded-xl shadow-lg border-2 border-gray-100 overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
                <div className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <h4 className="text-xl font-bold text-gray-900 mb-2">{hotel.name}</h4>
                      <p className="text-gray-600 mb-2">📍 {hotel.address}</p>
                      <p className="text-gray-700 text-sm leading-relaxed">{hotel.description}</p>
                    </div>
                    <div className="text-right ml-4">
                      <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-bold ${getScoreBgColor(hotel.score)} ${getScoreColor(hotel.score)}`}>
                        ⭐ {hotel.score.toFixed(1)}/10
                      </div>
                      <div className="text-2xl font-bold text-blue-600 mt-2">
                        {formatPrice(hotel.price_per_night)}
                      </div>
                      <div className="text-sm text-gray-500">per night</div>
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <div className="flex flex-wrap gap-2">
                      {hotel.amenities.map((amenity, idx) => (
                        <span key={idx} className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                          {amenity}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-sm font-medium text-gray-500">Price</div>
                      <div className="text-lg font-bold text-green-600">{(hotel.price_score || 0).toFixed(1)}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm font-medium text-gray-500">Location</div>
                      <div className="text-lg font-bold text-blue-600">{(hotel.location_score || 0).toFixed(1)}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm font-medium text-gray-500">Amenities</div>
                      <div className="text-lg font-bold text-purple-600">{(hotel.amenity_score || 0).toFixed(1)}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm font-medium text-gray-500">Quality</div>
                      <div className="text-lg font-bold text-yellow-600">{(hotel.quality_score || 0).toFixed(1)}</div>
                    </div>
                  </div>
                  
                  <div className="flex gap-3">
                    <a
                      href={hotel.booking_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 px-6 rounded-lg font-bold text-center hover:from-blue-700 hover:to-blue-800 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                    >
                      🏨 Book This Hotel
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}