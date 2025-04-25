'use client';
import { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [questions, setQuestions] = useState('');
  const [labels, setLabels] = useState('');
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [downloadUrls, setDownloadUrls] = useState<{csv?: string; json?: string}>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!files || files.length === 0) {
      setError('Please select files to process');
      return;
    }
    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('questions', questions.trim());
      formData.append('labels', labels.trim());
      
      Array.from(files).forEach(file => {
        formData.append('files', file);
      });

      const API_URL = process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, '') || 'http://localhost:10000';

      const response = await axios.post(`${API_URL}/api/process`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.success) {
        setDownloadUrls({
          csv: `${API_URL}${response.data.csvUrl}`,
          json: `${API_URL}${response.data.jsonUrl}`,
        });
      }
    } catch (err) {
      setError('An error occurred while processing your request.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-8 max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-8 text-center">ExtractoMate</h1>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium mb-2">
            Upload Files
          </label>
          <input
            type="file"
            multiple
            onChange={(e) => setFiles(e.target.files)}
            className="w-full p-3 border rounded-lg shadow-sm"
            accept=".txt,.doc,.docx,.pdf"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Questions (comma-separated)
          </label>
          <textarea
            value={questions}
            onChange={(e) => setQuestions(e.target.value)}
            className="w-full p-3 border rounded-lg shadow-sm"
            rows={4}
            placeholder="Enter your questions, separated by commas"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Labels (comma-separated)
          </label>
          <textarea
            value={labels}
            onChange={(e) => setLabels(e.target.value)}
            className="w-full p-3 border rounded-lg shadow-sm"
            rows={4}
            placeholder="Enter your labels, separated by commas"
          />
        </div>

        {error && (
          <div className="text-red-500 text-sm">{error}</div>
        )}

        <button
          type="submit"
          disabled={loading}
          className={`w-full py-3 px-4 rounded-lg text-white font-medium
            ${loading 
              ? 'bg-blue-400 cursor-not-allowed' 
              : 'bg-blue-600 hover:bg-blue-700'
            }`}
        >
          {loading ? 'Processing...' : 'Process Files'}
        </button>
      </form>

      {(downloadUrls.csv || downloadUrls.json) && (
        <div className="mt-8 p-6 bg-gray-50 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Download Results</h2>
          <div className="space-y-3">
            {downloadUrls.csv && (
              <a 
                href={downloadUrls.csv}
                className="block text-blue-600 hover:text-blue-800"
                download
              >
                Download CSV Results
              </a>
            )}
            {downloadUrls.json && (
              <a 
                href={downloadUrls.json}
                className="block text-blue-600 hover:text-blue-800"
                download
              >
                Download JSON Results
              </a>
            )}
          </div>
        </div>
      )}
    </main>
  );
}