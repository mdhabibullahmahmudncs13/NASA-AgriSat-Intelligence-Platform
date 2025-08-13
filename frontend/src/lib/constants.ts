// Application constants

// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
} as const;

// NASA API Configuration
export const NASA_CONFIG = {
  POWER_API_URL: 'https://power.larc.nasa.gov/api',
  EARTH_API_URL: 'https://api.nasa.gov/planetary/earth',
  MODIS_API_URL: 'https://modis.gsfc.nasa.gov/data',
  FIRMS_API_URL: 'https://firms.modaps.eosdis.nasa.gov/api',
} as const;

// Crop Types
export const CROP_TYPES = [
  { value: 'wheat', label: 'Wheat', icon: '🌾', color: '#f59e0b' },
  { value: 'corn', label: 'Corn', icon: '🌽', color: '#22c55e' },
  { value: 'rice', label: 'Rice', icon: '🌾', color: '#3b82f6' },
  { value: 'soybean', label: 'Soybean', icon: '🫘', color: '#8b5cf6' },
  { value: 'cotton', label: 'Cotton', icon: '🌱', color: '#ec4899' },
  { value: 'barley', label: 'Barley', icon: '🌾', color: '#f97316' },
  { value: 'other', label: 'Other', icon: '🌱', color: '#6b7280' },
] as const;

// Growth Stages
export const GROWTH_STAGES = [
  { value: 'germination', label: 'Germination', progress: 20 },
  { value: 'vegetative', label: 'Vegetative', progress: 40 },
  { value: 'reproductive', label: 'Reproductive', progress: 70 },
  { value: 'maturation', label: 'Maturation', progress: 90 },
  { value: 'harvest', label: 'Harvest', progress: 100 },
] as const;

// Health Status
export const HEALTH_STATUS = [
  { value: 'excellent', label: 'Excellent', color: 'text-green-600 bg-green-100', range: [90, 100] },
  { value: 'good', label: 'Good', color: 'text-blue-600 bg-blue-100', range: [75, 89] },
  { value: 'fair', label: 'Fair', color: 'text-yellow-600 bg-yellow-100', range: [60, 74] },
  { value: 'poor', label: 'Poor', color: 'text-orange-600 bg-orange-100', range: [40, 59] },
  { value: 'critical', label: 'Critical', color: 'text-red-600 bg-red-100', range: [0, 39] },
] as const;

// Alert Types
export const ALERT_TYPES = [
  { value: 'weather', label: 'Weather Alert', icon: '🌦️', color: 'text-blue-600' },
  { value: 'pest', label: 'Pest Detection', icon: '🐛', color: 'text-red-600' },
  { value: 'disease', label: 'Disease Alert', icon: '🦠', color: 'text-purple-600' },
  { value: 'irrigation', label: 'Irrigation Alert', icon: '💧', color: 'text-cyan-600' },
  { value: 'harvest', label: 'Harvest Alert', icon: '🌾', color: 'text-yellow-600' },
  { value: 'maintenance', label: 'Maintenance', icon: '🔧', color: 'text-gray-600' },
  { value: 'other', label: 'Other', icon: '⚠️', color: 'text-orange-600' },
] as const;

// Alert Severity
export const ALERT_SEVERITY = [
  { value: 'low', label: 'Low', color: 'text-blue-600 bg-blue-100' },
  { value: 'medium', label: 'Medium', color: 'text-yellow-600 bg-yellow-100' },
  { value: 'high', label: 'High', color: 'text-orange-600 bg-orange-100' },
  { value: 'critical', label: 'Critical', color: 'text-red-600 bg-red-100' },
] as const;

// Weather Conditions
export const WEATHER_CONDITIONS = [
  { value: 'clear', label: 'Clear', icon: '☀️' },
  { value: 'partly_cloudy', label: 'Partly Cloudy', icon: '⛅' },
  { value: 'cloudy', label: 'Cloudy', icon: '☁️' },
  { value: 'rain', label: 'Rain', icon: '🌧️' },
  { value: 'storm', label: 'Storm', icon: '⛈️' },
  { value: 'snow', label: 'Snow', icon: '❄️' },
  { value: 'fog', label: 'Fog', icon: '🌫️' },
] as const;

// Data Sources
export const DATA_SOURCES = {
  SATELLITE: {
    MODIS: 'MODIS Terra/Aqua',
    LANDSAT: 'Landsat 8/9',
    SENTINEL: 'Sentinel-2',
  },
  WEATHER: {
    NASA_POWER: 'NASA POWER',
    NOAA: 'NOAA',
    LOCAL_STATION: 'Local Weather Station',
  },
  SOIL: {
    SMAP: 'NASA SMAP',
    FIELD_SENSOR: 'Field Sensor',
  },
} as const;

