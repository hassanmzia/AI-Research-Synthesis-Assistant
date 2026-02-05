import React, { useCallback, useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { projectAPI, paperAPI, conversationAPI } from '../services/api';
import { Project, Paper, Conversation } from '../types';

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [papers, setPapers] = useState<Paper[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeTab, setActiveTab] = useState<'papers' | 'conversations'>('papers');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (id) {
      projectAPI.get(id).then((res) => setProject(res.data));
      paperAPI.list({ project_id: id }).then((res) => setPapers(res.data.results || res.data));
      conversationAPI.list({ project_id: id }).then((res) => setConversations(res.data.results || res.data));
    }
  }, [id]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (!id) return;
    setUploading(true);
    try {
      for (const file of acceptedFiles) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('project_id', id);
        await paperAPI.upload(formData);
      }
      toast.success(`${acceptedFiles.length} paper(s) uploaded!`);
      paperAPI.list({ project_id: id }).then((res) => setPapers(res.data.results || res.data));
    } catch {
      toast.error('Upload failed');
    } finally {
      setUploading(false);
    }
  }, [id]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxSize: 100 * 1024 * 1024,
  });

  const startConversation = async () => {
    if (!id) return;
    try {
      const res = await conversationAPI.create({ project: id, title: 'New Conversation' });
      const conv = res.data;
      navigate(`/projects/${id}/chat/${conv.id}`);
    } catch {
      toast.error('Failed to create conversation');
    }
  };

  if (!project) {
    return <div className="p-6"><div className="card animate-pulse h-64" /></div>;
  }

  const statusColors: Record<string, string> = {
    pending: 'badge-warning',
    processing: 'badge-info',
    completed: 'badge-success',
    failed: 'badge-error',
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Project Header */}
      <div className="card mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{project.name}</h1>
            <p className="text-gray-500 dark:text-gray-400 mt-1">{project.description}</p>
            <div className="flex gap-4 mt-3 text-sm text-gray-500">
              <span>{project.paper_count} papers</span>
              <span>{project.total_chunks} chunks</span>
              <span>Owner: {project.owner_name}</span>
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={startConversation} className="btn-primary flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              Ask Questions
            </button>
          </div>
        </div>
      </div>

      {/* Upload Zone */}
      <div
        {...getRootProps()}
        className={`card mb-6 border-2 border-dashed cursor-pointer transition-colors ${
          isDragActive ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/10' : 'border-gray-300 dark:border-dark-border hover:border-primary-300'
        }`}
      >
        <input {...getInputProps()} />
        <div className="text-center py-6">
          <svg className="mx-auto h-10 w-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p className="mt-2 text-sm font-medium">
            {uploading ? 'Uploading...' : isDragActive ? 'Drop PDF files here' : 'Drop PDF research papers here, or click to browse'}
          </p>
          <p className="text-xs text-gray-500 mt-1">PDF files up to 100MB</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-4 border-b border-gray-200 dark:border-dark-border">
        {(['papers', 'conversations'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
            <span className="ml-2 text-xs bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full">
              {tab === 'papers' ? papers.length : conversations.length}
            </span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'papers' ? (
        papers.length === 0 ? (
          <div className="card text-center py-8">
            <p className="text-gray-500">No papers uploaded yet. Drop PDFs above to get started.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {papers.map((paper) => (
              <div key={paper.id} className="card flex items-center justify-between">
                <div className="min-w-0 flex-1">
                  <h3 className="font-medium truncate">{paper.title}</h3>
                  <div className="flex gap-3 mt-1 text-xs text-gray-500">
                    <span>{paper.file_name}</span>
                    <span>{paper.page_count} pages</span>
                    <span>{paper.chunk_count} chunks</span>
                    <span>{(paper.file_size / 1024 / 1024).toFixed(1)} MB</span>
                  </div>
                  {paper.authors && paper.authors.length > 0 && (
                    <p className="text-xs text-gray-400 mt-1">{paper.authors.join(', ')}</p>
                  )}
                </div>
                <span className={statusColors[paper.processing_status] || 'badge-info'}>
                  {paper.processing_status}
                </span>
              </div>
            ))}
          </div>
        )
      ) : (
        <div className="space-y-3">
          {conversations.length === 0 ? (
            <div className="card text-center py-8">
              <p className="text-gray-500">No conversations yet.</p>
              <button onClick={startConversation} className="btn-primary mt-3">Start Conversation</button>
            </div>
          ) : (
            conversations.map((conv) => (
              <Link
                key={conv.id}
                to={`/projects/${id}/chat/${conv.id}`}
                className="card block hover:shadow-md transition-shadow"
              >
                <h3 className="font-medium">{conv.title}</h3>
                <div className="flex gap-3 mt-1 text-xs text-gray-500">
                  <span>{conv.message_count} messages</span>
                  <span>{new Date(conv.updated_at).toLocaleString()}</span>
                </div>
                {conv.last_message && (
                  <p className="text-sm text-gray-500 mt-2 truncate">
                    {conv.last_message.content}
                  </p>
                )}
              </Link>
            ))
          )}
        </div>
      )}
    </div>
  );
}
