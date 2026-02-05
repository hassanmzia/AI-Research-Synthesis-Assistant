import { Router } from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';
import { logger } from '../services/logger';

const BACKEND_URL = process.env.DJANGO_BACKEND_URL || 'http://backend:8000';

export const proxyRoutes = Router();

// Proxy all /api requests to Django backend
proxyRoutes.use(
  '/',
  createProxyMiddleware({
    target: BACKEND_URL,
    changeOrigin: true,
    pathRewrite: { '^/api': '/api' },
    timeout: 300000,
    on: {
      proxyReq: (proxyReq, req) => {
        // Forward request ID
        if ((req as any).requestId) {
          proxyReq.setHeader('X-Request-ID', (req as any).requestId);
        }
        // Forward user info
        if ((req as any).userId) {
          proxyReq.setHeader('X-User-ID', (req as any).userId);
        }
      },
      error: (err, _req, res) => {
        logger.error(`Proxy error: ${err.message}`);
        if ('writeHead' in res && typeof res.writeHead === 'function') {
          (res as any).status(502).json({
            error: 'Backend service unavailable',
          });
        }
      },
    },
  })
);
