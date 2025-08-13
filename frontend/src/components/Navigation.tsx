'use client';

import { useAuth } from '@/contexts/AuthContext';
import { logout } from '@/lib/auth';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navigation() {
  const { isAuthenticated, user, loading } = useAuth();
  const pathname = usePathname();

  // Don't show navigation on auth pages
  if (pathname?.startsWith('/auth/')) {
    return null;
  }

  const handleLogout = async () => {
    await logout();
  };

  return (
    <header className="header-gradient shadow-xl border-b border-gray-100/50 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          <div className="flex items-center space-x-4">
            <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-br from-emerald-600 to-emerald-700 rounded-xl shadow-lg">
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <Link href={isAuthenticated ? "/dashboard" : "/"} className="block">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-emerald-700 bg-clip-text text-transparent">
                  NASA AgriSat Intelligence
                </h1>
                <p className="text-sm text-gray-500 font-medium">Agricultural Monitoring Platform</p>
              </Link>
            </div>
          </div>
          
          {!loading && (
            <nav className="flex items-center space-x-2">
              {isAuthenticated ? (
                <>
                  <Link href="/dashboard" className={`nav-link ${pathname === '/dashboard' ? 'bg-emerald-50 text-emerald-700' : ''}`}>
                    <svg className="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    Dashboard
                  </Link>
                  <Link href="/fields" className={`nav-link ${pathname === '/fields' ? 'bg-emerald-50 text-emerald-700' : ''}`}>
                    <svg className="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                    Fields
                  </Link>
                  <Link href="/weather" className={`nav-link ${pathname === '/weather' ? 'bg-emerald-50 text-emerald-700' : ''}`}>
                    <svg className="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
                    </svg>
                    Weather
                  </Link>
                  <Link href="/analytics" className={`nav-link ${pathname === '/analytics' ? 'bg-emerald-50 text-emerald-700' : ''}`}>
                    <svg className="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    Analytics
                  </Link>
                  <Link href="/farm-visualization" className={`nav-link ${pathname === '/farm-visualization' ? 'bg-emerald-50 text-emerald-700' : ''}`}>
                    <svg className="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                    </svg>
                    Farm Visualization
                  </Link>
                  
                  {/* User Menu */}
                  <div className="flex items-center space-x-3 ml-4 pl-4 border-l border-gray-200">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 bg-emerald-600 rounded-full flex items-center justify-center">
                        <span className="text-white text-sm font-medium">
                          {user?.first_name?.[0]}{user?.last_name?.[0]}
                        </span>
                      </div>
                      <div className="hidden sm:block">
                        <p className="text-sm font-medium text-gray-900">
                          {user?.first_name} {user?.last_name}
                        </p>
                        <p className="text-xs text-gray-500">{user?.email}</p>
                      </div>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="btn-secondary text-sm py-2 px-3"
                    >
                      <svg className="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      Logout
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <Link href="/auth/login" className="btn-secondary">
                    Sign In
                  </Link>
                  <Link href="/auth/register" className="btn-primary">
                    Sign Up
                  </Link>
                </>
              )}
            </nav>
          )}
        </div>
      </div>
    </header>
  );
}