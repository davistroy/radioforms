/**
 * Form Service Abstraction Layer
 * 
 * This service provides a unified interface for form operations that
 * works with both the mock service (development) and real Tauri commands
 * (production). It automatically detects the environment and uses the
 * appropriate backend.
 * 
 * Business Logic:
 * - Provides consistent API regardless of backend
 * - Automatically switches between mock and Tauri based on environment
 * - Handles error translation and logging
 * - Maintains exact same interface as backend
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

import { mockFormService } from './mockFormService';

/**
 * Checks if we're running in Tauri environment
 */
function isTauriEnvironment(): boolean {
  return typeof window !== 'undefined' && '__TAURI__' in window;
}

/**
 * Unified form service that works with both mock and Tauri backends
 */
class FormService {
  /**
   * Creates a new form with the specified data.
   */
  async createForm(request: CreateFormRequest): Promise<Form> {
    if (isTauriEnvironment()) {
      // Use Tauri commands
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke('create_form', {
        formType: request.form_type,
        incidentName: request.incident_name,
        incidentNumber: request.incident_number,
        preparerName: request.preparer_name,
        initialData: request.initial_data
      });
    } else {
      // Use mock service
      return await mockFormService.createForm(request);
    }
  }

  /**
   * Retrieves a form by its ID.
   */
  async getForm(id: number): Promise<Form | undefined> {
    if (isTauriEnvironment()) {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke('get_form', { id });
    } else {
      return await mockFormService.getForm(id);
    }
  }

  /**
   * Updates an existing form with new data.
   */
  async updateForm(id: number, request: UpdateFormRequest): Promise<Form> {
    if (isTauriEnvironment()) {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke('update_form', {
        id,
        updates: request
      });
    } else {
      return await mockFormService.updateForm(id, request);
    }
  }

  /**
   * Deletes a form by ID.
   */
  async deleteForm(id: number, force: boolean = false): Promise<boolean> {
    if (isTauriEnvironment()) {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke('delete_form', { id, force });
    } else {
      return await mockFormService.deleteForm(id, force);
    }
  }

  /**
   * Searches forms based on the provided filters.
   */
  async searchForms(filters: FormFilters): Promise<FormSearchResult> {
    if (isTauriEnvironment()) {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke('search_forms', { filters });
    } else {
      return await mockFormService.searchForms(filters);
    }
  }

  /**
   * Gets all forms for a specific incident.
   */
  async getFormsByIncident(incidentName: string): Promise<Form[]> {
    if (isTauriEnvironment()) {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke('get_forms_by_incident', { incidentName });
    } else {
      return await mockFormService.getFormsByIncident(incidentName);
    }
  }

  /**
   * Gets recent forms (most recently updated).
   */
  async getRecentForms(limit: number = 10): Promise<Form[]> {
    if (isTauriEnvironment()) {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke('get_recent_forms', { limit });
    } else {
      return await mockFormService.getRecentForms(limit);
    }
  }

  /**
   * Duplicates an existing form as a new draft.
   */
  async duplicateForm(sourceId: number, newIncidentName?: string): Promise<Form> {
    if (isTauriEnvironment()) {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke('duplicate_form', {
        sourceId,
        newIncidentName
      });
    } else {
      return await mockFormService.duplicateForm(sourceId, newIncidentName);
    }
  }

  /**
   * Gets list of all supported ICS form types.
   */
  async getFormTypes(): Promise<FormTypeInfo[]> {
    if (isTauriEnvironment()) {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke('get_form_types');
    } else {
      return await mockFormService.getFormTypes();
    }
  }

  /**
   * Gets database statistics for monitoring.
   */
  async getDatabaseStats(): Promise<DatabaseStats> {
    if (isTauriEnvironment()) {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke('get_database_stats');
    } else {
      return await mockFormService.getDatabaseStats();
    }
  }

  /**
   * Checks if we're currently using the mock backend
   */
  isUsingMockBackend(): boolean {
    return !isTauriEnvironment();
  }

  /**
   * Gets information about the current backend
   */
  getBackendInfo(): { type: 'mock' | 'tauri'; description: string } {
    if (isTauriEnvironment()) {
      return {
        type: 'tauri',
        description: 'Using Tauri Rust backend with SQLite database'
      };
    } else {
      return {
        type: 'mock',
        description: 'Using mock backend with localStorage (development mode)'
      };
    }
  }

  /**
   * Clears all data (development only - mock backend)
   */
  async clearAllData(): Promise<void> {
    if (isTauriEnvironment()) {
      throw new Error('clearAllData is not available in production Tauri environment');
    } else {
      return await mockFormService.clearAllData();
    }
  }

  /**
   * Initializes sample data (development only - mock backend)
   */
  async initializeSampleData(): Promise<void> {
    if (isTauriEnvironment()) {
      console.log('Sample data initialization not needed in Tauri environment');
    } else {
      return await mockFormService.initializeSampleData();
    }
  }
}

// Export singleton instance
export const formService = new FormService();