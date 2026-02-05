import { WebSocketServer, WebSocket } from 'ws';
import jwt from 'jsonwebtoken';
import { logger } from './logger';

const JWT_SECRET = process.env.JWT_SECRET || 'arsa-jwt-secret-change-in-production';

interface Client {
  ws: WebSocket;
  userId: string;
  username: string;
  subscriptions: Set<string>;
}

const clients = new Map<string, Client>();

export function setupWebSocket(wss: WebSocketServer): void {
  wss.on('connection', (ws: WebSocket, req) => {
    const url = new URL(req.url || '/', `http://${req.headers.host}`);
    const token = url.searchParams.get('token');

    if (!token) {
      ws.close(4001, 'Authentication required');
      return;
    }

    let decoded: any;
    try {
      decoded = jwt.verify(token, JWT_SECRET);
    } catch {
      ws.close(4001, 'Invalid token');
      return;
    }

    const clientId = decoded.user_id;
    const client: Client = {
      ws,
      userId: clientId,
      username: decoded.username,
      subscriptions: new Set(),
    };

    clients.set(clientId, client);
    logger.info(`WebSocket connected: ${decoded.username}`);

    // Send connection confirmation
    ws.send(JSON.stringify({
      type: 'connected',
      data: {
        userId: clientId,
        username: decoded.username,
        timestamp: new Date().toISOString(),
      },
    }));

    ws.on('message', (data: Buffer) => {
      try {
        const message = JSON.parse(data.toString());
        handleMessage(client, message);
      } catch (err) {
        logger.error(`WebSocket message parse error: ${err}`);
      }
    });

    ws.on('close', () => {
      clients.delete(clientId);
      logger.info(`WebSocket disconnected: ${decoded.username}`);
    });

    ws.on('error', (err) => {
      logger.error(`WebSocket error for ${decoded.username}: ${err.message}`);
    });
  });

  logger.info('WebSocket server initialized');
}

function handleMessage(client: Client, message: any): void {
  switch (message.type) {
    case 'subscribe':
      // Subscribe to project/conversation events
      if (message.channel) {
        client.subscriptions.add(message.channel);
        client.ws.send(JSON.stringify({
          type: 'subscribed',
          channel: message.channel,
        }));
      }
      break;

    case 'unsubscribe':
      if (message.channel) {
        client.subscriptions.delete(message.channel);
      }
      break;

    case 'ping':
      client.ws.send(JSON.stringify({ type: 'pong' }));
      break;

    default:
      logger.warn(`Unknown WebSocket message type: ${message.type}`);
  }
}

/**
 * Broadcast a message to all subscribers of a channel.
 */
export function broadcast(channel: string, data: any): void {
  const message = JSON.stringify({
    type: 'event',
    channel,
    data,
    timestamp: new Date().toISOString(),
  });

  for (const client of clients.values()) {
    if (client.subscriptions.has(channel) && client.ws.readyState === WebSocket.OPEN) {
      client.ws.send(message);
    }
  }
}

/**
 * Send a message to a specific user.
 */
export function sendToUser(userId: string, data: any): void {
  const client = clients.get(userId);
  if (client && client.ws.readyState === WebSocket.OPEN) {
    client.ws.send(JSON.stringify({
      type: 'notification',
      data,
      timestamp: new Date().toISOString(),
    }));
  }
}
