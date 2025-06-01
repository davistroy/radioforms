/**
 * ICS-201 Incident Briefing Form Template
 * 
 * This template defines the structure and validation rules for the
 * ICS-201 Incident Briefing form, which provides initial incident
 * information and situation assessment.
 * 
 * Business Logic:
 * - Captures initial incident assessment information
 * - Provides situation overview for incoming personnel
 * - Includes map/sketch area for incident visualization
 * - Supports both typed and handwritten completion
 * 
 * Based on: FEMA ICS-201 official form specifications
 */

import type { FormTemplate } from '../types/forms';

export const ics201Template: FormTemplate = {
  form_type: 'ICS-201',
  name: 'Incident Briefing',
  description: 'Initial incident briefing and situation assessment',
  category: 'Planning',
  
  sections: [
    {
      id: 'incident_info',
      title: '1. Incident Information',
      description: 'Basic incident identification and classification',
      fields: [
        {
          id: 'incident_name',
          label: 'Incident Name',
          type: 'text',
          required: true,
          placeholder: 'Enter incident name',
          help_text: 'Unique name for this incident'
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
          id: 'incident_type',
          label: 'Type of Incident',
          type: 'select',
          required: true,
          options: [
            { value: 'wildfire', label: 'Wildfire' },
            { value: 'structure_fire', label: 'Structure Fire' },
            { value: 'medical', label: 'Medical Emergency' },
            { value: 'hazmat', label: 'Hazardous Materials' },
            { value: 'search_rescue', label: 'Search and Rescue' },
            { value: 'flood', label: 'Flood' },
            { value: 'earthquake', label: 'Earthquake' },
            { value: 'severe_weather', label: 'Severe Weather' },
            { value: 'other', label: 'Other' }
          ]
        },
        {
          id: 'date_prepared',
          label: 'Date Prepared',
          type: 'date',
          required: true,
          help_text: 'Date this briefing was prepared'
        },
        {
          id: 'time_prepared',
          label: 'Time Prepared',
          type: 'time',
          required: true,
          help_text: 'Time this briefing was prepared (24-hour format)'
        }
      ]
    },

    {
      id: 'location_info',
      title: '2. Location and Area Description',
      description: 'Geographic and physical details of the incident',
      fields: [
        {
          id: 'location',
          label: 'Location (Address, Coordinates, or Description)',
          type: 'textarea',
          required: true,
          placeholder: 'Provide specific location information',
          validation: {
            minLength: 10,
            maxLength: 500
          },
          help_text: 'Include coordinates, landmarks, or detailed address'
        },
        {
          id: 'area_description',
          label: 'Area Description',
          type: 'textarea',
          required: true,
          placeholder: 'Describe the physical characteristics of the area',
          validation: {
            minLength: 20,
            maxLength: 1000
          },
          help_text: 'Terrain, vegetation, structures, access routes, hazards'
        },
        {
          id: 'jurisdiction',
          label: 'Jurisdiction',
          type: 'text',
          required: true,
          placeholder: 'Responsible jurisdiction',
          help_text: 'Agency or entity with primary jurisdiction'
        }
      ]
    },

    {
      id: 'incident_timeline',
      title: '3. Incident Timeline',
      description: 'When the incident started and key timeline information',
      fields: [
        {
          id: 'started_date',
          label: 'Date/Time Started',
          type: 'date',
          required: true,
          help_text: 'When the incident began'
        },
        {
          id: 'started_time',
          label: 'Time Started',
          type: 'time',
          required: true,
          help_text: 'Time incident started (24-hour format)'
        },
        {
          id: 'cause',
          label: 'Cause (if known)',
          type: 'text',
          required: false,
          placeholder: 'Known or suspected cause',
          help_text: 'What caused this incident (if determined)'
        }
      ]
    },

    {
      id: 'current_situation',
      title: '4. Current Situation',
      description: 'Present status and immediate conditions',
      fields: [
        {
          id: 'current_situation',
          label: 'Current Situation',
          type: 'textarea',
          required: true,
          placeholder: 'Describe the current status of the incident',
          validation: {
            minLength: 50,
            maxLength: 2000
          },
          help_text: 'Size, containment, injuries, damages, immediate threats'
        },
        {
          id: 'initial_response',
          label: 'Initial Response Actions',
          type: 'textarea',
          required: true,
          placeholder: 'Actions taken so far',
          validation: {
            minLength: 20,
            maxLength: 1000
          },
          help_text: 'What has been done in response to this incident'
        },
        {
          id: 'resource_summary',
          label: 'Current Resource Summary',
          type: 'textarea',
          required: false,
          placeholder: 'Resources currently on scene',
          validation: {
            maxLength: 1000
          },
          help_text: 'Personnel, equipment, aircraft currently assigned'
        }
      ]
    },

    {
      id: 'priorities_objectives',
      title: '5. Priorities and General Objectives',
      description: 'Immediate priorities and initial operational objectives',
      fields: [
        {
          id: 'life_safety_issues',
          label: 'Life Safety Issues',
          type: 'textarea',
          required: true,
          placeholder: 'Life safety concerns and actions',
          validation: {
            minLength: 10,
            maxLength: 500
          },
          help_text: 'Immediate threats to life and safety'
        },
        {
          id: 'priorities',
          label: 'Incident Priorities (in order)',
          type: 'textarea',
          required: true,
          placeholder: 'List priorities in order of importance',
          validation: {
            minLength: 20,
            maxLength: 1000
          },
          help_text: 'Numbered list of incident priorities (1, 2, 3, etc.)'
        },
        {
          id: 'immediate_objectives',
          label: 'Immediate Objectives',
          type: 'textarea',
          required: true,
          placeholder: 'Immediate operational objectives',
          validation: {
            minLength: 20,
            maxLength: 1000
          },
          help_text: 'Specific objectives for the next operational period'
        }
      ]
    },

    {
      id: 'resource_needs',
      title: '6. Resource and Organizational Needs',
      description: 'Additional resources and organizational requirements',
      fields: [
        {
          id: 'resource_needs',
          label: 'Additional Resource Needs',
          type: 'textarea',
          required: false,
          placeholder: 'List additional resources needed',
          validation: {
            maxLength: 1000
          },
          help_text: 'Personnel, equipment, specialists needed'
        },
        {
          id: 'organizational_needs',
          label: 'Organizational/ICS Structure',
          type: 'textarea',
          required: false,
          placeholder: 'Organizational structure needs',
          validation: {
            maxLength: 500
          },
          help_text: 'Command structure, positions to be filled'
        }
      ]
    },

    {
      id: 'weather_conditions',
      title: '7. Weather Information',
      description: 'Current and forecasted weather conditions',
      fields: [
        {
          id: 'current_weather',
          label: 'Current Weather',
          type: 'textarea',
          required: false,
          placeholder: 'Current weather conditions',
          validation: {
            maxLength: 500
          },
          help_text: 'Temperature, humidity, wind speed/direction, visibility'
        },
        {
          id: 'predicted_weather',
          label: 'Predicted Weather',
          type: 'textarea',
          required: false,
          placeholder: 'Weather forecast',
          validation: {
            maxLength: 500
          },
          help_text: 'Forecast for next 12-24 hours'
        }
      ]
    },

    {
      id: 'safety_considerations',
      title: '8. Safety Considerations',
      description: 'Known hazards and safety concerns',
      fields: [
        {
          id: 'known_hazards',
          label: 'Known Hazards',
          type: 'textarea',
          required: false,
          placeholder: 'List known safety hazards',
          validation: {
            maxLength: 1000
          },
          help_text: 'Environmental, structural, or operational hazards'
        },
        {
          id: 'safety_message',
          label: 'Safety Message/Considerations',
          type: 'textarea',
          required: false,
          placeholder: 'Key safety messages',
          validation: {
            maxLength: 500
          },
          help_text: 'Important safety reminders for all personnel'
        }
      ]
    },

    {
      id: 'communications',
      title: '9. Communications',
      description: 'Communication procedures and frequencies',
      fields: [
        {
          id: 'command_frequency',
          label: 'Incident Command Frequency',
          type: 'text',
          required: false,
          placeholder: 'Primary command frequency',
          help_text: 'Main incident command radio frequency'
        },
        {
          id: 'tactical_frequencies',
          label: 'Tactical Frequencies',
          type: 'textarea',
          required: false,
          placeholder: 'List tactical frequencies in use',
          validation: {
            maxLength: 300
          },
          help_text: 'Division/group tactical frequencies'
        },
        {
          id: 'special_instructions',
          label: 'Special Communication Instructions',
          type: 'textarea',
          required: false,
          placeholder: 'Special communication procedures',
          validation: {
            maxLength: 500
          },
          help_text: 'Unique communication requirements or procedures'
        }
      ]
    },

    {
      id: 'preparation_info',
      title: '10. Prepared By',
      description: 'Information about who prepared this briefing',
      fields: [
        {
          id: 'preparer_name',
          label: 'Prepared By (Name)',
          type: 'text',
          required: true,
          placeholder: 'Name of person preparing this briefing',
          help_text: 'Full name of the preparer'
        },
        {
          id: 'preparer_position',
          label: 'ICS Position/Title',
          type: 'text',
          required: false,
          placeholder: 'ICS position or job title',
          help_text: 'ICS position (e.g., Incident Commander, Planning Chief)'
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
        fields: ['started_date', 'started_time', 'date_prepared', 'time_prepared'],
        message: 'Preparation date/time must be after or equal to incident start date/time'
      }
    ],
    completion_requirements: {
      draft_to_completed: [
        'incident_name', 'incident_type', 'date_prepared', 'time_prepared',
        'location', 'area_description', 'started_date', 'started_time',
        'current_situation', 'initial_response', 'life_safety_issues',
        'priorities', 'immediate_objectives', 'preparer_name'
      ],
      completed_to_final: 'all_required_fields'
    }
  }
};