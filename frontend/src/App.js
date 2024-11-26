import React, { useState } from 'react';

export default function WeatherApp() {
  const [location, setLocation] = useState('');
  const [agents, setAgents] = useState([]);
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const API_URL = 'http://localhost:5001';

  const searchAgents = async () => {
    if (!location.trim()) {
      setError('Please enter a location');
      return;
    }
    
    setLoading(true);
    setError('');
    setAgents([]);
    setWeather(null);
    
    try {
      const response = await fetch(`${API_URL}/api/search-agents`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      setAgents(data.agents);
    } catch (error) {
      setError('Failed to fetch weather agents: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const getWeather = async (agentAddress) => {
    setLoading(true);
    setError('');
    setWeather(null);
    
    try {
      const response = await fetch(`${API_URL}/api/get-weather`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ location, agentAddress })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Poll for response
      const pollInterval = setInterval(async () => {
        const pollResponse = await fetch(`${API_URL}/api/get-weather-response`, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          credentials: 'include'
        });
        
        if (!pollResponse.ok) {
          throw new Error(`HTTP error! status: ${pollResponse.status}`);
        }
        
        const data = await pollResponse.json();
        
        if (data.analysis) {
          clearInterval(pollInterval);
          setWeather(data);
          setLoading(false);
        }
      }, 1000);

      // Stop polling after timeout
      setTimeout(() => {
        clearInterval(pollInterval);
        if (!weather) {
          setError('Request timed out');
          setLoading(false);
        }
      }, 30000);
      
    } catch (error) {
      setError('Failed to get weather: ' + error.message);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Weather Forecast</h1>
          <p className="text-gray-600">Choose from available weather agents</p>
        </header>

        {/* Search Input */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex gap-3">
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Enter location..."
              className="flex-1 p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={searchAgents}
              disabled={loading}
              className="px-6 py-3 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
            >
              {loading ? 'Searching...' : 'Search Agents'}
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">
              {error}
            </div>
          )}
        </div>

        {/* Agents List */}
        {agents.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Available Agents</h2>
            <div className="space-y-3">
              {agents.map((agent) => (
                <div 
                  key={agent.address}
                  className="flex justify-between items-center p-4 border rounded-md hover:bg-gray-50"
                >
                  <div>
                    <p className="font-medium text-gray-800">{agent.name}</p>
                    <p className="text-sm text-gray-600">Price: ${agent.price}</p>
                  </div>
                  <button
                    onClick={() => getWeather(agent.address)}
                    disabled={loading}
                    className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50"
                  >
                    {loading ? 'Getting Weather...' : 'Get Weather'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Weather Report */}
        {weather && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Weather Report</h2>
            <div className="space-y-2">
              <p><span className="font-medium">Location:</span> {weather.location}</p>
              <p><span className="font-medium">Price:</span> ${weather.price}</p>
              <p><span className="font-medium">Analysis:</span> {weather.analysis}</p>
            </div>
          </div>
        )}

        {/* Loading Indicator */}
        {loading && (
          <div className="text-center p-4">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
            <p className="mt-2 text-gray-600">Processing your request...</p>
          </div>
        )}
      </div>
    </div>
  );
}