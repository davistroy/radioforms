# ICS 210 - Resource Status Change Analysis

## 1. Form Overview

### Form Name
ICS 210 - Resource Status Change

### Purpose
The Resource Status Change form is used by the Incident Communications Center Manager to record status change information received on resources assigned to the incident. This information is used to maintain status on incident resources and can be transmitted with a General Message (ICS 213). The form can also be used by Operations as a worksheet to track entry, etc.

### Primary Users
- Incident Communications Center Manager (preparer)
- Radio/Telephone Operators
- Resources Unit
- Documentation Unit
- Status/Check-in Recorders
- Operations Section personnel
- Staging Area Managers
- Helibase Managers

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics210_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics210_operational_period | Operational Period | Complex | Yes | Valid date/time range | Time interval for which the form applies |
| ics210_resource_status_changes | Resource Status Changes | Complex | Yes | - | Detailed listing of resource status changes |
| ics210_comments | Comments | Text | No | Multi-line | Any additional information about the status changes |
| ics210_prepared_by | Prepared By | Complex | Yes | - | Information about the person preparing the form |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics210_form_version | Form Version | Text | No | - | Version of the ICS 210 form being used |
| ics210_prepared_date_time | Preparation Date/Time | DateTime | Yes | Valid date/time | Date and time the form was prepared |

### Repeatable Section Fields - Resource Status Changes

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics210_resource_number | Resource Number | Text | Yes | - | Resource identification number or identifier |
| ics210_new_status | New Status | Enum | Yes | Available/Assigned/O/S | New status of the resource |
| ics210_from_assignment_status | From (Assignment and Status) | Text | Yes | - | Current location and status of the resource |
| ics210_to_assignment_status | To (Assignment and Status) | Text | Yes | - | New location and status assignment |
| ics210_time_date_change | Time and Date of Change | DateTime | Yes | Valid date/time | When the status change occurred |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS210-01**: Incident Name must be provided
2. **R-ICS210-02**: Operational Period must be a valid date/time range
3. **R-ICS210-03**: At least one Resource Status Change entry must be provided
4. **R-ICS210-04**: New Status must be one of: Available, Assigned, or Out of Service (O/S)
5. **R-ICS210-05**: If status is "O/S" (Out of Service), a reason should be indicated (Mechanical, Rest, Personnel)
6. **R-ICS210-06**: If "O/S" status includes ETR (Estimated Time of Return), it should be provided
7. **R-ICS210-07**: Time and Date of Change must be a valid date/time
8. **R-ICS210-08**: Prepared By must include at minimum a name, position/title, and signature

### Form Lifecycle Rules

1. **L-ICS210-01**: The form is completed by radio/telephone operators who receive status change information
2. **L-ICS210-02**: Status change information may be received from individual resources, Task Forces, Strike Teams, and Division/Group Supervisors
3. **L-ICS210-03**: Status information may also be reported by Staging Area and Helibase Managers and fixed-wing facilities
4. **L-ICS210-04**: The completed form is maintained by the Communications Unit and copied to Resources Unit
5. **L-ICS210-05**: Original forms must be filed by the Documentation Unit
6. **L-ICS210-06**: The form is used to update Resource Status Cards or T-Cards (ICS 219) for incident-level resource management

### Conditional Requirements

1. **C-ICS210-01**: If a resource is marked "O/S" (Out of Service), the reason should be specified (e.g., "O/S - Mech", "O/S - Rest", "O/S - Pers")
2. **C-ICS210-02**: If ETR (Estimated Time of Return) is known for an out-of-service resource, it should be indicated
3. **C-ICS210-03**: If additional pages are needed, a blank ICS 210 can be used and repaginated
4. **C-ICS210-04**: If multiple locations are used (multiple Divisions, Staging Areas, or Camps), the specific location should be identified

## 4. User Interface Layout

### Section Definitions

1. **Header Section** - Contains incident identification and operational period
2. **Resource Status Change Section** - Tabular listing of resource status changes
3. **Comments Section** - Additional information about status changes
4. **Footer Section** - Contains prepared by information

### Layout Specifications

- The form is designed as a one-page document, possibly extending to multiple pages if needed
- Resource Status Change section should be displayed as a table with multiple rows
- Comments section should provide adequate space for additional notes
- Each row in the status change table should clearly indicate the change in status/location

### Field Groupings

- Incident identification fields grouped together in the header
- Operational period fields (from/to) grouped together
- Resource status change information grouped in rows
- Each status change includes resource identifier, status change details, and timing information

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 210 form
2. **Update** - Add additional status changes to an existing form
3. **Print** - Generate a printable version of the form
4. **Share** - Distribute the form electronically (particularly to Resources Unit)
5. **Use as Worksheet** - Operations personnel may use as a tracking worksheet

### State Transitions

1. **Draft** → **Completed**: When the form is filled in by Communications Center personnel
2. **Completed** → **Transmitted**: When copied to Resources Unit
3. **Transmitted** → **Recorded**: When status changes are updated on Resource Status Cards
4. **Recorded** → **Archived**: When filed by Documentation Unit
5. **Any State** → **Updated**: When additional status changes are added

### Access Control

1. Incident Communications Center Manager: Create, Update
2. Radio/Telephone Operators: Create, Update
3. Resources Unit: View, Update resource status records
4. Operations Section Personnel: View, Use as worksheet
5. Documentation Unit: Archive

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, times, and status enumerations
2. Must maintain chronological order of status changes
3. Should preserve all versions throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data
6. Should maintain relationship to resource management system

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Must maintain consistent formatting across printed pages
3. Should support export to PDF and other common formats
4. Should support integration with messaging systems (e.g., ICS 213)
5. Should support compilation of status changes for reporting purposes

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Should support rapid entry of status changes during high-volume communication periods
3. Should provide clear indication of current status vs. new status
4. Should validate proper status values and provide pick lists
5. Should support timestamp automation where possible
6. Should alert users to potentially conflicting status information

### Integration Requirements

1. Should integrate with Resource Status Cards (ICS 219)
2. Should integrate with General Message form (ICS 213)
3. Should enable pre-population of incident information from existing data
4. Should support integration with resource tracking systems
5. Should allow for compilation of status changes by resource
6. Should support real-time synchronization with resource tracking displays

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should support batch entry of multiple status changes
4. Should include version control for updates
5. Must comply with accessibility standards
6. Should enable collaborative editing with appropriate access controls
7. Must maintain data integrity during concurrent access
8. Should support voice-to-text or other rapid entry methods for busy communications centers
9. Should provide status change history for each resource
