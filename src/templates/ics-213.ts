/**
 * ICS-213 General Message Form Template
 * 
 * This template defines the structure and validation rules for the
 * ICS-213 General Message form, which is used for transmitting
 * messages between incident personnel and external agencies.
 * 
 * Business Logic:
 * - Captures critical communication messages during incidents
 * - Provides standardized format for emergency communications
 * - Supports multiple delivery methods (radio, phone, in person)
 * - Includes priority levels for message urgency
 * - Tracks message delivery confirmation and replies
 * 
 * Based on: FEMA ICS-213 official form specifications
 */

import type { FormTemplate } from '../types/forms';

export const ics213Template: FormTemplate = {
  form_type: 'ICS-213',
  name: 'General Message',
  description: 'General message form for incident communications',
  category: 'Communications',
  
  sections: [
    {
      id: 'message_header',
      title: '1. Message Information',
      description: 'Basic message identification and routing',
      fields: [
        {
          id: 'incident_name',
          label: 'Incident Name',
          type: 'text',
          required: true,
          placeholder: 'Enter incident name',
          help_text: 'Name of the incident this message relates to'
        },
        {
          id: 'message_number',
          label: 'Message Number',
          type: 'text',
          required: false,
          placeholder: 'Sequential message number',
          help_text: 'Sequential numbering for message tracking'
        },
        {
          id: 'date',
          label: 'Date',
          type: 'date',
          required: true,
          help_text: 'Date the message was prepared'
        },
        {
          id: 'time',
          label: 'Time',
          type: 'time',
          required: true,
          help_text: 'Time the message was prepared (24-hour format)'
        },
        {
          id: 'priority',
          label: 'Priority',
          type: 'select',
          required: true,
          options: [
            { value: 'routine', label: 'Routine' },
            { value: 'priority', label: 'Priority' },
            { value: 'immediate', label: 'Immediate' },
            { value: 'flash', label: 'Flash' }
          ],
          help_text: 'Message priority level for handling'
        }
      ]
    },

    {
      id: 'routing_info',
      title: '2. Message Routing',
      description: 'From and to information for message delivery',
      fields: [
        {
          id: 'from_name',
          label: 'From (Name)',
          type: 'text',
          required: true,
          placeholder: 'Sender name',
          help_text: 'Name of person sending the message'
        },
        {
          id: 'from_position',
          label: 'From (Position/Title)',
          type: 'text',
          required: false,
          placeholder: 'Sender position or title',
          help_text: 'ICS position or job title of sender'
        },
        {
          id: 'from_agency',
          label: 'From (Agency/Organization)',
          type: 'text',
          required: false,
          placeholder: 'Sender agency or organization',
          help_text: 'Agency or organization of sender'
        },
        {
          id: 'to_name',
          label: 'To (Name)',
          type: 'text',
          required: true,
          placeholder: 'Recipient name',
          help_text: 'Name of person receiving the message'
        },
        {
          id: 'to_position',
          label: 'To (Position/Title)',
          type: 'text',
          required: false,
          placeholder: 'Recipient position or title',
          help_text: 'ICS position or job title of recipient'
        },
        {
          id: 'to_agency',
          label: 'To (Agency/Organization)',
          type: 'text',
          required: false,
          placeholder: 'Recipient agency or organization',
          help_text: 'Agency or organization of recipient'
        }
      ]
    },

    {
      id: 'message_content',
      title: '3. Message Content',
      description: 'Subject and body of the message',
      fields: [
        {
          id: 'subject',
          label: 'Subject',
          type: 'text',
          required: true,
          placeholder: 'Brief subject line describing the message',
          validation: {
            maxLength: 200
          },
          help_text: 'Concise subject describing the message content'
        },
        {
          id: 'message_body',
          label: 'Message',
          type: 'textarea',
          required: true,
          placeholder: 'Enter the complete message content',
          validation: {
            minLength: 10,
            maxLength: 2000
          },
          help_text: 'Complete message text - be clear and concise'
        },
        {
          id: 'action_requested',
          label: 'Action Requested',
          type: 'textarea',
          required: false,
          placeholder: 'Specific action requested from recipient',
          validation: {
            maxLength: 500
          },
          help_text: 'What action, if any, is requested from the recipient'
        }
      ]
    },

    {
      id: 'delivery_info',
      title: '4. Delivery Information',
      description: 'How the message was or will be delivered',
      fields: [
        {
          id: 'delivery_method',
          label: 'Method of Delivery',
          type: 'select',
          required: true,
          options: [
            { value: 'radio', label: 'Radio' },
            { value: 'telephone', label: 'Telephone' },
            { value: 'in_person', label: 'In Person' },
            { value: 'email', label: 'Email' },
            { value: 'fax', label: 'Fax' },
            { value: 'courier', label: 'Courier' },
            { value: 'other', label: 'Other' }
          ],
          help_text: 'How this message was or will be delivered'
        },
        {
          id: 'delivery_details',
          label: 'Delivery Details',
          type: 'text',
          required: false,
          placeholder: 'Additional delivery information',
          help_text: 'Radio frequency, phone number, or other delivery details'
        },
        {
          id: 'reply_required',
          label: 'Reply Required',
          type: 'select',
          required: true,
          options: [
            { value: 'yes', label: 'Yes' },
            { value: 'no', label: 'No' }
          ],
          help_text: 'Whether a reply is required from the recipient'
        },
        {
          id: 'reply_by_date',
          label: 'Reply By Date',
          type: 'date',
          required: false,
          help_text: 'Date reply is needed by (if reply required)'
        },
        {
          id: 'reply_by_time',
          label: 'Reply By Time',
          type: 'time',
          required: false,
          help_text: 'Time reply is needed by (if reply required)'
        }
      ]
    },

    {
      id: 'confirmation',
      title: '5. Delivery Confirmation',
      description: 'Confirmation of message delivery and receipt',
      fields: [
        {
          id: 'delivered_date',
          label: 'Date Delivered',
          type: 'date',
          required: false,
          help_text: 'Date the message was actually delivered'
        },
        {
          id: 'delivered_time',
          label: 'Time Delivered',
          type: 'time',
          required: false,
          help_text: 'Time the message was actually delivered'
        },
        {
          id: 'delivered_by',
          label: 'Delivered By',
          type: 'text',
          required: false,
          placeholder: 'Name of person who delivered the message',
          help_text: 'Name of person who physically delivered the message'
        },
        {
          id: 'received_by',
          label: 'Received By',
          type: 'text',
          required: false,
          placeholder: 'Name of person who received the message',
          help_text: 'Name of person who confirmed receipt of the message'
        },
        {
          id: 'delivery_notes',
          label: 'Delivery Notes',
          type: 'textarea',
          required: false,
          placeholder: 'Notes about message delivery',
          validation: {
            maxLength: 500
          },
          help_text: 'Any special notes about message delivery or receipt'
        }
      ]
    },

    {
      id: 'authorization',
      title: '6. Authorization',
      description: 'Signature and authorization information',
      fields: [
        {
          id: 'prepared_by_name',
          label: 'Prepared By (Name)',
          type: 'text',
          required: true,
          placeholder: 'Name of person preparing this message',
          help_text: 'Full name of the person who prepared this message'
        },
        {
          id: 'prepared_by_position',
          label: 'Prepared By (Position/Title)',
          type: 'text',
          required: false,
          placeholder: 'Position or title of preparer',
          help_text: 'ICS position or job title of the preparer'
        },
        {
          id: 'prepared_by_signature',
          label: 'Signature',
          type: 'text',
          required: false,
          placeholder: 'Digital signature or initials',
          help_text: 'Electronic signature field for preparer'
        },
        {
          id: 'authorized_by_name',
          label: 'Authorized By (Name)',
          type: 'text',
          required: false,
          placeholder: 'Name of authorizing official',
          help_text: 'Name of person authorizing this message (if required)'
        },
        {
          id: 'authorized_by_position',
          label: 'Authorized By (Position/Title)',
          type: 'text',
          required: false,
          placeholder: 'Position of authorizing official',
          help_text: 'ICS position or title of authorizing official'
        },
        {
          id: 'authorized_by_signature',
          label: 'Authorization Signature',
          type: 'text',
          required: false,
          placeholder: 'Digital signature of authorizing official',
          help_text: 'Electronic signature field for authorizing official'
        }
      ]
    }
  ],

  validation_rules: {
    cross_field_validations: [
      {
        rule: 'reply_deadline_validation',
        fields: ['reply_required', 'reply_by_date', 'reply_by_time'],
        message: 'If reply is required, reply deadline date and time should be specified'
      },
      {
        rule: 'delivery_time_sequence',
        fields: ['date', 'time', 'delivered_date', 'delivered_time'],
        message: 'Delivery date/time must be after or equal to message preparation date/time'
      },
      {
        rule: 'authorization_consistency',
        fields: ['authorized_by_name', 'authorized_by_signature'],
        message: 'If authorizing official is specified, signature should be provided'
      }
    ],
    completion_requirements: {
      draft_to_completed: [
        'incident_name', 'date', 'time', 'priority',
        'from_name', 'to_name', 'subject', 'message_body',
        'delivery_method', 'reply_required', 'prepared_by_name'
      ],
      completed_to_final: 'all_required_fields'
    }
  }
};