import React, { useEffect, useState } from 'react';
import { agentAPI } from '../services/api';
import { AgentCard, AgentLog } from '../types';

export default function AgentsPage() {
  const [agents, setAgents] = useState<AgentCard[]>([]);
  const [logs, setLogs] = useState<AgentLog[]>([]);
  const [activeTab, setActiveTab] = useState<'agents' | 'logs' | 'interactions'>('agents');
  const [interactions, setInteractions] = useState<any[]>([]);

  useEffect(() => {
    agentAPI.list().then((res) => setAgents(res.data.agents || []));
    agentAPI.logs().then((res) => setLogs(res.data.results || res.data || []));
    agentAPI.interactions().then((res) => setInteractions(res.data.results || res.data || []));
  }, []);

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

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Multi-Agent System</h1>
        <p className="text-gray-500 mt-1">Monitor AI agents, A2A interactions, and MCP tools</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-gray-200 dark:border-dark-border">
        {(['agents', 'logs', 'interactions'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors capitalize ${
              activeTab === tab
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab === 'interactions' ? 'A2A Interactions' : tab}
          </button>
        ))}
      </div>

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

      {/* Agent Logs */}
      {activeTab === 'logs' && (
        <div className="space-y-2">
          {logs.length === 0 ? (
            <div className="card text-center py-8">
              <p className="text-gray-500">No agent activity yet</p>
            </div>
          ) : (
            logs.map((log) => (
              <div key={log.id} className="card flex items-center justify-between py-3">
                <div className="flex items-center gap-3">
                  <div className={`w-2.5 h-2.5 rounded-full ${agentColors[log.agent_name] || 'bg-gray-500'}`} />
                  <span className="font-medium capitalize text-sm">{log.agent_name}</span>
                  <span className={`badge ${
                    log.status === 'completed' ? 'badge-success' :
                    log.status === 'failed' ? 'badge-error' :
                    log.status === 'running' ? 'badge-info' : 'badge-warning'
                  }`}>
                    {log.status}
                  </span>
                </div>
                <div className="flex gap-4 text-xs text-gray-500">
                  {log.duration_ms > 0 && <span>{log.duration_ms}ms</span>}
                  {log.tokens_used > 0 && <span>{log.tokens_used} tokens</span>}
                  <span>{new Date(log.created_at).toLocaleString()}</span>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* A2A Interactions */}
      {activeTab === 'interactions' && (
        <div className="space-y-2">
          {interactions.length === 0 ? (
            <div className="card text-center py-8">
              <p className="text-gray-500">No agent interactions yet</p>
            </div>
          ) : (
            interactions.map((interaction: any) => (
              <div key={interaction.id} className="card flex items-center justify-between py-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium capitalize">{interaction.source_agent}</span>
                  <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                  <span className="text-sm font-medium capitalize">{interaction.target_agent}</span>
                  <span className="badge-info">{interaction.protocol}</span>
                </div>
                <div className="flex gap-4 text-xs text-gray-500">
                  <span className={`badge ${interaction.status === 'success' ? 'badge-success' : 'badge-error'}`}>
                    {interaction.status}
                  </span>
                  {interaction.duration_ms > 0 && <span>{interaction.duration_ms}ms</span>}
                </div>
              </div>
            ))
          )}
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
