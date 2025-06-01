# ICS 208 - Safety Message/Plan Analysis

## 1. Form Overview

### Form Name
ICS 208 - Safety Message/Plan

### Purpose
The Safety Message/Plan form expands on the Safety Message and Site Safety Plan. It provides detailed safety information, priorities, and specific precautions to be observed during the current operational period or for a specific tactical assignment.

### Primary Users
- Safety Officer (preparer)
- Incident Commander/Unified Command (approver)
- Planning Section Chief
- Operations Section Chief
- All incident personnel
- Division/Group Supervisors
- Branch Directors

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics208_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics208_operational_period | Operational Period | Complex | Yes | Valid date/time range | Time interval for which the form applies |
| ics208_safety_message | Safety Message/Expanded Safety Message, Safety Plan, Site Safety Plan | Text | Yes | Multi-line | Detailed safety message or plan content |
| ics208_site_safety_plan_required | Site Safety Plan Required | Boolean | Yes | Yes/No checkbox | Indicates if a site safety plan is required |
| ics208_site_safety_plan_location | Approved Site Safety Plan(s) Located At | Text | No | Max 200 chars | Location of approved Site Safety Plan(s) |
| ics208_prepared_by | Prepared By | Complex | Yes | - | Information about the person preparing the form |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics208_form_version | Form Version | Text | No | - | Version of the ICS 208 form being used |
| ics208_prepared_date_time | Preparation Date/Time | DateTime | Yes | Valid date/time | Date and time the form was prepared |
| ics208_iap_page_number | IAP Page Number | Text | No | Format: "IAP Page ___" | Page number within the IAP |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS208-01**: Incident Name must be provided
2. **R-ICS208-02**: Operational Period must be a valid date/time range
3. **R-ICS208-03**: Safety Message content must be provided
4. **R-ICS208-04**: Prepared By must include at minimum a name, position/title, and signature
5. **R-ICS208-05**: If "Site Safety Plan Required" is checked "Yes", the "Approved Site Safety Plan(s) Located At" field should be completed
6. **R-ICS208-06**: Safety message should address known or potential hazards at the incident

### Form Lifecycle Rules

1. **L-ICS208-01**: The form is prepared by the Safety Officer
2. **L-ICS208-02**: The form may optionally be included in the IAP
3. **L-ICS208-03**: The form is distributed with the IAP if included
4. **L-ICS208-04**: All completed original forms must be given to the Documentation Unit
5. **L-ICS208-05**: A new ICS 208 is created for each operational period or when significant safety concerns change

### Conditional Requirements

1. **C-ICS208-01**: If hazardous materials are involved, specialized safety procedures should be included
2. **C-ICS208-02**: If additional pages are needed, blank ICS 208 forms can be used with appropriate pagination
3. **C-ICS208-03**: If specific hazards exist for different divisions/groups, separate safety messages may be needed
4. **C-ICS208-04**: If the safety message is included in the IAP, it should be consistent with any safety information in the ICS 202

## 4. User Interface Layout

### Section Definitions

1. **Header Section** - Contains incident identification and operational period
2. **Safety Message Section** - Contains the detailed safety message, expanded safety message, or site safety plan
3. **Site Safety Plan Section** - Information on site safety plan requirements and location
4. **Footer Section** - Contains prepared by information

### Layout Specifications

- The form is designed as a one-page document, possibly extending to multiple pages if needed
- Safety Message section should provide ample space for detailed text
- Site Safety Plan section should be clearly visible
- Layout should emphasize the safety message content as the primary focus

### Field Groupings

- Incident identification fields grouped together in the header
- Operational period fields (from/to) grouped together
- Site safety plan fields grouped together
- Prepared by fields grouped together in the footer

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 208 form
2. **Update** - Modify information on an existing form
3. **Print** - Generate a printable version of the form
4. **Share** - Distribute the form electronically
5. **Include in IAP** - Optionally add to Incident Action Plan package
6. **Post** - Display at strategic locations at the incident

### State Transitions

1. **Draft** → **Approved**: When the form is completed by Safety Officer
2. **Approved** → **Published**: When included in distributed IAP or otherwise shared
3. **Published** → **Archived**: When the operational period ends
4. **Any State** → **Superseded**: When replaced by a new version with updated safety information

### Access Control

1. Safety Officer: Create, Update, Print
2. Incident Commander: Review
3. Planning Section Chief: Include in IAP
4. All Incident Personnel: View
5. Documentation Unit: Archive

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, and boolean values
2. Must maintain relationship with other IAP components
3. Must preserve all versions throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data
6. Should maintain historical record of safety messages

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Must maintain consistent formatting across printed pages
3. Should support export to PDF and other common formats
4. Should support various output formats for inclusion in the IAP
5. Should facilitate printing of multiple copies for posting at incident facilities

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Should support rich text formatting in the Safety Message field
3. Should provide templates for common safety messages and hazards
4. Should support attachment of images, diagrams, or maps when relevant
5. Should support rapid duplication and modification from previous safety messages
6. Should clearly highlight critical safety information

### Integration Requirements

1. Should integrate with Incident Objectives (ICS 202) for safety considerations
2. Should integrate with Incident Action Plan Safety Analysis (ICS 215A)
3. Should enable pre-population of incident information from existing data
4. Must support integration with other IAP components
5. Should support integration with hazardous materials databases when applicable
6. Should allow for importing of standard safety protocols based on incident type

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should support digital signatures for approval fields
4. Should include version control for safety message updates
5. Must comply with accessibility standards
6. Should enable collaborative editing with appropriate access controls
7. Must maintain data integrity during concurrent access
8. Should support highlighting and emphasizing critical safety concerns
9. Should support multiple language versions when needed for diverse workforces
