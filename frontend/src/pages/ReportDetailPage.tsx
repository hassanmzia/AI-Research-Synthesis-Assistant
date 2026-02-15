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
  const [exporting, setExporting] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      reportAPI.get(id)
        .then((res) => setReport(res.data))
        .catch(() => toast.error('Failed to load report'))
        .finally(() => setLoading(false));
    }
  }, [id]);

  const handleExport = async (format: string) => {
    setExporting(format);
    const toastId = toast.loading(`Generating ${format.toUpperCase()}...`);

    try {
      // Create export job
      const createRes = await exportAPI.create({
        export_type: 'synthesis_report',
        output_format: format,
        parameters: { report_id: id },
      });

      const exportId = createRes.data.id;

      // Poll for completion
      let attempts = 0;
      const maxAttempts = 30; // 30 seconds max

      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        const statusRes = await exportAPI.get(exportId);

        if (statusRes.data.status === 'completed') {
          // Download the file
          const extMap: Record<string, string> = {
            pdf: 'pdf', json: 'json', markdown: 'md'
          };
          const ext = extMap[format] || 'txt';
          const filename = `${report?.title?.replace(/[^a-z0-9]/gi, '_') || 'report'}.${ext}`;

          await exportAPI.download(exportId, filename);
          toast.success(`${format.toUpperCase()} downloaded!`, { id: toastId });
          setExporting(null);
          return;
        } else if (statusRes.data.status === 'failed') {
          throw new Error(statusRes.data.error_message || 'Export failed');
        }

        attempts++;
      }

      throw new Error('Export timed out');
    } catch (err: any) {
      toast.error(err.message || 'Export failed', { id: toastId });
    } finally {
      setExporting(null);
    }
  };

  if (loading) {
    return <div className="p-6"><div className="card animate-pulse h-96" /></div>;
  }

  if (!report) {
    return <div className="p-6"><div className="card">Report not found</div></div>;
  }

  return (
    <div className="p-4 sm:p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="card mb-6">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
          <div className="min-w-0">
            <h1 className="text-xl sm:text-2xl font-bold">{report.title}</h1>
            <div className="flex flex-wrap gap-2 sm:gap-3 mt-2 text-xs sm:text-sm text-gray-500">
              <span className="capitalize">{report.report_type.replace('_', ' ')}</span>
              <span>{report.total_tokens_used.toLocaleString()} tokens</span>
              <span>{(report.generation_time_ms / 1000).toFixed(1)}s</span>
              <span>{new Date(report.created_at).toLocaleDateString()}</span>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleExport('pdf')}
              disabled={!!exporting}
              className="btn-primary text-sm disabled:opacity-50 flex-1 sm:flex-none"
            >
              {exporting === 'pdf' ? 'Generating...' : 'Export PDF'}
            </button>
            <button
              onClick={() => handleExport('markdown')}
              disabled={!!exporting}
              className="btn-secondary text-sm disabled:opacity-50 flex-1 sm:flex-none"
            >
              {exporting === 'markdown' ? 'Generating...' : 'Export MD'}
            </button>
            <button
              onClick={() => handleExport('json')}
              disabled={!!exporting}
              className="btn-secondary text-sm disabled:opacity-50 flex-1 sm:flex-none"
            >
              {exporting === 'json' ? 'Generating...' : 'Export JSON'}
            </button>
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
