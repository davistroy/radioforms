# ICS 214 - Activity Log Analysis

## 1. Form Overview

### Form Name
ICS 214 - Activity Log

### Purpose
The Activity Log records details of notable activities at any ICS level, including single resources, equipment, Task Forces, etc. These logs provide basic incident activity documentation and serve as a reference for any after-action reports. They capture chronological events and significant occurrences for individuals or units during incident operations.

### Primary Users
- All personnel at various ICS levels
- Individual resources
- Equipment operators
- Task Force/Strike Team leaders
- Unit Leaders
- Division/Group Supervisors
- Branch Directors
- Command and General Staff

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics214_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics214_operational_period | Operational Period | Complex | Yes | Valid date/time range | Time interval for which the form applies |
| ics214_name | Name | Text | Yes | - | Name of individual completing the log |
| ics214_ics_position | ICS Position | Text | Yes | - | ICS position of individual completing the log |
| ics214_home_agency | Home Agency (and Unit) | Text | Yes | - | Agency and unit of the individual |
| ics214_resources_assigned | Resources Assigned | Complex | No | - | Resources assigned to the individual |
| ics214_activity_log | Activity Log | Complex | Yes | - | Chronological list of notable activities |
| ics214_prepared_by | Prepared By | Complex | Yes | - | Information about the person preparing the form |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics214_form_version | Form Version | Text | No | - | Version of the ICS 214 form being used |
| ics214_prepared_date_time | Preparation Date/Time | DateTime | Yes | Valid date/time | Date and time the form was prepared |
| ics214_page_number | Page Number | Text | Yes | Format: "Page X" | Page number information |

### Repeatable Section Fields - Resources Assigned

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics214_resource_name | Name | Text | Yes | - | Name of the resource |
| ics214_resource_position | ICS Position | Text | No | - | ICS position of the resource |
| ics214_resource_home_agency | Home Agency (and Unit) | Text | No | - | Agency and unit of the resource |

### Repeatable Section Fields - Activity Log

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics214_activity_datetime | Date/Time | DateTime | Yes | Valid date/time | When the activity occurred |
| ics214_notable_activities | Notable Activities | Text | Yes | Multi-line | Description of the activity |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS214-01**: Incident Name must be provided
2. **R-ICS214-02**: Operational Period must be a valid date/time range
3. **R-ICS214-03**: Name and ICS Position of the individual completing the log must be provided
4. **R-ICS214-04**: Home Agency must be provided
5. **R-ICS214-05**: At least one activity entry should be recorded
6. **R-ICS214-06**: Activity entries must include both date/time and description
7. **R-ICS214-07**: Activities should be listed in chronological order
8. **R-ICS214-08**: Prepared By must include at minimum a name, position/title, and signature
9. **R-ICS214-09**: If the activity spans multiple operational periods, the times should reflect the actual time of the activity

### Form Lifecycle Rules

1. **L-ICS214-01**: The form may be initiated by any ICS personnel as appropriate
2. **L-ICS214-02**: The form can be maintained throughout the operational period
3. **L-ICS214-03**: The form is submitted to supervisors at the end of each operational period
4. **L-ICS214-04**: All completed original forms must be given to the Documentation Unit
5. **L-ICS214-05**: A new ICS 214 is typically started for each operational period
6. **L-ICS214-06**: The form may be printed two-sided if needed for additional space

### Conditional Requirements

1. **C-ICS214-01**: If activities cover more than a 24-hour period, the date should be noted along with the time
2. **C-ICS214-02**: If additional pages are needed, use additional copies with appropriate pagination
3. **C-ICS214-03**: If resources are assigned to the individual, these should be listed in the Resources Assigned section
4. **C-ICS214-04**: If the form is used by a unit or team rather than an individual, all personnel should be listed

## 4. User Interface Layout

### Section Definitions

1. **Header Section** - Contains incident identification, operational period, and individual identification
2. **Resources Assigned Section** - Tabular listing of resources assigned to the individual
3. **Activity Log Section** - Chronological listing of notable activities
4. **Footer Section** - Contains prepared by information

### Layout Specifications

- The form is designed as a two-sided document
- Header information appears at the top of the form
- Resources Assigned section appears below the header
- Activity Log section occupies most of the form space
- Footer section appears at the bottom of each page
- Page 2 (and any additional pages) contains continuation of the Activity Log

### Field Groupings

- Incident identification fields grouped together in the header
- Operational period fields (from/to) grouped together
- Individual identification fields grouped together
- Resource information grouped in rows in the Resources table
- Activity information grouped chronologically in rows in the Activity Log

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 214 form
2. **Update** - Add additional activities as they occur
3. **Print** - Generate a printable version of the form
4. **Submit** - Provide to supervisor at end of operational period
5. **Extend** - Add additional pages as needed

### State Transitions

1. **Blank** → **In Use**: When the form is initiated by an individual
2. **In Use** → **Updated**: As activities are added throughout the operational period
3. **Updated** → **Completed**: When the operational period ends
4. **Completed** → **Submitted**: When given to supervisor
5. **Submitted** → **Archived**: When filed by Documentation Unit
6. **In Use** → **Extended**: When additional pages are added

### Access Control

1. Individual or Unit Leader: Create, Update
2. Supervisor: Review
3. Documentation Unit: Archive
4. After-Action Team: Reference

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, and times
2. Must maintain chronological order of activities
3. Should preserve all forms throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data
6. Should maintain relationship between multiple pages of the same log

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Should support two-sided printing
3. Should support export to PDF and other common formats
4. Should maintain proper pagination for multi-page logs
5. Should facilitate printing of partial logs (e.g., specific timeframes)

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Should support rapid entry of activities during operations
3. Should provide timestamp automation where possible
4. Should support both tabular and chronological views of activities
5. Should enable easy continuation to additional pages
6. Should provide sorting and filtering capabilities for review

### Integration Requirements

1. Should integrate with individual's assignment information
2. Should enable pre-population of incident information from existing data
3. Should support aggregation of multiple logs for incident summaries
4. Should allow incorporation into after-action reports
5. Should support integration with other documentation systems
6. Should enable data extraction for timeline creation

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments with offline capabilities
3. Should support digital signatures for verification
4. Should include version control for updates
5. Must comply with accessibility standards
6. Should enable collaborative editing with appropriate access controls
7. Must maintain data integrity during concurrent access
8. Should support voice-to-text or other rapid entry methods for field use
9. Should provide templates for common activities based on position
