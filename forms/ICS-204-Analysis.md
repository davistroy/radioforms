# ICS 204 - Assignment List Analysis

## 1. Form Overview

### Form Name
ICS 204 - Assignment List

### Purpose
The Assignment List informs Division and Group supervisors of incident assignments. It details specific tactical work assignments, resources, and supporting information needed to safely and efficiently accomplish specific operational tasks for each operational period.

### Primary Users
- Resources Unit Leader (preparer)
- Operations Section Chief (reviewer)
- Planning Section Chief (reviewer)
- Incident Commander (approver)
- Division/Group Supervisors (end users)
- Branch Directors
- Task Force/Strike Team Leaders

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics204_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics204_operational_period | Operational Period | Complex | Yes | Valid date/time range | Time interval for which the form applies |
| ics204_branch | Branch | Text | No | Max 50 chars | Branch name (if applicable) |
| ics204_division_group | Division/Group | Text | Yes | Max 50 chars | Division/Group identifier |
| ics204_staging_area | Staging Area | Text | No | Max 50 chars | Staging area name (if applicable) |
| ics204_operations_personnel | Operations Personnel | Complex | Yes | - | Key operations personnel information |
| ics204_work_assignments | Work Assignments | Text | Yes | Multi-line | Specific tasks to be accomplished |
| ics204_special_instructions | Special Instructions | Text | No | Multi-line | Safety messages, specific precautions, etc. |
| ics204_communications | Communications | Complex | No | - | Radio and phone information for the assignment |
| ics204_prepared_by | Prepared By | Complex | Yes | - | Information about the person preparing the form |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics204_form_version | Form Version | Text | No | - | Version of the ICS 204 form being used |
| ics204_prepared_date_time | Preparation Date/Time | DateTime | Yes | Valid date/time | Date and time the form was prepared |
| ics204_iap_page_number | IAP Page Number | Text | Yes | Format: "IAP Page ___" | Page number within the IAP |

### Repeatable Section Fields - Operations Personnel

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics204_operations_chief | Operations Section Chief | Text | No | - | Name of Operations Section Chief |
| ics204_branch_director | Branch Director | Text | No | - | Name of Branch Director |
| ics204_division_group_supervisor | Division/Group Supervisor | Text | Yes | - | Name of Division/Group Supervisor |

### Repeatable Section Fields - Resources Assigned

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics204_resource_identifier | Resource Identifier | Text | No | Max 50 chars | ID for the assigned resource |
| ics204_resource_leader | Leader | Text | No | Max 50 chars | Name of Resource Leader |
| ics204_num_persons | # of Persons | Number | No | Positive integer | Number of persons assigned to resource |
| ics204_contact_info | Contact (e.g., phone, pager, radio) | Text | No | - | Primary contact method/information |
| ics204_reporting_location | Reporting Location | Text | No | - | Where resource should report |
| ics204_resource_notes | Notes | Text | No | Multi-line | Special equipment, supplies, remarks, etc. |

### Repeatable Section Fields - Communications

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics204_name_function | Name/Function | Text | No | - | Name and/or function of person/role |
| ics204_primary_contact | Primary Contact | Text | No | - | Cell, pager, radio frequency, etc. |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS204-01**: Incident Name must be provided
2. **R-ICS204-02**: Operational Period must be a valid date/time range
3. **R-ICS204-03**: Division/Group must be specified
4. **R-ICS204-04**: Work Assignments must be provided
5. **R-ICS204-05**: Division/Group Supervisor name must be provided
6. **R-ICS204-06**: Prepared By must include at minimum a name, position/title, and signature
7. **R-ICS204-07**: If resources are assigned, at least one resource must be described

### Form Lifecycle Rules

