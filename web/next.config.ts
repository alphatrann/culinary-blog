import type { NextConfig } from "next";

// Thumbnails are served from object storage; allow its host for `next/image` (e.g. IMAGE_HOSTNAME=minio.example.com).
const imageHost = process.env.IMAGE_HOSTNAME;

const nextConfig: NextConfig = {
  output: "standalone",
  // `new` is reserved for the create route (see RESERVED_SLUGS in the API); without this, /recipes/new would
  // resolve to the recipe detail page. Temporary, so the mapping can change without caching surprises.
  async redirects() {
    return [{ source: "/recipes/new", destination: "/dashboard/recipes/new", permanent: false }];
  },
  // robots.txt points crawlers at /sitemap.xml on the web origin. In production nginx routes it to the API;
  // in `next dev` this rewrite does the same job.
  async rewrites() {
    if (process.env.NODE_ENV !== "development") return [];
    return [
      {
        source: "/sitemap.xml",
        destination: `${process.env.API_BASE_URL ?? "http://localhost:8000"}/sitemap.xml`,
      },
    ];
  },
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
