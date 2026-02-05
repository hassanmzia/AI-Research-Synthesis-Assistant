import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET || 'arsa-jwt-secret-change-in-production';

interface JWTPayload {
  user_id: string;
  username: string;
  exp: number;
  iat: number;
}

declare global {
  namespace Express {
    interface Request {
      userId?: string;
      username?: string;
    }
  }
}

export function authMiddleware(req: Request, res: Response, next: NextFunction): void {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    // Allow unauthenticated requests to pass through
    // Django will handle auth enforcement
    next();
    return;
  }

  const token = authHeader.substring(7);

  try {
    const decoded = jwt.verify(token, JWT_SECRET) as JWTPayload;
    req.userId = decoded.user_id;
    req.username = decoded.username;
    next();
  } catch {
    res.status(401).json({
      error: 'Invalid or expired token',
    });
  }
}
