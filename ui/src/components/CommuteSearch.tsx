"use client";

import React, { useState } from "react";

interface CommuteOption {
  mode: string;
  duration: string;
  cost: string;
  distance: string;
  description: string;
  booking_url: string;
  provider: string;
  real_time_info?: string;
}

interface CommuteResponse {
  origin: string;
  destination: string;
  options: CommuteOption[];
  total_options: number;
  search_time: string;
}

const CommuteSearch: React.FC = () => {
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [transportMode, setTransportMode] = useState("all");
  const [results, setResults] = useState<CommuteResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const transportModes = [
    { value: "all", label: "All Modes" },
    { value: "public_transit", label: "Public Transit" },
    { value: "rideshare", label: "Rideshare" },
    { value: "driving", label: "Driving" },
    { value: "walking", label: "Walking" },
    { value: "cycling", label: "Cycling" },
  ];

  const getModeIcon = (mode: string) => {
    switch (mode.toLowerCase()) {
      case "public transit":
        return "🚌";
      case "rideshare":
        return "🚗";
      case "driving":
        return "🚙";
      case "walking":
        return "🚶";
      case "cycling":
        return "🚴";
      default:
        return "🚌";
    }
  };

  const getModeColor = (mode: string) => {
    switch (mode.toLowerCase()) {
      case "public transit":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "rideshare":
        return "bg-purple-100 text-purple-800 border-purple-200";
      case "driving":
        return "bg-green-100 text-green-800 border-green-200";
      case "walking":
        return "bg-orange-100 text-orange-800 border-orange-200";
      case "cycling":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const handleSearch = async () => {
    if (!origin.trim() || !destination.trim()) {
      setError("Please enter both origin and destination");
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch("/api/commute", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          origin: origin.trim(),
          destination: destination.trim(),
          transport_mode: transportMode,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Commute Agent error: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-6">
        <span className="text-3xl mr-3">🚌</span>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Commute Search</h2>
          <p className="text-gray-600">Find the best way to get from A to B</p>
        </div>
      </div>

      <div className="space-y-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              From (Origin)
            </label>
            <input
              type="text"
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter starting location"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              To (Destination)
            </label>
            <input
              type="text"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter destination"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Transport Mode
          </label>
          <select
            value={transportMode}
            onChange={(e) => setTransportMode(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
          >
            {transportModes.map((mode) => (
              <option key={mode.value} value={mode.value}>
                {mode.label}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={handleSearch}
          disabled={loading}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? "Searching..." : "Find Commute Options"}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <span className="text-red-500 text-xl mr-2">❌</span>
            <p className="text-red-700 font-medium">Error: {error}</p>
          </div>
        </div>
      )}

      {results && (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center">
              <span className="text-green-500 text-xl mr-2">✅</span>
              <p className="text-green-700 font-medium">
                Found {results.total_options} commute options from {results.origin} to {results.destination}
              </p>
            </div>
          </div>

          <div className="space-y-4">
            {results.options.map((option, index) => (
              <div
                key={index}
                className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center">
                    <span className="text-2xl mr-3">
                      {getModeIcon(option.mode)}
                    </span>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {option.mode}
                      </h3>
                      <p className="text-sm text-gray-600">{option.provider}</p>
                    </div>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium border ${getModeColor(
                      option.mode
                    )}`}
                  >
                    {option.mode}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Duration</p>
                    <p className="font-semibold text-gray-900">{option.duration}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Cost</p>
                    <p className="font-semibold text-gray-900">{option.cost}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">Distance</p>
                    <p className="font-semibold text-gray-900">{option.distance}</p>
                  </div>
                </div>

                <p className="text-gray-700 mb-4">{option.description}</p>

                {option.real_time_info && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                    <div className="flex items-center">
                      <span className="text-blue-500 text-sm mr-2">ℹ️</span>
                      <p className="text-blue-700 text-sm font-medium">
                        {option.real_time_info}
                      </p>
                    </div>
                  </div>
                )}

                <a
                  href={option.booking_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  <span className="mr-2">🚀</span>
                  Book Now
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CommuteSearch;
