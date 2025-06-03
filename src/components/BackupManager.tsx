/**
 * Simple Backup Manager Component
 * 
 * Following MANDATORY.md: Basic backup/restore for single-user app with simple UI.
 */

import { useState } from 'react';
import { formService } from '../services/formService';

export function BackupManager() {
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const clearMessages = () => {
    setError('');
    setSuccess('');
  };

  const handleCreateBackup = async () => {
    try {
      clearMessages();
      setLoading(true);

      // Simple file path input - user provides full path
      const backupPath = prompt('Enter backup file path (e.g., C:\\backup\\radioforms_backup.db):');
      if (!backupPath?.trim()) return;

      const result = await formService.createBackup(backupPath.trim());
      setSuccess(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create backup');
    } finally {
      setLoading(false);
    }
  };

  const handleRestoreBackup = async () => {
    try {
      clearMessages();
      setLoading(true);

      // Simple file path input - user provides full path
      const backupPath = prompt('Enter backup file path to restore from:');
      if (!backupPath?.trim()) return;

      // Confirm restore operation
      const confirmed = confirm(
        'WARNING: This will replace your current database with the backup. ' +
        'Your current data will be backed up first. Continue?'
      );
      if (!confirmed) return;

      const result = await formService.restoreBackup(backupPath.trim());
      setSuccess(result + '\n\nPlease restart the application to reload the restored data.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to restore backup');
    } finally {
      setLoading(false);
    }
  };

  const handleGetBackupInfo = async () => {
    try {
      clearMessages();
      setLoading(true);

      const backupPath = prompt('Enter backup file path to get information:');
      if (!backupPath?.trim()) return;

      const info = await formService.getBackupInfo(backupPath.trim());
      setSuccess(info);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get backup info');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="backup-manager">
      <h2 className="text-xl font-bold mb-4">Database Backup & Restore</h2>
      
      <div className="space-y-4">
        {/* Error/Success Messages */}
        {error && (
          <div 
            role="alert" 
            aria-live="polite"
            className="text-red-600 p-3 border border-red-300 rounded bg-red-50 whitespace-pre-line"
          >
            {error}
          </div>
        )}
        
        {success && (
          <div 
            role="alert" 
            aria-live="polite"
            className="text-green-600 p-3 border border-green-300 rounded bg-green-50 whitespace-pre-line"
          >
            {success}
          </div>
        )}

        {/* Backup Operations */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Backup Operations</h3>
            <p className="card-description">
              Create and manage database backups for data protection
            </p>
          </div>
          <div className="card-content space-y-4">
            <div className="flex space-x-4">
              <button
                onClick={handleCreateBackup}
                disabled={loading}
                className="btn btn-primary"
              >
                {loading ? 'Creating...' : 'Create Backup'}
              </button>
              
              <button
                onClick={handleGetBackupInfo}
                disabled={loading}
                className="btn btn-outline"
              >
                Get Backup Info
              </button>
            </div>
            
            <div className="text-sm text-muted-foreground">
              <p>• Backup includes all forms and metadata</p>
              <p>• Backup files have .db extension with optional .meta files</p>
              <p>• Store backups in a safe location (external drive, cloud storage)</p>
            </div>
          </div>
        </div>

        {/* Restore Operations */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Restore Operations</h3>
            <p className="card-description">
              Restore database from backup files
            </p>
          </div>
          <div className="card-content space-y-4">
            <div className="bg-yellow-50 border border-yellow-300 rounded p-3">
              <div className="text-yellow-800 text-sm">
                <strong>⚠️ Warning:</strong> Restoring will replace all current data. 
                Your current database will be backed up automatically before restore.
              </div>
            </div>
            
            <button
              onClick={handleRestoreBackup}
              disabled={loading}
              className="btn btn-destructive"
            >
              {loading ? 'Restoring...' : 'Restore from Backup'}
            </button>
            
            <div className="text-sm text-muted-foreground">
              <p>• Select a .db backup file to restore from</p>
              <p>• Current database is automatically backed up first</p>
              <p>• Application restart required after restore</p>
            </div>
          </div>
        </div>

        {/* Quick Backup Guide */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Backup Best Practices</h3>
          </div>
          <div className="card-content">
            <div className="text-sm text-muted-foreground space-y-2">
              <p>• <strong>Regular Backups:</strong> Create backups before important incidents</p>
              <p>• <strong>Multiple Locations:</strong> Store backups on external drives and cloud storage</p>
              <p>• <strong>Test Restores:</strong> Periodically test backup files to ensure they work</p>
              <p>• <strong>File Naming:</strong> Use descriptive names like "radioforms_2025-06-03.db"</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}