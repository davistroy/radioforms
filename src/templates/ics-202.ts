/**
 * ICS-202 Incident Objectives Form Template
 * 
 * This template defines the structure and validation rules for the
 * ICS-202 Incident Objectives form, which outlines specific objectives
 * and current actions for an operational period.
 * 
 * Business Logic:
 * - Captures specific incident objectives with measurable criteria
 * - Documents current and planned actions
 * - Includes site safety plan considerations
 * - Supports operational period planning
 * 
 * Based on: FEMA ICS-202 official form specifications
 */

import type { FormTemplate } from '../types/forms';

export const ics202Template: FormTemplate = {
  form_type: 'ICS-202',
  name: 'Incident Objectives',
  description: 'Incident objectives, current actions, and operational planning',
  category: 'Planning',
  
  sections: [
    {
      id: 'incident_info',
      title: '1. Incident Information',
      description: 'Basic incident identification and operational period',
      fields: [
        {
          id: 'incident_name',
          label: 'Incident Name',
          type: 'text',
          required: true,
          placeholder: 'Enter incident name',
          help_text: 'Name of the incident'
        },
        {
          id: 'incident_number',
          label: 'Incident Number',
          type: 'text',
          required: false,
          placeholder: 'Enter incident number if assigned',
          help_text: 'Official incident tracking number'
        },
        {
          id: 'operational_period',
          label: 'Operational Period',
          type: 'text',
          required: true,
          placeholder: 'Date/Time From - Date/Time To',
          help_text: 'Time period these objectives cover'
        },
        {
          id: 'date_prepared',
          label: 'Date Prepared',
          type: 'date',
          required: true,
          help_text: 'Date this form was prepared'
        },
        {
          id: 'time_prepared',
          label: 'Time Prepared',
          type: 'time',
          required: true,
          help_text: 'Time this form was prepared (24-hour format)'
        },
        {
          id: 'incident_commander',
          label: 'Incident Commander',
          type: 'text',
          required: true,
          placeholder: 'Name of Incident Commander',
          help_text: 'Name of the current Incident Commander'
        }
      ]
    },

    {
      id: 'incident_objectives',
      title: '2. Incident Objectives',
      description: 'Specific, measurable objectives for the operational period',
      fields: [
        {
          id: 'objective_1',
          label: 'Objective 1',
          type: 'textarea',
          required: true,
          placeholder: 'State the first operational objective with measurable criteria',
          validation: {
            minLength: 20,
            maxLength: 500
          },
          help_text: 'Primary objective with specific, measurable outcomes'
        },
        {
          id: 'objective_2',
          label: 'Objective 2',
          type: 'textarea',
          required: false,
          placeholder: 'State the second operational objective (if applicable)',
          validation: {
            maxLength: 500
          },
          help_text: 'Second objective with specific, measurable outcomes'
        },
        {
          id: 'objective_3',
          label: 'Objective 3',
          type: 'textarea',
          required: false,
          placeholder: 'State the third operational objective (if applicable)',
          validation: {
            maxLength: 500
          },
          help_text: 'Third objective with specific, measurable outcomes'
        }
      ]
    },

    {
      id: 'current_actions',
      title: '3. Current Actions',
      description: 'Actions currently being taken to achieve the objectives',
      fields: [
        {
          id: 'current_actions',
          label: 'Current Actions Being Taken',
          type: 'textarea',
          required: true,
          placeholder: 'Describe actions currently in progress',
          validation: {
            minLength: 20,
            maxLength: 1500
          },
          help_text: 'Specific actions being implemented now to meet objectives'
        },
        {
          id: 'resource_summary',
          label: 'Resources Currently Assigned',
          type: 'textarea',
          required: false,
          placeholder: 'Summary of resources currently assigned',
          validation: {
            maxLength: 1000
          },
          help_text: 'Personnel, equipment, and other resources in use'
        }
      ]
    },

    {
      id: 'planned_actions',
      title: '4. Planned Actions',
      description: 'Actions planned for the next operational period',
      fields: [
        {
          id: 'planned_actions',
          label: 'Planned Actions for Next Operational Period',
          type: 'textarea',
          required: true,
          placeholder: 'Describe planned actions for the next operational period',
          validation: {
            minLength: 20,
            maxLength: 1500
          },
          help_text: 'Specific actions planned to continue meeting objectives'
        },
        {
          id: 'resource_needs',
          label: 'Additional Resources Needed',
          type: 'textarea',
          required: false,
          placeholder: 'List additional resources needed',
          validation: {
            maxLength: 1000
          },
          help_text: 'Personnel, equipment, or other resources required'
        }
      ]
    },

    {
      id: 'site_safety_plan',
      title: '5. Site Safety Plan',
      description: 'Key safety considerations and hazards',
      fields: [
        {
          id: 'primary_hazards',
          label: 'Primary Hazards and Safety Concerns',
          type: 'textarea',
          required: true,
          placeholder: 'Identify primary safety hazards',
          validation: {
            minLength: 10,
            maxLength: 1000
          },
          help_text: 'Key hazards that all personnel should be aware of'
        },
        {
          id: 'safety_measures',
          label: 'Safety Measures in Place',
          type: 'textarea',
          required: false,
          placeholder: 'Describe safety measures being implemented',
          validation: {
            maxLength: 1000
          },
          help_text: 'Current safety protocols and protective measures'
        },
        {
          id: 'ppe_requirements',
          label: 'PPE Requirements',
          type: 'text',
          required: false,
          placeholder: 'Required personal protective equipment',
          help_text: 'Mandatory PPE for incident personnel'
        }
      ]
    },

    {
      id: 'attachments_assignment',
      title: '6. Attachments and Assignment',
      description: 'References to other ICS forms and assignments',
      fields: [
        {
          id: 'weather_forecast',
          label: 'Weather Forecast (ICS-206)',
          type: 'text',
          required: false,
          placeholder: 'Reference to weather forecast or attach ICS-206',
          help_text: 'Weather information or reference to ICS-206'
        },
        {
          id: 'organization_chart',
          label: 'Organization Chart (ICS-203)',
          type: 'text',
          required: false,
          placeholder: 'Reference to organization chart or attach ICS-203',
          help_text: 'Organization structure or reference to ICS-203'
        },
        {
          id: 'assignment_list',
          label: 'Assignment List (ICS-204)',
          type: 'text',
          required: false,
          placeholder: 'Reference to assignment list or attach ICS-204',
          help_text: 'Division assignments or reference to ICS-204'
        },
        {
          id: 'other_attachments',
          label: 'Other Attachments',
          type: 'textarea',
          required: false,
          placeholder: 'List other relevant attachments or references',
          validation: {
            maxLength: 500
          },
          help_text: 'Additional forms, maps, or documents referenced'
        }
      ]
    },

    {
      id: 'preparation_info',
      title: '7. Prepared By',
      description: 'Information about who prepared this form',
      fields: [
        {
          id: 'preparer_name',
          label: 'Prepared By (Name)',
          type: 'text',
          required: true,
          placeholder: 'Name of person preparing this form',
          help_text: 'Full name of the preparer'
        },
        {
          id: 'preparer_position',
          label: 'ICS Position/Title',
          type: 'text',
          required: false,
          placeholder: 'ICS position or job title',
          help_text: 'ICS position (e.g., Planning Section Chief, Plans Unit Leader)'
        },
        {
          id: 'preparer_signature',
          label: 'Signature',
          type: 'text',
          required: false,
          placeholder: 'Digital signature or initials',
          help_text: 'Electronic signature field'
        }
      ]
    }
  ],

  validation_rules: {
    cross_field_validations: [
      {
        rule: 'time_sequence',
        fields: ['date_prepared', 'time_prepared'],
        message: 'Preparation date and time must be valid'
      }
    ],
    completion_requirements: {
      draft_to_completed: [
        'incident_name', 'operational_period', 'date_prepared', 'time_prepared',
        'incident_commander', 'objective_1', 'current_actions', 'planned_actions',
        'primary_hazards', 'preparer_name'
      ],
      completed_to_final: 'all_required_fields'
    }
  }
};