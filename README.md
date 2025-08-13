# NASA AgriSat Intelligence Platform

Comprehensive Agricultural Monitoring System Using NASA APIs and Earth Observation Data

## Executive Summary

AgriSat Intelligence Platform is an integrated web application that leverages NASA's Earth observation data, weather systems, and satellite imagery to provide farmers and agricultural professionals with real-time crop monitoring, weather forecasting, water management, disaster response, and precision agriculture insights.

## Features

- **Real-time Crop Monitoring**: NDVI and EVI analysis using MODIS satellite data
- **Weather Forecasting**: NASA POWER API integration for agricultural weather data
- **Soil Moisture Monitoring**: SMAP satellite data for irrigation planning
- **Disaster Response**: FIRMS fire detection and alert system
- **Interactive Maps**: Leaflet-based field visualization and management
- **Analytics Dashboard**: Comprehensive crop health and yield predictions

## Tech Stack

### Backend
- Django 4.2.7 with Django REST Framework
- PostgreSQL with PostGIS for geographic data
- Celery for background tasks
- Redis for caching and task queue
- NASA APIs integration

### Frontend
- Next.js 14 with TypeScript
- Tailwind CSS for styling
- Leaflet for interactive maps
- Recharts for data visualization
- SWR for data fetching

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL with PostGIS
- Redis
- NASA API Key (free from https://api.nasa.gov/)

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd agrisat-platform
```

2. Set up backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

3. Set up frontend
```bash
cd frontend
npm install
npm run dev
```

4. Start background services
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery worker
cd backend
celery -A agrisat worker -l info
```

## NASA APIs Used

- **NASA POWER**: Weather and solar data
- **MODIS**: Vegetation indices (NDVI/EVI)
- **Landsat**: High-resolution imagery
- **SMAP**: Soil moisture data
- **FIRMS**: Fire detection
- **Earth Imagery API**: Satellite imagery

## Project Structure

```
agrisat-platform/
├── backend/          # Django REST API
├── frontend/         # Next.js application
├── infra/           # Infrastructure configs
├── docker-compose.yml
└── README.md
```

## Development

### Running with Docker
```bash
docker-compose up -d
```

### API Documentation
Once running, visit:
- Backend API: http://localhost:8000/api/
- API Docs: http://localhost:8000/api/schema/swagger-ui/
- Frontend: http://localhost:3000

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For support and questions, please open an issue in the GitHub repository.