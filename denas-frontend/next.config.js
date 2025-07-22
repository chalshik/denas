/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    unoptimized: true
  },
  trailingSlash: false,
  experimental: {
    // Enable if you need server actions or other experimental features
  },
};

module.exports = nextConfig;