1. **L-ICS204-01**: The form is normally prepared by the Resources Unit during the action planning process
2. **L-ICS204-02**: The form must be approved by the Incident Commander, but may be reviewed and initialed by the Planning Section Chief and Operations Section Chief
3. **L-ICS204-03**: The form is duplicated and attached to the ICS 202 as part of the IAP
4. **L-ICS204-04**: The form is distributed to all recipients of the IAP
5. **L-ICS204-05**: Original completed forms must be given to the Documentation Unit
6. **L-ICS204-06**: A new ICS 204 is created for each Division/Group for each operational period
7. **L-ICS204-07**: In some cases, assignments may be communicated via radio/telephone/fax

### Conditional Requirements

1. **C-ICS204-01**: If a Staging Area is specified, appropriate resources should be assigned to it
2. **C-ICS204-02**: If multiple pages are needed, use a blank ICS 204 and repaginate as needed
3. **C-ICS204-03**: If emergency communications are required, specific instructions should be provided in the Special Instructions section
4. **C-ICS204-04**: If there are safety concerns specific to the assignment, they should be noted in the Special Instructions section

## 4. User Interface Layout

### Section Definitions

1. **Header Section** - Contains incident identification, operational period, and assignment identification
2. **Operations Personnel Section** - Lists key supervisory personnel
3. **Resources Section** - Tabular listing of assigned resources and details
4. **Work Assignments Section** - Detailed description of tasks to accomplish
5. **Special Instructions Section** - Safety messages and other special needs
6. **Communications Section** - Contact information for assignment personnel
7. **Footer Section** - Contains prepared by information

### Layout Specifications

- The form is designed as a one-page document per Division/Group
- Resources Section should be displayed as a table with multiple rows
- Communications Section should be displayed as a table with multiple rows
- Work Assignments section should have ample space for detailed instructions
- Special Instructions section should support multiple paragraphs

### Field Groupings

- Incident identification fields grouped together in the header
- Operational period fields (from/to) grouped together
- Operations personnel grouped together
- Resource information grouped in rows in the Resources table
- Communications information grouped in rows in the Communications table

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 204 form
2. **Update** - Modify information on an existing form
3. **Approve** - Obtain necessary signatures and approvals
4. **Print** - Generate a printable version of the form
5. **Share** - Distribute the form electronically
6. **Include in IAP** - Add to complete Incident Action Plan package

### State Transitions

1. **Draft** → **Reviewed**: When the form is reviewed by Operations Section Chief
2. **Reviewed** → **Approved**: When approved by Incident Commander
3. **Approved** → **Published**: When included in distributed IAP
4. **Published** → **Archived**: When the operational period ends
5. **Any State** → **Superseded**: When replaced by a new version for the same Division/Group

### Access Control

1. Resources Unit Leader: Create, Update, Print
2. Operations Section Chief: Review, Update
3. Planning Section Chief: Review
4. Incident Commander: Approve
5. Division/Group Supervisors: View
6. Documentation Unit: Archive

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, times, and numeric values
2. Must maintain relationship with other IAP components
3. Must preserve all versions throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data
6. Should maintain linkage between assignments and resources

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Must maintain consistent formatting across printed pages
3. Should support export to PDF and other common formats
4. Should support various output formats for inclusion in the IAP
5. Should support printing of multiple Division/Group assignments in sequence

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Should support quick entry of resource information
3. Should provide templates for common assignment types
4. Should provide real-time validation of entered data
5. Must clearly indicate required fields
6. Should support rapid duplication for similar assignments

### Integration Requirements

1. Should integrate with resource management systems
2. Should enable pre-population of incident information from ICS 201 or ICS 202
3. Should enable pre-population of resource information from ICS 203
4. Must support integration with other IAP components
5. Should support radio communications plan integration (ICS 205)

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should support digital signatures for approval fields
4. Should include version control for assignment updates
5. Must comply with accessibility standards
6. Should enable collaborative editing with appropriate access controls
7. Must maintain data integrity during concurrent access
8. Should provide a mechanism for urgent updates and distribution
