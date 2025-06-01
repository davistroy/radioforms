/**
 * Form Service for Tauri Backend
 * 
 * This service provides a unified interface for form operations using
 * the Tauri Rust backend. All operations are performed through Tauri
 * commands that communicate with the SQLite database.
 * 
 * Business Logic:
 * - All operations use real Tauri commands
 * - Proper error handling and logging
 * - Type-safe interfaces with backend
 * - Comprehensive form lifecycle management
 */

import type {
  Form,
  CreateFormRequest,
  UpdateFormRequest,
  FormFilters,
  FormSearchResult,
  FormTypeInfo,
  DatabaseStats
} from '../types/forms';

/**
 * Form service that uses the Tauri Rust backend
 */
class FormService {
  /**
   * Creates a new form with the specified data.
   */
  async createForm(request: CreateFormRequest): Promise<Form> {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke('create_form', {
      formType: request.form_type,
      incidentName: request.incident_name,
      incidentNumber: request.incident_number,
      preparerName: request.preparer_name,
      initialData: request.initial_data
    });
  }

  /**
   * Retrieves a form by its ID.
   */
  async getForm(id: number): Promise<Form | undefined> {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke('get_form', { id });
  }

  /**
   * Updates an existing form with new data.
   */
  async updateForm(id: number, request: UpdateFormRequest): Promise<Form> {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke('update_form', {
      id,
      updates: request
    });
  }

  /**
   * Deletes a form by ID.
   */
  async deleteForm(id: number, force: boolean = false): Promise<boolean> {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke('delete_form', { id, force });
  }

  /**
   * Searches forms based on the provided filters.
   */
  async searchForms(filters: FormFilters): Promise<FormSearchResult> {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke('search_forms', { filters });
  }

  /**
   * Gets all forms for a specific incident.
   */
  async getFormsByIncident(incidentName: string): Promise<Form[]> {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke('get_forms_by_incident', { incidentName });
  }

  /**
   * Gets recent forms (most recently updated).
   */
  async getRecentForms(limit: number = 10): Promise<Form[]> {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke('get_recent_forms', { limit });
  }

  /**
   * Duplicates an existing form as a new draft.
   */
  async duplicateForm(sourceId: number, newIncidentName?: string): Promise<Form> {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke('duplicate_form', {
      sourceId,
      newIncidentName
    });
  }

  /**
   * Gets list of all supported ICS form types.
   */
  async getFormTypes(): Promise<FormTypeInfo[]> {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke('get_form_types');
  }

  /**
   * Gets database statistics for monitoring.
   */
  async getDatabaseStats(): Promise<DatabaseStats> {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke('get_database_stats');
  }

  /**
   * Gets information about the current backend
   */
  getBackendInfo(): { type: 'tauri'; description: string } {
    return {
      type: 'tauri',
      description: 'Using Tauri Rust backend with SQLite database'
    };
  }

  /**
   * Always returns false since we no longer use mock backend
   */
  isUsingMockBackend(): boolean {
    return false;
  }
}

// Export singleton instance
export const formService = new FormService();