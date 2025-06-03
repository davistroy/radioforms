/**
 * Simple Export/Import Component for RadioForms
 * 
 * Following MANDATORY.md: Simple interface for emergency responders.
 * Export all forms to JSON, import forms from JSON file.
 */

import React, { useState } from 'react';
import { formService } from '../services/formService';

export function ExportImport() {
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleExportAll = async () => {
    try {
      setLoading(true);
      setError('');
      setMessage('');
      
      const jsonData = await formService.exportFormsJSON();
      
      // Create download link
      const blob = new Blob([jsonData], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `radioforms-export-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      setMessage('Forms exported successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setLoading(true);
      setError('');
      setMessage('');
      
      // Read file content
      const text = await file.text();
      
      // Import forms
      const result = await formService.importFormsJSON(text);
      setMessage(result);
      
      // Clear file input
      event.target.value = '';
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Import failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Export/Import Forms</h2>
      
      {message && (
        <div className="mb-4 p-3 bg-green-100 text-green-700 rounded">
          {message}
        </div>
      )}
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}
      
      <div className="space-y-4">
        {/* Export Section */}
        <div>
          <h3 className="font-semibold mb-2">Export All Forms</h3>
          <p className="text-sm text-gray-600 mb-3">
            Download all forms as a JSON file for backup or transfer.
          </p>
          <button
            onClick={handleExportAll}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Exporting...' : 'Export All Forms'}
          </button>
        </div>
        
        <hr className="my-6" />
        
        {/* Import Section */}
        <div>
          <h3 className="font-semibold mb-2">Import Forms</h3>
          <p className="text-sm text-gray-600 mb-3">
            Import forms from a JSON file. Duplicate forms will be skipped.
          </p>
          <input
            type="file"
            accept=".json"
            onChange={handleImport}
            disabled={loading}
            className="block w-full text-sm text-gray-900 border border-gray-300 rounded cursor-pointer bg-gray-50 focus:outline-none"
          />
          <p className="mt-1 text-xs text-gray-500">
            Select a JSON file exported from RadioForms
          </p>
        </div>
      </div>
    </div>
  );
}