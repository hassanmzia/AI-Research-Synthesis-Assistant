import { Router, Request, Response } from 'express';

export const healthRoutes = Router();

healthRoutes.get('/', (_req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    service: 'ARSA API Gateway',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});
