# NASA AgriSat Intelligence Platform - Backend

A comprehensive Django REST API backend for agricultural intelligence using NASA satellite data, weather information, and disaster monitoring.

## Features

- **Farm & Field Management**: Create and manage agricultural farms and fields with geospatial boundaries
- **Weather Data Integration**: Real-time and historical weather data from NASA POWER API
- **Satellite Imagery & NDVI**: MODIS and Landsat satellite data for crop health monitoring
- **Fire Detection**: Real-time fire alerts using NASA FIRMS data
- **Crop Health Monitoring**: Automated NDVI analysis and health scoring
- **Alert System**: Comprehensive alerting for weather, fire, and crop health events
- **Background Processing**: Celery-based async tasks for data fetching and processing

## Technology Stack

- **Framework**: Django 4.2.7 with Django REST Framework
- **Database**: PostgreSQL with PostGIS for geospatial data
- **Cache & Message Broker**: Redis
- **Background Tasks**: Celery with Redis broker
- **Authentication**: Token-based authentication with DRF
- **Documentation**: DRF Spectacular (OpenAPI/Swagger)
- **Geospatial**: GeoDjango with GDAL/GEOS

## Project Structure

```
backend/
├── agrisat/                 # Main Django project
│   ├── settings/           # Environment-specific settings
│   ├── celery.py          # Celery configuration
│   ├── wsgi.py            # WSGI application
│   └── urls.py            # Main URL configuration
├── apps/                   # Django applications
│   ├── authentication/    # User authentication
│   ├── fields/            # Farm and field management
│   ├── weather/           # Weather data integration
│   ├── satellites/        # Satellite imagery and NDVI
│   └── disasters/         # Fire monitoring and alerts
├── requirements.txt       # Python dependencies
└── manage.py             # Django management script
```

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 13+ with PostGIS extension
- Redis server
- GDAL/GEOS libraries

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "NASA AgriSat Intelligence Platform/backend"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   Create a `.env` file in the backend directory:
   ```env
   # Database
   DATABASE_URL=postgres://username:password@localhost:5432/agrisat_db
   
   # Redis
   REDIS_URL=redis://localhost:6379/0
   
   # Django
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # NASA API Keys
   NASA_API_KEY=your-nasa-api-key
   NASA_FIRMS_API_KEY=your-firms-api-key
   
   # Email (optional)
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

5. **Database setup**
   ```bash
   # Create PostgreSQL database with PostGIS
   createdb agrisat_db
   psql agrisat_db -c "CREATE EXTENSION postgis;"
   
   # Run migrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

8. **Start Celery worker** (in separate terminal)
   ```bash
   celery -A agrisat worker --loglevel=info
   ```

9. **Start Celery beat** (in separate terminal)
   ```bash
   celery -A agrisat beat --loglevel=info
   ```

## API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: `http://localhost:8000/docs/`
- Admin Interface: `http://localhost:8000/admin/`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - User profile
- `PUT /api/auth/profile/` - Update profile
- `POST /api/auth/change-password/` - Change password

### Fields Management
- `GET /api/fields/farms/` - List farms
- `POST /api/fields/farms/` - Create farm
- `GET /api/fields/farms/{id}/` - Farm details
- `GET /api/fields/fields/` - List fields
- `POST /api/fields/fields/` - Create field
- `GET /api/fields/fields/{id}/` - Field details
- `GET /api/fields/crop-health/` - Crop health data
- `GET /api/fields/alerts/` - Field alerts

### Weather Data
- `GET /api/weather/field/{field_id}/weather/` - Field weather data
- `POST /api/weather/field/{field_id}/fetch/` - Fetch weather data
- `GET /api/weather/field/{field_id}/summary/` - Weather summary
- `GET /api/weather/field/{field_id}/current/` - Current conditions
- `POST /api/weather/bulk-fetch/` - Bulk weather fetch

### Satellite Data
- `GET /api/satellites/field/{field_id}/images/` - Satellite images
- `POST /api/satellites/field/{field_id}/fetch/` - Fetch satellite data
- `GET /api/satellites/field/{field_id}/ndvi/` - NDVI data
- `POST /api/satellites/field/{field_id}/ndvi/process/` - Process NDVI
- `GET /api/satellites/field/{field_id}/coverage/` - Satellite coverage
- `GET /api/satellites/field/{field_id}/latest/` - Latest satellite data

### Disaster Monitoring
- `GET /api/disasters/field/{field_id}/fire-data/` - Fire risk data
- `POST /api/disasters/field/{field_id}/check-alerts/` - Check fire alerts
- `GET /api/disasters/alerts/` - Fire alerts
- `POST /api/disasters/alerts/{alert_id}/resolve/` - Resolve alert
- `POST /api/disasters/alerts/bulk-check/` - Bulk fire check
- `GET /api/disasters/statistics/` - Fire statistics

## Background Tasks

The system uses Celery for background processing:

### Scheduled Tasks (Celery Beat)
- **Daily weather update**: Fetches weather data for all fields
- **Daily fire monitoring**: Checks for fire alerts
- **Weekly NDVI processing**: Processes satellite data for crop health
- **Monthly cleanup**: Removes old data to prevent database bloat

### On-Demand Tasks
- Weather data fetching for specific fields
- Satellite data processing
- Fire alert checking
- NDVI analysis and crop health scoring

## NASA API Integration

### NASA POWER API
- **Purpose**: Weather and solar data
- **Data**: Temperature, precipitation, humidity, solar radiation
- **Coverage**: Global, daily data
- **Documentation**: https://power.larc.nasa.gov/docs/

### NASA FIRMS API
- **Purpose**: Active fire detection
- **Data**: MODIS and VIIRS fire hotspots
- **Coverage**: Global, near real-time
- **Documentation**: https://firms.modaps.eosdis.nasa.gov/api/

### NASA Satellite APIs
- **MODIS**: Moderate Resolution Imaging Spectroradiometer
- **Landsat**: Land observation satellites
- **Data**: NDVI, surface reflectance, land cover

## Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
# Format code
black .
isort .

# Lint code
flake8 .
```

### Database Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Custom Management Commands
```bash
# Fetch weather data for all fields
python manage.py fetch_weather_data

# Check fire alerts
python manage.py check_fire_alerts

# Process NDVI data
python manage.py process_ndvi
```

## Deployment

### Production Settings
1. Set `DEBUG=False` in environment
2. Configure proper `ALLOWED_HOSTS`
3. Use production database (PostgreSQL)
4. Set up proper Redis configuration
5. Configure email settings for notifications
6. Set up monitoring with Sentry

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Environment Variables
See `.env.example` for all required environment variables.

## Monitoring and Logging

- **Application logs**: Django logging configuration
- **Celery monitoring**: Flower web interface
- **Error tracking**: Sentry integration
- **Performance monitoring**: Django Debug Toolbar (development)

## Security

- Token-based authentication
- CORS configuration for frontend integration
- Input validation and sanitization
- Rate limiting (recommended for production)
- HTTPS enforcement (production)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and ensure code quality
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation
- Review the Django and DRF documentation

## Acknowledgments

- NASA for providing free access to satellite and weather data
- Django and Django REST Framework communities
- PostGIS and GDAL projects for geospatial capabilities