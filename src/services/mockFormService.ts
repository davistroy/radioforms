/**
 * Mock form service for frontend development
 * 
 * This service provides the same interface as the Tauri commands
 * but uses localStorage for data persistence during development.
 * It will be replaced with actual Tauri commands once the Rust
 * backend is compiled.
 * 
 * Business Logic:
 * - Maintains exact same interface as Rust backend
 * - Uses localStorage for data persistence
 * - Implements proper form lifecycle management
 * - Provides realistic data for UI development
 */

import type {
  Form,
  CreateFormRequest,
  UpdateFormRequest,
  FormFilters,
  FormSearchResult,
  FormTypeInfo,
  ICSFormType,
  FormStatus,
  ErrorResponse,
  DatabaseStats
} from '../types/forms';

/**
 * Local storage key for forms data
 */
const FORMS_STORAGE_KEY = 'radioforms_forms';
const SETTINGS_STORAGE_KEY = 'radioforms_settings';
const ID_COUNTER_KEY = 'radioforms_id_counter';

/**
 * Mock form service class that mimics Tauri command functionality
 */
class MockFormService {
  /**
   * Gets the next available form ID
   */
  private getNextId(): number {
    const current = parseInt(localStorage.getItem(ID_COUNTER_KEY) || '0', 10);
    const next = current + 1;
    localStorage.setItem(ID_COUNTER_KEY, next.toString());
    return next;
  }

  /**
   * Gets all forms from localStorage
   */
  private getAllForms(): Form[] {
    const formsJson = localStorage.getItem(FORMS_STORAGE_KEY);
    if (!formsJson) {
      return [];
    }
    try {
      return JSON.parse(formsJson);
    } catch (error) {
      console.error('Failed to parse forms from localStorage:', error);
      return [];
    }
  }

  /**
   * Saves forms to localStorage
   */
  private saveForms(forms: Form[]): void {
    localStorage.setItem(FORMS_STORAGE_KEY, JSON.stringify(forms));
  }

  /**
   * Creates a new form with the specified data.
   * 
   * Business Logic:
   * - Validates incident name is not empty
   * - Sets initial status to Draft
   * - Creates timestamps for creation and update
   * - Initializes form data with defaults if none provided
   */
  async createForm(request: CreateFormRequest): Promise<Form> {
    // Validate required fields
    if (!request.incident_name?.trim()) {
      throw new Error('Incident name cannot be empty');
    }

    // Prepare initial form data
    const initialData = request.initial_data || {
      incident_name: request.incident_name,
      form_type: request.form_type,
      date_prepared: new Date().toISOString().split('T')[0],
      time_prepared: new Date().toTimeString().slice(0, 5),
      ...(request.preparer_name && { preparer_name: request.preparer_name })
    };

    const now = new Date().toISOString();
    const form: Form = {
      id: this.getNextId(),
      form_type: request.form_type,
      incident_name: request.incident_name,
      incident_number: request.incident_number,
      status: 'draft' as FormStatus,
      data: initialData,
      notes: undefined,
      preparer_name: request.preparer_name,
      created_at: now,
      updated_at: now,
    };

    const forms = this.getAllForms();
    forms.push(form);
    this.saveForms(forms);

    console.log(`Mock: Created form ${form.id} (${form.form_type})`);
    return form;
  }

  /**
   * Retrieves a form by its ID.
   * 
   * Business Logic:
   * - Returns undefined if form doesn't exist
   * - Performs ID validation
   * - Includes all form data and metadata
   */
  async getForm(id: number): Promise<Form | undefined> {
    if (id <= 0) {
      throw new Error(`Invalid form ID: ${id}`);
    }

    const forms = this.getAllForms();
    const form = forms.find(f => f.id === id);
    
    console.log(`Mock: Retrieved form ${id}:`, form ? 'found' : 'not found');
    return form;
  }

