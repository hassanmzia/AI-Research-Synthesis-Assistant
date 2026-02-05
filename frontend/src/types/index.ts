// ── User & Auth ─────────────────────────────────
export interface User {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  bio: string;
  institution: string;
  research_interests: string[];
  avatar_url: string;
  usage_quota_tokens: number;
  tokens_used_this_month: number;
  quota_remaining: number;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  updateUser: (data: Partial<User>) => Promise<void>;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  institution?: string;
}

// ── Project ─────────────────────────────────────
export interface Project {
  id: string;
  name: string;
  description: string;
  tags: string[];
  is_public: boolean;
  status: 'active' | 'archived' | 'processing';
  paper_count: number;
  total_chunks: number;
  owner: string;
  owner_name: string;
  collaborators: Collaborator[];
  created_at: string;
  updated_at: string;
}

export interface Collaborator {
  id: string;
  user: string;
  username: string;
  email: string;
  role: 'viewer' | 'editor' | 'admin';
  created_at: string;
}

// ── Paper ───────────────────────────────────────
export interface Paper {
  id: string;
  project: string;
  title: string;
  authors: string[];
  abstract: string;
  publication_date: string | null;
  journal: string;
  doi: string;
  file_name: string;
  file_size: number;
  page_count: number;
  chunk_count: number;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  processing_error: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// ── Conversation & Messages ─────────────────────
export interface Conversation {
  id: string;
  project: string;
  title: string;
  is_pinned: boolean;
  message_count: number;
  messages: Message[];
  last_message?: {
    role: string;
    content: string;
    created_at: string;
  };
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources: SourceRef[];
  agent_name: string;
  token_count: number;
  latency_ms: number;
  metadata: Record<string, any>;
  created_at: string;
}

export interface SourceRef {
  paper_id: string;
  paper_title: string;
  page_number?: number;
}

// ── Query & Evaluation ──────────────────────────
export interface QueryResult {
  answer: string;
  sources: SourceRef[];
  query_id: string;
  model: string;
  tokens: {
    prompt: number;
    completion: number;
    total: number;
  };
  latency_ms: number;
  evaluation: {
    evaluations: Record<string, EvalResult>;
    composite_score: number;
  };
}

export interface EvalResult {
  score: number;
  explanation: string;
}

export interface QueryHistory {
  id: string;
  question: string;
  answer: string;
  model_used: string;
  total_tokens: number;
  latency_ms: number;
  evaluations: EvalRecord[];
  created_at: string;
}

export interface EvalRecord {
  id: string;
  eval_type: string;
  score: number;
  explanation: string;
  created_at: string;
}

// ── Synthesis Report ────────────────────────────
export interface SynthesisReport {
  id: string;
  project: string;
  title: string;
  description: string;
  report_type: string;
  content_markdown: string;
  status: 'pending' | 'generating' | 'completed' | 'failed';
  total_tokens_used: number;
  generation_time_ms: number;
  sections: ReportSection[];
  created_at: string;
  updated_at: string;
}

export interface ReportSection {
  id: string;
  title: string;
  content: string;
  order: number;
}

// ── Agent ───────────────────────────────────────
export interface AgentCard {
  name: string;
  description: string;
  capabilities: string[];
  protocol: string;
  version: string;
}

export interface AgentLog {
  id: string;
  agent_name: string;
  task_id: string;
  status: string;
  duration_ms: number;
  tokens_used: number;
  created_at: string;
}

// ── Analytics ───────────────────────────────────
export interface DashboardData {
  total_projects: number;
  total_papers: number;
  total_queries: number;
  total_tokens_used: number;
  avg_groundedness_score: number;
  avg_relevance_score: number;
  queries_by_day: { date: string; count: number }[];
  top_papers: { id: string; title: string; query_count: number }[];
  agent_performance: {
    agent_name: string;
    total_calls: number;
    avg_duration: number;
    total_tokens: number;
  }[];
}
