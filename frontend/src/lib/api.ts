// API utility functions for communicating with Django backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Types
export interface Farm {
  id: string;
  name: string;
  description: string;
  total_area: number;
  fields_count: number;
  average_health: number;
}

export interface Field {
  id: string;
  name: string;
  crop_type: string;
  area_hectares: number;
  planting_date: string;
  expected_harvest: string;
  growth_stage: string;
  current_health?: CropHealth;
  health_trend: number;
}

export interface CropHealth {
  id: string;
  field_id: string;
  ndvi_value: number;
  evi_value?: number;
  health_score: number;
  status: 'excellent' | 'good' | 'fair' | 'poor' | 'critical';
  analysis_notes: string;
  measured_at: string;
  data_source: string;
}

export interface WeatherData {
  id: string;
  field_id: string;
  temperature_min: number;
  temperature_max: number;
  precipitation: number;
  humidity: number;
  wind_speed: number;
  solar_radiation: number;
  weather_date: string;
  data_source: string;
}

export interface Alert {
  id: string;
  field_id: string;
  alert_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  is_resolved: boolean;
  created_at: string;
  resolved_at?: string;
}

// API Error handling
class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

// Generic API request function
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new APIError(response.status, `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(0, `Network error: ${error}`);
  }
}

// Farm API functions
export const farmAPI = {
  // Get all farms
  async getFarms(): Promise<Farm[]> {
    return apiRequest<Farm[]>('/farms/');
  },

  // Get single farm
  async getFarm(id: string): Promise<Farm> {
    return apiRequest<Farm>(`/farms/${id}/`);
  },

  // Create farm
  async createFarm(farm: Omit<Farm, 'id' | 'fields_count' | 'average_health'>): Promise<Farm> {
    return apiRequest<Farm>('/farms/', {
      method: 'POST',
      body: JSON.stringify(farm),
    });
  },

  // Update farm
  async updateFarm(id: string, farm: Partial<Farm>): Promise<Farm> {
    return apiRequest<Farm>(`/farms/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(farm),
    });
  },

  // Delete farm
  async deleteFarm(id: string): Promise<void> {
    return apiRequest<void>(`/farms/${id}/`, {
      method: 'DELETE',
    });
  },
};

// Field API functions
export const fieldAPI = {
  // Get all fields
  async getFields(): Promise<Field[]> {
    return apiRequest<Field[]>('/fields/');
  },

  // Get single field
  async getField(id: string): Promise<Field> {
    return apiRequest<Field>(`/fields/${id}/`);
  },

  // Get fields by farm
  async getFieldsByFarm(farmId: string): Promise<Field[]> {
    return apiRequest<Field[]>(`/farms/${farmId}/fields/`);
  },

  // Create field
  async createField(field: Omit<Field, 'id' | 'current_health' | 'health_trend'>): Promise<Field> {
    return apiRequest<Field>('/fields/', {
      method: 'POST',
      body: JSON.stringify(field),
    });
  },

  // Update field
  async updateField(id: string, field: Partial<Field>): Promise<Field> {
    return apiRequest<Field>(`/fields/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(field),
    });
  },

  // Delete field
  async deleteField(id: string): Promise<void> {
    return apiRequest<void>(`/fields/${id}/`, {
      method: 'DELETE',
    });
  },

  // Get field health data
  async getFieldHealth(id: string): Promise<CropHealth[]> {
    return apiRequest<CropHealth[]>(`/fields/${id}/health/`);
  },

  // Get field weather data
  async getFieldWeather(
    id: string,
    startDate?: string,
    endDate?: string
  ): Promise<WeatherData[]> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const queryString = params.toString();
    const endpoint = `/fields/${id}/weather/${queryString ? `?${queryString}` : ''}`;
    
    return apiRequest<WeatherData[]>(endpoint);
  },

  // Get field alerts
  async getFieldAlerts(id: string): Promise<Alert[]> {
    return apiRequest<Alert[]>(`/fields/${id}/alerts/`);
  },
};

// Weather API functions
export const weatherAPI = {
  // Get weather data for coordinates
  async getWeatherByCoordinates(
    lat: number,
    lon: number,
    startDate: string,
    endDate: string
  ): Promise<WeatherData[]> {
    const params = new URLSearchParams({
      lat: lat.toString(),
      lon: lon.toString(),
      start_date: startDate,
      end_date: endDate,
    });
    
    return apiRequest<WeatherData[]>(`/weather/?${params.toString()}`);
  },

  // Get current weather
  async getCurrentWeather(lat: number, lon: number): Promise<WeatherData> {
    const params = new URLSearchParams({
      lat: lat.toString(),
      lon: lon.toString(),
    });
    
    return apiRequest<WeatherData>(`/weather/current/?${params.toString()}`);
  },
};

// Alert API functions
export const alertAPI = {
  // Get all alerts
  async getAlerts(): Promise<Alert[]> {
    return apiRequest<Alert[]>('/alerts/');
  },

  // Get alert by ID
  async getAlert(id: string): Promise<Alert> {
    return apiRequest<Alert>(`/alerts/${id}/`);
  },

  // Mark alert as resolved
  async resolveAlert(id: string): Promise<Alert> {
    return apiRequest<Alert>(`/alerts/${id}/resolve/`, {
      method: 'POST',
    });
  },

  // Create alert
  async createAlert(alert: Omit<Alert, 'id' | 'created_at' | 'resolved_at'>): Promise<Alert> {
    return apiRequest<Alert>('/alerts/', {
      method: 'POST',
      body: JSON.stringify(alert),
    });
  },
};

// Satellite API functions
export const satelliteAPI = {
  // Get satellite images for field
  async getFieldImages(fieldId: string): Promise<any[]> {
    return apiRequest<any[]>(`/fields/${fieldId}/satellite-images/`);
  },

  // Request new satellite image analysis
  async requestImageAnalysis(fieldId: string): Promise<any> {
    return apiRequest<any>(`/fields/${fieldId}/analyze/`, {
      method: 'POST',
    });
  },
};

// Analytics API functions
export const analyticsAPI = {
  // Get dashboard statistics
  async getDashboardStats(): Promise<any> {
    return apiRequest<any>('/analytics/dashboard/');
  },

  // Get yield predictions
  async getYieldPredictions(fieldId?: string): Promise<any> {
    const endpoint = fieldId ? `/analytics/yield/${fieldId}/` : '/analytics/yield/';
    return apiRequest<any>(endpoint);
  },

  // Get crop health trends
  async getHealthTrends(timeRange: string = '30d'): Promise<any> {
    return apiRequest<any>(`/analytics/health-trends/?range=${timeRange}`);
  },
};

export { APIError };