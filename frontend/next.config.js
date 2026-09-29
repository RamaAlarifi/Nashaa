/** @type {import('next').NextConfig} */
const nextConfig = {
  // Produce a self-contained server build for the Docker image (smaller,
  // no node_modules needed at runtime). Does not affect `npm run dev`.
  output: "standalone",

  // Proxy /api/* to the FastAPI backend so the browser app calls same-origin
  // endpoints without CORS configuration. The destination is configurable so
  // the same code works for local dev (127.0.0.1) and Docker (service name).
  async rewrites() {
    const backend = process.env.BACKEND_URL || "http://127.0.0.1:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${backend}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
