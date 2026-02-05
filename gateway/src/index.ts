import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import http from 'http';
import { WebSocketServer } from 'ws';

import { proxyRoutes } from './routes/proxy';
import { healthRoutes } from './routes/health';
import { mcpRoutes } from './routes/mcp';
import { rateLimiterMiddleware } from './middleware/rateLimiter';
import { authMiddleware } from './middleware/auth';
import { requestIdMiddleware } from './middleware/requestId';
import { setupWebSocket } from './services/websocket';
import { logger } from './services/logger';

const app = express();
const PORT = parseInt(process.env.PORT || '4000', 10);

// ── Middleware ──────────────────────────────────
app.use(helmet({ contentSecurityPolicy: false }));
app.use(cors({
  origin: (process.env.CORS_ORIGIN || 'http://localhost:3066').split(','),
  credentials: true,
}));
app.use(morgan('combined', {
  stream: { write: (msg: string) => logger.info(msg.trim()) },
}));
app.use(express.json({ limit: '10mb' }));
app.use(requestIdMiddleware);
app.use(rateLimiterMiddleware);

// ── Routes ─────────────────────────────────────
app.use('/health', healthRoutes);
app.use('/api', authMiddleware, proxyRoutes);
app.use('/mcp', mcpRoutes);

// ── Error Handler ──────────────────────────────
app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  logger.error(`Unhandled error: ${err.message}`, { stack: err.stack });
  res.status(500).json({
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined,
  });
});

// ── Server & WebSocket ─────────────────────────
const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: '/ws' });

setupWebSocket(wss);

server.listen(PORT, '0.0.0.0', () => {
  logger.info(`Gateway running on port ${PORT}`);
  logger.info(`WebSocket listening on /ws`);
  logger.info(`Backend: ${process.env.DJANGO_BACKEND_URL || 'http://backend:8000'}`);
});
