/**
 * RadioForms Main Application Component
 * 
 * This is the root component of the RadioForms application.
 * It provides the main dashboard and navigation for managing ICS forms.
 * 
 * Business Logic:
 * - Displays recent forms and quick actions
 * - Provides navigation to different parts of the application
 * - Shows application status and backend information
 * - Handles form creation workflow
 */

import { useState, useEffect } from "react";
import { formService } from "./services/formService";
import { getAvailableFormTypes } from "./templates";
import type { Form, DatabaseStats, ICSFormType } from "./types/forms";

function App() {
  const [recentForms, setRecentForms] = useState<Form[]>([]);
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load recent forms and stats in parallel
      const [forms, statistics] = await Promise.all([
        formService.getRecentForms(5),
        formService.getDatabaseStats()
      ]);

      setRecentForms(forms);
      setStats(statistics);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const createNewForm = async (formType: ICSFormType) => {
    try {
      const incidentName = prompt('Enter incident name:');
      if (!incidentName?.trim()) return;

      const form = await formService.createForm({
        form_type: formType,
        incident_name: incidentName.trim(),
        preparer_name: 'Current User' // TODO: Get from settings
      });

      console.log('Created form:', form);
      
      // Refresh dashboard data
      await loadDashboardData();
      
      alert(`Form ${form.form_type} created successfully (ID: ${form.id})`);
    } catch (err) {
      console.error('Failed to create form:', err);
      alert('Failed to create form: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const formatStatus = (status: string) => {
    switch (status) {
      case 'draft': return 'Draft';
      case 'completed': return 'Completed';
      case 'final': return 'Final';
      default: return status;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'status-badge-draft';
      case 'completed': return 'status-badge-completed';
      case 'final': return 'status-badge-final';
      default: return 'status-badge-draft';
    }
  };

  const backendInfo = formService.getBackendInfo();
  const availableFormTypes = getAvailableFormTypes();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading RadioForms...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <h1 className="text-2xl font-bold text-destructive mb-4">Error</h1>
          <p className="text-muted-foreground mb-4">{error}</p>
          <button 
            onClick={loadDashboardData}
            className="btn btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container-app">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gradient">RadioForms</h1>
              <span className="text-sm text-muted-foreground">
                ICS Forms Management
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-muted-foreground">
                Backend: {backendInfo.type === 'mock' ? 'Development Mode' : 'Production'}
              </span>
              {backendInfo.type === 'mock' && (
                <button
                  onClick={() => formService.initializeSampleData()}
                  className="btn btn-outline btn-sm"
                  title="Reinitialize sample data"
                >
                  Reset Data
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container-app py-8">
        {/* Stats Overview */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="card">
              <div className="card-content pt-6">
                <div className="text-2xl font-bold">{stats.total_forms}</div>
                <p className="text-xs text-muted-foreground">Total Forms</p>
              </div>
            </div>
            <div className="card">
              <div className="card-content pt-6">
                <div className="text-2xl font-bold text-yellow-600">{stats.draft_forms}</div>
                <p className="text-xs text-muted-foreground">Draft Forms</p>
              </div>
            </div>
            <div className="card">
              <div className="card-content pt-6">
                <div className="text-2xl font-bold text-green-600">{stats.completed_forms}</div>
                <p className="text-xs text-muted-foreground">Completed Forms</p>
              </div>
            </div>
            <div className="card">
              <div className="card-content pt-6">
                <div className="text-2xl font-bold text-indigo-600">{stats.final_forms}</div>
                <p className="text-xs text-muted-foreground">Final Forms</p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Forms */}
          <div className="lg:col-span-2">
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Recent Forms</h2>
                <p className="card-description">
                  Your most recently updated forms
                </p>
              </div>
              <div className="card-content">
                {recentForms.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-muted-foreground">No forms yet</p>
                    <p className="text-sm text-muted-foreground mt-2">
                      Create your first form using the quick actions
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {recentForms.map((form) => (
                      <div key={form.id} className="flex items-center justify-between p-4 border border-border rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <span className="font-medium">{form.form_type}</span>
                            <span className={`status-badge ${getStatusColor(form.status)}`}>
                              {formatStatus(form.status)}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mt-1">
                            {form.incident_name}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            Updated: {new Date(form.updated_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex space-x-2">
                          <button className="btn btn-outline btn-sm">
                            Edit
                          </button>
                          <button className="btn btn-ghost btn-sm">
                            View
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div>
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Quick Actions</h2>
                <p className="card-description">
                  Create new forms and manage data
                </p>
              </div>
              <div className="card-content space-y-4">
                <div>
                  <h3 className="font-medium mb-3">Create New Form</h3>
                  <div className="space-y-2">
                    {availableFormTypes.slice(0, 3).map((formType) => (
                      <button
                        key={formType}
                        onClick={() => createNewForm(formType)}
                        className="w-full btn btn-outline text-left justify-start"
                      >
                        {formType}
                      </button>
                    ))}
                  </div>
                  {availableFormTypes.length > 3 && (
                    <button className="w-full btn btn-ghost text-sm mt-2">
                      View All Form Types ({availableFormTypes.length} available)
                    </button>
                  )}
                </div>

                <div className="border-t border-border pt-4">
                  <h3 className="font-medium mb-3">Other Actions</h3>
                  <div className="space-y-2">
                    <button className="w-full btn btn-outline text-left justify-start">
                      Search Forms
                    </button>
                    <button className="w-full btn btn-outline text-left justify-start">
                      Export Data
                    </button>
                    <button className="w-full btn btn-outline text-left justify-start">
                      Settings
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Backend Info */}
            <div className="card mt-6">
              <div className="card-header">
                <h2 className="card-title text-base">System Info</h2>
              </div>
              <div className="card-content">
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Backend:</span>
                    <span>{backendInfo.type === 'mock' ? 'Mock (Dev)' : 'Tauri'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Version:</span>
                    <span>1.0.0</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Forms Available:</span>
                    <span>{availableFormTypes.length}</span>
                  </div>
                </div>
                
                {backendInfo.type === 'mock' && (
                  <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                    <p className="text-xs text-yellow-800">
                      <strong>Development Mode:</strong> Using mock backend with localStorage.
                      Data will be lost when clearing browser data.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
