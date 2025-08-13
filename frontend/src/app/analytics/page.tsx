'use client';

import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';

interface YieldData {
  month: string;
  predicted: number;
  actual: number;
}

interface CropDistribution {
  name: string;
  value: number;
  color: string;
}

interface HealthTrend {
  date: string;
  wheat: number;
  corn: number;
  soybean: number;
  rice: number;
}

export default function AnalyticsPage() {
  const [yieldData, setYieldData] = useState<YieldData[]>([]);
  const [cropDistribution, setCropDistribution] = useState<CropDistribution[]>([]);
  const [healthTrends, setHealthTrends] = useState<HealthTrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');

  useEffect(() => {
    // Mock data - replace with actual API calls
    const mockYieldData: YieldData[] = [
      { month: 'Jan', predicted: 2.5, actual: 2.3 },
      { month: 'Feb', predicted: 2.8, actual: 2.9 },
      { month: 'Mar', predicted: 3.2, actual: 3.1 },
      { month: 'Apr', predicted: 3.8, actual: 3.6 },
      { month: 'May', predicted: 4.2, actual: 4.4 },
      { month: 'Jun', predicted: 4.5, actual: 4.3 },
      { month: 'Jul', predicted: 4.8, actual: 4.9 },
    ];

    const mockCropDistribution: CropDistribution[] = [
      { name: 'Wheat', value: 35, color: '#f59e0b' },
      { name: 'Corn', value: 28, color: '#22c55e' },
      { name: 'Soybean', value: 20, color: '#3b82f6' },
      { name: 'Rice', value: 12, color: '#8b5cf6' },
      { name: 'Other', value: 5, color: '#6b7280' },
    ];

    const mockHealthTrends: HealthTrend[] = [
      { date: '2024-01-01', wheat: 85, corn: 78, soybean: 92, rice: 67 },
      { date: '2024-01-02', wheat: 87, corn: 80, soybean: 89, rice: 69 },
      { date: '2024-01-03', wheat: 89, corn: 82, soybean: 91, rice: 71 },
      { date: '2024-01-04', wheat: 86, corn: 79, soybean: 88, rice: 68 },
      { date: '2024-01-05', wheat: 91, corn: 85, soybean: 94, rice: 73 },
      { date: '2024-01-06', wheat: 88, corn: 83, soybean: 90, rice: 70 },
      { date: '2024-01-07', wheat: 92, corn: 87, soybean: 96, rice: 75 },
    ];

    setTimeout(() => {
      setYieldData(mockYieldData);
      setCropDistribution(mockCropDistribution);
      setHealthTrends(mockHealthTrends);
      setLoading(false);
    }, 1000);
  }, [selectedTimeRange]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="px-4 py-6">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
            <p className="text-gray-600">Advanced analytics and insights for your agricultural operations</p>
          </div>
          <div className="flex space-x-2">
            {(['7d', '30d', '90d', '1y'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setSelectedTimeRange(range)}
                className={`px-3 py-1 rounded-md text-sm font-medium ${
                  selectedTimeRange === range ? 'bg-primary-100 text-primary-800' : 'bg-gray-100 text-gray-600'
                }`}
              >
                {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : range === '90d' ? '90 Days' : '1 Year'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-success-100 rounded-lg">
              <svg className="w-6 h-6 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Yield</p>
              <p className="text-2xl font-bold text-gray-900">4.2 t/ha</p>
              <p className="text-xs text-success-600">+12% from last month</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-primary-100 rounded-lg">
              <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Efficiency</p>
              <p className="text-2xl font-bold text-gray-900">87%</p>
              <p className="text-xs text-primary-600">+5% from last month</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-warning-100 rounded-lg">
              <svg className="w-6 h-6 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Revenue</p>
              <p className="text-2xl font-bold text-gray-900">$125K</p>
              <p className="text-xs text-warning-600">+8% from last month</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-danger-100 rounded-lg">
              <svg className="w-6 h-6 text-danger-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Risk Score</p>
              <p className="text-2xl font-bold text-gray-900">23</p>
              <p className="text-xs text-success-600">-15% from last month</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Yield Prediction Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Yield Prediction vs Actual</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={yieldData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis label={{ value: 'Yield (t/ha)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="predicted" stroke="#3b82f6" strokeWidth={2} name="Predicted" strokeDasharray="5 5" />
              <Line type="monotone" dataKey="actual" stroke="#22c55e" strokeWidth={2} name="Actual" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Crop Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Crop Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={cropDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {cropDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Health Trends Chart */}
      <div className="card mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Crop Health Trends by Type</h3>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={healthTrends}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis label={{ value: 'Health Score', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="wheat" stroke="#f59e0b" strokeWidth={2} name="Wheat" />
            <Line type="monotone" dataKey="corn" stroke="#22c55e" strokeWidth={2} name="Corn" />
            <Line type="monotone" dataKey="soybean" stroke="#3b82f6" strokeWidth={2} name="Soybean" />
            <Line type="monotone" dataKey="rice" stroke="#8b5cf6" strokeWidth={2} name="Rice" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Insights and Recommendations */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">AI-Powered Insights & Recommendations</h3>
        <div className="space-y-4">
          <div className="flex items-start p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex-shrink-0">
              <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-blue-800">Yield Optimization Opportunity</h4>
              <p className="text-sm text-blue-700 mt-1">
                Based on satellite data analysis, fields in the northeast sector show 15% higher NDVI values. 
                Consider applying similar fertilization patterns to other areas for potential yield improvement.
              </p>
            </div>
          </div>

          <div className="flex items-start p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex-shrink-0">
              <svg className="w-5 h-5 text-green-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-green-800">Optimal Harvest Timing</h4>
              <p className="text-sm text-green-700 mt-1">
                Weather patterns and crop maturity indicators suggest optimal harvest window for wheat fields 
                is between August 15-25. This timing could maximize yield quality and quantity.
              </p>
            </div>
          </div>

          <div className="flex items-start p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex-shrink-0">
              <svg className="w-5 h-5 text-yellow-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-yellow-800">Resource Allocation Alert</h4>
              <p className="text-sm text-yellow-700 mt-1">
                Rice fields are showing lower efficiency compared to other crops. Consider reallocating 
                water resources or adjusting planting density for the next season to improve ROI.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}