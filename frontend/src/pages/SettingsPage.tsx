import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { useAuthStore } from '../store/authStore';
import { apiKeyAPI, exportAPI } from '../services/api';

export default function SettingsPage() {
  const { user, updateUser } = useAuthStore();
  const [apiKeys, setApiKeys] = useState<any[]>([]);
  const [exports, setExports] = useState<any[]>([]);
  const [profile, setProfile] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    bio: user?.bio || '',
    institution: user?.institution || '',
  });
  const [newKey, setNewKey] = useState({ provider: 'openai', api_key: '', base_url: '' });
  const [activeTab, setActiveTab] = useState<'profile' | 'api-keys' | 'exports'>('profile');

  useEffect(() => {
    apiKeyAPI.list().then((res) => setApiKeys(res.data.results || res.data || []));
    exportAPI.list().then((res) => setExports(res.data.results || res.data || []));
  }, []);

  const saveProfile = async () => {
    try {
      await updateUser(profile);
      toast.success('Profile updated!');
    } catch {
      toast.error('Failed to update profile');
    }
  };

  const addApiKey = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiKeyAPI.create(newKey);
      toast.success('API key added!');
      setNewKey({ provider: 'openai', api_key: '', base_url: '' });
      apiKeyAPI.list().then((res) => setApiKeys(res.data.results || res.data || []));
    } catch {
      toast.error('Failed to add API key');
    }
  };

  const handleDownload = async (exp: any) => {
    const extMap: Record<string, string> = {
      pdf: 'pdf', json: 'json', markdown: 'md', csv: 'csv', bibtex: 'bib'
    };
    const ext = extMap[exp.output_format] || 'txt';
    const filename = `${exp.export_type}_${exp.id.slice(0, 8)}.${ext}`;
    try {
      await exportAPI.download(exp.id, filename);
      toast.success('Download started!');
    } catch {
      toast.error('Download failed');
    }
  };

  const tabs = [
    { id: 'profile', label: 'Profile' },
    { id: 'api-keys', label: 'API Keys' },
    { id: 'exports', label: 'Exports' },
  ] as const;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      <div className="flex gap-1 mb-6 border-b border-gray-200 dark:border-dark-border">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Profile */}
      {activeTab === 'profile' && (
        <div className="card space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">First Name</label>
              <input type="text" value={profile.first_name} onChange={(e) => setProfile({ ...profile, first_name: e.target.value })} className="input-field" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Last Name</label>
              <input type="text" value={profile.last_name} onChange={(e) => setProfile({ ...profile, last_name: e.target.value })} className="input-field" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Institution</label>
            <input type="text" value={profile.institution} onChange={(e) => setProfile({ ...profile, institution: e.target.value })} className="input-field" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Bio</label>
            <textarea value={profile.bio} onChange={(e) => setProfile({ ...profile, bio: e.target.value })} className="input-field" rows={4} />
          </div>
          <div className="flex justify-end">
            <button onClick={saveProfile} className="btn-primary">Save Profile</button>
          </div>
          <div className="pt-4 border-t border-gray-200 dark:border-dark-border">
            <h3 className="font-medium mb-2">Account Info</h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div><span className="text-gray-500">Username:</span> {user?.username}</div>
              <div><span className="text-gray-500">Email:</span> {user?.email}</div>
              <div><span className="text-gray-500">Token Quota:</span> {user?.usage_quota_tokens?.toLocaleString()}</div>
              <div><span className="text-gray-500">Tokens Used:</span> {user?.tokens_used_this_month?.toLocaleString()}</div>
            </div>
          </div>
        </div>
      )}

      {/* API Keys */}
      {activeTab === 'api-keys' && (
        <div className="space-y-4">
          <div className="card">
            <h3 className="font-semibold mb-4">Add API Key</h3>
            <form onSubmit={addApiKey} className="space-y-3">
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-sm font-medium mb-1">Provider</label>
                  <select value={newKey.provider} onChange={(e) => setNewKey({ ...newKey, provider: e.target.value })} className="input-field">
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="cohere">Cohere</option>
                    <option value="huggingface">HuggingFace</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">API Key</label>
                  <input type="password" value={newKey.api_key} onChange={(e) => setNewKey({ ...newKey, api_key: e.target.value })} className="input-field" required />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Base URL (optional)</label>
                  <input type="url" value={newKey.base_url} onChange={(e) => setNewKey({ ...newKey, base_url: e.target.value })} className="input-field" />
                </div>
              </div>
              <button type="submit" className="btn-primary">Add Key</button>
            </form>
          </div>

          {apiKeys.length > 0 && (
            <div className="card">
              <h3 className="font-semibold mb-4">Configured Keys</h3>
              <div className="space-y-2">
                {apiKeys.map((key: any) => (
                  <div key={key.id} className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-dark-border">
                    <div>
                      <span className="text-sm font-medium capitalize">{key.provider}</span>
                      <span className="text-xs text-gray-500 ml-3">{key.api_key_masked}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={key.is_active ? 'badge-success' : 'badge-error'}>
                        {key.is_active ? 'Active' : 'Inactive'}
                      </span>
                      <button
                        onClick={async () => {
                          await apiKeyAPI.delete(key.id);
                          setApiKeys(apiKeys.filter((k: any) => k.id !== key.id));
                          toast.success('API key deleted');
                        }}
                        className="text-red-500 hover:text-red-600 text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Exports */}
      {activeTab === 'exports' && (
        <div className="card">
          <h3 className="font-semibold mb-4">Export History</h3>
          {exports.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-6">No exports yet</p>
          ) : (
            <div className="space-y-2">
              {exports.map((exp: any) => (
                <div key={exp.id} className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-dark-border">
                  <div>
                    <span className="text-sm font-medium capitalize">{exp.export_type.replace('_', ' ')}</span>
                    <span className="text-xs text-gray-500 ml-3 uppercase">{exp.output_format}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`badge ${
                      exp.status === 'completed' ? 'badge-success' :
                      exp.status === 'processing' ? 'badge-info' : 'badge-warning'
                    }`}>
                      {exp.status}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(exp.created_at).toLocaleString()}
                    </span>
                    {exp.status === 'completed' && (
                      <button
                        onClick={() => handleDownload(exp)}
                        className="btn-primary text-xs px-2 py-1"
                      >
                        Download
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
