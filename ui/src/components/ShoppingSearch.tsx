'use client';

import { useState } from 'react';

export default function ShoppingSearch() {
  const [searchData, setSearchData] = useState({
    location: 'Hawaii',
    category: 'all',
    price_range: 'all',
    brand: 'all'
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
          agent: 'shopping',
          action: 'search',
          ...searchData
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to search products');
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
      <h2 className="text-2xl font-bold text-gray-900 mb-6">🛍️ Shopping Search</h2>
      
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
            Category
          </label>
          <select
            value={searchData.category}
            onChange={(e) => setSearchData({...searchData, category: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
          >
            <option value="all">All Categories</option>
            <option value="fashion">Fashion & Clothing</option>
            <option value="electronics">Electronics</option>
            <option value="home">Home & Garden</option>
            <option value="beauty">Beauty & Health</option>
            <option value="sports">Sports & Outdoors</option>
            <option value="books">Books & Media</option>
            <option value="toys">Toys & Games</option>
            <option value="automotive">Automotive</option>
            <option value="jewelry">Jewelry & Watches</option>
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
            <option value="under-25">Under $25</option>
            <option value="25-50">$25 - $50</option>
            <option value="50-100">$50 - $100</option>
            <option value="100-250">$100 - $250</option>
            <option value="250-500">$250 - $500</option>
            <option value="over-500">Over $500</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Store Type
          </label>
          <select
            value={searchData.brand}
            onChange={(e) => setSearchData({...searchData, brand: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
          >
            <option value="all">All Stores</option>
            <option value="department">Department Stores</option>
            <option value="boutique">Boutiques</option>
            <option value="outlet">Outlet Malls</option>
            <option value="local">Local Shops</option>
            <option value="online">Online Only</option>
            <option value="market">Markets & Bazaars</option>
          </select>
        </div>
      </div>
      
      <button
        onClick={handleSearch}
        disabled={loading}
        className="w-full bg-blue-600 text-white py-3 px-6 rounded-md font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'Searching...' : 'Search Shopping'}
      </button>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <strong>Error:</strong> {error}
        </div>
      )}

      {results && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            🛍️ Shopping Results ({results.total_results} found)
          </h3>
          <div className="grid gap-4">
            {results.options?.map((product: any, index: number) => (
              <div key={index} className="bg-white p-4 rounded-lg shadow border">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="text-lg font-semibold text-gray-900">{product.name}</h4>
                  <span className="text-lg font-bold text-blue-600">${product.price}</span>
                </div>
                <p className="text-gray-600 mb-2">{product.description}</p>
                <div className="flex justify-between items-center">
                  <div className="flex space-x-4 text-sm text-gray-500">
                    <span>🏪 {product.store}</span>
                    <span>⭐ {product.rating}/5</span>
                    <span>📍 {product.location}</span>
                  </div>
                  <a
                    href={product.booking_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
                  >
                    Buy Now
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
