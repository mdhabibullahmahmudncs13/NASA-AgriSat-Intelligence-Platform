# NASA AgriSat Intelligence Platform - Frontend

A modern Next.js frontend application for the NASA AgriSat Intelligence Platform, providing comprehensive agricultural monitoring and analytics using NASA APIs and Earth observation data.

## Features

- 🌾 **Farm & Field Management** - Comprehensive farm and field monitoring
- 🛰️ **Satellite Data Integration** - Real-time satellite imagery and analysis
- 🌦️ **Weather Monitoring** - Advanced weather tracking and alerts
- 📊 **Analytics Dashboard** - AI-powered insights and yield predictions
- 🚨 **Smart Alerts** - Automated notifications for critical events
- 📱 **Responsive Design** - Optimized for desktop and mobile devices

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **State Management**: React Hooks

## Prerequisites

- Node.js 18.0 or higher
- npm or yarn package manager
- Running Django backend (see backend README)

## Installation

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Set up environment variables**:
   Create a `.env.local` file in the frontend root:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   NEXT_PUBLIC_NASA_API_KEY=your_nasa_api_key_here
   ```

## Development

1. **Start the development server**:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

2. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── dashboard/       # Dashboard page
│   │   ├── fields/          # Fields management
│   │   ├── weather/         # Weather monitoring
│   │   ├── analytics/       # Analytics dashboard
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home page
│   │   └── globals.css      # Global styles
│   ├── components/          # Reusable components
│   │   ├── ui/              # UI components
│   │   ├── charts/          # Chart components
│   │   ├── forms/           # Form components
│   │   └── layout/          # Layout components
│   ├── lib/                 # Utility libraries
│   │   ├── api.ts           # API client
│   │   ├── utils.ts         # Utility functions
│   │   └── constants.ts     # Application constants
│   ├── hooks/               # Custom React hooks
│   ├── types/               # TypeScript type definitions
│   └── styles/              # Additional styles
├── public/                  # Static assets
├── next.config.js           # Next.js configuration
├── tailwind.config.js       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Dependencies and scripts
```

## API Integration

The frontend communicates with the Django backend through RESTful APIs:

- **Farms API**: `/api/farms/`
- **Fields API**: `/api/fields/`
- **Weather API**: `/api/weather/`
- **Satellite API**: `/api/satellite/`
- **Alerts API**: `/api/alerts/`
- **Analytics API**: `/api/analytics/`

## Key Components

### Dashboard
- Real-time farm statistics
- Health monitoring charts
- Weather overview
- Recent alerts

### Fields Management
- Field listing and search
- Health status indicators
- Crop information
- Satellite imagery

### Weather Monitoring
- Current weather conditions
- 7-day forecast
- Historical trends
- Weather alerts

### Analytics
- Yield predictions
- Crop health trends
- Performance metrics
- AI-powered insights

## Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000/api` |
| `NEXT_PUBLIC_NASA_API_KEY` | NASA API key | - |
| `NEXT_PUBLIC_MAP_API_KEY` | Map service API key | - |

## Styling Guidelines

- Use Tailwind CSS utility classes
- Follow mobile-first responsive design
- Maintain consistent color scheme
- Use semantic HTML elements
- Ensure accessibility compliance

## Performance Optimization

- Image optimization with Next.js Image component
- Code splitting with dynamic imports
- API response caching
- Lazy loading for charts and heavy components
- Bundle size optimization

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow the existing code style
2. Write TypeScript for type safety
3. Add proper error handling
4. Include responsive design
5. Test on multiple browsers

## Troubleshooting

### Common Issues

1. **API Connection Failed**:
   - Ensure backend server is running
   - Check API URL in environment variables
   - Verify CORS settings

2. **Build Errors**:
   - Clear `.next` directory
   - Delete `node_modules` and reinstall
   - Check TypeScript errors

3. **Styling Issues**:
   - Verify Tailwind CSS configuration
   - Check for conflicting styles
   - Clear browser cache

### Development Tips

- Use React Developer Tools for debugging
- Enable TypeScript strict mode
- Utilize Next.js built-in performance metrics
- Monitor bundle size with webpack-bundle-analyzer

## Deployment

### Production Build

```bash
npm run build
npm run start
```

### Environment Setup

1. Set production environment variables
2. Configure API endpoints
3. Optimize images and assets
4. Enable compression
5. Set up monitoring

## License

This project is part of the NASA AgriSat Intelligence Platform.

## Support

For technical support or questions:
- Email: support@nasa-agrisat.com
- Documentation: https://docs.nasa-agrisat.com
- Issues: GitHub Issues