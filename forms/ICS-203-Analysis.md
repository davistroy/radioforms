# ICS 203 - Organization Assignment List Analysis

## 1. Form Overview

### Form Name
ICS 203 - Organization Assignment List

### Purpose
The Organization Assignment List provides information on the personnel staffing each position within the Incident Command System structure. It documents the current incident organization and is used to complete the Incident Organization Chart (ICS 207), which is posted on the Incident Command Post display.

### Primary Users
- Resources Unit Leader (preparer)
- Planning Section Chief (overseer)
- Incident Command and General Staff
- All supervisory personnel

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics203_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics203_operational_period | Operational Period | Complex | Yes | Valid date/time range | Time interval for which the form applies |
| ics203_incident_command | Incident Commander(s) and Command Staff | Complex | Yes | - | Personnel assigned to Command positions |
| ics203_agency_representatives | Agency/Organization Representatives | Complex | No | - | Representatives from other agencies |
| ics203_planning_section | Planning Section | Complex | No | - | Personnel assigned to Planning Section positions |
| ics203_logistics_section | Logistics Section | Complex | No | - | Personnel assigned to Logistics Section positions |
| ics203_operations_section | Operations Section | Complex | No | - | Personnel assigned to Operations Section positions |
| ics203_finance_section | Finance/Administration Section | Complex | No | - | Personnel assigned to Finance/Admin Section positions |
| ics203_prepared_by | Prepared By | Complex | Yes | - | Information about the person preparing the form |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics203_form_version | Form Version | Text | No | - | Version of the ICS 203 form being used |
| ics203_prepared_date_time | Preparation Date/Time | DateTime | Yes | Valid date/time | Date and time the form was prepared |
| ics203_iap_page_number | IAP Page Number | Text | Yes | Format: "IAP Page ___" | Page number within the IAP |

### Repeatable Section Fields - Command Staff

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics203_ic_name | IC/UC Name | Text | Yes | - | Name of Incident Commander or Unified Commander |
| ics203_deputy_name | Deputy Name | Text | No | - | Name of Deputy Incident Commander |
| ics203_safety_officer_name | Safety Officer Name | Text | No | - | Name of Safety Officer |
| ics203_public_info_officer_name | Public Info Officer Name | Text | No | - | Name of Public Information Officer |
| ics203_liaison_officer_name | Liaison Officer Name | Text | No | - | Name of Liaison Officer |

### Repeatable Section Fields - Agency Representatives

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics203_agency_org_name | Agency/Organization Name | Text | No | - | Name of represented agency or organization |
| ics203_representative_name | Representative Name | Text | No | - | Name of agency/organization representative |

### Repeatable Section Fields - Planning Section

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics203_planning_chief_name | Chief Name | Text | No | - | Name of Planning Section Chief |
| ics203_planning_deputy_name | Deputy Name | Text | No | - | Name of Deputy Planning Section Chief |
| ics203_resources_unit_leader_name | Resources Unit Leader Name | Text | No | - | Name of Resources Unit Leader |
| ics203_situation_unit_leader_name | Situation Unit Leader Name | Text | No | - | Name of Situation Unit Leader |
| ics203_documentation_unit_leader_name | Documentation Unit Leader Name | Text | No | - | Name of Documentation Unit Leader |
| ics203_demobilization_unit_leader_name | Demobilization Unit Leader Name | Text | No | - | Name of Demobilization Unit Leader |
| ics203_technical_specialists_names | Technical Specialists Names | Text | No | Multi-line | Names of Technical Specialists |

### Repeatable Section Fields - Logistics Section

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics203_logistics_chief_name | Chief Name | Text | No | - | Name of Logistics Section Chief |
| ics203_logistics_deputy_name | Deputy Name | Text | No | - | Name of Deputy Logistics Section Chief |
| ics203_support_branch_director_name | Support Branch Director Name | Text | No | - | Name of Support Branch Director |
| ics203_supply_unit_leader_name | Supply Unit Leader Name | Text | No | - | Name of Supply Unit Leader |
| ics203_facilities_unit_leader_name | Facilities Unit Leader Name | Text | No | - | Name of Facilities Unit Leader |
| ics203_ground_support_unit_leader_name | Ground Support Unit Leader Name | Text | No | - | Name of Ground Support Unit Leader |
| ics203_service_branch_director_name | Service Branch Director Name | Text | No | - | Name of Service Branch Director |
| ics203_communications_unit_leader_name | Communications Unit Leader Name | Text | No | - | Name of Communications Unit Leader |
| ics203_medical_unit_leader_name | Medical Unit Leader Name | Text | No | - | Name of Medical Unit Leader |
| ics203_food_unit_leader_name | Food Unit Leader Name | Text | No | - | Name of Food Unit Leader |

### Repeatable Section Fields - Operations Section

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics203_operations_chief_name | Chief Name | Text | No | - | Name of Operations Section Chief |
| ics203_operations_deputy_name | Deputy Name | Text | No | - | Name of Deputy Operations Section Chief |
| ics203_staging_area_name | Staging Area Name | Text | No | - | Name of Staging Area Manager |
| ics203_branch_name | Branch Name | Text | No | - | Name of Branch (e.g., Branch 1) |
| ics203_branch_director_name | Branch Director Name | Text | No | - | Name of Branch Director |
| ics203_branch_deputy_name | Branch Deputy Name | Text | No | - | Name of Deputy Branch Director |
| ics203_division_group_name | Division/Group Name | Text | No | - | Name of Division or Group |
| ics203_division_group_supervisor_name | Division/Group Supervisor Name | Text | No | - | Name of Division/Group Supervisor |
| ics203_air_ops_branch_director_name | Air Operations Branch Director Name | Text | No | - | Name of Air Operations Branch Director |

