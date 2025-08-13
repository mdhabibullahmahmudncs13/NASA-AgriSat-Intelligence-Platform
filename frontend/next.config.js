/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['api.nasa.gov', 'earthdata.nasa.gov', 'modis.gsfc.nasa.gov'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*', // Django backend
      },
    ];
  },
};

module.exports = nextConfig;