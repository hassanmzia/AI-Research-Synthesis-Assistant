import { Router, Request, Response } from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';

const BACKEND_URL = process.env.DJANGO_BACKEND_URL || 'http://backend:8000';

export const mcpRoutes = Router();

// Proxy MCP requests to Django backend
mcpRoutes.use(
  '/',
  createProxyMiddleware({
    target: BACKEND_URL,
    changeOrigin: true,
    pathRewrite: { '^/mcp': '/mcp' },
    timeout: 300000,
  })
);