### Repeatable Section Fields - Finance/Administration Section

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics203_finance_chief_name | Chief Name | Text | No | - | Name of Finance/Administration Section Chief |
| ics203_finance_deputy_name | Deputy Name | Text | No | - | Name of Deputy Finance/Administration Chief |
| ics203_time_unit_leader_name | Time Unit Leader Name | Text | No | - | Name of Time Unit Leader |
| ics203_procurement_unit_leader_name | Procurement Unit Leader Name | Text | No | - | Name of Procurement Unit Leader |
| ics203_comp_claims_unit_leader_name | Compensation/Claims Unit Leader Name | Text | No | - | Name of Compensation/Claims Unit Leader |
| ics203_cost_unit_leader_name | Cost Unit Leader Name | Text | No | - | Name of Cost Unit Leader |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS203-01**: Incident Name must be provided
2. **R-ICS203-02**: Operational Period must be a valid date/time range
3. **R-ICS203-03**: At least one Incident Commander must be listed
4. **R-ICS203-04**: Prepared By must include at minimum a name, position/title, and signature
5. **R-ICS203-05**: If a Section has personnel listed, the Section Chief should be identified
6. **R-ICS203-06**: If multiple individuals occupy the same position, they should be separated by slashes
7. **R-ICS203-07**: For Unified Command, agency names should be included with IC names

### Form Lifecycle Rules

1. **L-ICS203-01**: The form is created by the Resources Unit under the direction of the Planning Section Chief
2. **L-ICS203-02**: The form is updated as personnel assignments change
3. **L-ICS203-03**: The form is duplicated and attached to the ICS 202 as part of the IAP
4. **L-ICS203-04**: The form is distributed to all recipients of the IAP
5. **L-ICS203-05**: All completed original forms must be given to the Documentation Unit
6. **L-ICS203-06**: A new ICS 203 is created for each operational period

### Conditional Requirements

1. **C-ICS203-01**: If personnel change during an operational period, the form should be updated
2. **C-ICS203-02**: If additional space is needed for any section, a blank ICS 203 can be used and repaginated
3. **C-ICS203-03**: If the Intelligence/Investigations Function is activated, it can be placed in different locations in the organization structure and should be documented appropriately

## 4. User Interface Layout

### Section Definitions

1. **Header Section** - Contains incident identification and operational period
2. **Command Staff Section** - Lists Incident Commanders and Command Staff members
3. **Agency Representatives Section** - Lists representatives from participating agencies
4. **Planning Section** - Lists Planning Section personnel
5. **Logistics Section** - Lists Logistics Section personnel, divided into Support and Service Branches
6. **Operations Section** - Lists Operations Section personnel, arranged hierarchically by Branch, Division/Group
7. **Finance/Admin Section** - Lists Finance/Administration Section personnel
8. **Footer Section** - Contains prepared by information

### Layout Specifications

- The form is designed as a one-page document, possibly extending to multiple pages
- Each section is clearly labeled and separated from others
- Personnel names should be aligned for easy reading
- Operations Section should accommodate multiple Branches and Divisions/Groups
- For Unified Command, space is needed for multiple Incident Commanders with agency identifiers

### Field Groupings

- Incident identification fields grouped together in the header
- Operational period fields (from/to) grouped together
- Command Staff positions grouped together
- Each Section's personnel grouped separately
- Operations Branch personnel grouped by Branch and Division/Group
- Logistics personnel grouped by Support Branch and Service Branch

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 203 form
2. **Update** - Modify information on an existing form
3. **Print** - Generate a printable version of the form
4. **Share** - Distribute the form electronically
5. **Include in IAP** - Add to complete Incident Action Plan package
6. **Generate ICS 207** - Use information to create the Incident Organization Chart

### State Transitions

1. **Draft** → **Active**: When the form is completed by Resources Unit Leader
2. **Active** → **Updated**: When personnel assignments change
3. **Active/Updated** → **Published**: When included in distributed IAP
4. **Published** → **Archived**: When the operational period ends
5. **Any State** → **Superseded**: When replaced by a new version

### Access Control

1. Resources Unit Leader: Create, Update, Print
2. Planning Section Chief: Update, Approve
3. Command and General Staff: View, Suggest Updates
4. Documentation Unit: Archive
5. IAP Recipients: View

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, and times
2. Must maintain relationship with other IAP components
3. Must preserve all versions throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data
6. Should maintain historical record of personnel assignments

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Must maintain consistent formatting across printed pages
3. Should support export to PDF and other common formats
4. Should support various output formats for inclusion in the IAP

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Should support quick entry of personnel names and positions
3. Should provide organizational chart visualization capability
4. Should provide real-time validation of entered data
5. Should accommodate various organizational structures
6. Should provide templates for common ICS configurations

### Integration Requirements

1. Must integrate with ICS 207 to generate organization charts
2. Should enable pre-population of incident information from existing data
3. Should enable sharing of personnel assignments with other forms
4. Must support integration with other IAP components
5. Should allow for data exchange with resource management systems

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should include version control for form updates
4. Must comply with accessibility standards
5. Should enable collaborative editing with appropriate access controls
6. Must maintain data integrity during concurrent access
7. Should support rapid assembly of IAP components
