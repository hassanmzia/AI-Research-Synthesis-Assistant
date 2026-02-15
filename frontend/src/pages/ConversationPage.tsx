import React, { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import toast from 'react-hot-toast';
import { queryAPI, conversationAPI } from '../services/api';
import { Conversation, Message, QueryResult } from '../types';

export default function ConversationPage() {
  const { projectId, conversationId } = useParams();
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [lastEval, setLastEval] = useState<QueryResult['evaluation'] | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (conversationId) {
      conversationAPI.get(conversationId).then((res) => {
        setConversation(res.data);
        setMessages(res.data.messages || []);
      });
    }
  }, [conversationId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || !projectId || loading) return;

    const userMsg: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: question,
      sources: [],
      agent_name: '',
      token_count: 0,
      latency_ms: 0,
      metadata: {},
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setQuestion('');
    setLoading(true);
    setLastEval(null);

    try {
      const res = await queryAPI.ask({
        question: question.trim(),
        project_id: projectId,
        conversation_id: conversationId,
        run_evaluation: true,
      });

      const result: QueryResult = res.data;

      const assistantMsg: Message = {
        id: result.query_id || `resp-${Date.now()}`,
        role: 'assistant',
        content: result.answer,
        sources: result.sources || [],
        agent_name: 'synthesis',
        token_count: result.tokens?.total || 0,
        latency_ms: result.latency_ms || 0,
        metadata: {},
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
      if (result.evaluation) {
        setLastEval(result.evaluation);
      }
    } catch (err: any) {
      toast.error(err.response?.data?.error || 'Failed to get response');
      // Remove the temp user message on error
      setMessages((prev) => prev.filter((m) => m.id !== userMsg.id));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-200 dark:border-dark-border bg-white dark:bg-dark-surface">
        <h2 className="text-base sm:text-lg font-semibold truncate">
          {conversation?.title || 'Research Q&A'}
        </h2>
        <p className="text-xs sm:text-sm text-gray-500">
          Ask questions about your research papers using RAG
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-3 sm:px-6 py-4 space-y-4">
        {messages.length === 0 && !loading && (
          <div className="text-center py-20">
            <svg className="mx-auto h-16 w-16 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <h3 className="mt-4 text-lg font-medium text-gray-500">Start your research inquiry</h3>
            <p className="text-sm text-gray-400 mt-2 max-w-md mx-auto">
              Ask questions about your uploaded papers. The AI will search through your documents
              and synthesize answers using RAG (Retrieval-Augmented Generation).
            </p>
            <div className="mt-6 flex flex-wrap gap-2 justify-center">
              {[
                'What are the key findings across the papers?',
                'List the titles of all research papers',
                'What evaluation metrics are discussed?',
                'Compare the methodologies used',
              ].map((q) => (
                <button
                  key={q}
                  onClick={() => setQuestion(q)}
                  className="px-3 py-2 text-sm bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] sm:max-w-3xl rounded-2xl px-4 sm:px-5 py-3 ${
                msg.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border'
              }`}
            >
              {msg.role === 'assistant' ? (
                <div className="prose dark:prose-invert prose-sm max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                </div>
              ) : (
                <p className="whitespace-pre-wrap">{msg.content}</p>
              )}

              {/* Sources */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
                  <p className="text-xs font-medium text-gray-500 mb-1">Sources:</p>
                  <div className="flex flex-wrap gap-1">
                    {msg.sources.map((src, i) => (
                      <span key={i} className="text-xs px-2 py-0.5 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-full">
                        {src.paper_title || 'Paper'}
                        {src.page_number != null && ` (p.${src.page_number})`}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Metadata */}
              {msg.role === 'assistant' && (msg.token_count > 0 || msg.latency_ms > 0) && (
                <div className="mt-2 flex gap-3 text-xs text-gray-400">
                  {msg.token_count > 0 && <span>{msg.token_count} tokens</span>}
                  {msg.latency_ms > 0 && <span>{(msg.latency_ms / 1000).toFixed(1)}s</span>}
                  {msg.agent_name && <span>via {msg.agent_name}</span>}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border rounded-2xl px-5 py-4">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-sm text-gray-500">Synthesizing answer from research papers...</span>
              </div>
            </div>
          </div>
        )}

        {/* Evaluation Display */}
        {lastEval && lastEval.evaluations && (
          <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-4 max-w-3xl">
            <h4 className="text-sm font-semibold mb-2">Quality Evaluation (LLM-as-Judge)</h4>
            <div className="flex gap-4 flex-wrap">
              {Object.entries(lastEval.evaluations).map(([type, result]) => (
                <div key={type} className="text-center">
                  <div className={`text-lg font-bold ${
                    result.score >= 4 ? 'text-green-500' : result.score >= 3 ? 'text-yellow-500' : 'text-red-500'
                  }`}>
                    {result.score}/5
                  </div>
                  <div className="text-xs text-gray-500 capitalize">{type}</div>
                </div>
              ))}
              <div className="text-center">
                <div className="text-lg font-bold text-primary-500">
                  {lastEval.composite_score}/5
                </div>
                <div className="text-xs text-gray-500">Composite</div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-3 sm:px-6 py-3 sm:py-4 border-t border-gray-200 dark:border-dark-border bg-white dark:bg-dark-surface">
        <form onSubmit={handleSubmit} className="flex gap-2 sm:gap-3">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask about your papers..."
            className="input-field flex-1"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="btn-primary px-4 sm:px-6 flex-shrink-0"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}
