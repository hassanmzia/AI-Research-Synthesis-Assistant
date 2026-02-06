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

  const formatJson = (obj: any) => {
    if (!obj || Object.keys(obj).length === 0) return <span className="text-gray-400">Empty</span>;
    return (
      <pre className="text-xs bg-gray-50 dark:bg-gray-800 p-3 rounded overflow-x-auto max-h-64">
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
                      {formatJson(log.input_data)}
                    </div>

                    {/* Output Data */}
                    <div>
                      <h4 className="text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">Output Data</h4>
                      {formatJson(log.output_data)}
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
                    <div className="grid grid-cols-2 gap-4">
                      {/* Request Payload */}
                      <div>
                        <h4 className="text-sm font-semibold mb-2 text-blue-600 dark:text-blue-400">
                          Request Payload
                        </h4>
                        {formatJson(interaction.request_payload)}
                      </div>

                      {/* Response Payload */}
                      <div>
                        <h4 className="text-sm font-semibold mb-2 text-green-600 dark:text-green-400">
                          Response Payload
                        </h4>
                        {formatJson(interaction.response_payload)}
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
