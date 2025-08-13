'use client';

import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';

interface WeatherData {
  date: string;
  temperature: number;
  humidity: number;
  precipitation: number;
  windSpeed: number;
  solarRadiation: number;
}

interface CurrentWeather {
  temperature: number;
  humidity: number;
  windSpeed: number;
  condition: string;
  icon: string;
}

export default function WeatherPage() {
  const [weatherData, setWeatherData] = useState<WeatherData[]>([]);
  const [currentWeather, setCurrentWeather] = useState<CurrentWeather | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedMetric, setSelectedMetric] = useState<'temperature' | 'humidity' | 'precipitation' | 'solarRadiation'>('temperature');

  useEffect(() => {
    // Mock data - replace with actual NASA POWER API calls
    const mockWeatherData: WeatherData[] = [
      { date: '2024-01-01', temperature: 22, humidity: 65, precipitation: 0, windSpeed: 12, solarRadiation: 18.5 },
      { date: '2024-01-02', temperature: 24, humidity: 70, precipitation: 2, windSpeed: 8, solarRadiation: 16.2 },
      { date: '2024-01-03', temperature: 26, humidity: 60, precipitation: 0, windSpeed: 15, solarRadiation: 20.1 },
      { date: '2024-01-04', temperature: 23, humidity: 75, precipitation: 5, windSpeed: 10, solarRadiation: 14.8 },
      { date: '2024-01-05', temperature: 25, humidity: 68, precipitation: 0, windSpeed: 13, solarRadiation: 19.3 },
      { date: '2024-01-06', temperature: 27, humidity: 62, precipitation: 1, windSpeed: 9, solarRadiation: 21.7 },
      { date: '2024-01-07', temperature: 28, humidity: 58, precipitation: 0, windSpeed: 11, solarRadiation: 22.4 },
    ];

    const mockCurrentWeather: CurrentWeather = {
      temperature: 25,
      humidity: 68,
      windSpeed: 12,
      condition: 'Partly Cloudy',
      icon: '⛅'
    };

    setTimeout(() => {
      setWeatherData(mockWeatherData);
      setCurrentWeather(mockCurrentWeather);
      setLoading(false);
    }, 1000);
  }, []);

  const getMetricData = () => {
    switch (selectedMetric) {
      case 'temperature':
        return { dataKey: 'temperature', color: '#f59e0b', unit: '°C', name: 'Temperature' };
      case 'humidity':
        return { dataKey: 'humidity', color: '#3b82f6', unit: '%', name: 'Humidity' };
      case 'precipitation':
        return { dataKey: 'precipitation', color: '#06b6d4', unit: 'mm', name: 'Precipitation' };
      case 'solarRadiation':
        return { dataKey: 'solarRadiation', color: '#f97316', unit: 'MJ/m²', name: 'Solar Radiation' };
      default:
        return { dataKey: 'temperature', color: '#f59e0b', unit: '°C', name: 'Temperature' };
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const metricInfo = getMetricData();

  return (
    <div className="px-4 py-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Weather Monitoring</h1>
        <p className="text-gray-600">Real-time weather data from NASA POWER API for agricultural planning</p>
      </div>

      {/* Current Weather Card */}
      {currentWeather && (
        <div className="card mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Current Conditions</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="flex items-center">
              <div className="text-4xl mr-4">{currentWeather.icon}</div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{currentWeather.temperature}°C</p>
                <p className="text-sm text-gray-600">{currentWeather.condition}</p>
              </div>
            </div>
            
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg mr-3">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
                </svg>
              </div>
              <div>
                <p className="text-lg font-semibold text-gray-900">{currentWeather.humidity}%</p>
                <p className="text-sm text-gray-600">Humidity</p>
              </div>
            </div>
            
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg mr-3">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m-9 0h10m-10 0a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V6a2 2 0 00-2-2" />
                </svg>
              </div>
              <div>
                <p className="text-lg font-semibold text-gray-900">{currentWeather.windSpeed} km/h</p>
                <p className="text-sm text-gray-600">Wind Speed</p>
              </div>
            </div>
            
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg mr-3">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <div>
                <p className="text-lg font-semibold text-gray-900">Clear</p>
                <p className="text-sm text-gray-600">UV Index: 6</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Weather Chart */}
      <div className="card mb-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900">7-Day Weather Trends</h2>
          <div className="flex space-x-2">
            <button
              onClick={() => setSelectedMetric('temperature')}
              className={`px-3 py-1 rounded-md text-sm font-medium ${
                selectedMetric === 'temperature' ? 'bg-orange-100 text-orange-800' : 'bg-gray-100 text-gray-600'
              }`}
            >
              Temperature
            </button>
            <button
              onClick={() => setSelectedMetric('humidity')}
              className={`px-3 py-1 rounded-md text-sm font-medium ${
                selectedMetric === 'humidity' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-600'
              }`}
            >
              Humidity
            </button>
            <button
              onClick={() => setSelectedMetric('precipitation')}
              className={`px-3 py-1 rounded-md text-sm font-medium ${
                selectedMetric === 'precipitation' ? 'bg-cyan-100 text-cyan-800' : 'bg-gray-100 text-gray-600'
              }`}
            >
              Precipitation
            </button>
            <button
              onClick={() => setSelectedMetric('solarRadiation')}
              className={`px-3 py-1 rounded-md text-sm font-medium ${
                selectedMetric === 'solarRadiation' ? 'bg-orange-100 text-orange-800' : 'bg-gray-100 text-gray-600'
              }`}
            >
              Solar Radiation
            </button>
          </div>
        </div>
        
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={weatherData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis label={{ value: metricInfo.unit, angle: -90, position: 'insideLeft' }} />
            <Tooltip formatter={(value) => [`${value} ${metricInfo.unit}`, metricInfo.name]} />
            <Area 
              type="monotone" 
              dataKey={metricInfo.dataKey} 
              stroke={metricInfo.color} 
              fill={metricInfo.color}
              fillOpacity={0.3}
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Weather Alerts */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Weather Alerts & Recommendations</h2>
        <div className="space-y-4">
          <div className="flex items-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex-shrink-0">
              <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-blue-800">Optimal Growing Conditions</h4>
              <p className="text-sm text-blue-700">Current weather conditions are ideal for crop growth. Temperature and humidity levels are within optimal range.</p>
            </div>
          </div>

          <div className="flex items-center p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex-shrink-0">
              <svg className="w-5 h-5 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-yellow-800">Irrigation Recommendation</h4>
              <p className="text-sm text-yellow-700">Low precipitation expected in the next 3 days. Consider scheduling irrigation for fields with moisture-sensitive crops.</p>
            </div>
          </div>

          <div className="flex items-center p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex-shrink-0">
              <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-green-800">High Solar Radiation</h4>
              <p className="text-sm text-green-700">Excellent solar radiation levels detected. Perfect conditions for photosynthesis and crop energy production.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}