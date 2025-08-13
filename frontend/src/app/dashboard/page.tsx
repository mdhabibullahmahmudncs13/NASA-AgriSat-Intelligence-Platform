'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import FarmBackground from '@/components/FarmBackground';

interface DashboardStats {
  totalFields: number;
  activeAlerts: number;
  weatherStatus: string;
  lastUpdate: string;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    totalFields: 0,
    activeAlerts: 0,
    weatherStatus: 'Loading...',
    lastUpdate: new Date().toLocaleString()
  });

  useEffect(() => {
    // Simulate loading dashboard data
    const loadDashboardData = async () => {
      // This would typically fetch from your API
      setStats({
        totalFields: 12,
        activeAlerts: 3,
        weatherStatus: 'Partly Cloudy',
        lastUpdate: new Date().toLocaleString()
      });
    };

    loadDashboardData();
  }, []);

  return (
    <ProtectedRoute>
      <div className="min-h-screen relative">
        <FarmBackground opacity={0.15} className="absolute inset-0" />
        
        <div className="relative z-10 p-6">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>
            
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Fields</h3>
                <p className="text-3xl font-bold text-blue-600">{stats.totalFields}</p>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-700 mb-2">Active Alerts</h3>
                <p className="text-3xl font-bold text-red-600">{stats.activeAlerts}</p>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-700 mb-2">Weather Status</h3>
                <p className="text-lg font-medium text-green-600">{stats.weatherStatus}</p>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-700 mb-2">Last Update</h3>
                <p className="text-sm text-gray-600">{stats.lastUpdate}</p>
              </div>
            </div>
            
            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors">
                  Add New Field
                </button>
                <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors">
                  View Weather Data
                </button>
                <button className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg transition-colors">
                  Generate Report
                </button>
              </div>
            </div>
            
            {/* Recent Activity */}
            <div className="bg-white rounded-lg shadow p-6 mt-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Recent Activity</h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between py-2 border-b">
                  <span className="text-gray-700">Field #3 irrigation completed</span>
                  <span className="text-sm text-gray-500">2 hours ago</span>
                </div>
                <div className="flex items-center justify-between py-2 border-b">
                  <span className="text-gray-700">Weather alert: High winds expected</span>
                  <span className="text-sm text-gray-500">4 hours ago</span>
                </div>
                <div className="flex items-center justify-between py-2">
                  <span className="text-gray-700">Satellite data updated</span>
                  <span className="text-sm text-gray-500">6 hours ago</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}