'use client';

import { useState } from 'react';

export default function RestaurantSearch() {
  const [searchData, setSearchData] = useState({
    location: 'Hawaii',
    cuisine: 'all',
    price_range: 'all',
    rating: 'all'
  });
  
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<{
    total_results: number;
    options: Array<{
      name: string;
      cuisine: string;
      price_range: string;
      rating: number;
      address: string;
      description: string;
      website: string;
      booking_url: string;
      score: number;
    }>;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Convert rating to number if it's not "all"
      const searchPayload = {
        agent: 'food',
        action: 'search',
        ...searchData,
        rating: searchData.rating === 'all' ? 0.0 : parseFloat(searchData.rating)
      };
      
      const response = await fetch('/api/proxy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchPayload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to search restaurants');
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
      <h2 className="text-2xl font-bold text-gray-900 mb-6">🍽️ Restaurant Search</h2>
      
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
            placeholder="City or area"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Cuisine
          </label>
          <select
            value={searchData.cuisine}
            onChange={(e) => setSearchData({...searchData, cuisine: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
          >
            <option value="all">All Cuisines</option>
            <option value="italian">Italian</option>
            <option value="chinese">Chinese</option>
            <option value="japanese">Japanese</option>
            <option value="mexican">Mexican</option>
            <option value="indian">Indian</option>
            <option value="thai">Thai</option>
            <option value="french">French</option>
            <option value="american">American</option>
            <option value="seafood">Seafood</option>
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
            <option value="$">$ (Budget)</option>
            <option value="$$">$$ (Moderate)</option>
            <option value="$$$">$$$ (Expensive)</option>
            <option value="$$$$">$$$$ (Very Expensive)</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Minimum Rating
          </label>
          <select
            value={searchData.rating}
            onChange={(e) => setSearchData({...searchData, rating: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
          >
            <option value="all">All Ratings</option>
            <option value="4.5">4.5+ Stars</option>
            <option value="4.0">4.0+ Stars</option>
            <option value="3.5">3.5+ Stars</option>
            <option value="3.0">3.0+ Stars</option>
          </select>
        </div>
      </div>
      
      <button
        onClick={handleSearch}
        disabled={loading}
        className="w-full bg-blue-600 text-white py-3 px-6 rounded-md font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'Searching...' : 'Search Restaurants'}
      </button>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          Restaurant search error: {error}
        </div>
      )}

      {results && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Found {results.total_results} restaurants
          </h3>
          <div className="grid gap-4">
            {results.options?.map((restaurant, index: number) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="text-lg font-semibold text-gray-900">{restaurant.name}</h4>
                  <div className="text-right">
                    <div className="text-lg font-bold text-green-600">
                      {restaurant.price_range}
                    </div>
                    <div className="text-sm text-gray-500">
                      {restaurant.cuisine}
                    </div>
                  </div>
                </div>
                <p className="text-gray-600 mb-2">{restaurant.address}</p>
                <p className="text-sm text-gray-700 mb-3">{restaurant.description}</p>
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center">
                      <span className="text-yellow-400">★</span>
                      <span className="ml-1 text-sm text-gray-600">
                        {restaurant.rating} ({restaurant.reviews_count || 0} reviews)
                      </span>
                    </div>
                    <span className="text-sm text-green-600 font-medium">
                      {restaurant.availability || 'Available'}
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-500">Overall Score</div>
                    <div className="text-lg font-bold text-blue-600">
                      {restaurant.score?.toFixed(1)}/100
                    </div>
                  </div>
                </div>
                <div className="mt-4 flex gap-2">
                  {restaurant.website && (
                    <a
                      href={restaurant.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
                    >
                      Visit Website
                    </a>
                  )}
                  {restaurant.booking_url && (
                    <a
                      href={restaurant.booking_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    >
                      Book Table
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
