/**
 * Form Template Registry
 * 
 * This module exports all available ICS form templates and provides
 * utilities for working with form templates.
 * 
 * Business Logic:
 * - Centralized registry of all form templates
 * - Type-safe template access
 * - Template validation utilities
 * - Support for dynamic form rendering
 */

import type { FormTemplate, ICSFormType } from '../types/forms';
import { ics201Template } from './ics-201';

/**
 * Registry of all available form templates
 */
export const formTemplates: Record<ICSFormType, FormTemplate> = {
  'ICS-201': ics201Template,
  
  // TODO: Implement remaining form templates in subsequent phases
  'ICS-202': null as any, // Placeholder
  'ICS-203': null as any, // Placeholder
  'ICS-204': null as any, // Placeholder
  'ICS-205': null as any, // Placeholder
  'ICS-205A': null as any, // Placeholder
  'ICS-206': null as any, // Placeholder
  'ICS-207': null as any, // Placeholder
  'ICS-208': null as any, // Placeholder
  'ICS-209': null as any, // Placeholder
  'ICS-210': null as any, // Placeholder
  'ICS-211': null as any, // Placeholder
  'ICS-213': null as any, // Placeholder
  'ICS-214': null as any, // Placeholder
  'ICS-215': null as any, // Placeholder
  'ICS-215A': null as any, // Placeholder
  'ICS-218': null as any, // Placeholder
  'ICS-220': null as any, // Placeholder
  'ICS-221': null as any, // Placeholder
  'ICS-225': null as any, // Placeholder
};

/**
 * Gets a form template by type
 * 
 * @param formType - The ICS form type
 * @returns The form template or undefined if not available
 */
export function getFormTemplate(formType: ICSFormType): FormTemplate | undefined {
  return formTemplates[formType] || undefined;
}

/**
 * Gets all available form templates
 * 
 * @returns Array of all implemented form templates
 */
export function getAllAvailableTemplates(): FormTemplate[] {
  return Object.values(formTemplates).filter(template => template !== null);
}

/**
 * Checks if a form template is available
 * 
 * @param formType - The ICS form type to check
 * @returns True if template is available, false otherwise
 */
export function isTemplateAvailable(formType: ICSFormType): boolean {
  return formTemplates[formType] !== null && formTemplates[formType] !== undefined;
}

/**
 * Gets the list of form types that have templates available
 * 
 * @returns Array of available form types
 */
export function getAvailableFormTypes(): ICSFormType[] {
  return Object.entries(formTemplates)
    .filter(([_, template]) => template !== null)
    .map(([formType, _]) => formType as ICSFormType);
}

/**
 * Validates that a form template is properly structured
 * 
 * @param template - The template to validate
 * @returns Validation result with any errors found
 */
export function validateTemplate(template: FormTemplate): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  // Check required properties
  if (!template.form_type) {
    errors.push('Template must have a form_type');
  }
  
  if (!template.name) {
    errors.push('Template must have a name');
  }
  
  if (!template.sections || template.sections.length === 0) {
    errors.push('Template must have at least one section');
  }

  // Validate sections
  template.sections?.forEach((section, index) => {
    if (!section.id) {
      errors.push(`Section ${index} must have an id`);
    }
    
    if (!section.title) {
      errors.push(`Section ${index} must have a title`);
    }
    
    if (!section.fields || section.fields.length === 0) {
      errors.push(`Section ${index} must have at least one field`);
    }

    // Validate fields
    section.fields?.forEach((field, fieldIndex) => {
      if (!field.id) {
        errors.push(`Section ${index}, Field ${fieldIndex} must have an id`);
      }
      
      if (!field.label) {
        errors.push(`Section ${index}, Field ${fieldIndex} must have a label`);
      }
      
      if (!field.type) {
        errors.push(`Section ${index}, Field ${fieldIndex} must have a type`);
      }
    });
  });

  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Creates default form data from a template
 * 
 * @param template - The form template
 * @returns Object with default values for all fields
 */
export function createDefaultFormData(template: FormTemplate): Record<string, any> {
  const defaultData: Record<string, any> = {};

  template.sections.forEach(section => {
    section.fields.forEach(field => {
      // Set default values based on field type
      switch (field.type) {
        case 'checkbox':
          defaultData[field.id] = false;
          break;
        case 'number':
          defaultData[field.id] = field.validation?.min || 0;
          break;
        case 'select':
          if (field.options && field.options.length > 0) {
            defaultData[field.id] = field.options[0].value;
          }
          break;
        case 'date':
          if (field.id.includes('prepared') || field.id.includes('current')) {
            defaultData[field.id] = new Date().toISOString().split('T')[0];
          } else {
            defaultData[field.id] = '';
          }
          break;
        case 'time':
          if (field.id.includes('prepared') || field.id.includes('current')) {
            defaultData[field.id] = new Date().toTimeString().slice(0, 5);
          } else {
            defaultData[field.id] = '';
          }
          break;
        default:
          defaultData[field.id] = '';
      }
    });
  });

  return defaultData;
}

/**
 * Gets all required field IDs from a template
 * 
 * @param template - The form template
 * @returns Array of required field IDs
 */
export function getRequiredFields(template: FormTemplate): string[] {
  const requiredFields: string[] = [];

  template.sections.forEach(section => {
    section.fields.forEach(field => {
      if (field.required) {
        requiredFields.push(field.id);
      }
    });
  });

  return requiredFields;
}