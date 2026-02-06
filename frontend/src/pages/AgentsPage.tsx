import React, { useEffect, useState } from 'react';
import { agentAPI } from '../services/api';
import { AgentCard } from '../types';

interface AgentLogDetail {
  id: string;
  agent_name: string;
  task_id: string;
  status: string;
  input_data: Record<string, any>;
  output_data: Record<string, any>;
  error_message: string;
  duration_ms: number;
  tokens_used: number;
  parent_log_id: string | null;
  parent_agent_name: string | null;
  child_logs: Array<{
    id: string;
    agent_name: string;
    status: string;
    duration_ms: number;
    tokens_used: number;
  }>;
  outgoing_interactions: Array<{
    id: string;
    target_agent: string;
    status: string;
    duration_ms: number;
    request_summary: string;
    response_summary: string;
  }>;
  created_at: string;
}

interface AgentInteractionDetail {
  id: string;
  source_agent: string;
  target_agent: string;
  protocol: string;
  request_payload: Record<string, any>;
  response_payload: Record<string, any>;
  status: string;
  duration_ms: number;
  parent_log_id: string | null;
  child_log_id: string | null;
  created_at: string;
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<AgentCard[]>([]);
  const [logs, setLogs] = useState<AgentLogDetail[]>([]);
  const [activeTab, setActiveTab] = useState<'agents' | 'logs' | 'interactions'>('logs');
  const [interactions, setInteractions] = useState<AgentInteractionDetail[]>([]);
  const [expandedLogs, setExpandedLogs] = useState<Set<string>>(new Set());
  const [expandedInteractions, setExpandedInteractions] = useState<Set<string>>(new Set());

  useEffect(() => {
    agentAPI.list().then((res) => setAgents(res.data.agents || []));
    agentAPI.logs().then((res) => setLogs(res.data.results || res.data || []));
    agentAPI.interactions().then((res) => setInteractions(res.data.results || res.data || []));
  }, []);

