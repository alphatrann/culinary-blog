import type { NextConfig } from "next";

// Thumbnails are served from object storage; allow its host for `next/image` (e.g. IMAGE_HOSTNAME=minio.example.com).
const imageHost = process.env.IMAGE_HOSTNAME;

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [
      ...(imageHost ? [{ protocol: "https" as const, hostname: imageHost }] : []),
      // Local MinIO from compose.development.yml.
      ...(process.env.NODE_ENV === "development"
        ? [{ protocol: "http" as const, hostname: "localhost", port: "9000" }]
        : []),
    ],
  },
};

export default nextConfig;