// Chart Colors
export const CHART_COLORS = {
  PRIMARY: '#3b82f6',
  SECONDARY: '#64748b',
  SUCCESS: '#22c55e',
  WARNING: '#f59e0b',
  DANGER: '#ef4444',
  INFO: '#06b6d4',
  PURPLE: '#8b5cf6',
  PINK: '#ec4899',
  INDIGO: '#6366f1',
  TEAL: '#14b8a6',
} as const;

// Map Configuration
export const MAP_CONFIG = {
  DEFAULT_CENTER: [39.8283, -98.5795], // Geographic center of USA
  DEFAULT_ZOOM: 4,
  MIN_ZOOM: 3,
  MAX_ZOOM: 18,
  TILE_LAYER: {
    URL: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    ATTRIBUTION: '© OpenStreetMap contributors',
  },
  SATELLITE_LAYER: {
    URL: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    ATTRIBUTION: '© Esri, Maxar, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AeroGRID, IGN, and the GIS User Community',
  },
} as const;

// Time Ranges
export const TIME_RANGES = [
  { value: '7d', label: '7 Days', days: 7 },
  { value: '30d', label: '30 Days', days: 30 },
  { value: '90d', label: '90 Days', days: 90 },
  { value: '1y', label: '1 Year', days: 365 },
] as const;

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
  MAX_PAGE_SIZE: 100,
} as const;

// File Upload
export const FILE_UPLOAD = {
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_TYPES: {
    IMAGES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    DOCUMENTS: ['application/pdf', 'text/csv', 'application/json'],
    GEOSPATIAL: ['application/json', 'text/csv'], // GeoJSON, CSV with coordinates
  },
} as const;

// Validation Rules
export const VALIDATION = {
  FIELD_NAME: {
    MIN_LENGTH: 2,
    MAX_LENGTH: 100,
  },
  FARM_NAME: {
    MIN_LENGTH: 2,
    MAX_LENGTH: 200,
  },
  DESCRIPTION: {
    MAX_LENGTH: 1000,
  },
  AREA: {
    MIN: 0.01, // 0.01 hectares
    MAX: 10000, // 10,000 hectares
  },
  COORDINATES: {
    LAT_MIN: -90,
    LAT_MAX: 90,
    LON_MIN: -180,
    LON_MAX: 180,
  },
  HEALTH_SCORE: {
    MIN: 0,
    MAX: 100,
  },
  NDVI: {
    MIN: -1,
    MAX: 1,
  },
} as const;

// Cache Configuration
export const CACHE_CONFIG = {
  WEATHER_DATA: 3600000, // 1 hour
  SATELLITE_IMAGES: 86400000, // 24 hours
  FIELD_DATA: 1800000, // 30 minutes
  DASHBOARD_STATS: 300000, // 5 minutes
} as const;

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection and try again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  NOT_FOUND: 'The requested resource was not found.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  UNKNOWN_ERROR: 'An unexpected error occurred. Please try again.',
} as const;

// Success Messages
export const SUCCESS_MESSAGES = {
  FARM_CREATED: 'Farm created successfully!',
  FARM_UPDATED: 'Farm updated successfully!',
  FARM_DELETED: 'Farm deleted successfully!',
  FIELD_CREATED: 'Field created successfully!',
  FIELD_UPDATED: 'Field updated successfully!',
  FIELD_DELETED: 'Field deleted successfully!',
  ALERT_RESOLVED: 'Alert resolved successfully!',
  DATA_REFRESHED: 'Data refreshed successfully!',
} as const;

// Feature Flags
export const FEATURES = {
  SATELLITE_ANALYSIS: true,
  WEATHER_ALERTS: true,
  YIELD_PREDICTION: true,
  PEST_DETECTION: false, // Coming soon
  MOBILE_APP: false, // Future feature
  ADVANCED_ANALYTICS: true,
  EXPORT_DATA: true,
  REAL_TIME_MONITORING: true,
} as const;

// Application Metadata
export const APP_METADATA = {
  NAME: 'NASA AgriSat Intelligence Platform',
  VERSION: '1.0.0',
  DESCRIPTION: 'Comprehensive Agricultural Monitoring System Using NASA APIs and Earth Observation Data',
  AUTHOR: 'NASA AgriSat Team',
  REPOSITORY: 'https://github.com/nasa-agrisat/platform',
  DOCUMENTATION: 'https://docs.nasa-agrisat.com',
  SUPPORT_EMAIL: 'support@nasa-agrisat.com',
} as const;