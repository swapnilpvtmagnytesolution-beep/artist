/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
    NEXT_PUBLIC_APP_NAME: 'Eddits Admin Portal',
    NEXT_PUBLIC_APP_VERSION: '1.0.0',
  },
  
  // Image optimization
  images: {
    domains: [
      'localhost',
      '127.0.0.1',
      // Add your production domains here
      's3.amazonaws.com',
      'storage.googleapis.com',
      'digitaloceanspaces.com',
    ],
    formats: ['image/webp', 'image/avif'],
  },
  
  // API routes configuration
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/:path*`,
      },
    ];
  },
  
  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
    ];
  },
  
  // Webpack configuration
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Custom webpack configurations if needed
    return config;
  },
  
  // Experimental features
  experimental: {
    // Enable if needed
    // appDir: true,
  },
  
  // Output configuration for deployment
  output: 'standalone',
  
  // Compression
  compress: true,
  
  // Power by header
  poweredByHeader: false,
  
  // Trailing slash
  trailingSlash: false,
};

module.exports = nextConfig;