  const toggleLog = (id: string) => {
    setExpandedLogs(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleInteraction = (id: string) => {
    setExpandedInteractions(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const agentColors: Record<string, string> = {
    orchestrator: 'bg-purple-500',
    ingestion: 'bg-blue-500',
    embedding: 'bg-cyan-500',
    retrieval: 'bg-green-500',
    synthesis: 'bg-orange-500',
    evaluation: 'bg-yellow-500',
    citation: 'bg-pink-500',
    summary: 'bg-indigo-500',
  };

  // Score badge with color coding
  const ScoreBadge = ({ score, label }: { score: number; label?: string }) => {
    const percentage = Math.round(score * 100);
    const colorClass = percentage >= 80 ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                       percentage >= 60 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' :
                       'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium ${colorClass}`}>
        {label && <span className="mr-1">{label}:</span>}
        {percentage}%
      </span>
    );
  };

  // Render evaluation results
  const renderEvaluations = (evaluations: Record<string, any>) => {
    if (!evaluations || Object.keys(evaluations).length === 0) return null;

    return (
      <div className="space-y-3">
        {Object.entries(evaluations).map(([key, eval_data]: [string, any]) => (
          <div key={key} className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium capitalize text-gray-700 dark:text-gray-300">
                {key.replace(/_/g, ' ')}
              </span>
              {eval_data?.score !== undefined && <ScoreBadge score={eval_data.score} />}
            </div>
            {eval_data?.explanation && (
              <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                {eval_data.explanation}
              </p>
            )}
          </div>
        ))}
      </div>
    );
  };

  // Render question/answer pair
  const renderQA = (question: string, answer?: string) => (
    <div className="space-y-3">
      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border-l-4 border-blue-500">
        <div className="text-xs font-semibold text-blue-600 dark:text-blue-400 mb-1 uppercase">Question</div>
        <p className="text-gray-800 dark:text-gray-200">{question}</p>
      </div>
      {answer && (
        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 border-l-4 border-green-500">
          <div className="text-xs font-semibold text-green-600 dark:text-green-400 mb-1 uppercase">Answer</div>
          <p className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{answer}</p>
        </div>
      )}
    </div>
  );

  // Render context/sources
  const renderContext = (context: string | string[]) => {
    const contexts = Array.isArray(context) ? context : [context];
    if (contexts.length === 0 || !contexts[0]) return null;

    return (
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
        <div className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2 uppercase">
          Retrieved Context ({contexts.length} {contexts.length === 1 ? 'source' : 'sources'})
        </div>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {contexts.map((ctx, idx) => (
            <div key={idx} className="text-sm text-gray-700 dark:text-gray-300 p-2 bg-white dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600">
              {typeof ctx === 'string' ? ctx.substring(0, 300) + (ctx.length > 300 ? '...' : '') : JSON.stringify(ctx)}
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Smart payload renderer that detects content type
  const formatPayload = (obj: any, type: 'request' | 'response' | 'input' | 'output') => {
    if (!obj || Object.keys(obj).length === 0) return <span className="text-gray-400 italic">No data</span>;

    const elements: JSX.Element[] = [];
    const handledKeys = new Set<string>();

    // Handle model info
    if (obj.model) {
      handledKeys.add('model');
      elements.push(
        <div key="model" className="mb-3 flex items-center gap-2">
          <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Model:</span>
          <span className="text-xs px-2 py-0.5 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-full">{obj.model}</span>
        </div>
      );
    }

    // Handle question/answer content
    if (obj.question || obj.query) {
      handledKeys.add('question');
      handledKeys.add('query');
      handledKeys.add('answer');
      elements.push(
        <div key="qa" className="mb-4">
          {renderQA(obj.question || obj.query, obj.answer)}
        </div>
      );
    } else if (obj.answer) {
      // Handle standalone answer (without question in same payload)
      handledKeys.add('answer');
      elements.push(
        <div key="answer" className="mb-4">
          <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 border-l-4 border-green-500">
            <div className="text-xs font-semibold text-green-600 dark:text-green-400 mb-1 uppercase">Answer</div>
            <p className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap leading-relaxed">{obj.answer}</p>
          </div>
        </div>
      );
    }

    // Handle context/sources
    if (obj.context || obj.contexts || obj.retrieved_context) {
      handledKeys.add('context');
      handledKeys.add('contexts');
      handledKeys.add('retrieved_context');
      elements.push(
        <div key="context" className="mb-4">
          {renderContext(obj.context || obj.contexts || obj.retrieved_context)}
        </div>
      );
    }

    // Handle sources (paper references)
    if (obj.sources && Array.isArray(obj.sources) && obj.sources.length > 0) {
      handledKeys.add('sources');
      elements.push(
        <div key="sources" className="mb-4">
          <div className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2 uppercase">
            Sources ({obj.sources.length})
          </div>
          <div className="space-y-2">
            {obj.sources.slice(0, 5).map((source: any, idx: number) => (
              <div key={idx} className="text-sm p-2 bg-white dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600">
                <div className="font-medium text-gray-800 dark:text-gray-200">
                  {source.paper_title || source.title || `Source ${idx + 1}`}
                </div>
                <div className="flex gap-3 mt-1 text-xs text-gray-500">
                  {source.page_number !== undefined && <span>Page {source.page_number + 1}</span>}
                  {source.chunk_index !== undefined && <span>Chunk {source.chunk_index}</span>}
                  {source.relevance_score !== undefined && (
                    <span className="text-green-600 dark:text-green-400">
                      Relevance: {(source.relevance_score * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
              </div>
            ))}
            {obj.sources.length > 5 && (
              <div className="text-xs text-gray-500">...and {obj.sources.length - 5} more</div>
            )}
          </div>
        </div>
      );
    }

    // Handle nested evaluation object (common pattern)
    if (obj.evaluation && typeof obj.evaluation === 'object') {
      handledKeys.add('evaluation');
      const evalData = obj.evaluation;

      if (evalData.evaluations) {
        elements.push(
          <div key="evaluations" className="mb-4">
            <div className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2 uppercase">Evaluation Results</div>
            {renderEvaluations(evalData.evaluations)}
          </div>
        );
      }

      if (evalData.composite_score !== undefined) {
        elements.push(
          <div key="composite" className="mb-4 flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Overall Score:</span>
            <ScoreBadge score={evalData.composite_score / 5} />
            <span className="text-xs text-gray-500">({evalData.composite_score}/5)</span>
          </div>
        );
      }

      if (evalData.total_tokens) {
        elements.push(
          <div key="eval-tokens" className="mb-2 text-sm text-gray-500">
            <span className="font-medium">Evaluation tokens:</span> {evalData.total_tokens.toLocaleString()}
          </div>
        );
      }
    }

    // Handle top-level evaluations
    if (obj.evaluations && !obj.evaluation) {
      handledKeys.add('evaluations');
      elements.push(
        <div key="evaluations" className="mb-4">
          <div className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2 uppercase">Evaluation Results</div>
          {renderEvaluations(obj.evaluations)}
        </div>
      );
    }

    // Handle composite score (top-level)
    if (obj.composite_score !== undefined && !obj.evaluation) {
      handledKeys.add('composite_score');
      elements.push(
        <div key="composite" className="mb-4 flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Overall Score:</span>
          <ScoreBadge score={obj.composite_score / 5} />
          <span className="text-xs text-gray-500">({obj.composite_score}/5)</span>
        </div>
      );
    }

    // Handle tokens object (with total, prompt, completion) or simple tokens
    if (obj.tokens && typeof obj.tokens === 'object') {
      handledKeys.add('tokens');
      elements.push(
        <div key="tokens" className="mb-4">
          <div className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2 uppercase">Token Usage</div>
          <div className="flex gap-4 text-sm">
            {obj.tokens.total !== undefined && (
              <div className="bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded">
                <span className="text-gray-500 dark:text-gray-400">Total: </span>
                <span className="font-medium text-gray-800 dark:text-gray-200">{obj.tokens.total.toLocaleString()}</span>
              </div>
            )}
            {obj.tokens.prompt !== undefined && (
              <div className="bg-blue-50 dark:bg-blue-900/20 px-3 py-1 rounded">
                <span className="text-blue-600 dark:text-blue-400">Prompt: </span>
                <span className="font-medium">{obj.tokens.prompt.toLocaleString()}</span>
              </div>
            )}
            {obj.tokens.completion !== undefined && (
              <div className="bg-green-50 dark:bg-green-900/20 px-3 py-1 rounded">
                <span className="text-green-600 dark:text-green-400">Completion: </span>
                <span className="font-medium">{obj.tokens.completion.toLocaleString()}</span>
              </div>
            )}
          </div>
        </div>
      );
    } else if (obj.total_tokens || obj.tokens_used) {
      handledKeys.add('total_tokens');
      handledKeys.add('tokens_used');
      elements.push(
        <div key="tokens" className="mb-4 text-sm text-gray-500">
          <span className="font-medium">Tokens used:</span> {(obj.total_tokens || obj.tokens_used).toLocaleString()}
        </div>
      );
    }

    // Handle latency
    if (obj.latency_ms !== undefined) {
      handledKeys.add('latency_ms');
      elements.push(
        <div key="latency" className="mb-3 text-sm text-gray-500">
          <span className="font-medium">Latency:</span> {obj.latency_ms.toLocaleString()}ms
        </div>
      );
    }

    // Handle papers/documents
    if (obj.papers && Array.isArray(obj.papers)) {
      handledKeys.add('papers');
      elements.push(
        <div key="papers" className="mb-4">
          <div className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2 uppercase">
            Papers ({obj.papers.length})
          </div>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {obj.papers.slice(0, 5).map((paper: any, idx: number) => (
              <div key={idx} className="text-sm p-2 bg-white dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600">
                <div className="font-medium">{paper.title || paper.name || `Paper ${idx + 1}`}</div>
                {paper.authors && <div className="text-xs text-gray-500">{paper.authors}</div>}
              </div>
            ))}
            {obj.papers.length > 5 && (
              <div className="text-xs text-gray-500">...and {obj.papers.length - 5} more</div>
            )}
          </div>
        </div>
      );
    }

    // Handle synthesis/report content
    if (obj.synthesis || obj.report || obj.content) {
      const content = obj.synthesis || obj.report || obj.content;
      handledKeys.add('synthesis');
      handledKeys.add('report');
      handledKeys.add('content');
      elements.push(
        <div key="content" className="mb-4">
          <div className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2 uppercase">
            {obj.synthesis ? 'Synthesis' : obj.report ? 'Report' : 'Content'}
          </div>
          <div className="text-sm text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 p-3 rounded border border-gray-200 dark:border-gray-600 max-h-48 overflow-y-auto whitespace-pre-wrap">
            {typeof content === 'string' ? content.substring(0, 1000) + (content.length > 1000 ? '...' : '') : JSON.stringify(content, null, 2)}
          </div>
        </div>
      );
    }

    // Handle citations
    if (obj.citations && Array.isArray(obj.citations)) {
      handledKeys.add('citations');
      elements.push(
        <div key="citations" className="mb-4">
          <div className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2 uppercase">
            Citations ({obj.citations.length})
          </div>
          <div className="space-y-1">
            {obj.citations.slice(0, 5).map((citation: any, idx: number) => (
              <div key={idx} className="text-sm text-gray-600 dark:text-gray-400">
                [{idx + 1}] {typeof citation === 'string' ? citation : citation.formatted || citation.title || JSON.stringify(citation)}
              </div>
            ))}
          </div>
        </div>
      );
    }

    // Handle status field
    if (obj.status) {
      handledKeys.add('status');
      const statusColor = obj.status === 'completed' || obj.status === 'success' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                          obj.status === 'failed' || obj.status === 'error' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' :
                          'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
      elements.push(
        <div key="status" className="mb-3 flex items-center gap-2">
          <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Status:</span>
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusColor}`}>{obj.status}</span>
        </div>
      );
    }

    // Handle chunks_embedded (from embedding agent)
    if (obj.chunks_embedded !== undefined) {
      handledKeys.add('chunks_embedded');
      elements.push(
        <div key="chunks" className="mb-3 text-sm">
          <span className="font-medium text-gray-700 dark:text-gray-300">Chunks embedded:</span>
          <span className="ml-2 text-green-600 dark:text-green-400 font-medium">{obj.chunks_embedded}</span>
        </div>
      );
    }

    // Handle collection name
    if (obj.collection) {
      handledKeys.add('collection');
      elements.push(
        <div key="collection" className="mb-3 text-sm text-gray-500">
          <span className="font-medium">Collection:</span>
          <code className="ml-2 bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded text-xs">{obj.collection}</code>
        </div>
      );
    }

    // Handle error
    if (obj.error) {
      handledKeys.add('error');
      elements.push(
        <div key="error" className="mb-4 bg-red-50 dark:bg-red-900/20 p-3 rounded border-l-4 border-red-500">
          <div className="text-xs font-semibold text-red-600 dark:text-red-400 mb-1 uppercase">Error</div>
          <p className="text-red-700 dark:text-red-300">{obj.error}</p>
        </div>
      );
    }

    // Handle action field
    if (obj.action) {
      handledKeys.add('action');
      elements.push(
        <div key="action" className="mb-3 flex items-center gap-2">
          <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Action:</span>
          <span className="text-sm font-medium text-indigo-600 dark:text-indigo-400">{obj.action.replace(/_/g, ' ')}</span>
        </div>
      );
    }

    // Handle agents array (from discover_agents)
    if (obj.agents && Array.isArray(obj.agents)) {
      handledKeys.add('agents');
      elements.push(
        <div key="agents" className="mb-4">
          <div className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2 uppercase">
            Discovered Agents ({obj.agents.length})
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {obj.agents.map((agent: any, idx: number) => (
              <div key={idx} className="text-sm p-3 bg-white dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-gray-800 dark:text-gray-200 capitalize">{agent.name}</span>
                  <span className="text-xs px-1.5 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded">v{agent.version}</span>
                  <span className="text-xs px-1.5 py-0.5 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded">{agent.protocol}</span>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">{agent.description}</p>
                <div className="flex flex-wrap gap-1">
                  {agent.capabilities?.slice(0, 4).map((cap: string, capIdx: number) => (
                    <span key={capIdx} className="text-xs px-1.5 py-0.5 bg-gray-100 dark:bg-gray-600 text-gray-600 dark:text-gray-300 rounded">
                      {cap.replace(/_/g, ' ')}
                    </span>
                  ))}
                  {agent.capabilities?.length > 4 && (
                    <span className="text-xs text-gray-400">+{agent.capabilities.length - 4} more</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    }

    // Handle ID fields (paper_id, project_id, query_id, etc.)
    const idFields = ['paper_id', 'project_id', 'query_id', 'report_id', 'task_id', 'session_id'];
    const foundIds = idFields.filter(key => obj[key]);
    if (foundIds.length > 0) {
      foundIds.forEach(key => handledKeys.add(key));
      elements.push(
        <div key="ids" className="mb-3">
          <div className="flex flex-wrap gap-3">
            {foundIds.map(key => (
              <div key={key} className="text-sm">
                <span className="text-gray-500 dark:text-gray-400">{key.replace(/_/g, ' ').replace(/\bid\b/i, 'ID')}:</span>
                <code className="ml-1.5 text-xs bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded font-mono">
                  {String(obj[key]).substring(0, 8)}...
                </code>
              </div>
            ))}
          </div>
        </div>
      );
    }

    // Common IDs to skip in "other fields" (already handled above)
    handledKeys.add('query_id');
    handledKeys.add('paper_id');
    handledKeys.add('project_id');

    // If we rendered specific content, return it
    if (elements.length > 0) {
      // Show any remaining fields not yet rendered
      const otherFields = Object.entries(obj).filter(([key]) => !handledKeys.has(key));

      if (otherFields.length > 0) {
        elements.push(
          <details key="other" className="mt-2">
            <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700 dark:hover:text-gray-300">
              Other fields ({otherFields.length})
            </summary>
            <pre className="text-xs bg-gray-100 dark:bg-gray-900 p-2 mt-1 rounded overflow-x-auto">
              {JSON.stringify(Object.fromEntries(otherFields), null, 2)}
            </pre>
          </details>
        );
      }

      return <div>{elements}</div>;
    }

    // Fallback to formatted JSON for unrecognized structures
    return (
      <pre className="text-xs bg-gray-100 dark:bg-gray-900 p-3 rounded overflow-x-auto max-h-64">
        {JSON.stringify(obj, null, 2)}
      </pre>
    );
  };

  // Filter to show only root logs (no parent) for cleaner hierarchy
  const rootLogs = logs.filter(log => !log.parent_log_id);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Multi-Agent System</h1>
        <p className="text-gray-500 mt-1">Monitor AI agents, A2A interactions, and execution details</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-gray-200 dark:border-dark-border">
        {(['logs', 'interactions', 'agents'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors capitalize ${
              activeTab === tab
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab === 'interactions' ? 'A2A Interactions' : tab === 'logs' ? 'Agent Logs' : tab}
          </button>
        ))}
      </div>

      {/* Agent Logs with Details */}
      {activeTab === 'logs' && (
        <div className="space-y-3">
          {rootLogs.length === 0 ? (
            <div className="card text-center py-8">
              <p className="text-gray-500">No agent activity yet</p>
            </div>
          ) : (
            rootLogs.map((log) => (
              <div key={log.id} className="card p-0 overflow-hidden">
                {/* Log Header - Clickable */}
                <div
                  onClick={() => toggleLog(log.id)}
                  className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${agentColors[log.agent_name] || 'bg-gray-500'}`} />
                    <span className="font-semibold capitalize">{log.agent_name}</span>
                    <span className={`badge ${
                      log.status === 'completed' ? 'badge-success' :
                      log.status === 'failed' ? 'badge-error' :
                      log.status === 'running' ? 'badge-info' : 'badge-warning'
                    }`}>
                      {log.status}
                    </span>
                    {log.child_logs.length > 0 && (
                      <span className="text-xs text-gray-500">
                        ({log.child_logs.length} child agents)
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex gap-3 text-xs text-gray-500">
                      {log.duration_ms > 0 && <span>{log.duration_ms}ms</span>}
                      {log.tokens_used > 0 && <span>{log.tokens_used} tokens</span>}
                      <span>{new Date(log.created_at).toLocaleString()}</span>
                    </div>
                    <svg
                      className={`w-5 h-5 text-gray-400 transition-transform ${expandedLogs.has(log.id) ? 'rotate-180' : ''}`}
                      fill="none" viewBox="0 0 24 24" stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>

                {/* Expanded Details */}
                {expandedLogs.has(log.id) && (
                  <div className="border-t border-gray-200 dark:border-gray-700 p-4 space-y-4 bg-gray-50/50 dark:bg-gray-800/30">
                    {/* Task ID */}
                    <div className="text-xs text-gray-500">
                      Task ID: <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">{log.task_id}</code>
                    </div>

                    {/* Input Data */}
                    <div>
                      <h4 className="text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">Input Data</h4>
                      {formatPayload(log.input_data, 'input')}
                    </div>

                    {/* Output Data */}
                    <div>
                      <h4 className="text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">Output Data</h4>
                      {formatPayload(log.output_data, 'output')}
                    </div>

                    {/* Error Message */}
                    {log.error_message && (
                      <div>
                        <h4 className="text-sm font-semibold mb-2 text-red-600">Error</h4>
                        <pre className="text-xs bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 p-3 rounded">
                          {log.error_message}
                        </pre>
                      </div>
                    )}

                    {/* A2A Calls Made */}
                    {log.outgoing_interactions.length > 0 && (
                      <div>
                        <h4 className="text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                          A2A Calls ({log.outgoing_interactions.length})
                        </h4>
                        <div className="space-y-2">
                          {log.outgoing_interactions.map((int) => (
                            <div key={int.id} className="flex items-center gap-2 text-sm p-2 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                              <svg className="w-4 h-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                              </svg>
                              <span className="capitalize font-medium">{int.target_agent}</span>
                              <span className={`badge text-xs ${int.status === 'success' ? 'badge-success' : 'badge-error'}`}>
                                {int.status}
                              </span>
                              {int.duration_ms > 0 && <span className="text-xs text-gray-500">{int.duration_ms}ms</span>}
                              {int.request_summary && (
                                <span className="text-xs text-gray-400 truncate max-w-xs">→ {int.request_summary}</span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Child Logs */}
                    {log.child_logs.length > 0 && (
                      <div>
                        <h4 className="text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
                          Child Agent Executions
                        </h4>
                        <div className="space-y-1 ml-4 border-l-2 border-purple-200 dark:border-purple-800 pl-4">
                          {log.child_logs.map((child) => (
                            <div key={child.id} className="flex items-center gap-2 text-sm">
                              <div className={`w-2 h-2 rounded-full ${agentColors[child.agent_name] || 'bg-gray-500'}`} />
                              <span className="capitalize">{child.agent_name}</span>
                              <span className={`badge text-xs ${
                                child.status === 'completed' ? 'badge-success' :
                                child.status === 'failed' ? 'badge-error' : 'badge-warning'
                              }`}>
                                {child.status}
                              </span>
                              {child.duration_ms > 0 && <span className="text-xs text-gray-500">{child.duration_ms}ms</span>}
                              {child.tokens_used > 0 && <span className="text-xs text-gray-500">{child.tokens_used} tokens</span>}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* A2A Interactions with Details */}
      {activeTab === 'interactions' && (
        <div className="space-y-3">
          {interactions.length === 0 ? (
            <div className="card text-center py-8">
              <p className="text-gray-500">No agent interactions yet</p>
            </div>
          ) : (
            interactions.map((interaction) => (
              <div key={interaction.id} className="card p-0 overflow-hidden">
                {/* Interaction Header - Clickable */}
                <div
                  onClick={() => toggleInteraction(interaction.id)}
                  className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-2.5 h-2.5 rounded-full ${agentColors[interaction.source_agent] || 'bg-gray-500'}`} />
                    <span className="font-medium capitalize">{interaction.source_agent}</span>
                    <svg className="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                    <div className={`w-2.5 h-2.5 rounded-full ${agentColors[interaction.target_agent] || 'bg-gray-500'}`} />
                    <span className="font-medium capitalize">{interaction.target_agent}</span>
                    <span className="badge-info text-xs">{interaction.protocol.toUpperCase()}</span>
                    <span className={`badge ${interaction.status === 'success' ? 'badge-success' : 'badge-error'}`}>
                      {interaction.status}
                    </span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex gap-3 text-xs text-gray-500">
                      {interaction.duration_ms > 0 && <span>{interaction.duration_ms}ms</span>}
                      <span>{new Date(interaction.created_at).toLocaleString()}</span>
                    </div>
                    <svg
                      className={`w-5 h-5 text-gray-400 transition-transform ${expandedInteractions.has(interaction.id) ? 'rotate-180' : ''}`}
                      fill="none" viewBox="0 0 24 24" stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>

                {/* Expanded Details */}
                {expandedInteractions.has(interaction.id) && (
                  <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-gray-50/50 dark:bg-gray-800/30">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      {/* Request Payload */}
                      <div className="bg-blue-50/50 dark:bg-blue-900/10 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
                        <h4 className="text-sm font-semibold mb-3 text-blue-600 dark:text-blue-400 flex items-center gap-2">
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16l-4-4m0 0l4-4m-4 4h18" />
                          </svg>
                          Request from {interaction.source_agent}
                        </h4>
                        {formatPayload(interaction.request_payload, 'request')}
                      </div>

                      {/* Response Payload */}
                      <div className="bg-green-50/50 dark:bg-green-900/10 rounded-lg p-4 border border-green-200 dark:border-green-800">
                        <h4 className="text-sm font-semibold mb-3 text-green-600 dark:text-green-400 flex items-center gap-2">
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                          </svg>
                          Response from {interaction.target_agent}
                        </h4>
                        {formatPayload(interaction.response_payload, 'response')}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Agent Cards */}
      {activeTab === 'agents' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {agents.map((agent) => (
            <div key={agent.name} className="card">
              <div className="flex items-center gap-3 mb-3">
                <div className={`w-3 h-3 rounded-full ${agentColors[agent.name] || 'bg-gray-500'}`} />
                <h3 className="font-semibold capitalize">{agent.name}</h3>
              </div>
              <p className="text-sm text-gray-500 mb-3">{agent.description}</p>
              <div className="flex flex-wrap gap-1">
                {agent.capabilities.map((cap) => (
                  <span key={cap} className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded-full">
                    {cap}
                  </span>
                ))}
              </div>
              <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
                <span className="badge-info">Protocol: {agent.protocol}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Architecture Diagram */}
      <div className="card mt-6">
        <h3 className="text-lg font-semibold mb-4">System Architecture</h3>
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6 text-center">
          <div className="grid grid-cols-4 gap-4 max-w-2xl mx-auto">
            <div className="col-span-4 p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
              <span className="text-sm font-bold text-purple-700 dark:text-purple-300">Orchestrator Agent</span>
              <p className="text-xs text-gray-500 mt-1">Routes & coordinates all requests</p>
            </div>
            {['Ingestion', 'Embedding', 'Retrieval', 'Synthesis'].map((name) => (
              <div key={name} className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <span className="text-xs font-bold text-blue-700 dark:text-blue-300">{name}</span>
              </div>
            ))}
            {['Evaluation', 'Citation', 'Summary'].map((name) => (
              <div key={name} className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <span className="text-xs font-bold text-green-700 dark:text-green-300">{name}</span>
              </div>
            ))}
            <div className="p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
              <span className="text-xs font-bold text-orange-700 dark:text-orange-300">MCP + A2A</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
