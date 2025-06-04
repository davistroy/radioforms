/**
 * Simple Backup Service Tests
 * 
 * Following MANDATORY.md: Basic tests for backup functionality.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { formService } from './formService';

// Mock Tauri invoke
vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(),
}));

import { invoke } from '@tauri-apps/api/core';
const mockInvoke = vi.mocked(invoke);

describe('Backup Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('createBackup', () => {
    it('calls create_backup command with correct parameters', async () => {
      const mockResult = 'Backup created successfully with 5 forms (checksum: 12345)';
      mockInvoke.mockResolvedValue(mockResult);

      const result = await formService.createBackup('/path/to/backup.db');
      
      expect(mockInvoke).toHaveBeenCalledWith('create_backup', {
        backupPath: '/path/to/backup.db'
      });
      expect(result).toBe(mockResult);
    });

    it('handles backup creation errors', async () => {
      const errorMessage = 'Failed to create backup';
      mockInvoke.mockRejectedValue(new Error(errorMessage));

      await expect(formService.createBackup('/invalid/path.db'))
        .rejects.toThrow(errorMessage);
    });
  });

  describe('restoreBackup', () => {
    it('calls restore_backup command with correct parameters', async () => {
      const mockResult = 'Database restored successfully from backup created on 2025-06-03 with 5 forms';
      mockInvoke.mockResolvedValue(mockResult);

      const result = await formService.restoreBackup('/path/to/backup.db');
      
      expect(mockInvoke).toHaveBeenCalledWith('restore_backup', {
        backupPath: '/path/to/backup.db'
      });
      expect(result).toBe(mockResult);
    });

    it('handles restore errors', async () => {
      const errorMessage = 'Backup file not found';
      mockInvoke.mockRejectedValue(new Error(errorMessage));

      await expect(formService.restoreBackup('/nonexistent.db'))
        .rejects.toThrow(errorMessage);
    });
  });

  describe('listBackups', () => {
    it('calls list_backups command and returns file list', async () => {
      const mockBackups = ['backup1.db (with metadata)', 'backup2.db'];
      mockInvoke.mockResolvedValue(mockBackups);

      const result = await formService.listBackups('/backup/directory');
      
      expect(mockInvoke).toHaveBeenCalledWith('list_backups', {
        directoryPath: '/backup/directory'
      });
      expect(result).toEqual(mockBackups);
    });

    it('handles directory read errors', async () => {
      const errorMessage = 'Directory not found';
      mockInvoke.mockRejectedValue(new Error(errorMessage));

      await expect(formService.listBackups('/invalid/directory'))
        .rejects.toThrow(errorMessage);
    });
  });

  describe('getBackupInfo', () => {
    it('calls get_backup_info command and returns metadata', async () => {
      const mockInfo = 'Created: 2025-06-03 12:00:00\nForms: 5\nVersion: 1.0.0\nChecksum: 12345';
      mockInvoke.mockResolvedValue(mockInfo);

      const result = await formService.getBackupInfo('/path/to/backup.db');
      
      expect(mockInvoke).toHaveBeenCalledWith('get_backup_info', {
        backupPath: '/path/to/backup.db'
      });
      expect(result).toBe(mockInfo);
    });

    it('handles backup info errors', async () => {
      const errorMessage = 'Backup file not found';
      mockInvoke.mockRejectedValue(new Error(errorMessage));

      await expect(formService.getBackupInfo('/nonexistent.db'))
        .rejects.toThrow(errorMessage);
    });
  });
});