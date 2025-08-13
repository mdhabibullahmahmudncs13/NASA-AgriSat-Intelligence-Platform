import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Utility function to merge Tailwind CSS classes
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Date formatting utilities
export const formatDate = {
  // Format date to YYYY-MM-DD
  toISO: (date: Date): string => {
    return date.toISOString().split('T')[0];
  },

  // Format date to readable format
  toReadable: (date: string | Date): string => {
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  },

  // Format date with time
  toDateTime: (date: string | Date): string => {
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  },

  // Get relative time (e.g., "2 hours ago")
  toRelative: (date: string | Date): string => {
    const d = typeof date === 'string' ? new Date(date) : date;
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - d.getTime()) / 1000);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days ago`;
    if (diffInSeconds < 31536000) return `${Math.floor(diffInSeconds / 2592000)} months ago`;
    return `${Math.floor(diffInSeconds / 31536000)} years ago`;
  },
};

// Number formatting utilities
export const formatNumber = {
  // Format number with commas
  withCommas: (num: number): string => {
    return num.toLocaleString();
  },

  // Format as currency
  asCurrency: (num: number, currency: string = 'USD'): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(num);
  },

  // Format as percentage
  asPercentage: (num: number, decimals: number = 1): string => {
    return `${num.toFixed(decimals)}%`;
  },

  // Format with units (e.g., hectares, tons)
  withUnit: (num: number, unit: string, decimals: number = 1): string => {
    return `${num.toFixed(decimals)} ${unit}`;
  },

  // Format large numbers with K, M, B suffixes
  compact: (num: number): string => {
    if (num >= 1e9) return `${(num / 1e9).toFixed(1)}B`;
    if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`;
    if (num >= 1e3) return `${(num / 1e3).toFixed(1)}K`;
    return num.toString();
  },
};

// Health score utilities
export const healthScore = {
  // Get health status from score
  getStatus: (score: number): 'excellent' | 'good' | 'fair' | 'poor' | 'critical' => {
    if (score >= 90) return 'excellent';
    if (score >= 75) return 'good';
    if (score >= 60) return 'fair';
    if (score >= 40) return 'poor';
    return 'critical';
  },

  // Get color class for health status
  getColorClass: (status: string): string => {
    switch (status) {
      case 'excellent': return 'text-green-600 bg-green-100';
      case 'good': return 'text-blue-600 bg-blue-100';
      case 'fair': return 'text-yellow-600 bg-yellow-100';
      case 'poor': return 'text-orange-600 bg-orange-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  },

  // Get progress bar color
  getProgressColor: (score: number): string => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  },
};

// Coordinate utilities
export const coordinates = {
  // Validate latitude
  isValidLatitude: (lat: number): boolean => {
    return lat >= -90 && lat <= 90;
  },

  // Validate longitude
  isValidLongitude: (lon: number): boolean => {
    return lon >= -180 && lon <= 180;
  },

  // Format coordinates for display
  format: (lat: number, lon: number): string => {
    const latDir = lat >= 0 ? 'N' : 'S';
    const lonDir = lon >= 0 ? 'E' : 'W';
    return `${Math.abs(lat).toFixed(4)}°${latDir}, ${Math.abs(lon).toFixed(4)}°${lonDir}`;
  },

  // Calculate distance between two points (Haversine formula)
  distance: (lat1: number, lon1: number, lat2: number, lon2: number): number => {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  },
};

// Crop utilities
export const crops = {
  // Get crop icon/emoji
  getIcon: (cropType: string): string => {
    const icons: Record<string, string> = {
      wheat: '🌾',
      corn: '🌽',
      rice: '🌾',
      soybean: '🫘',
      cotton: '🌱',
      barley: '🌾',
      other: '🌱',
    };
    return icons[cropType.toLowerCase()] || '🌱';
  },

  // Get crop color
  getColor: (cropType: string): string => {
    const colors: Record<string, string> = {
      wheat: '#f59e0b',
      corn: '#22c55e',
      rice: '#3b82f6',
      soybean: '#8b5cf6',
      cotton: '#ec4899',
      barley: '#f97316',
      other: '#6b7280',
    };
    return colors[cropType.toLowerCase()] || '#6b7280';
  },

  // Get growth stage progress percentage
  getGrowthProgress: (stage: string): number => {
    const stages: Record<string, number> = {
      germination: 20,
      vegetative: 40,
      reproductive: 70,
      maturation: 90,
      harvest: 100,
    };
    return stages[stage.toLowerCase()] || 0;
  },
};

// Weather utilities
export const weather = {
  // Get weather icon
  getIcon: (condition: string): string => {
    const icons: Record<string, string> = {
      clear: '☀️',
      'partly cloudy': '⛅',
      cloudy: '☁️',
      rain: '🌧️',
      storm: '⛈️',
      snow: '❄️',
      fog: '🌫️',
    };
    return icons[condition.toLowerCase()] || '☀️';
  },

  // Convert temperature units
  convertTemp: {
    celsiusToFahrenheit: (celsius: number): number => (celsius * 9/5) + 32,
    fahrenheitToCelsius: (fahrenheit: number): number => (fahrenheit - 32) * 5/9,
  },

  // Get wind direction from degrees
  getWindDirection: (degrees: number): string => {
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    const index = Math.round(degrees / 22.5) % 16;
    return directions[index];
  },
};

// Alert utilities
export const alerts = {
  // Get alert severity color
  getSeverityColor: (severity: string): string => {
    switch (severity.toLowerCase()) {
      case 'low': return 'text-blue-600 bg-blue-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  },

  // Get alert icon
  getIcon: (type: string): string => {
    const icons: Record<string, string> = {
      weather: '🌦️',
      pest: '🐛',
      disease: '🦠',
      irrigation: '💧',
      harvest: '🌾',
      maintenance: '🔧',
      other: '⚠️',
    };
    return icons[type.toLowerCase()] || '⚠️';
  },
};

// Local storage utilities
export const storage = {
  // Set item in localStorage
  set: (key: string, value: any): void => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  },

  // Get item from localStorage
  get: <T>(key: string, defaultValue?: T): T | null => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue || null;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return defaultValue || null;
    }
  },

  // Remove item from localStorage
  remove: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Error removing from localStorage:', error);
    }
  },

  // Clear all localStorage
  clear: (): void => {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('Error clearing localStorage:', error);
    }
  },
};

// Debounce utility
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// Throttle utility
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}