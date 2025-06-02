/**
 * Simple Form Search Component
 * 
 * Following MANDATORY.md UI Rules: basic useState, simple error messages, no complex patterns.
 */

import { useState } from 'react';
import type { FormEvent } from 'react';
import { formService, SimpleForm } from '../services/formService';

interface FormSearchProps {
  onFormSelect?: (form: SimpleForm) => void;
}

export function FormSearch({ onFormSelect }: FormSearchProps) {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [results, setResults] = useState<SimpleForm[]>([]);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault();
    
    try {
      setError('');
      setLoading(true);
      setHasSearched(true);

      const searchResults = await formService.searchForms(searchTerm.trim() || undefined);
      setResults(searchResults);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSearchTerm('');
    setResults([]);
    setError('');
    setHasSearched(false);
  };

  return (
    <div className="form-search">
      <h2 className="text-xl font-bold mb-4">Search Forms</h2>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex space-x-3">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Enter incident name to search (leave empty for all forms)"
            className="flex-1 p-2 border border-gray-300 rounded"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
          {hasSearched && (
            <button
              type="button"
              onClick={handleClear}
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              Clear
            </button>
          )}
        </div>
      </form>

      {error && (
        <div className="text-red-600 mb-4 p-3 border border-red-300 rounded bg-red-50">
          Error: {error}
        </div>
      )}

      {hasSearched && !loading && (
        <div className="search-results">
          <h3 className="text-lg font-semibold mb-3">
            Search Results ({results.length} found)
          </h3>

          {results.length === 0 ? (
            <p className="text-gray-500">
              {searchTerm.trim() 
                ? `No forms found containing "${searchTerm}"`
                : 'No forms found'
              }
            </p>
          ) : (
            <div className="space-y-3">
              {results.map(form => (
                <div
                  key={form.id}
                  className={`border p-4 rounded bg-white ${
                    onFormSelect ? 'cursor-pointer hover:bg-gray-50' : ''
                  }`}
                  onClick={() => onFormSelect?.(form)}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold">{form.incident_name}</h4>
                      <p className="text-sm text-gray-600">Type: {form.form_type}</p>
                      <p className="text-sm text-gray-600">Status: {form.status}</p>
                      <p className="text-xs text-gray-400">
                        Created: {new Date(form.created_at).toLocaleDateString()}
                      </p>
                      <p className="text-xs text-gray-400">
                        Updated: {new Date(form.updated_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">ID: {form.id}</p>
                      {onFormSelect && (
                        <p className="text-xs text-blue-600 mt-1">Click to select</p>
                      )}
                    </div>
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