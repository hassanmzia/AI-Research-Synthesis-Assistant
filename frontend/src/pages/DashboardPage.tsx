import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { analyticsAPI } from '../services/api';
import { DashboardData } from '../types';
import { useAuthStore } from '../store/authStore';

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsAPI.dashboard()
      .then((res) => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const stats = data
    ? [
        { label: 'Projects', value: data.total_projects, color: 'bg-blue-500' },
        { label: 'Papers', value: data.total_papers, color: 'bg-green-500' },
        { label: 'Queries', value: data.total_queries, color: 'bg-purple-500' },
        { label: 'Tokens Used', value: (data.total_tokens_used || 0).toLocaleString(), color: 'bg-orange-500' },
      ]
    : [];

  return (
    <div className="p-4 sm:p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Welcome back, {user?.first_name || user?.username}
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Here's an overview of your research activity
        </p>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-3" />
              <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
            </div>
          ))}
        </div>
      ) : (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 mb-8">
            {stats.map((stat) => (
              <div key={stat.label} className="card">
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${stat.color}`} />
                  <span className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</span>
                </div>
                <p className="text-2xl font-bold mt-2 text-gray-900 dark:text-white">{stat.value}</p>
              </div>
            ))}
          </div>

          {/* Quality Scores */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">RAG Quality Scores</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Groundedness</span>
                    <span className="text-sm font-medium">{data?.avg_groundedness_score || 0}/5</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full transition-all"
                      style={{ width: `${((data?.avg_groundedness_score || 0) / 5) * 100}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Relevance</span>
                    <span className="text-sm font-medium">{data?.avg_relevance_score || 0}/5</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all"
                      style={{ width: `${((data?.avg_relevance_score || 0) / 5) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Agent Performance</h3>
              <div className="space-y-3">
                {(data?.agent_performance || []).slice(0, 5).map((agent) => (
                  <div key={agent.agent_name} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-primary-500" />
                      <span className="text-sm capitalize">{agent.agent_name}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-medium">{agent.total_calls} calls</span>
                      <span className="text-xs text-gray-500 ml-2">
                        ~{Math.round(agent.avg_duration || 0)}ms
                      </span>
                    </div>
                  </div>
                ))}
                {(!data?.agent_performance || data.agent_performance.length === 0) && (
                  <p className="text-sm text-gray-500">No agent activity yet</p>
                )}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              <Link to="/projects" className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 dark:border-dark-border hover:border-primary-300 dark:hover:border-primary-600 transition-colors">
                <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium">New Project</p>
                  <p className="text-xs text-gray-500">Start a new research workspace</p>
                </div>
              </Link>
              <Link to="/reports" className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 dark:border-dark-border hover:border-primary-300 dark:hover:border-primary-600 transition-colors">
                <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium">Generate Report</p>
                  <p className="text-xs text-gray-500">Create a synthesis report</p>
                </div>
              </Link>
              <Link to="/agents" className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 dark:border-dark-border hover:border-primary-300 dark:hover:border-primary-600 transition-colors">
                <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium">View Agents</p>
                  <p className="text-xs text-gray-500">Monitor AI agent system</p>
                </div>
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
