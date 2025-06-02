/**
 * Form Validation UI Component
 * 
 * Following MANDATORY.md: Simple validation display for emergency responders.
 * Clear error messages that can be understood at 2 AM under stress.
 */

import React from 'react';

interface ValidationError {
  field: string;
  message: string;
}

interface FormValidationProps {
  errors: ValidationError[];
  onNavigateToError?: (field: string) => void;
}

// Simple error summary component - shows all errors at top of form
export function ErrorSummary({ errors, onNavigateToError }: FormValidationProps) {
  if (errors.length === 0) return null;

  return (
    <div 
      role="alert"
      aria-live="polite"
      className="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-6"
    >
      <div className="flex items-start">
        <span className="text-red-600 text-2xl mr-3" aria-hidden="true">⚠️</span>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-red-800 mb-2">
            {errors.length === 1 ? '1 Error Found' : `${errors.length} Errors Found`}
          </h3>
          <p className="text-sm text-red-700 mb-3">
            Please fix the following errors before continuing:
          </p>
          <ul className="space-y-2">
            {errors.map((error, index) => (
              <li key={`${error.field}-${index}`} className="flex items-start">
                <span className="text-red-600 mr-2">•</span>
                {onNavigateToError ? (
                  <button
                    type="button"
                    onClick={() => onNavigateToError(error.field)}
                    className="text-left text-red-700 hover:text-red-900 underline focus:outline-none focus:ring-2 focus:ring-red-500 rounded"
                  >
                    {error.message}
                  </button>
                ) : (
                  <span className="text-red-700">{error.message}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

// Simple field error display - shows error below field
interface FieldErrorProps {
  error?: string;
  fieldId: string;
}

export function FieldError({ error, fieldId }: FieldErrorProps) {
  if (!error) return null;

  return (
    <div 
      id={`${fieldId}-error`}
      role="alert"
      className="mt-1 text-sm text-red-600 flex items-center"
    >
      <span className="mr-1" aria-hidden="true">❌</span>
      <span>{error}</span>
    </div>
  );
}

// Simple field wrapper with error styling
interface ValidatedFieldProps {
  children: React.ReactNode;
  error?: string;
  label: string;
  required?: boolean;
  fieldId: string;
}

export function ValidatedField({ 
  children, 
  error, 
  label, 
  required, 
  fieldId 
}: ValidatedFieldProps) {
  return (
    <div className="mb-4">
      <label 
        htmlFor={fieldId}
        className="block text-sm font-medium text-gray-700 mb-1"
      >
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      <div className={error ? 'ring-2 ring-red-500 rounded' : ''}>
        {React.cloneElement(children as React.ReactElement, {
          id: fieldId,
          'aria-invalid': error ? 'true' : 'false',
          'aria-describedby': error ? `${fieldId}-error` : undefined,
          className: `${(children as React.ReactElement).props.className || ''} ${
            error ? 'border-red-500' : ''
          }`,
        })}
      </div>
      <FieldError error={error} fieldId={fieldId} />
    </div>
  );
}

