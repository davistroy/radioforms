/**
 * Simple Form List Component
 * 
 * Following MANDATORY.md UI Rules: basic useState, direct Tauri commands, simple error messages.
 */

import { useState, useEffect } from 'react';
import { formService, SimpleForm } from '../services/formService';
import { exportFormToPDF, exportFormsSummaryToPDF } from '../services/pdfService';

export function FormList() {
  const [forms, setForms] = useState<SimpleForm[]>([]);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadForms();
  }, []);

  const loadForms = async () => {
    try {
      setError('');
      setLoading(true);
      const allForms = await formService.getAllForms();
      setForms(allForms);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load forms');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this form?')) return;
    
    try {
      await formService.deleteForm(id);
      await loadForms(); // Refresh list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete form');
    }
  };

  const handleExportPDF = async (form: SimpleForm) => {
    try {
      setError('');
      await exportFormToPDF(form);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export PDF');
    }
  };

  const handleExportAllPDF = async () => {
    try {
      setError('');
      if (forms.length === 0) {
        setError('No forms to export');
        return;
      }
      await exportFormsSummaryToPDF(forms);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export summary PDF');
    }
  };

  if (loading) {
    return <div className="text-center py-4">Loading forms...</div>;
  }

  if (error) {
    return <div className="text-red-600 py-4">Error: {error}</div>;
  }

  return (
    <div className="form-list">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">All Forms</h2>
        {forms.length > 0 && (
          <button
            onClick={handleExportAllPDF}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Export Summary PDF
          </button>
        )}
      </div>
      
      {forms.length === 0 ? (
        <p className="text-gray-500">No forms found</p>
      ) : (
        <div className="space-y-2">
          {forms.map(form => (
            <div key={form.id} className="border p-4 rounded bg-white">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold">{form.incident_name}</h3>
                  <p className="text-sm text-gray-600">Type: {form.form_type}</p>
                  <p className="text-sm text-gray-600">Status: {form.status}</p>
                  <p className="text-xs text-gray-400">Created: {form.created_at}</p>
                </div>
                <div className="flex space-x-2">
                  <button 
                    onClick={() => handleExportPDF(form)}
                    className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                  >
                    Export PDF
                  </button>
                  <button 
                    onClick={() => handleDelete(form.id)}
                    className="text-red-600 hover:text-red-800 text-sm px-3 py-1"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}