import React, { useEffect, useState } from 'react';
import { analyticsAPI } from '../services/api';
import { DashboardData } from '../types';

export default function AnalyticsPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [usage, setUsage] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      analyticsAPI.dashboard().then((res) => setData(res.data)),
      analyticsAPI.usage().then((res) => setUsage(res.data)),
    ])
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="card animate-pulse h-24" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 max-w-7xl mx-auto">
      <h1 className="text-xl sm:text-2xl font-bold mb-6">Analytics & Usage</h1>

      {/* Usage Quota */}
      {usage && (
        <div className="card mb-6">
          <h3 className="text-lg font-semibold mb-3">Token Usage This Month</h3>
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4">
                <div
                  className={`h-4 rounded-full transition-all ${
                    usage.percentage_used > 90 ? 'bg-red-500' :
                    usage.percentage_used > 70 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(usage.percentage_used, 100)}%` }}
                />
              </div>
            </div>
            <span className="text-sm font-medium whitespace-nowrap">
              {usage.tokens_used_this_month?.toLocaleString()} / {usage.quota_total?.toLocaleString()} tokens
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            {usage.quota_remaining?.toLocaleString()} tokens remaining ({usage.percentage_used}% used)
          </p>
        </div>
      )}

      {/* Stats Grid */}
      {data && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 mb-6">
            {[
              { label: 'Total Projects', value: data.total_projects, color: 'text-blue-600' },
              { label: 'Total Papers', value: data.total_papers, color: 'text-green-600' },
              { label: 'Total Queries', value: data.total_queries, color: 'text-purple-600' },
              { label: 'Total Tokens', value: data.total_tokens_used?.toLocaleString(), color: 'text-orange-600' },
            ].map((stat) => (
              <div key={stat.label} className="card">
                <p className="text-sm text-gray-500">{stat.label}</p>
                <p className={`text-2xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
              </div>
            ))}
          </div>

          {/* Quality Scores */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="card">
              <h3 className="font-semibold mb-4">RAG Quality Metrics</h3>
              <div className="space-y-4">
                {[
                  { label: 'Avg Groundedness', value: data.avg_groundedness_score, color: 'bg-green-500' },
                  { label: 'Avg Relevance', value: data.avg_relevance_score, color: 'bg-blue-500' },
                ].map((metric) => (
                  <div key={metric.label}>
                    <div className="flex justify-between text-sm mb-1">
                      <span>{metric.label}</span>
                      <span className="font-medium">{metric.value}/5.0</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                      <div
                        className={`${metric.color} h-2.5 rounded-full`}
                        style={{ width: `${(metric.value / 5) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card">
              <h3 className="font-semibold mb-4">Queries Over Time (30 days)</h3>
              {data.queries_by_day && data.queries_by_day.length > 0 ? (
                <div className="flex items-end gap-1 h-32">
                  {data.queries_by_day.map((day, i) => {
                    const maxCount = Math.max(...data.queries_by_day.map((d) => d.count));
                    const height = maxCount > 0 ? (day.count / maxCount) * 100 : 0;
                    return (
                      <div
                        key={i}
                        className="flex-1 bg-primary-500 rounded-t-sm min-h-[2px] transition-all"
                        style={{ height: `${height}%` }}
                        title={`${day.date}: ${day.count} queries`}
                      />
                    );
                  })}
                </div>
              ) : (
                <p className="text-sm text-gray-500 text-center py-8">No query data yet</p>
              )}
            </div>
          </div>

          {/* Top Papers & Agent Performance */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="card">
              <h3 className="font-semibold mb-4">Most Referenced Papers</h3>
              <div className="space-y-3">
                {(data.top_papers || []).map((paper, i) => (
                  <div key={paper.id} className="flex items-center gap-3">
                    <span className="text-lg font-bold text-gray-300 w-6">{i + 1}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{paper.title}</p>
                      <p className="text-xs text-gray-500">{paper.query_count} references</p>
                    </div>
                  </div>
                ))}
                {(!data.top_papers || data.top_papers.length === 0) && (
                  <p className="text-sm text-gray-500 text-center py-4">No data yet</p>
                )}
              </div>
            </div>

            <div className="card">
              <h3 className="font-semibold mb-4">Agent Performance</h3>
              <div className="space-y-3">
                {(data.agent_performance || []).map((agent) => (
                  <div key={agent.agent_name} className="flex items-center justify-between">
                    <span className="text-sm font-medium capitalize">{agent.agent_name}</span>
                    <div className="flex gap-4 text-xs text-gray-500">
                      <span>{agent.total_calls} calls</span>
                      <span>~{Math.round(agent.avg_duration || 0)}ms avg</span>
                      <span>{(agent.total_tokens || 0).toLocaleString()} tokens</span>
                    </div>
                  </div>
                ))}
                {(!data.agent_performance || data.agent_performance.length === 0) && (
                  <p className="text-sm text-gray-500 text-center py-4">No agent data yet</p>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
