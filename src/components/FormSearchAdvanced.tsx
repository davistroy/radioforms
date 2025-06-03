/**
 * Advanced Form Search Component
 * 
 * Following MANDATORY.md: Simple search interface for emergency responders
 * - Real-time search with debouncing to reduce server load
 * - Multiple filter criteria (incident name, form type, status, date range)
 * - Keyboard shortcuts for quick access during emergencies
 * - Clear visual feedback and error handling
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import type { FormEvent } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { SimpleForm } from '../services/formService';
import { debounce } from '../utils/debounce';

interface FormSearchAdvancedProps {
  onFormSelect?: (form: SimpleForm) => void;
  autoFocus?: boolean;
}

// Form types available in the system
const FORM_TYPES = [
  'ICS-201', 'ICS-202', 'ICS-203', 'ICS-204', 'ICS-205', 
  'ICS-206', 'ICS-207', 'ICS-208', 'ICS-209', 'ICS-210',
  'ICS-211', 'ICS-213', 'ICS-214', 'ICS-215', 'ICS-218',
  'ICS-220', 'ICS-221', 'ICS-225'
];

// Form statuses
const FORM_STATUSES = ['draft', 'completed', 'final', 'archived'];

export function FormSearchAdvanced({ onFormSelect, autoFocus = false }: FormSearchAdvancedProps) {
  // Search criteria state
  const [incidentName, setIncidentName] = useState('');
  const [formType, setFormType] = useState('');
  const [status, setStatus] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  
  // UI state
  const [results, setResults] = useState<SimpleForm[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  
  // Sorting and pagination
  const [sortBy, setSortBy] = useState<'created_at' | 'incident_name' | 'form_type' | 'status'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);

  // Saved searches
  const [savedSearches, setSavedSearches] = useState<Array<{
    id: string;
    name: string;
    incidentName: string;
    formType: string;
    status: string;
    dateFrom: string;
    dateTo: string;
    createdAt: string;
  }>>([]);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [saveSearchName, setSaveSearchName] = useState('');

  // Keyboard navigation
  const [selectedResultIndex, setSelectedResultIndex] = useState(-1);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const searchInputRef = useRef<any>(null);

  // Perform search with current criteria
  const performSearch = useCallback(async () => {
    try {
      setError('');
      setLoading(true);
      setHasSearched(true);

      // Call advanced search with all criteria
      const searchResults = await invoke<SimpleForm[]>('advanced_search', {
        incidentName: incidentName.trim() || null,
        formType: formType || null,
        status: status || null,
        dateFrom: dateFrom || null,
        dateTo: dateTo || null,
      });

      setResults(searchResults);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [incidentName, formType, status, dateFrom, dateTo]);

  // Debounced search for real-time filtering
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const debouncedSearch = useCallback(
    debounce(performSearch, 300),
    [incidentName, formType, status, dateFrom, dateTo]
  );

  // Auto-search when criteria change
  useEffect(() => {
    if (incidentName || formType || status || dateFrom || dateTo) {
      debouncedSearch();
    }
  }, [incidentName, formType, status, dateFrom, dateTo, debouncedSearch]);

  // Load saved searches from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem('radioforms-saved-searches');
      if (saved) {
        setSavedSearches(JSON.parse(saved));
      }
    } catch (error) {
      console.warn('Failed to load saved searches:', error);
    }
  }, []);

  // Save search to localStorage
  const saveCurrentSearch = () => {
    if (!saveSearchName.trim()) return;
    
    const newSearch = {
      id: Date.now().toString(),
      name: saveSearchName.trim(),
      incidentName,
      formType,
      status,
      dateFrom,
      dateTo,
      createdAt: new Date().toISOString(),
    };
    
    const updated = [...savedSearches, newSearch];
    setSavedSearches(updated);
    
    try {
      localStorage.setItem('radioforms-saved-searches', JSON.stringify(updated));
    } catch (error) {
      console.warn('Failed to save search:', error);
    }
    
    setSaveSearchName('');
    setShowSaveDialog(false);
  };

  // Load a saved search
  const loadSavedSearch = (search: typeof savedSearches[0]) => {
    setIncidentName(search.incidentName);
    setFormType(search.formType);
    setStatus(search.status);
    setDateFrom(search.dateFrom);
    setDateTo(search.dateTo);
  };

  // Delete a saved search
  const deleteSavedSearch = (id: string) => {
    const updated = savedSearches.filter(s => s.id !== id);
    setSavedSearches(updated);
    
    try {
      localStorage.setItem('radioforms-saved-searches', JSON.stringify(updated));
    } catch (error) {
      console.warn('Failed to delete saved search:', error);
    }
  };

  // Handle form submission
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    performSearch();
  };

  // Clear all filters
  const handleClearAll = () => {
    setIncidentName('');
    setFormType('');
    setStatus('');
    setDateFrom('');
    setDateTo('');
    setResults([]);
    setError('');
    setHasSearched(false);
  };

  // Quick filter buttons
  const handleQuickFilter = (filterType: 'today' | 'week' | 'draft') => {
    const today = new Date();
    
    switch (filterType) {
      case 'today': {
        const dateStr = today.toISOString().split('T')[0];
        setDateFrom(dateStr);
        setDateTo(dateStr);
        break;
      }
      case 'week': {
        const weekAgo = new Date(today);
        weekAgo.setDate(weekAgo.getDate() - 7);
        setDateFrom(weekAgo.toISOString().split('T')[0]);
        setDateTo(today.toISOString().split('T')[0]);
        break;
      }
      case 'draft':
        setStatus('draft');
        break;
    }
  };

  // Sort results
  const sortedResults = [...results].sort((a, b) => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let aVal: any = a[sortBy];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let bVal: any = b[sortBy];
    
    // Convert dates for comparison
    if (sortBy === 'created_at') {
      aVal = new Date(aVal).getTime();
      bVal = new Date(bVal).getTime();
    }
    
    if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
    return 0;
  });

  // Paginate results
  const totalPages = Math.ceil(sortedResults.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedResults = sortedResults.slice(startIndex, startIndex + itemsPerPage);

  // Handle sort change
  const handleSort = (field: typeof sortBy) => {
    if (field === sortBy) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
    setCurrentPage(1); // Reset to first page when sorting
  };

  // Keyboard navigation for results
  const handleKeyDown = useCallback((e: globalThis.KeyboardEvent) => {
    if (!hasSearched || paginatedResults.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedResultIndex(prev => 
          prev < paginatedResults.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedResultIndex(prev => prev > 0 ? prev - 1 : 0);
        break;
      case 'Enter':
        if (selectedResultIndex >= 0 && onFormSelect) {
          e.preventDefault();
          onFormSelect(paginatedResults[selectedResultIndex]);
        }
        break;
      case 'Escape':
        e.preventDefault();
        setSelectedResultIndex(-1);
        if (showSaveDialog) {
          setShowSaveDialog(false);
          setSaveSearchName('');
        } else {
          searchInputRef.current?.focus();
        }
        break;
      // Quick shortcuts for emergency responders
      case 'f':
        if (e.ctrlKey || e.metaKey) {
          e.preventDefault();
          searchInputRef.current?.focus();
        }
        break;
      case 't':
        if (e.ctrlKey || e.metaKey) {
          e.preventDefault();
          handleQuickFilter('today');
        }
        break;
      case 'w':
        if (e.ctrlKey || e.metaKey) {
          e.preventDefault();
          handleQuickFilter('week');
        }
        break;
      case 'd':
        if (e.ctrlKey || e.metaKey) {
          e.preventDefault();
          handleQuickFilter('draft');
        }
        break;
    }
  }, [hasSearched, paginatedResults, selectedResultIndex, onFormSelect, showSaveDialog]);

  // Reset selected index when results change
  useEffect(() => {
    setSelectedResultIndex(-1);
  }, [results, currentPage]);

  // Add global keyboard listeners
  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  // Focus management
  useEffect(() => {
    if (autoFocus && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [autoFocus]);

  return (
    <div className="form-search-advanced">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Search Forms</h2>
        <div className="flex items-center space-x-4">
          <div className="text-xs text-gray-500">
            <span className="font-mono">Ctrl+F</span> Focus search |{' '}
            <span className="font-mono">↑↓</span> Navigate |{' '}
            <span className="font-mono">Enter</span> Select |{' '}
            <span className="font-mono">Esc</span> Clear
          </div>
          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            {showFilters ? 'Hide Filters' : 'Show Filters'} ▼
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Main search input */}
        <div className="relative">
          <input
            ref={searchInputRef}
            type="text"
            value={incidentName}
            onChange={(e) => setIncidentName(e.target.value)}
            placeholder="Search by incident name... (Ctrl+F to focus)"
            className="w-full p-3 border border-gray-300 rounded-lg text-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            autoFocus={autoFocus}
            aria-label="Search by incident name"
          />
          {loading && (
            <div className="absolute right-3 top-3">
              <div className="animate-spin h-6 w-6 border-2 border-blue-500 border-t-transparent rounded-full"></div>
            </div>
          )}
        </div>

        {/* Quick filters */}
        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={() => handleQuickFilter('today')}
            className="px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 text-sm"
          >
            Today's Forms
          </button>
          <button
            type="button"
            onClick={() => handleQuickFilter('week')}
            className="px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 text-sm"
          >
            Last 7 Days
          </button>
          <button
            type="button"
            onClick={() => handleQuickFilter('draft')}
            className="px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 text-sm"
          >
            Draft Forms
          </button>
          
          {/* Save search button */}
          {(incidentName || formType || status || dateFrom || dateTo) && (
            <button
              type="button"
              onClick={() => setShowSaveDialog(true)}
              className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
            >
              Save Search
            </button>
          )}
        </div>

        {/* Saved searches */}
        {savedSearches.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-700">Saved Searches:</h4>
            <div className="flex flex-wrap gap-2">
              {savedSearches.map(search => (
                <div key={search.id} className="flex items-center bg-blue-50 rounded border">
                  <button
                    type="button"
                    onClick={() => loadSavedSearch(search)}
                    className="px-3 py-1 text-sm text-blue-700 hover:bg-blue-100 rounded-l"
                    title={`Load search: ${search.name}`}
                  >
                    {search.name}
                  </button>
                  <button
                    type="button"
                    onClick={() => deleteSavedSearch(search.id)}
                    className="px-2 py-1 text-red-600 hover:bg-red-100 rounded-r text-sm"
                    title="Delete saved search"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Save search dialog */}
        {showSaveDialog && (
          <div className="bg-blue-50 border border-blue-200 rounded p-4 space-y-3">
            <h4 className="font-medium text-blue-900">Save Current Search</h4>
            <div className="flex space-x-3">
              <input
                type="text"
                value={saveSearchName}
                onChange={(e) => setSaveSearchName(e.target.value)}
                placeholder="Enter search name..."
                className="flex-1 p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    saveCurrentSearch();
                  } else if (e.key === 'Escape') {
                    setShowSaveDialog(false);
                    setSaveSearchName('');
                  }
                }}
                autoFocus
              />
              <button
                type="button"
                onClick={saveCurrentSearch}
                disabled={!saveSearchName.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                Save
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowSaveDialog(false);
                  setSaveSearchName('');
                }}
                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Advanced filters */}
        {showFilters && (
          <div className="bg-gray-50 p-4 rounded-lg space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Form Type */}
              <div>
                <label htmlFor="formType" className="block text-sm font-medium text-gray-700 mb-1">
                  Form Type
                </label>
                <select
                  id="formType"
                  value={formType}
                  onChange={(e) => setFormType(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Types</option>
                  {FORM_TYPES.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              {/* Status */}
              <div>
                <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  id="status"
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Statuses</option>
                  {FORM_STATUSES.map(st => (
                    <option key={st} value={st}>
                      {st.charAt(0).toUpperCase() + st.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              {/* Date From */}
              <div>
                <label htmlFor="dateFrom" className="block text-sm font-medium text-gray-700 mb-1">
                  From Date
                </label>
                <input
                  id="dateFrom"
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Date To */}
              <div>
                <label htmlFor="dateTo" className="block text-sm font-medium text-gray-700 mb-1">
                  To Date
                </label>
                <input
                  id="dateTo"
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex space-x-3">
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50 font-medium"
          >
            Search
          </button>
          {hasSearched && (
            <button
              type="button"
              onClick={handleClearAll}
              className="bg-gray-500 text-white px-6 py-2 rounded hover:bg-gray-600 font-medium"
            >
              Clear All
            </button>
          )}
        </div>
      </form>

      {/* Error display */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-300 rounded text-red-700" role="alert">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Results */}
      {hasSearched && !loading && (
        <div className="mt-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">
              Search Results ({results.length} found)
            </h3>
            {results.length > 0 && (
              <span className="text-sm text-gray-500">
                Showing {startIndex + 1}-{Math.min(startIndex + itemsPerPage, results.length)} of {results.length}
              </span>
            )}
          </div>

          {/* Sort controls */}
          {results.length > 0 && (
            <div className="mb-4 flex flex-wrap gap-2">
              <span className="text-sm text-gray-600 self-center">Sort by:</span>
              <button
                onClick={() => handleSort('created_at')}
                className={`px-3 py-1 text-sm rounded ${
                  sortBy === 'created_at' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Date {sortBy === 'created_at' && (sortOrder === 'asc' ? '↑' : '↓')}
              </button>
              <button
                onClick={() => handleSort('incident_name')}
                className={`px-3 py-1 text-sm rounded ${
                  sortBy === 'incident_name' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Name {sortBy === 'incident_name' && (sortOrder === 'asc' ? '↑' : '↓')}
              </button>
              <button
                onClick={() => handleSort('form_type')}
                className={`px-3 py-1 text-sm rounded ${
                  sortBy === 'form_type' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Type {sortBy === 'form_type' && (sortOrder === 'asc' ? '↑' : '↓')}
              </button>
              <button
                onClick={() => handleSort('status')}
                className={`px-3 py-1 text-sm rounded ${
                  sortBy === 'status' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Status {sortBy === 'status' && (sortOrder === 'asc' ? '↑' : '↓')}
              </button>
            </div>
          )}

          {results.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p className="text-lg">No forms found matching your criteria</p>
              <p className="text-sm mt-2">Try adjusting your search filters</p>
            </div>
          ) : (
            <>
              <div className="grid gap-3">
                {paginatedResults.map((form, index) => (
                <div
                  key={form.id}
                  className={`border rounded-lg p-4 shadow-sm transition-colors ${
                    index === selectedResultIndex 
                      ? 'bg-blue-50 border-blue-500 shadow-md' 
                      : 'bg-white'
                  } ${
                    onFormSelect ? 'cursor-pointer hover:bg-gray-50 hover:shadow-md' : ''
                  }`}
                  onClick={() => onFormSelect?.(form)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      onFormSelect?.(form);
                    }
                  }}
                  tabIndex={onFormSelect ? 0 : -1}
                  role={onFormSelect ? 'button' : 'article'}
                  aria-label={`Form ${form.incident_name}, Type ${form.form_type}, Status ${form.status}`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className="font-semibold text-lg">{form.incident_name}</h4>
                      <div className="mt-1 space-y-1">
                        <p className="text-sm text-gray-600">
                          <span className="font-medium">Type:</span> {form.form_type}
                        </p>
                        <p className="text-sm text-gray-600">
                          <span className="font-medium">Status:</span>{' '}
                          <span className={`inline-block px-2 py-1 text-xs rounded ${
                            form.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                            form.status === 'completed' ? 'bg-green-100 text-green-800' :
                            form.status === 'final' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {form.status.toUpperCase()}
                          </span>
                        </p>
                        <p className="text-xs text-gray-500">
                          Created: {new Date(form.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right ml-4">
                      <p className="text-sm font-mono text-gray-500">ID: {form.id}</p>
                    </div>
                  </div>
                </div>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="mt-6 flex justify-center items-center space-x-2">
                  <button
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                    className="px-3 py-2 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  
                  <div className="flex space-x-1">
                    {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                      let pageNum;
                      if (totalPages <= 5) {
                        pageNum = i + 1;
                      } else if (currentPage <= 3) {
                        pageNum = i + 1;
                      } else if (currentPage >= totalPages - 2) {
                        pageNum = totalPages - 4 + i;
                      } else {
                        pageNum = currentPage - 2 + i;
                      }
                      
                      return (
                        <button
                          key={pageNum}
                          onClick={() => setCurrentPage(pageNum)}
                          className={`px-3 py-2 text-sm rounded ${
                            currentPage === pageNum
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                          }`}
                        >
                          {pageNum}
                        </button>
                      );
                    })}
                  </div>
                  
                  <button
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                    className="px-3 py-2 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}