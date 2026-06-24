import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Proxy para desarrollo: Next.js reenvía /api/v1/* → FastAPI en :8000
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: "http://localhost:8000/api/v1/:path*",
      },
    ];
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === "production",
  },
};

export default nextConfig;
