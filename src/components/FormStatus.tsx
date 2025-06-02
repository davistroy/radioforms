/**
 * Form Status Component - Simple Lifecycle Management
 * 
 * Following MANDATORY.md: Simple React component for emergency responders.
 * Shows current status and available transitions with clear visual indicators.
 */

import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';

interface FormStatusProps {
  formId: number;
  currentStatus: string;
  onStatusChanged?: (newStatus: string) => void;
}

interface StatusInfo {
  status: string;
  color: string;
  description: string;
  icon: string;
}

// Simple status mapping for emergency responders
const STATUS_INFO: Record<string, StatusInfo> = {
  draft: {
    status: 'Draft',
    color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    description: 'Being edited - changes automatically saved',
    icon: '✏️'
  },
  completed: {
    status: 'Completed',
    color: 'bg-blue-100 text-blue-800 border-blue-200',
    description: 'Ready for review - can still be edited',
    icon: '✅'
  },
  final: {
    status: 'Final',
    color: 'bg-green-100 text-green-800 border-green-200',
    description: 'Submitted - no more changes allowed',
    icon: '🔒'
  },
  archived: {
    status: 'Archived',
    color: 'bg-gray-100 text-gray-800 border-gray-200',
    description: 'Archived - for historical reference only',
    icon: '📁'
  }
};

export function FormStatus({ formId, currentStatus, onStatusChanged }: FormStatusProps) {
  const [availableTransitions, setAvailableTransitions] = useState<string[]>([]);
  const [canEdit, setCanEdit] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const statusInfo = STATUS_INFO[currentStatus] || STATUS_INFO.draft;

  // Load available transitions when component mounts or status changes
  useEffect(() => {
    loadAvailableTransitions();
    checkCanEdit();
  }, [formId, currentStatus]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadAvailableTransitions = async () => {
    try {
      const transitions = await invoke<string[]>('get_available_transitions', { id: formId });
      setAvailableTransitions(transitions);
    } catch (err) {
      console.error('Failed to load available transitions:', err);
      setError(err instanceof Error ? err.message : 'Failed to load transitions');
    }
  };

  const checkCanEdit = async () => {
    try {
      const editable = await invoke<boolean>('can_edit_form', { id: formId });
      setCanEdit(editable);
    } catch (err) {
      console.error('Failed to check edit status:', err);
    }
  };

  const handleStatusTransition = async (newStatus: string) => {
    if (loading) return;

    try {
      setLoading(true);
      setError('');
      
      await invoke('update_form_status', {
        id: formId,
        newStatus: newStatus
      });

      // Notify parent component
      if (onStatusChanged) {
        onStatusChanged(newStatus);
      }

      // Reload available transitions
      await loadAvailableTransitions();
      await checkCanEdit();
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update status');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-status bg-white border border-gray-200 rounded-lg p-4 mb-4">
      <h3 className="text-lg font-semibold mb-3">Form Status</h3>
      
      {/* Current Status Display */}
      <div className={`inline-flex items-center px-3 py-1 rounded-full border ${statusInfo.color} mb-3`}>
        <span className="mr-2">{statusInfo.icon}</span>
        <span className="font-medium">{statusInfo.status}</span>
      </div>
      
      <p className="text-sm text-gray-600 mb-4">{statusInfo.description}</p>

      {/* Edit Status Indicator */}
      <div className="mb-4">
        <span className="text-sm font-medium">
          Can Edit: {canEdit ? (
            <span className="text-green-600">✅ Yes</span>
          ) : (
            <span className="text-red-600">❌ No</span>
          )}
        </span>
      </div>

      {/* Error Display */}
      {error && (
        <div className="text-red-600 text-sm mb-4 p-2 border border-red-300 rounded bg-red-50">
          Error: {error}
        </div>
      )}

      {/* Available Transitions */}
      {availableTransitions.length > 0 && (
        <div>
          <h4 className="text-sm font-medium mb-2">Available Actions:</h4>
          <div className="flex flex-wrap gap-2">
            {availableTransitions.map((status) => {
              const targetInfo = STATUS_INFO[status];
              if (!targetInfo) return null;

              return (
                <button
                  key={status}
                  onClick={() => handleStatusTransition(status)}
                  disabled={loading}
                  className="inline-flex items-center px-3 py-1 text-sm bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  title={`Change to ${targetInfo.status}: ${targetInfo.description}`}
                >
                  <span className="mr-1">{targetInfo.icon}</span>
                  <span>Mark as {targetInfo.status}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {availableTransitions.length === 0 && currentStatus !== 'archived' && (
        <p className="text-sm text-gray-500">No status changes available</p>
      )}

      {loading && (
        <div className="mt-2 text-sm text-blue-600">Updating status...</div>
      )}
    </div>
  );
}