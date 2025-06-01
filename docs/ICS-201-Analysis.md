# ICS 201 - Incident Briefing Analysis

## 1. Form Overview

### Form Name
ICS 201 - Incident Briefing

### Purpose
The Incident Briefing form provides the Incident Commander and Command and General Staff with basic information regarding the incident situation and resources allocated to the incident. It serves as both a briefing document and an initial action worksheet, creating a permanent record of the initial response to the incident.

### Primary Users
- Initial Incident Commander
- Incoming Incident Commander
- Command and General Staff
- Situation Unit
- Resources Unit

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics201_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics201_incident_number | Incident Number | Text | No | Max 50 chars | Number assigned to the incident |
| ics201_date_time_initiated | Date/Time Initiated | DateTime | Yes | Valid date/time | Date and time when the form was initiated |
| ics201_prepared_by | Prepared By | Complex | Yes | - | Information about the person preparing the form |
| ics201_map_sketch | Map/Sketch | Image/Drawing | No | - | Visual representation of the incident area |
| ics201_situation_summary | Situation Summary and Health and Safety Briefing | Text | Yes | Multi-line | Summary of the situation and health/safety information |
| ics201_current_objectives | Current and Planned Objectives | Text | Yes | Multi-line | List of current objectives for the incident |
| ics201_current_actions | Current and Planned Actions | Complex | Yes | - | Time-based actions planned or in progress |
| ics201_current_organization | Current Organization | Complex | Yes | - | Organizational structure of the incident response |
| ics201_resource_summary | Resource Summary | Complex | Yes | - | List of resources assigned to the incident |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics201_form_version | Form Version | Text | No | - | Version of the ICS 201 form being used |
| ics201_prepared_date_time | Preparation Date/Time | DateTime | Yes | Valid date/time | Date and time the form was prepared |
| ics201_page_number | Page Number | Text | Yes | Format: "Page X of Y" | Page numbering information |

### Repeatable Section Fields - Current and Planned Actions

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics201_action_time | Time | Time | Yes | Valid time format | Time when action is planned or was taken |
| ics201_action_description | Actions | Text | Yes | Multi-line | Description of the action taken or planned |

### Repeatable Section Fields - Resource Summary

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics201_resource_name | Resource | Text | Yes | Max 100 chars | Name or type of resource |
| ics201_resource_identifier | Resource Identifier | Text | No | Max 50 chars | ID number or other identifier for the resource |
| ics201_resource_datetime_ordered | Date/Time Ordered | DateTime | No | Valid date/time | When the resource was requested |
| ics201_resource_eta | ETA | Time | No | Valid time format | Estimated time of arrival |
| ics201_resource_arrived | Arrived | Boolean | No | Checkbox | Indicates if resource has arrived at the incident |
| ics201_resource_notes | Notes | Text | No | Multi-line | Location, assignment, status or other notes |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS201-01**: Incident Name must be provided
2. **R-ICS201-02**: Date/Time Initiated must be a valid date and time
3. **R-ICS201-03**: Prepared By must include at minimum a name and position/title
4. **R-ICS201-04**: If an ETA is provided for a resource, it must be a valid time format
5. **R-ICS201-05**: Current Organization section must include at minimum an Incident Commander
6. **R-ICS201-06**: Action times must be in chronological order

### Form Lifecycle Rules

1. **L-ICS201-01**: The form is initially created by the first Incident Commander at the incident
2. **L-ICS201-02**: The form may be updated during the initial operational period
3. **L-ICS201-03**: The form is transferred to incoming Incident Commander during transfer of command
4. **L-ICS201-04**: Copies are distributed to Command and General Staff
5. **L-ICS201-05**: Map/Sketch and Current/Planned Actions sections given to the Situation Unit
6. **L-ICS201-06**: Current Organization and Resource Summary sections given to the Resources Unit
7. **L-ICS201-07**: Can serve as part of the initial Incident Action Plan (IAP)

### Conditional Requirements

1. **C-ICS201-01**: If a Resource is marked as "Arrived," the ETA field becomes N/A
2. **C-ICS201-02**: If additional pages are needed for any section, the form can be extended with appropriate pagination updates

## 4. User Interface Layout

### Section Definitions

1. **Header Information Section** - Contains incident identification and form metadata (Page 1-4)
2. **Map/Sketch Section** - Visual representation of the incident (Page 1)
3. **Situation Summary Section** - Text description of the situation and safety briefing (Page 1)
4. **Current and Planned Objectives Section** - List of objectives (Page 2)
5. **Current and Planned Actions Section** - Chronological list of actions (Page 2)
6. **Current Organization Section** - Organizational chart (Page 3)
7. **Resource Summary Section** - Tabular list of resources (Page 4)
8. **Footer Section** - Contains prepared by information (Page 1-4)

### Layout Specifications

- The form is designed as a four-page document
- Each page has a consistent header containing incident identification information
- Each page has a consistent footer with preparer information
- Map/Sketch section should allow for drawing or attaching a map image
- Current Organization section should display a hierarchical organization chart
- Resource Summary section should display in a tabular format with multiple rows

### Field Groupings

- Incident identification fields grouped together in the header
- Preparer information fields grouped together in the footer
- Resource information fields grouped in rows in the Resource Summary table
- Action information fields grouped chronologically in the Actions section

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 201 form
2. **Update** - Modify information on an existing form
3. **Print** - Generate a printable version of the form
4. **Share** - Distribute the form electronically
5. **Extend** - Add additional pages for sections as needed
6. **Convert to IAP** - Use as part of the initial Incident Action Plan

### State Transitions

1. **Draft** → **Active**: When the form is initially completed and signed
2. **Active** → **Transferred**: When command is transferred to another Incident Commander
3. **Active** → **Superseded**: When replaced by formal IAP components
4. **Any State** → **Archived**: When the incident is closed

### Access Control

1. Initial Incident Commander: Create, Update, Print, Share
2. Incoming Incident Commander: Update, Print, Share
3. Command and General Staff: View, Print
4. Situation Unit: View, Update (Map/Sketch and Actions sections)
5. Resources Unit: View, Update (Organization and Resource sections)
6. Documentation Unit: Archive

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, times, boolean values, and images
2. Must maintain relationship between parent form and any extension pages
3. Must preserve all form versions throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Must maintain consistent formatting of all sections across printed pages
3. Should support export to PDF and other common formats
4. Should preserve the visual layout of the Map/Sketch section in exports

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Must support both keyboard and pointer-based input
3. Should support drawing or importing images for the Map/Sketch section
4. Should provide real-time validation of entered data
5. Must clearly indicate required fields
6. Should support rapid entry of time-based information in the Actions section
7. Should support both table and form views for resource information

### Integration Requirements

1. Should support integration with resource tracking systems
2. Should allow importing of map/GIS data
3. Should enable integration with incident management systems
4. Must support integration with other ICS forms (especially IAP components)
5. Should enable sharing of organization structure with ICS 203 and ICS 207

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should support digital signatures for prepared by/approval fields
4. Should include version control for form updates
5. Must comply with accessibility standards
6. Should enable collaborative editing with appropriate access controls
7. Must maintain data integrity during concurrent access
