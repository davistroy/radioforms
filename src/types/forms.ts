/**
 * TypeScript type definitions for RadioForms
 * 
 * These types mirror the Rust backend data structures to ensure
 * compatibility between the frontend and backend.
 * 
 * Business Logic:
 * - Maintains exact compatibility with Rust backend types
 * - Supports all 20 ICS form types
 * - Includes form lifecycle management
 * - Provides type safety for form operations
 */

/**
 * Form status enumeration.
 * Represents the lifecycle of an ICS form from creation to finalization.
 */
export type FormStatus = 'draft' | 'completed' | 'final';

/**
 * ICS Form type enumeration.
 * Represents the different types of ICS forms supported by the application.
 */
export type ICSFormType = 
  | 'ICS-201' | 'ICS-202' | 'ICS-203' | 'ICS-204' | 'ICS-205' | 'ICS-205A'
  | 'ICS-206' | 'ICS-207' | 'ICS-208' | 'ICS-209' | 'ICS-210' | 'ICS-211'
  | 'ICS-213' | 'ICS-214' | 'ICS-215' | 'ICS-215A' | 'ICS-218' | 'ICS-220'
  | 'ICS-221' | 'ICS-225';

/**
 * Main form record structure.
 * 
 * Business Logic:
 * - Represents a single ICS form instance
 * - Form data stored as JSON object for flexibility
 * - Simple status tracking for workflow management
 * - Timestamps for sorting and audit purposes
 */
export interface Form {
  /** Unique identifier for the form (auto-increment primary key) */
  id: number;
  
  /** Type of ICS form (ICS-201, ICS-202, etc.) */
  form_type: ICSFormType;
  
  /** Name of the incident this form relates to */
  incident_name: string;
  
  /** Optional incident number for cross-referencing */
  incident_number?: string;
  
  /** Current status of the form (draft, completed, final) */
  status: FormStatus;
  
  /** Complete form data as structured object */
  data: Record<string, any>;
  
  /** Optional notes or comments about the form */
  notes?: string;
  
  /** Name of the person who prepared the form */
  preparer_name?: string;
  
  /** When the form was first created */
  created_at: string; // ISO string
  
  /** When the form was last modified */
  updated_at: string; // ISO string
}

/**
 * Form creation data transfer object.
 * Used when creating new forms to specify initial values.
 */
export interface CreateFormRequest {
  form_type: ICSFormType;
  incident_name: string;
  incident_number?: string;
  preparer_name?: string;
  initial_data?: Record<string, any>;
}

/**
 * Form update data transfer object.
 * Used when updating existing forms.
 */
export interface UpdateFormRequest {
  incident_name?: string;
  incident_number?: string;
  status?: FormStatus;
  data?: Record<string, any>;
  notes?: string;
  preparer_name?: string;
}

/**
 * Form search filters.
 * Supports filtering forms by multiple criteria.
 */
export interface FormFilters {
  incident_name?: string;
  form_type?: ICSFormType;
  status?: FormStatus;
  preparer_name?: string;
  date_from?: string; // ISO string
  date_to?: string; // ISO string
  limit?: number;
  offset?: number;
}

/**
 * Form search results with pagination information.
 */
export interface FormSearchResult {
  forms: Form[];
  total_count: number;
  has_more: boolean;
}

/**
 * Form type information for frontend display
 */
export interface FormTypeInfo {
  code: ICSFormType;
  name: string;
  description: string;
  category: string;
}

/**
 * Error response structure for consistent error handling
 */
export interface ErrorResponse {
  error: string;
  details?: string;
}

/**
 * Database statistics for monitoring and debugging.
 */
export interface DatabaseStats {
  total_forms: number;
  draft_forms: number;
  completed_forms: number;
  final_forms: number;
  database_size_bytes: number;
  last_backup?: string; // ISO string
}

/**
 * Form field definition for dynamic form rendering
 */
export interface FormField {
  id: string;
  label: string;
  type: 'text' | 'textarea' | 'number' | 'date' | 'time' | 'select' | 'checkbox' | 'radio';
  required: boolean;
  placeholder?: string;
  options?: { value: string; label: string }[];
  validation?: {
    pattern?: string;
    min?: number;
    max?: number;
    minLength?: number;
    maxLength?: number;
  };
  section?: string;
  help_text?: string;
}

/**
 * Form template definition for dynamic form generation
 */
export interface FormTemplate {
  form_type: ICSFormType;
  name: string;
  description: string;
  category: string;
  sections: FormSection[];
  validation_rules?: Record<string, any>;
}

/**
 * Form section for organizing related fields
 */
export interface FormSection {
  id: string;
  title: string;
  description?: string;
  fields: FormField[];
  collapsible?: boolean;
  required_fields?: string[];
}

/**
 * Form validation result
 */
export interface ValidationResult {
  is_valid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
}

/**
 * Individual validation error
 */
export interface ValidationError {
  field_id: string;
  field_label: string;
  message: string;
  error_type: 'required' | 'format' | 'range' | 'custom';
}

/**
 * Export options for forms
 */
export interface ExportOptions {
  format: 'pdf' | 'json' | 'ics-des';
  forms: number[]; // Form IDs
  include_metadata?: boolean;
  pdf_options?: {
    include_logos?: boolean;
    orientation?: 'portrait' | 'landscape';
    paper_size?: 'letter' | 'a4';
  };
}

/**
 * Application settings
 */
export interface AppSettings {
  theme: 'light' | 'dark' | 'auto';
  auto_save_interval: number; // seconds
  default_preparer_name: string;
  last_backup?: string; // ISO string
  form_templates_enabled: ICSFormType[];
  export_preferences: {
    default_format: 'pdf' | 'json' | 'ics-des';
    include_metadata: boolean;
  };
}