  /**
   * Updates an existing form with new data.
   * 
   * Business Logic:
   * - Validates form exists before updating
   * - Checks status transition validity
   * - Updates only provided fields
   * - Automatically updates updated_at timestamp
   */
  async updateForm(id: number, request: UpdateFormRequest): Promise<Form> {
    const forms = this.getAllForms();
    const formIndex = forms.findIndex(f => f.id === id);
    
    if (formIndex === -1) {
      throw new Error(`Form not found with ID: ${id}`);
    }

    const currentForm = forms[formIndex];

    // Validate status transition if requested
    if (request.status && !this.canTransitionTo(currentForm.status, request.status)) {
      throw new Error(`Invalid status transition from ${currentForm.status} to ${request.status}`);
    }

    // Validate incident name if provided
    if (request.incident_name !== undefined && !request.incident_name.trim()) {
      throw new Error('Incident name cannot be empty');
    }

    // Update form fields
    const updatedForm: Form = {
      ...currentForm,
      ...(request.incident_name !== undefined && { incident_name: request.incident_name }),
      ...(request.incident_number !== undefined && { incident_number: request.incident_number }),
      ...(request.status !== undefined && { status: request.status }),
      ...(request.data !== undefined && { data: { ...currentForm.data, ...request.data } }),
      ...(request.notes !== undefined && { notes: request.notes }),
      ...(request.preparer_name !== undefined && { preparer_name: request.preparer_name }),
      updated_at: new Date().toISOString(),
    };

    forms[formIndex] = updatedForm;
    this.saveForms(forms);

    console.log(`Mock: Updated form ${id}`, request);
    return updatedForm;
  }

  /**
   * Checks if a form can transition to the specified status
   */
  private canTransitionTo(currentStatus: FormStatus, newStatus: FormStatus): boolean {
    // Same status is always allowed
    if (currentStatus === newStatus) return true;

    // Forward transitions only
    switch (currentStatus) {
      case 'draft':
        return newStatus === 'completed' || newStatus === 'final';
      case 'completed':
        return newStatus === 'final';
      case 'final':
        return false; // No transitions from final
      default:
        return false;
    }
  }

  /**
   * Deletes a form by ID.
   * 
   * Business Logic:
   * - Only allows deletion of draft forms by default
   * - Requires force flag to delete completed/final forms
   * - Returns true if form was deleted, false if not found
   */
  async deleteForm(id: number, force: boolean = false): Promise<boolean> {
    const forms = this.getAllForms();
    const formIndex = forms.findIndex(f => f.id === id);
    
    if (formIndex === -1) {
      return false; // Form not found
    }

    const form = forms[formIndex];

    // Check if deletion is allowed
    if (form.status === 'final' && !force) {
      throw new Error(`Cannot delete final form without force flag. Form ID: ${id}`);
    }

    forms.splice(formIndex, 1);
    this.saveForms(forms);

    console.log(`Mock: Deleted form ${id}`);
    return true;
  }

  /**
   * Searches forms based on the provided filters.
   * 
   * Business Logic:
   * - Supports partial text matching for incident names
   * - Date range filtering for created_at timestamps
   * - Pagination with limit and offset
   * - Returns total count for pagination UI
   */
  async searchForms(filters: FormFilters): Promise<FormSearchResult> {
    let forms = this.getAllForms();

    // Apply filters
    if (filters.incident_name) {
      const searchTerm = filters.incident_name.toLowerCase();
      forms = forms.filter(f => f.incident_name.toLowerCase().includes(searchTerm));
    }

    if (filters.form_type) {
      forms = forms.filter(f => f.form_type === filters.form_type);
    }

    if (filters.status) {
      forms = forms.filter(f => f.status === filters.status);
    }

    if (filters.preparer_name) {
      const searchTerm = filters.preparer_name.toLowerCase();
      forms = forms.filter(f => f.preparer_name?.toLowerCase().includes(searchTerm));
    }

    if (filters.date_from) {
      forms = forms.filter(f => f.created_at >= filters.date_from!);
    }

    if (filters.date_to) {
      forms = forms.filter(f => f.created_at <= filters.date_to!);
    }

    // Sort by updated_at desc (newest first)
    forms.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());

    const total_count = forms.length;
    const offset = filters.offset || 0;
    const limit = filters.limit || 50;

    // Apply pagination
    const paginatedForms = forms.slice(offset, offset + limit);
    const has_more = (offset + paginatedForms.length) < total_count;

    console.log(`Mock: Search returned ${paginatedForms.length} of ${total_count} forms`);

