/**
 * Simple Form Editor Component
 * 
 * Following MANDATORY.md UI Rules: React Hook Form, basic useState, simple error messages.
 */

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { formService } from '../services/formService';
import { exportFormToPDF } from '../services/pdfService';
import { FormStatus } from './FormStatus';
import { ErrorSummary, ValidatedField } from './FormValidation';
import { ValidationHelpers } from '../utils/validation';

interface FormEditorProps {
  formId?: number;
  onSave?: (id: number) => void;
  onCancel?: () => void;
}

interface FormData {
  incident_name: string;
  form_type: string;
  form_data: string;
}

interface FormInfo {
  id: number;
  incident_name: string;
  form_type: string;
  status: string;
  form_data: string;
  created_at: string;
  updated_at: string;
}

export function FormEditor({ formId, onSave, onCancel }: FormEditorProps) {
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(!!formId);
  const [currentForm, setCurrentForm] = useState<FormInfo | null>(null);

  const { register, handleSubmit, setValue, formState: { errors }, setFocus } = useForm<FormData>({
    defaultValues: {
      incident_name: '',
      form_type: 'ICS-201',
      form_data: '{}'
    }
  });

  // Load existing form if editing
  useEffect(() => {
    if (formId) {
      loadForm();
    }
  }, [formId]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadForm = async () => {
    if (!formId) return;
    
    try {
      setInitialLoading(true);
      const form = await formService.getForm(formId);
      if (form) {
        setCurrentForm(form);
        setValue('incident_name', form.incident_name);
        setValue('form_type', form.form_type);
        setValue('form_data', form.form_data);
      } else {
        setError('Form not found');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load form');
    } finally {
      setInitialLoading(false);
    }
  };

  const onSubmit = async (data: FormData) => {
    try {
      setError('');
      setLoading(true);

      let savedId: number;
      if (formId) {
        await formService.updateForm(formId, data.form_data);
        savedId = formId;
      } else {
        savedId = await formService.saveForm(data.incident_name, data.form_type, data.form_data);
      }

      onSave?.(savedId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save form');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChanged = (newStatus: string) => {
    if (currentForm) {
      setCurrentForm({
        ...currentForm,
        status: newStatus
      });
    }
  };

  const handleExportPDF = async () => {
    if (!formId) {
      setError('Cannot export unsaved form. Please save first.');
      return;
    }

    try {
      setError('');
      const form = await formService.getForm(formId);
      if (form) {
        await exportFormToPDF(form);
      } else {
        setError('Form not found');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export PDF');
    }
  };

  if (initialLoading) {
    return <div className="text-center py-4">Loading form...</div>;
  }

  return (
    <div className="form-editor">
      <h2 className="text-xl font-bold mb-4">
        {formId ? 'Edit Form' : 'Create New Form'}
      </h2>

      {/* Form validation error summary */}
      <ErrorSummary 
        errors={Object.entries(errors).map(([field, error]) => ({
          field,
          message: error?.message || 'Invalid value'
        }))}
        onNavigateToError={(field) => setFocus(field as keyof FormData)}
      />

      {/* General API errors */}
      {error && (
        <div 
          role="alert" 
          aria-live="polite"
          className="text-red-600 mb-4 p-3 border border-red-300 rounded bg-red-50"
        >
          Error: {error}
        </div>
      )}

      {/* Form Status Component for existing forms */}
      {currentForm && (
        <FormStatus
          formId={currentForm.id}
          currentStatus={currentForm.status}
          onStatusChanged={handleStatusChanged}
        />
      )}

      <form 
        onSubmit={handleSubmit(onSubmit)} 
        className="space-y-4"
        noValidate
        aria-label={formId ? 'Edit form' : 'Create new form'}
      >
        <ValidatedField
          label="Incident Name"
          required
          fieldId="incident_name"
          error={errors.incident_name?.message}
        >
          <input
            {...register('incident_name', { 
              required: 'Incident name is required',
              maxLength: {
                value: 100,
                message: 'Incident name must be 100 characters or less'
              }
            })}
            className="w-full p-2 border border-gray-300 rounded"
            placeholder="Enter incident name"
          />
        </ValidatedField>

        <ValidatedField
          label="Form Type"
          required
          fieldId="form_type"
          error={errors.form_type?.message}
        >
          <select
            {...register('form_type', {
              validate: ValidationHelpers.validFormType
            })}
            className="w-full p-2 border border-gray-300 rounded"
            aria-label="Select ICS form type"
          >
            <option value="ICS-201">ICS-201 - Incident Briefing</option>
            <option value="ICS-202">ICS-202 - Incident Objectives</option>
            <option value="ICS-203">ICS-203 - Organization Assignment List</option>
            <option value="ICS-204">ICS-204 - Assignment List</option>
            <option value="ICS-205">ICS-205 - Incident Radio Communications Plan</option>
            <option value="ICS-213">ICS-213 - General Message</option>
            <option value="ICS-214">ICS-214 - Unit Log</option>
            <option value="ICS-215">ICS-215 - Operational Planning Worksheet</option>
          </select>
        </ValidatedField>

        <ValidatedField
          label="Form Data (JSON)"
          required
          fieldId="form_data"
          error={errors.form_data?.message}
        >
          <textarea
            {...register('form_data', {
              validate: ValidationHelpers.validJSON
            })}
            rows={6}
            className="w-full p-2 border border-gray-300 rounded font-mono text-sm"
            placeholder='{"field": "value"}'
          />
        </ValidatedField>

        <div className="flex space-x-3">
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Saving...' : (formId ? 'Update Form' : 'Create Form')}
          </button>
          
          {formId && (
            <button
              type="button"
              onClick={handleExportPDF}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Export PDF
            </button>
          )}
          
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
}