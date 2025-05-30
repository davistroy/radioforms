# ICS 202 - Incident Objectives Analysis

## 1. Form Overview

### Form Name
ICS 202 - Incident Objectives

### Purpose
The Incident Objectives form describes the basic incident strategy, incident objectives, command emphasis/priorities, and safety considerations for use during the next operational period. It serves as the cornerstone of the Incident Action Plan (IAP).

### Primary Users
- Planning Section Chief (preparer)
- Incident Commander/Unified Command (approver)
- Command and General Staff
- Division/Group Supervisors
- All supervisory personnel

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics202_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics202_operational_period | Operational Period | Complex | Yes | Valid date/time range | Time interval for which the form applies |
| ics202_objectives | Objective(s) | Text | Yes | Multi-line | Clear, concise statements of objectives for managing the response |
| ics202_command_emphasis | Operational Period Command Emphasis | Text | No | Multi-line | Command emphasis for the operational period |
| ics202_general_situational_awareness | General Situational Awareness | Text | No | Multi-line | Weather forecast, incident conditions, or general safety message |
| ics202_site_safety_plan_required | Site Safety Plan Required | Boolean | Yes | Yes/No checkbox | Indicates if a site safety plan is required |
| ics202_site_safety_plan_location | Approved Site Safety Plan(s) Located At | Text | No | Max 200 chars | Location of the approved Site Safety Plan(s) |
| ics202_incident_action_plan_components | Incident Action Plan Components | Complex | Yes | Checkbox list | List of ICS forms included in this Incident Action Plan |
| ics202_prepared_by | Prepared By | Complex | Yes | - | Information about the person preparing the form |
| ics202_approved_by | Approved By | Complex | Yes | - | Information about the Incident Commander approving the form |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics202_form_version | Form Version | Text | No | - | Version of the ICS 202 form being used |
| ics202_prepared_date_time | Preparation Date/Time | DateTime | Yes | Valid date/time | Date and time the form was prepared |
| ics202_iap_page_number | IAP Page Number | Text | Yes | Format: "IAP Page ___" | Page number within the IAP |

### Repeatable Section Fields - IAP Components

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics202_component_id | Component ID | Text | Yes | Valid ICS form identifier | Form identifier (e.g., ICS 203, ICS 204) |
| ics202_component_included | Included | Boolean | Yes | Checkbox | Indicates if the component is included in the IAP |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS202-01**: Incident Name must be provided
2. **R-ICS202-02**: Operational Period must be a valid date/time range
3. **R-ICS202-03**: At least one Objective must be provided
4. **R-ICS202-04**: If "Site Safety Plan Required" is checked "Yes", the "Approved Site Safety Plan(s) Located At" field should be completed
5. **R-ICS202-05**: At least one IAP component must be checked
6. **R-ICS202-06**: Prepared By must include at minimum a name, position/title, and signature
7. **R-ICS202-07**: Approved By must include at minimum a name and signature

### Form Lifecycle Rules

1. **L-ICS202-01**: The form is created by the Planning Section Chief after Command and General Staff meetings
2. **L-ICS202-02**: The form must be approved by the Incident Commander/Unified Command
3. **L-ICS202-03**: The form becomes the opening/cover page of the IAP
4. **L-ICS202-04**: The form is duplicated and distributed with the IAP to all supervisory personnel
5. **L-ICS202-05**: Original completed form must be given to the Documentation Unit
6. **L-ICS202-06**: A new ICS 202 is created for each operational period

### Conditional Requirements

1. **C-ICS202-01**: If Unified Command is being used, multiple Incident Commanders may approve the form (attach additional signature page if needed)
2. **C-ICS202-02**: If "Site Safety Plan Required" is checked "Yes", the Safety Officer should review the safety message and approve it
3. **C-ICS202-03**: If a Safety Message is included in "General Situational Awareness", it should be aligned with the Safety Message/Plan (ICS 208)

## 4. User Interface Layout

### Section Definitions

1. **Header Section** - Contains incident identification and operational period
2. **Objectives Section** - List of clear, concise statements of incident objectives
3. **Command Emphasis Section** - Command emphasis and general situational awareness
4. **Safety Plan Section** - Information on site safety plan requirements
5. **IAP Components Section** - Checklist of forms included in the IAP
6. **Approval Section** - Contains prepared by and approved by information

### Layout Specifications

- The form is designed as a single-page document
- Objectives section should provide sufficient space for multiple objectives
- Command emphasis and situational awareness sections should allow for detailed text
- IAP components section should be arranged as a checklist with two columns for standard components
- Approval section should include space for multiple approvers if Unified Command is used

### Field Groupings

- Incident identification fields grouped together in the header
- Operational period fields (from/to) grouped together
- IAP components grouped by form types (organization forms, planning forms, etc.)
- Approval fields grouped by role (prepared by, approved by)

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 202 form
2. **Update** - Modify information on an existing form
3. **Approve** - Obtain Incident Commander signature and approval
4. **Print** - Generate a printable version of the form
5. **Share** - Distribute the form electronically
6. **Include in IAP** - Add to complete Incident Action Plan package

### State Transitions

1. **Draft** → **Pending Approval**: When the form is completed by Planning Section Chief
2. **Pending Approval** → **Approved**: When signed by Incident Commander
3. **Approved** → **Published**: When included in distributed IAP
4. **Published** → **Archived**: When the operational period ends
5. **Any State** → **Superseded**: When replaced by a new version for the same operational period

### Access Control

1. Planning Section Chief: Create, Update, Print
2. Incident Commander/Unified Command: Approve, Update
3. Command and General Staff: View, Print
4. Safety Officer: View, Update (safety-related fields)
5. Documentation Unit: Archive
6. Supervisory Personnel: View

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, times, and boolean values
2. Must maintain relationship with other IAP components
3. Must preserve all versions throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Must maintain consistent formatting across printed pages
3. Should support export to PDF and other common formats
4. Should be identifiable as the initial page of the IAP package

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Must clearly distinguish between required and optional fields
3. Should provide templates or examples for effective objective statements (SMART format)
4. Should provide real-time validation of entered data
5. Must clearly indicate IAP components included vs. not included
6. Should support digital signature capabilities

### Integration Requirements

1. Should integrate with other IAP component forms
2. Should enable pre-population of incident information from existing data
3. Should allow information sharing with incident management systems
4. Must support integration with other ICS forms (especially those checked in IAP components)
5. Should enable creation of a complete IAP package

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should support digital signatures for approval fields
4. Should include version control for form updates
5. Must comply with accessibility standards
6. Should enable collaborative editing with appropriate access controls
7. Must maintain data integrity during concurrent access
