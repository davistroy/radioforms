/**
 * Simple Form Service for RadioForms
 * 
 * Following MANDATORY.md UI Rules: direct Tauri command calls, simple interfaces.
 * No complex state management, classes, or abstractions.
 */

import { invoke } from '@tauri-apps/api/core';

export interface SimpleForm {
  id: number;
  incident_name: string;
  form_type: string;
  status: string;
  form_data: string;
  created_at: string;
  updated_at: string;
}

// Simple functions that directly call Tauri commands
export const formService = {
  async saveForm(incidentName: string, formType: string, formData: string): Promise<number> {
    return await invoke('save_form', { incidentName, formType, formData });
  },

  async getForm(id: number): Promise<SimpleForm | null> {
    return await invoke('get_form', { id });
  },

  async updateForm(id: number, formData: string): Promise<void> {
    return await invoke('update_form', { id, formData });
  },

  async searchForms(incidentName?: string): Promise<SimpleForm[]> {
    return await invoke('search_forms', { incidentName });
  },

  async getAllForms(): Promise<SimpleForm[]> {
    return await invoke('get_all_forms');
  },

  async deleteForm(id: number): Promise<boolean> {
    return await invoke('delete_form', { id });
  }
};