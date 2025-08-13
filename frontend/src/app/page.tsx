'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import FarmBackground from '@/components/FarmBackground';
import ThreeDVisualization from '@/components/ThreeDVisualization';

interface DashboardStats {
  totalFarms: number;
  totalFields: number;
  averageHealth: number;
  activeAlerts: number;
}

export default function HomePage() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats>({
    totalFarms: 0,
    totalFields: 0,
    averageHealth: 0,
    activeAlerts: 0
  });

  useEffect(() => {
    if (!loading) {
      if (isAuthenticated) {
        router.push('/dashboard');
      }
    }
  }, [isAuthenticated, loading, router]);

  useEffect(() => {
    // Load dashboard stats for authenticated users
    const loadStats = async () => {
      // This would typically fetch from your API
      setStats({
        totalFarms: 25,
        totalFields: 156,
        averageHealth: 87,
        activeAlerts: 3
      });
    };

    if (isAuthenticated) {
      loadStats();
    }
  }, [isAuthenticated]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  // Landing page for unauthenticated users
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-emerald-50 relative overflow-hidden">
        <FarmBackground opacity={0.4} />
        
        {/* Hero Section */}
        <div className="relative z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
            <div className="text-center">
              {/* 3D Globe Visualization */}
              <div className="flex justify-center mb-8">
                <div className="relative w-48 h-48">
                  <ThreeDVisualization type="globe" className="w-full h-full" />
                </div>
              </div>
              
              {/* Enhanced Hero Title */}
              <h1 className="text-6xl md:text-7xl font-extrabold bg-gradient-to-r from-emerald-600 via-blue-600 to-emerald-700 bg-clip-text text-transparent mb-6 leading-tight">
                NASA AgriSat
                <br />
                <span className="text-5xl md:text-6xl">Intelligence Platform</span>
              </h1>
              
              {/* Enhanced Subtitle */}
              <p className="text-xl md:text-2xl text-gray-700 mb-4 max-w-4xl mx-auto font-medium leading-relaxed">
                Revolutionary Agricultural Monitoring System
              </p>
              <p className="text-lg text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed">
                Harness the power of NASA APIs and Earth observation data to monitor crop health, 
                track weather patterns, and receive real-time disaster alerts for smarter farming decisions.
              </p>
              
              {/* Enhanced CTA Buttons */}
              <div className="flex flex-col sm:flex-row justify-center gap-4 mb-20">
                <Link href="/auth/register" className="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-white bg-gradient-to-r from-emerald-600 to-blue-600 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300">
                  <span className="absolute inset-0 bg-gradient-to-r from-emerald-700 to-blue-700 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></span>
                  <span className="relative flex items-center">
                    Get Started Free
                    <svg className="w-5 h-5 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                    </svg>
                  </span>
                </Link>
                <Link href="/auth/login" className="group inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-gray-700 bg-white border-2 border-gray-300 rounded-xl shadow-lg hover:shadow-xl hover:border-emerald-500 transform hover:scale-105 transition-all duration-300">
                  <span className="flex items-center">
                    Sign In
                    <svg className="w-5 h-5 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                    </svg>
                  </span>
                </Link>
              </div>
            </div>
          </div>
        </div>
        
        {/* Features Section */}
        <div className="relative z-10 py-20 bg-white/80 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
                Powerful Features for Modern Agriculture
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Leverage cutting-edge technology to transform your agricultural operations
              </p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8">
              <div className="group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transform hover:-translate-y-2 transition-all duration-300 border border-gray-100">
                <div className="absolute inset-0 bg-gradient-to-br from-emerald-50 to-blue-50 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div className="relative">
                  <div className="w-32 h-32 mx-auto mb-6">
                    <ThreeDVisualization type="chart" className="w-full h-full" data={[
                      { label: 'Healthy', value: 75, color: '#10b981' },
                      { label: 'Warning', value: 20, color: '#f59e0b' },
                      { label: 'Critical', value: 5, color: '#ef4444' }
                    ]} />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4 text-center">Real-time Monitoring</h3>
                  <p className="text-gray-600 text-center leading-relaxed">Monitor your agricultural fields in real-time using NASA satellite data and advanced analytics for optimal crop management.</p>
                </div>
              </div>
              
              <div className="group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transform hover:-translate-y-2 transition-all duration-300 border border-gray-100">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div className="relative">
                  <div className="w-32 h-32 mx-auto mb-6">
                    <ThreeDVisualization type="satellite" className="w-full h-full" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4 text-center">Weather Intelligence</h3>
                  <p className="text-gray-600 text-center leading-relaxed">Access comprehensive weather data and forecasts to make informed agricultural decisions with precision timing.</p>
                </div>
              </div>
              
              <div className="group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transform hover:-translate-y-2 transition-all duration-300 border border-gray-100">
                <div className="absolute inset-0 bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div className="relative">
                  <div className="w-32 h-32 mx-auto mb-6">
                    <ThreeDVisualization type="particles" className="w-full h-full" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4 text-center">Disaster Alerts</h3>
                  <p className="text-gray-600 text-center leading-relaxed">Receive early warnings about natural disasters and environmental threats to protect your crops and investments.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Stats Section */}
        <div className="relative z-10 py-20 bg-gradient-to-r from-emerald-600 to-blue-600 overflow-hidden">
          {/* Floating Particles Background */}
          <div className="absolute inset-0 opacity-30">
            <ThreeDVisualization type="particles" className="w-full h-full" />
          </div>
          <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-white mb-4">
                Trusted by Agricultural Professionals
              </h2>
              <p className="text-xl text-emerald-100">
                Join thousands of farmers using NASA technology for better yields
              </p>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-white mb-2">10K+</div>
                <div className="text-emerald-100 font-medium">Active Users</div>
              </div>
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-white mb-2">50M+</div>
                <div className="text-emerald-100 font-medium">Acres Monitored</div>
              </div>
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-white mb-2">99.9%</div>
                <div className="text-emerald-100 font-medium">Uptime</div>
              </div>
              <div className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-white mb-2">24/7</div>
                <div className="text-emerald-100 font-medium">Support</div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Footer CTA */}
        <div className="relative z-10 py-20 bg-gray-900">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-4xl font-bold text-white mb-6">
              Ready to Transform Your Agriculture?
            </h2>
            <p className="text-xl text-gray-300 mb-8">
              Start monitoring your fields with NASA satellite technology today
            </p>
            <Link href="/auth/register" className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-gray-900 bg-white rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300">
              Get Started Now
              <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 py-8 relative min-h-screen">
      <FarmBackground opacity={0.35} />
      <div className="mb-12 text-center relative z-10">
        <h1 className="heading-primary mb-4">
          Welcome to NASA AgriSat Intelligence Platform
        </h1>
        <p className="text-muted text-xl max-w-3xl mx-auto">
          Monitor your agricultural operations with real-time satellite data and NASA APIs. 
          Get comprehensive insights into crop health, weather patterns, and field analytics.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16 relative z-10">
        <div className="stat-card">
          <div className="flex items-center">
            <div className="icon-primary">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div className="ml-5">
              <p className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Total Farms</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.totalFarms}</p>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center">
            <div className="icon-success">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <div className="ml-5">
              <p className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Total Fields</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.totalFields}</p>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center">
            <div className="icon-warning">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="ml-5">
              <p className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Average Health</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.averageHealth}%</p>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center">
            <div className="icon-danger">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div className="ml-5">
              <p className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Active Alerts</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.activeAlerts}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mb-8 relative z-10">
        <h2 className="heading-secondary mb-8 text-center">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <Link href="/dashboard" className="card group cursor-pointer">
            <div className="flex items-center mb-4">
              <div className="icon-primary mr-4">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900">Dashboard</h3>
            </div>
            <p className="text-muted mb-6 leading-relaxed">View comprehensive analytics and monitoring data with real-time insights into your agricultural operations.</p>
            <div className="flex items-center text-emerald-600 font-semibold group-hover:text-emerald-700 transition-colors">
              <span>Go to Dashboard</span>
              <svg className="w-5 h-5 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </div>
          </Link>

          <Link href="/fields" className="card group cursor-pointer">
            <div className="flex items-center mb-4">
              <div className="icon-success mr-4">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900">Manage Fields</h3>
            </div>
            <p className="text-muted mb-6 leading-relaxed">Add, edit, and monitor your agricultural fields with satellite imagery and health analytics.</p>
            <div className="flex items-center text-emerald-600 font-semibold group-hover:text-emerald-700 transition-colors">
              <span>Manage Fields</span>
              <svg className="w-5 h-5 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </div>
          </Link>

          <Link href="/weather" className="card group cursor-pointer">
            <div className="flex items-center mb-4">
              <div className="icon-warning mr-4">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900">Weather Data</h3>
            </div>
            <p className="text-muted mb-6 leading-relaxed">Access real-time weather information from NASA with detailed forecasts and historical data.</p>
            <div className="flex items-center text-teal-600 font-semibold group-hover:text-teal-700 transition-colors">
              <span>View Weather</span>
              <svg className="w-5 h-5 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}