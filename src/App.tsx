/**
 * RadioForms Simple Application Component
 * 
 * Following MANDATORY.md UI Rules: basic useState, simple error messages, direct Tauri commands.
 */

import { useState, useEffect } from "react";
import { formService, SimpleForm } from "./services/formService";
import { getAvailableFormTypes } from "./templates";
import { FormList } from "./components/FormList";
import { FormEditor } from "./components/FormEditor";
import { FormSearch } from "./components/FormSearch";
import { ThemeToggle } from "./components/ThemeToggle";
import { BackupManager } from "./components/BackupManager";
import type { ICSFormType } from "./types/forms";

function App() {
  const [currentView, setCurrentView] = useState<'dashboard' | 'list' | 'search' | 'create' | 'edit' | 'backup'>('dashboard');
  const [recentForms, setRecentForms] = useState<SimpleForm[]>([]);
  const [editingFormId, setEditingFormId] = useState<number | undefined>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRecentForms();
  }, []);

  const loadRecentForms = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get all forms and take first 5 for recent
      const allForms = await formService.getAllForms();
      const recent = allForms.slice(0, 5);
      setRecentForms(recent);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load forms');
      console.error('Failed to load recent forms:', err);
    } finally {
      setLoading(false);
    }
  };

  const createNewForm = async (formType: ICSFormType) => {
    try {
      const incidentName = prompt('Enter incident name:');
      if (!incidentName?.trim()) return;

      const formId = await formService.saveForm(
        incidentName.trim(),
        formType,
        '{}'
      );

      alert(`Form ${formType} created successfully (ID: ${formId})`);
      await loadRecentForms();
    } catch (err) {
      console.error('Failed to create form:', err);
      alert('Failed to create form: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const handleFormSaved = async () => {
    setCurrentView('dashboard');
    await loadRecentForms();
  };

  const handleFormEdit = (formId: number) => {
    setEditingFormId(formId);
    setCurrentView('edit');
  };

  const availableFormTypes = getAvailableFormTypes();

  if (loading && currentView === 'dashboard') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading RadioForms...</p>
        </div>
      </div>
    );
  }

  if (error && currentView === 'dashboard') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <h1 className="text-2xl font-bold text-destructive mb-4">Error</h1>
          <p className="text-muted-foreground mb-4">{error}</p>
          <button 
            onClick={loadRecentForms}
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
            
            <nav className="flex items-center space-x-4">
              <button
                onClick={() => setCurrentView('dashboard')}
                className={`text-sm ${currentView === 'dashboard' ? 'font-semibold' : ''}`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setCurrentView('list')}
                className={`text-sm ${currentView === 'list' ? 'font-semibold' : ''}`}
              >
                All Forms
              </button>
              <button
                onClick={() => setCurrentView('search')}
                className={`text-sm ${currentView === 'search' ? 'font-semibold' : ''}`}
              >
                Search
              </button>
              <button
                onClick={() => setCurrentView('create')}
                className={`text-sm ${currentView === 'create' ? 'font-semibold' : ''}`}
              >
                Create
              </button>
              <button
                onClick={() => setCurrentView('backup')}
                className={`text-sm ${currentView === 'backup' ? 'font-semibold' : ''}`}
              >
                Backup
              </button>
              
              <div className="border-l border-border pl-4">
                <ThemeToggle />
              </div>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container-app py-8">
        {currentView === 'dashboard' && (
          <div>
            <h2 className="text-xl font-bold mb-6">Dashboard</h2>
            
            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="card">
                <div className="card-content pt-6">
                  <div className="text-2xl font-bold">{recentForms.length}</div>
                  <p className="text-xs text-muted-foreground">Recent Forms</p>
                </div>
              </div>
              <div className="card">
                <div className="card-content pt-6">
                  <div className="text-2xl font-bold">{availableFormTypes.length}</div>
                  <p className="text-xs text-muted-foreground">Form Types Available</p>
                </div>
              </div>
            </div>

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
                                <span className="status-badge status-badge-draft">
                                  {form.status}
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
                              <button 
                                onClick={() => handleFormEdit(form.id)}
                                className="btn btn-outline btn-sm"
                              >
                                Edit
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
                        <button 
                          onClick={() => setCurrentView('create')}
                          className="w-full btn btn-ghost text-sm mt-2"
                        >
                          View All Form Types ({availableFormTypes.length} available)
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentView === 'list' && (
          <FormList />
        )}

        {currentView === 'search' && (
          <FormSearch onFormSelect={(form) => handleFormEdit(form.id)} />
        )}

        {currentView === 'create' && (
          <FormEditor 
            onSave={handleFormSaved}
            onCancel={() => setCurrentView('dashboard')}
          />
        )}

        {currentView === 'edit' && editingFormId && (
          <FormEditor 
            formId={editingFormId}
            onSave={handleFormSaved}
            onCancel={() => setCurrentView('dashboard')}
          />
        )}

        {currentView === 'backup' && (
          <BackupManager />
        )}
      </main>
    </div>
  );
}

export default App;