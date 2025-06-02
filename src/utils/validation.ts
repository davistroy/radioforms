/**
 * Form Validation Helpers
 * 
 * Following MANDATORY.md: Simple validation functions for emergency responders.
 * Clear error messages that can be understood at 2 AM under stress.
 */

// Simple validation helpers for common patterns
export const ValidationHelpers = {
  // Check if field is empty
  required: (value: string, fieldName: string): string | undefined => {
    if (!value || value.trim() === '') {
      return `${fieldName} is required`;
    }
    return undefined;
  },

  // Check max length
  maxLength: (value: string, max: number, fieldName: string): string | undefined => {
    if (value && value.length > max) {
      return `${fieldName} must be ${max} characters or less`;
    }
    return undefined;
  },

  // Check if valid ICS form type
  validFormType: (value: string): string | undefined => {
    const validTypes = [
      'ICS-201', 'ICS-202', 'ICS-203', 'ICS-204', 'ICS-205', 'ICS-205A',
      'ICS-206', 'ICS-207', 'ICS-208', 'ICS-209', 'ICS-210', 'ICS-211',
      'ICS-213', 'ICS-214', 'ICS-215', 'ICS-215A', 'ICS-218', 'ICS-220',
      'ICS-221', 'ICS-225'
    ];
    if (!validTypes.includes(value)) {
      return 'Please select a valid ICS form type';
    }
    return undefined;
  },

  // Check if valid JSON
  validJSON: (value: string): string | undefined => {
    try {
      JSON.parse(value);
      return undefined;
    } catch {
      return 'Form data must be valid JSON format';
    }
  }
};