    return {
      forms: paginatedForms,
      total_count,
      has_more,
    };
  }

  /**
   * Gets all forms for a specific incident.
   */
  async getFormsByIncident(incidentName: string): Promise<Form[]> {
    if (!incidentName.trim()) {
      throw new Error('Incident name cannot be empty');
    }

    const forms = this.getAllForms();
    const incidentForms = forms.filter(f => f.incident_name === incidentName);
    
    // Sort by form type for logical ordering
    incidentForms.sort((a, b) => a.form_type.localeCompare(b.form_type));

    console.log(`Mock: Found ${incidentForms.length} forms for incident: ${incidentName}`);
    return incidentForms;
  }

  /**
   * Gets recent forms (most recently updated).
   */
  async getRecentForms(limit: number = 10): Promise<Form[]> {
    const forms = this.getAllForms();
    
    // Sort by updated_at desc (newest first)
    forms.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
    
    const recentForms = forms.slice(0, limit);
    
    console.log(`Mock: Retrieved ${recentForms.length} recent forms`);
    return recentForms;
  }

  /**
   * Duplicates an existing form as a new draft.
   */
  async duplicateForm(sourceId: number, newIncidentName?: string): Promise<Form> {
    const sourceForm = await this.getForm(sourceId);
    if (!sourceForm) {
      throw new Error(`Source form not found with ID: ${sourceId}`);
    }

    const formData = { ...sourceForm.data };
    
    // Update incident name if provided
    if (newIncidentName) {
      formData.incident_name = newIncidentName;
    }

    // Update preparation date/time to current
    formData.date_prepared = new Date().toISOString().split('T')[0];
    formData.time_prepared = new Date().toTimeString().slice(0, 5);

    const createRequest: CreateFormRequest = {
      form_type: sourceForm.form_type,
      incident_name: newIncidentName || sourceForm.incident_name,
      incident_number: sourceForm.incident_number,
      preparer_name: sourceForm.preparer_name,
      initial_data: formData,
    };

    const duplicatedForm = await this.createForm(createRequest);
    
    console.log(`Mock: Duplicated form ${sourceId} as ${duplicatedForm.id}`);
    return duplicatedForm;
  }

  /**
   * Gets list of all supported ICS form types.
   */
  async getFormTypes(): Promise<FormTypeInfo[]> {
    const formTypes: FormTypeInfo[] = [
      {
        code: 'ICS-201',
        name: 'Incident Briefing',
        description: 'Initial incident briefing and situation assessment',
        category: 'Planning'
      },
      {
        code: 'ICS-202',
        name: 'Incident Objectives',
        description: 'Incident objectives, priorities, and safety considerations',
        category: 'Planning'
      },
      {
        code: 'ICS-203',
        name: 'Organization Assignment List',
        description: 'Incident organization and personnel assignments',
        category: 'Planning'
      },
      {
        code: 'ICS-204',
        name: 'Assignment List',
        description: 'Assignment of operational personnel and resources',
        category: 'Operations'
      },
      {
        code: 'ICS-205',
        name: 'Incident Radio Communications Plan',
        description: 'Radio frequency assignments and communication procedures',
        category: 'Communications'
      },
      {
        code: 'ICS-205A',
        name: 'Communications List',
        description: 'Communications directory for incident personnel',
        category: 'Communications'
      },
      {
        code: 'ICS-206',
        name: 'Medical Plan',
        description: 'Medical emergency procedures and hospital information',
        category: 'Logistics'
      },
      {
        code: 'ICS-207',
        name: 'Incident Organization Chart',
        description: 'Visual representation of incident organization structure',
        category: 'Planning'
      },
      {
        code: 'ICS-208',
        name: 'Safety Analysis',
        description: 'Hazard analysis and safety recommendations',
        category: 'Safety'
      },
      {
        code: 'ICS-209',
        name: 'Incident Status Summary',
        description: 'Overall incident status and resource summary',
        category: 'Planning'
      },
      {
        code: 'ICS-210',
        name: 'Resource Status Change',
        description: 'Changes in resource status and availability',
        category: 'Logistics'
      },
      {
        code: 'ICS-211',
        name: 'Incident Check-In List',
        description: 'Personnel and equipment check-in tracking',
        category: 'Planning'
      },
      {
        code: 'ICS-213',
        name: 'General Message Form',
        description: 'General communications and message relay',
        category: 'Communications'
      },
      {
        code: 'ICS-214',
        name: 'Activity Log',
        description: 'Individual activity and time tracking log',
        category: 'Documentation'
      },
      {
        code: 'ICS-215',
        name: 'Operational Planning Worksheet',
        description: 'Operational period planning and resource calculations',
        category: 'Planning'
      },
      {
        code: 'ICS-215A',
        name: 'Incident Action Plan Safety Analysis',
        description: 'Safety analysis for operational period planning',
        category: 'Safety'
      },
      {
        code: 'ICS-218',
        name: 'Support Vehicle/Equipment Inventory',
        description: 'Inventory of support vehicles and equipment',
        category: 'Logistics'
      },
      {
        code: 'ICS-220',
        name: 'Air Operations Summary',
        description: 'Summary of air operations and aircraft assignments',
        category: 'Operations'
      },
      {
        code: 'ICS-221',
        name: 'Demobilization Check-Out',
        description: 'Resource demobilization and check-out procedures',
        category: 'Planning'
      },
      {
        code: 'ICS-225',
        name: 'Incident Personnel Performance Rating',
        description: 'Performance evaluation for incident personnel',
        category: 'Administration'
      }
    ];

    console.log(`Mock: Retrieved ${formTypes.length} form types`);
    return formTypes;
  }

  /**
   * Gets database statistics for monitoring.
   */
  async getDatabaseStats(): Promise<DatabaseStats> {
    const forms = this.getAllForms();
    
    const stats: DatabaseStats = {
      total_forms: forms.length,
      draft_forms: forms.filter(f => f.status === 'draft').length,
      completed_forms: forms.filter(f => f.status === 'completed').length,
      final_forms: forms.filter(f => f.status === 'final').length,
      database_size_bytes: JSON.stringify(forms).length, // Approximate
      last_backup: undefined, // Not implemented in mock
    };

    console.log('Mock: Database stats:', stats);
    return stats;
  }

  /**
   * Initializes the mock service with sample data if no data exists
   */
  async initializeSampleData(): Promise<void> {
    const existingForms = this.getAllForms();
    if (existingForms.length > 0) {
      console.log('Mock: Sample data already exists, skipping initialization');
      return;
    }

    console.log('Mock: Initializing with sample data...');

    // Create sample forms for demonstration
    await this.createForm({
      form_type: 'ICS-201',
      incident_name: 'Wildfire Response - Pine Valley',
      incident_number: 'WF-2024-001',
      preparer_name: 'John Smith',
      initial_data: {
        incident_type: 'Wildfire',
        location: 'Pine Valley State Park',
        started_date: '2024-05-30',
        started_time: '14:30',
        cause: 'Lightning strike',
        area_description: 'Forested area near main campground',
        weather: 'Hot, dry, winds 15-20 mph from SW',
        current_situation: 'Fire burning in timber, estimated 50 acres',
        initial_response: 'Two engine companies and one water tender on scene',
        resource_needs: 'Additional engines, hand crews, air support',
        priorities: '1. Life safety, 2. Campground protection, 3. Fire suppression',
      }
    });

    await this.createForm({
      form_type: 'ICS-202',
      incident_name: 'Wildfire Response - Pine Valley',
      incident_number: 'WF-2024-001',
      preparer_name: 'Jane Doe',
      initial_data: {
        operational_period: 'Day 1 - 0600 to 1800',
        incident_objectives: [
          'Ensure firefighter and public safety',
          'Protect Pine Valley Campground and structures',
          'Contain fire to current area',
          'Minimize environmental damage'
        ],
        operational_constraints: [
          'Steep terrain on north side',
          'Limited water sources',
          'High fire danger conditions',
          'Aircraft restrictions due to power lines'
        ],
        current_weather: 'Temperature 85°F, RH 15%, Wind SW 20 mph',
        predicted_weather: 'Hot and dry continues, winds may increase',
      }
    });

    await this.createForm({
      form_type: 'ICS-213',
      incident_name: 'Medical Emergency - Highway 101',
      incident_number: 'ME-2024-015',
      preparer_name: 'Mike Johnson',
      initial_data: {
        message_type: 'Emergency',
        priority: 'Urgent',
        to: 'Central Dispatch',
        from: 'Engine 42',
        subject: 'Multi-vehicle accident with injuries',
        message: 'Responding to MVA at Mile Post 15 on Highway 101. Three vehicles involved, multiple injuries reported. Requesting additional ambulances and traffic control.',
        date_sent: '2024-05-31',
        time_sent: '09:45',
      }
    });

    console.log('Mock: Sample data initialization complete');
  }

  /**
   * Clears all data (for testing purposes)
   */
  async clearAllData(): Promise<void> {
    localStorage.removeItem(FORMS_STORAGE_KEY);
    localStorage.removeItem(SETTINGS_STORAGE_KEY);
    localStorage.removeItem(ID_COUNTER_KEY);
    console.log('Mock: All data cleared');
  }
}

// Export singleton instance
export const mockFormService = new MockFormService();

// Initialize sample data on first load
mockFormService.initializeSampleData().catch(console.error);