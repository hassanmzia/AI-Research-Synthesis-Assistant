import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { reportAPI, projectAPI } from '../services/api';
import { SynthesisReport, Project } from '../types';

const REPORT_TYPES = [
  { value: 'literature_review', label: 'Literature Review', icon: '📚' },
  { value: 'comparative_analysis', label: 'Comparative Analysis', icon: '⚖️' },
  { value: 'research_gap', label: 'Research Gap Analysis', icon: '🔍' },
  { value: 'trend_analysis', label: 'Trend Analysis', icon: '📈' },
  { value: 'executive_summary', label: 'Executive Summary', icon: '📋' },
];

export default function ReportsPage() {
  const [reports, setReports] = useState<SynthesisReport[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showGenerate, setShowGenerate] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [genForm, setGenForm] = useState({ project_id: '', report_type: 'literature_review' });

  useEffect(() => {
    Promise.all([
      reportAPI.list().then((res) => setReports(res.data.results || res.data)),
      projectAPI.list().then((res) => setProjects(res.data.results || res.data)),
    ]).finally(() => setLoading(false));
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!genForm.project_id) {
      toast.error('Please select a project');
      return;
    }
    setGenerating(true);
    try {
      await reportAPI.generate(genForm);
      toast.success('Report generation started!');
      setShowGenerate(false);
      reportAPI.list().then((res) => setReports(res.data.results || res.data));
    } catch {
      toast.error('Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  const statusColors: Record<string, string> = {
    pending: 'badge-warning',
    generating: 'badge-info',
    completed: 'badge-success',
    failed: 'badge-error',
  };

  return (
    <div className="p-4 sm:p-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">Synthesis Reports</h1>
          <p className="text-gray-500 mt-1 text-sm sm:text-base">AI-generated research synthesis and analysis</p>
        </div>
        <button onClick={() => setShowGenerate(true)} className="btn-primary flex items-center justify-center gap-2 w-full sm:w-auto">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Generate Report
        </button>
      </div>

      {/* Generate Modal */}
      {showGenerate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="card w-full max-w-lg mx-4">
            <h2 className="text-lg font-bold mb-4">Generate Synthesis Report</h2>
            <form onSubmit={handleGenerate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Project *</label>
                <select
                  value={genForm.project_id}
                  onChange={(e) => setGenForm({ ...genForm, project_id: e.target.value })}
                  className="input-field"
                  required
                >
                  <option value="">Select a project</option>
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.paper_count} papers)
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Report Type *</label>
                <div className="grid grid-cols-1 gap-2">
                  {REPORT_TYPES.map((type) => (
                    <label
                      key={type.value}
                      className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                        genForm.report_type === type.value
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/10'
                          : 'border-gray-200 dark:border-dark-border hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="report_type"
                        value={type.value}
                        checked={genForm.report_type === type.value}
                        onChange={(e) => setGenForm({ ...genForm, report_type: e.target.value })}
                        className="hidden"
                      />
                      <span className="text-lg">{type.icon}</span>
                      <span className="text-sm font-medium">{type.label}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowGenerate(false)} className="btn-secondary">Cancel</button>
                <button type="submit" disabled={generating} className="btn-primary">
                  {generating ? 'Generating...' : 'Generate'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Reports List */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card animate-pulse h-24" />
          ))}
        </div>
      ) : reports.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No reports generated yet.</p>
          <button onClick={() => setShowGenerate(true)} className="btn-primary mt-4">Generate Your First Report</button>
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map((report) => (
            <Link key={report.id} to={`/reports/${report.id}`} className="card block hover:shadow-md transition-shadow">
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                <div className="min-w-0">
                  <h3 className="font-semibold truncate">{report.title}</h3>
                  <div className="flex flex-wrap gap-2 sm:gap-3 mt-1 text-xs text-gray-500">
                    <span className="capitalize">{report.report_type.replace('_', ' ')}</span>
                    <span>{report.total_tokens_used.toLocaleString()} tokens</span>
                    <span>{(report.generation_time_ms / 1000).toFixed(1)}s</span>
                    <span>{new Date(report.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <span className={`flex-shrink-0 ${statusColors[report.status]}`}>{report.status}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
