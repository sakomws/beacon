'use client';

import { useState } from 'react';

export default function WorkSearch() {
  const [searchData, setSearchData] = useState({
    location: 'Hawaii',
    space_type: 'all',
    amenities: [] as string[],
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
          agent: 'work',
          action: 'search',
          ...searchData
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to search coworking spaces');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const amenities = [
    'WiFi', 'Coffee', 'Parking', 'Printing', 'Kitchen', 
    'Meeting Rooms', 'Phone Booths', 'Gym', 'Shower', 'Rooftop'
  ];

  const toggleAmenity = (amenity: string) => {
    setSearchData(prev => ({
      ...prev,
      amenities: prev.amenities.includes(amenity)
        ? prev.amenities.filter(a => a !== amenity)
        : [...prev.amenities, amenity]
    }));
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">🏢 Coworking Space Search</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Location
          </label>
          <input
            type="text"
            value={searchData.location}
            onChange={(e) => setSearchData({...searchData, location: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
            placeholder="City or area"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Space Type
          </label>
          <select
            value={searchData.space_type}
            onChange={(e) => setSearchData({...searchData, space_type: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
          >
            <option value="all">All Space Types</option>
            <option value="shared">Shared Workspace</option>
            <option value="private">Private Office</option>
            <option value="meeting_room">Meeting Room</option>
            <option value="hot_desk">Hot Desk</option>
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
            <option value="all">All Price Ranges</option>
            <option value="budget">Budget ($20-40/day)</option>
            <option value="mid">Mid-range ($40-80/day)</option>
            <option value="premium">Premium ($80+/day)</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Amenities
        </label>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
          {amenities.map(amenity => (
            <label key={amenity} className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={searchData.amenities.includes(amenity)}
                onChange={() => toggleAmenity(amenity)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">{amenity}</span>
            </label>
          ))}
        </div>
      </div>
      
      <button
        onClick={handleSearch}
        disabled={loading}
        className="w-full bg-blue-600 text-white py-3 px-6 rounded-md font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'Searching...' : 'Search Coworking Spaces'}
      </button>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          {error}
        </div>
      )}

      {results && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Found {results.total_results} coworking spaces
          </h3>
          <div className="grid gap-4">
            {results.coworking_spaces?.map((space: any, index: number) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="text-lg font-semibold text-gray-900">{space.name}</h4>
                  <div className="text-right">
                    <div className="text-lg font-bold text-green-600">
                      ${space.price_per_day}/day
                    </div>
                    <div className="text-sm text-gray-500">
                      ${space.price_per_month}/month
                    </div>
                  </div>
                </div>
                <p className="text-gray-600 mb-2">{space.address}</p>
                <p className="text-sm text-gray-700 mb-3">{space.description}</p>
                <div className="flex flex-wrap gap-2 mb-3">
                  {space.amenities?.map((amenity: string, i: number) => (
                    <span key={i} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                      {amenity}
                    </span>
                  ))}
                </div>
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center">
                      <span className="text-yellow-400">★</span>
                      <span className="ml-1 text-sm text-gray-600">
                        {space.rating} ({space.reviews_count} reviews)
                      </span>
                    </div>
                    <span className="text-sm text-green-600 font-medium">
                      {space.availability}
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-500">Overall Score</div>
                    <div className="text-lg font-bold text-blue-600">
                      {space.score?.toFixed(1)}/100
                    </div>
                  </div>
                </div>
                <div className="mt-4 flex gap-2">
                  {space.website && (
                    <a
                      href={space.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
                    >
                      Visit Website
                    </a>
                  )}
                  {space.booking_url && (
                    <a
                      href={space.booking_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    >
                      Book Now
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
