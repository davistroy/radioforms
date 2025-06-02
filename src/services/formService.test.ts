/**
 * Simple tests for formService
 * 
 * Following MANDATORY.md: simple tests for core functionality that emergency responders need.
 * Tests the basic form operations: save, load, search, update, delete.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { formService } from './formService';

// Mock Tauri's invoke function
const mockInvoke = vi.fn();
vi.mock('@tauri-apps/api/core', () => ({
  invoke: mockInvoke,
}));

describe('FormService', () => {
  beforeEach(() => {
    mockInvoke.mockClear();
  });

  describe('saveForm', () => {
    it('should save a form with incident name, form type, and data', async () => {
      // Arrange
      const mockFormId = 123;
      mockInvoke.mockResolvedValue(mockFormId);

      // Act
      const result = await formService.saveForm('Test Incident', 'ICS-201', '{"test": "data"}');

      // Assert
      expect(mockInvoke).toHaveBeenCalledWith('save_form', {
        incidentName: 'Test Incident',
        formType: 'ICS-201',
        formData: '{"test": "data"}'
      });
      expect(result).toBe(mockFormId);
    });

    it('should handle empty incident name', async () => {
      // Arrange
      mockInvoke.mockRejectedValue(new Error('Incident name is required'));

      // Act & Assert
      await expect(formService.saveForm('', 'ICS-201', '{}'))
        .rejects.toThrow('Incident name is required');
    });
  });

  describe('getForm', () => {
    it('should get a form by ID', async () => {
      // Arrange
      const mockForm = {
        id: 1,
        incident_name: 'Test Incident',
        form_type: 'ICS-201',
        status: 'draft',
        form_data: '{"test": "data"}',
        created_at: '2025-01-01T12:00:00Z',
        updated_at: '2025-01-01T12:00:00Z'
      };
      mockInvoke.mockResolvedValue(mockForm);

      // Act
      const result = await formService.getForm(1);

      // Assert
      expect(mockInvoke).toHaveBeenCalledWith('get_form', { id: 1 });
      expect(result).toEqual(mockForm);
    });

    it('should return null for non-existent form', async () => {
      // Arrange
      mockInvoke.mockResolvedValue(null);

      // Act
      const result = await formService.getForm(999);

      // Assert
      expect(result).toBeNull();
    });
  });

  describe('searchForms', () => {
    it('should search forms by incident name', async () => {
      // Arrange
      const mockForms = [
        {
          id: 1,
          incident_name: 'Fire Incident',
          form_type: 'ICS-201',
          status: 'draft',
          form_data: '{}',
          created_at: '2025-01-01T12:00:00Z',
          updated_at: '2025-01-01T12:00:00Z'
        }
      ];
      mockInvoke.mockResolvedValue(mockForms);

      // Act
      const result = await formService.searchForms('Fire');

      // Assert
      expect(mockInvoke).toHaveBeenCalledWith('search_forms', { incidentName: 'Fire' });
      expect(result).toEqual(mockForms);
    });

    it('should handle undefined search term', async () => {
      // Arrange
      mockInvoke.mockResolvedValue([]);

      // Act
      const result = await formService.searchForms(undefined);

      // Assert
      expect(mockInvoke).toHaveBeenCalledWith('search_forms', { incidentName: undefined });
      expect(result).toEqual([]);
    });
  });

  describe('updateForm', () => {
    it('should update form data', async () => {
      // Arrange
      mockInvoke.mockResolvedValue(undefined);

      // Act
      await formService.updateForm(1, '{"updated": "data"}');

      // Assert
      expect(mockInvoke).toHaveBeenCalledWith('update_form', {
        id: 1,
        formData: '{"updated": "data"}'
      });
    });
  });

  describe('getAllForms', () => {
    it('should get all forms', async () => {
      // Arrange
      const mockForms = [
        {
          id: 1,
          incident_name: 'Test Incident 1',
          form_type: 'ICS-201',
          status: 'draft',
          form_data: '{}',
          created_at: '2025-01-01T12:00:00Z',
          updated_at: '2025-01-01T12:00:00Z'
        },
        {
          id: 2,
          incident_name: 'Test Incident 2',
          form_type: 'ICS-202',
          status: 'completed',
          form_data: '{}',
          created_at: '2025-01-01T13:00:00Z',
          updated_at: '2025-01-01T13:00:00Z'
        }
      ];
      mockInvoke.mockResolvedValue(mockForms);

      // Act
      const result = await formService.getAllForms();

      // Assert
      expect(mockInvoke).toHaveBeenCalledWith('list_all_forms');
      expect(result).toEqual(mockForms);
    });
  });

  describe('deleteForm', () => {
    it('should delete a form', async () => {
      // Arrange
      mockInvoke.mockResolvedValue(true);

      // Act
      const result = await formService.deleteForm(1);

      // Assert
      expect(mockInvoke).toHaveBeenCalledWith('delete_form', { id: 1 });
      expect(result).toBe(true);
    });

    it('should return false if form not found', async () => {
      // Arrange
      mockInvoke.mockResolvedValue(false);

      // Act
      const result = await formService.deleteForm(999);

      // Assert
      expect(result).toBe(false);
    });
  });
});