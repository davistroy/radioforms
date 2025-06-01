# ICS 207 - Incident Organization Chart Analysis

## 1. Form Overview

### Form Name
ICS 207 - Incident Organization Chart

### Purpose
The Incident Organization Chart provides a visual wall chart depicting the ICS organization position assignments for the incident. It shows what ICS organizational elements are currently activated and the names of personnel staffing each element, providing a clear visual representation of the incident command structure.

### Primary Users
- Resources Unit Leader (preparer)
- Incident Commander/Unified Command
- Command and General Staff
- All incident personnel
- Agency Administrators/Executives
- Incident facilities staff

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics207_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics207_operational_period | Operational Period | Complex | Yes | Valid date/time range | Time interval for which the form applies |
| ics207_organization_chart | Organization Chart | Complex | Yes | - | Visual representation of the command structure |
| ics207_prepared_by | Prepared By | Complex | Yes | - | Information about the person preparing the form |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics207_form_version | Form Version | Text | No | - | Version of the ICS 207 form being used |
| ics207_prepared_date_time | Preparation Date/Time | DateTime | Yes | Valid date/time | Date and time the form was prepared |
| ics207_iap_page_number | IAP Page Number | Text | No | Format: "IAP Page ___" | Page number within the IAP (optional) |

### Repeatable Section Fields - Organization Elements

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics207_position_title | Position Title | Text | Yes | - | Title of the ICS position |
| ics207_personnel_name | Personnel Name | Text | No | - | Name of person assigned to the position |
| ics207_agency | Agency | Text | No | - | Agency name (particularly for Unified Command) |
| ics207_parent_position | Parent Position | Text | No | - | Position this element reports to |
| ics207_subordinate_positions | Subordinate Positions | Complex | No | - | Positions reporting to this element |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS207-01**: Incident Name must be provided
2. **R-ICS207-02**: Operational Period must be a valid date/time range
3. **R-ICS207-03**: Organization Chart must include at minimum an Incident Commander
4. **R-ICS207-04**: Prepared By must include at minimum a name, position/title, and signature
5. **R-ICS207-05**: For all individuals, at least first initial and last name should be used
6. **R-ICS207-06**: For Unified Command, agency names should be included
7. **R-ICS207-07**: If there is a shift change during the operational period, both names should be listed, separated by a slash

### Form Lifecycle Rules

1. **L-ICS207-01**: The form is prepared by the Resources Unit Leader and reviewed by the Incident Commander
2. **L-ICS207-02**: The form is completed for each operational period
3. **L-ICS207-03**: The form is updated when organizational changes occur
4. **L-ICS207-04**: The form is wall-mounted at Incident Command Posts and other incident locations as needed
5. **L-ICS207-05**: The form is not typically part of the IAP
6. **L-ICS207-06**: All completed original forms must be given to the Documentation Unit

### Conditional Requirements

1. **C-ICS207-01**: If the Intelligence/Investigations Function is activated, it can be embedded in various locations based on incident needs
2. **C-ICS207-02**: If more than three branches are activated, additional pages are needed
3. **C-ICS207-03**: If personnel change during an operational period, both names should be listed with a slash separator
4. **C-ICS207-04**: If Unified Command is used, multiple Incident Commanders should be shown

## 4. User Interface Layout

### Section Definitions

1. **Header Section** - Contains incident identification, operational period, and form preparation information
2. **Organization Chart Section** - Visual hierarchical representation of the incident organization
3. **Footer Section** - Contains prepared by information

### Layout Specifications

- The form is intended to be wall-mounted and printed on a plotter
- Document size can be modified based on individual needs (legal size 8.5" x 14" also available)
- Organization Chart should use a hierarchical tree structure
- Lines should clearly indicate reporting relationships
- Boxes should be sized appropriately for position titles and names
- Multiple pages may be used for complex organizations

### Field Groupings

- Command Staff positions (Safety Officer, Public Information Officer, Liaison Officer) grouped with Incident Commander
- General Staff positions (Operations, Planning, Logistics, Finance/Admin) shown at same level
- Each Section shows its Units in hierarchical arrangement
- Operations Section may show Branches, Divisions/Groups in hierarchical arrangement
- For complex structures, grouping should maintain clarity of chains of command

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 207 form
2. **Update** - Modify information on an existing form
3. **Print** - Generate a printable version of the form (often large format)
4. **Display** - Post the chart at incident facilities
5. **Share** - Distribute the chart electronically
6. **Expand** - Add additional pages for complex organizations

### State Transitions

1. **Draft** → **Active**: When the form is completed by Resources Unit Leader
2. **Active** → **Updated**: When organizational changes occur
3. **Active/Updated** → **Posted**: When displayed at incident facilities
4. **Posted** → **Archived**: When the operational period ends
5. **Any State** → **Superseded**: When replaced by a new version

### Access Control

1. Resources Unit Leader: Create, Update, Print
2. Incident Commander: Review, Approve
3. All Incident Personnel: View
4. Documentation Unit: Archive

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of hierarchical organizational data
2. Must maintain relationships between positions in the hierarchy
3. Must preserve all versions throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data
6. Should maintain historical record of organizational structures

### Print and Export Requirements

1. Must generate standard wall-mount size printable output
2. Must support alternative sizes (8.5" x 14", 11" x 17")
3. Should support export to PDF and other common formats
4. Should preserve clear visualization of reporting relationships
5. Should support both color and monochrome printing
6. Should support printing of partial organization charts for specific Sections

### User Experience Requirements

1. Must provide intuitive interface for creating and editing organizational structures
2. Should support drag-and-drop editing of the organization chart
3. Should provide templates for common ICS structures
4. Should allow for rapid entry of personnel names into position boxes
5. Should provide validation of organizational relationships
6. Should support different visualization options (vertical, horizontal)
7. Should automatically adjust layout for readability

### Integration Requirements

1. Should integrate with Organization Assignment List (ICS 203)
2. Should enable pre-population of incident information from existing data
3. Should enable import of personnel assignments from other forms
4. Should support export of organization data to other systems
5. Should allow for quick update when assignments change
6. Should integrate with resource management systems

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should include version control for organization updates
4. Must comply with accessibility standards
5. Should enable collaborative editing with appropriate access controls
6. Must maintain data integrity during concurrent access
7. Should support large-format printing and display options
8. Should automatically scale to different display sizes
9. Should support both digital display and printed formats
