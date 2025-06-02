/**
 * Simple Form Editor Component
 * 
 * Following MANDATORY.md UI Rules: React Hook Form, basic useState, simple error messages.
 */

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { formService } from '../services/formService';

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

export function FormEditor({ formId, onSave, onCancel }: FormEditorProps) {
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(!!formId);

  const { register, handleSubmit, setValue, formState: { errors } } = useForm<FormData>({
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

  if (initialLoading) {
    return <div className="text-center py-4">Loading form...</div>;
  }

  return (
    <div className="form-editor">
      <h2 className="text-xl font-bold mb-4">
        {formId ? 'Edit Form' : 'Create New Form'}
      </h2>

      {error && (
        <div 
          role="alert" 
          aria-live="polite"
          className="text-red-600 mb-4 p-3 border border-red-300 rounded bg-red-50"
        >
          Error: {error}
        </div>
      )}

      <form 
        onSubmit={handleSubmit(onSubmit)} 
        className="space-y-4"
        noValidate
        aria-label={formId ? 'Edit form' : 'Create new form'}
      >
        <div>
          <label htmlFor="incident_name" className="block text-sm font-medium mb-1">
            Incident Name *
          </label>
          <input
            id="incident_name"
            {...register('incident_name', { 
              required: 'Incident name is required',
              maxLength: {
                value: 100,
                message: 'Incident name must be 100 characters or less'
              }
            })}
            className="w-full p-2 border border-gray-300 rounded"
            placeholder="Enter incident name"
            aria-required="true"
            aria-invalid={errors.incident_name ? 'true' : 'false'}
            aria-describedby={errors.incident_name ? 'incident_name_error' : undefined}
          />
          {errors.incident_name && (
            <p 
              id="incident_name_error" 
              className="text-red-600 text-sm mt-1"
              aria-live="polite"
            >
              {errors.incident_name.message}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="form_type" className="block text-sm font-medium mb-1">
            Form Type
          </label>
          <select
            id="form_type"
            {...register('form_type')}
            className="w-full p-2 border border-gray-300 rounded"
            aria-required="true"
            aria-label="Select ICS form type"
          >
            <option value="ICS-201">ICS-201 - Incident Briefing</option>
            <option value="ICS-202">ICS-202 - Incident Objectives</option>
            <option value="ICS-203">ICS-203 - Organization Assignment List</option>
            <option value="ICS-204">ICS-204 - Assignment List</option>
            <option value="ICS-205">ICS-205 - Incident Radio Communications Plan</option>
          </select>
        </div>

        <div>
          <label htmlFor="form_data" className="block text-sm font-medium mb-1">
            Form Data (JSON)
          </label>
          <textarea
            id="form_data"
            {...register('form_data', {
              validate: (value) => {
                try {
                  JSON.parse(value);
                  return true;
                } catch {
                  return 'Form data must be valid JSON format';
                }
              }
            })}
            rows={6}
            className="w-full p-2 border border-gray-300 rounded font-mono text-sm"
            placeholder='{"field": "value"}'
            aria-required="true"
            aria-invalid={errors.form_data ? 'true' : 'false'}
            aria-describedby={errors.form_data ? 'form_data_error' : 'form_data_help'}
          />
          {errors.form_data && (
            <p className="text-red-600 text-sm mt-1">{errors.form_data.message}</p>
          )}
        </div>

        <div className="flex space-x-3">
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Saving...' : (formId ? 'Update Form' : 'Create Form')}
          </button>
          
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