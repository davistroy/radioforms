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
  },

  async advancedSearch(
    incidentName?: string,
    formType?: string,
    status?: string,
    dateFrom?: string,
    dateTo?: string
  ): Promise<SimpleForm[]> {
    return await invoke('advanced_search', {
      incidentName,
      formType,
      status,
      dateFrom,
      dateTo
    });
  },

  async exportFormsJSON(): Promise<string> {
    return await invoke('export_forms_json');
  },

  async exportFormJSON(id: number): Promise<string> {
    return await invoke('export_form_json', { formId: id });
  },

  async importFormsJSON(jsonData: string): Promise<string> {
    return await invoke('import_forms_json', { jsonData });
  },

  async exportFormICSdes(id: number): Promise<string> {
    return await invoke('export_form_icsdes', { formId: id });
  },

  async createBackup(backupPath: string): Promise<string> {
    return await invoke('create_backup', { backupPath });
  },

  async restoreBackup(backupPath: string): Promise<string> {
    return await invoke('restore_backup', { backupPath });
  },

  async listBackups(directoryPath: string): Promise<string[]> {
    return await invoke('list_backups', { directoryPath });
  },

  async getBackupInfo(backupPath: string): Promise<string> {
    return await invoke('get_backup_info', { backupPath });
  }
};