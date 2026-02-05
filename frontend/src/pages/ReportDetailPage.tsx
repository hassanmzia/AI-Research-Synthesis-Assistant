import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import toast from 'react-hot-toast';
import { reportAPI, exportAPI } from '../services/api';
import { SynthesisReport } from '../types';

export default function ReportDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<SynthesisReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      reportAPI.get(id)
        .then((res) => setReport(res.data))
        .catch(() => toast.error('Failed to load report'))
        .finally(() => setLoading(false));
    }
  }, [id]);

  const handleExport = async (format: string) => {
    try {
      await exportAPI.create({
        export_type: 'synthesis_report',
        output_format: format,
        parameters: { report_id: id },
      });
      toast.success(`Export to ${format.toUpperCase()} started!`);
    } catch {
      toast.error('Export failed');
    }
  };

  if (loading) {
    return <div className="p-6"><div className="card animate-pulse h-96" /></div>;
  }

  if (!report) {
    return <div className="p-6"><div className="card">Report not found</div></div>;
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="card mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold">{report.title}</h1>
            <div className="flex gap-3 mt-2 text-sm text-gray-500">
              <span className="capitalize">{report.report_type.replace('_', ' ')}</span>
              <span>{report.total_tokens_used.toLocaleString()} tokens</span>
              <span>{(report.generation_time_ms / 1000).toFixed(1)}s</span>
              <span>{new Date(report.created_at).toLocaleString()}</span>
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={() => handleExport('markdown')} className="btn-secondary text-sm">Export MD</button>
            <button onClick={() => handleExport('json')} className="btn-secondary text-sm">Export JSON</button>
          </div>
        </div>
      </div>

      {/* Report Content */}
      <div className="card">
        <div className="prose dark:prose-invert prose-lg max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {report.content_markdown}
          </ReactMarkdown>
        </div>
      </div>

      {/* Sections */}
      {report.sections && report.sections.length > 0 && (
        <div className="mt-6 space-y-4">
          <h2 className="text-xl font-bold">Report Sections</h2>
          {report.sections.map((section) => (
            <div key={section.id} className="card">
              <h3 className="text-lg font-semibold mb-3">{section.title}</h3>
              <div className="prose dark:prose-invert prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{section.content}</ReactMarkdown>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
