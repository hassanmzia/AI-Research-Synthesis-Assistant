export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
  status_code?: number;
  request_id?: string;
}

export interface WSMessage {
  type: string;
  channel?: string;
  data?: any;
  timestamp?: string;
}

export interface AgentCard {
  name: string;
  description: string;
  capabilities: string[];
  protocol: string;
  version: string;
}

export interface MCPTool {
  name: string;
  description: string;
  inputSchema: Record<string, any>;
}

export interface A2ATask {
  id: string;
  status: {
    state: 'submitted' | 'working' | 'completed' | 'failed' | 'canceled';
    message?: {
      role: string;
      parts: Array<{ type: string; data?: any; text?: string }>;
    };
  };
  history?: Array<{
    state: string;
    timestamp: string;
  }>;
}
