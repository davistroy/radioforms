# ICS 215 - Operational Planning Worksheet Analysis

## 1. Form Overview

### Form Name
ICS 215 - Operational Planning Worksheet

### Purpose
The Operational Planning Worksheet communicates the decisions made by the Operations Section Chief during the Tactics Meeting concerning resource assignments and needs for the next operational period. It is used by the Resources Unit to complete the Assignment Lists (ICS 204) and by the Logistics Section Chief for ordering resources for the incident.

### Primary Users
- Operations Section Chief (preparer)
- Planning Section Chief
- Logistics Section Chief
- Resources Unit Leader
- Situation Unit Leader
- Safety Officer
- Division/Group Supervisors
- Branch Directors

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics215_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics215_operational_period | Operational Period | Complex | Yes | Valid date/time range | Time interval for which the form applies |
| ics215_branch_divisions | Branch and Divisions | Complex | Yes | - | Branch and divisions or groups for work assignments |
| ics215_resources | Resources | Complex | Yes | - | Resource requirements and availability |
| ics215_prepared_by | Prepared By | Complex | Yes | - | Information about the person preparing the form |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics215_form_version | Form Version | Text | No | - | Version of the ICS 215 form being used |
| ics215_prepared_date_time | Preparation Date/Time | DateTime | Yes | Valid date/time | Date and time the form was prepared |

### Repeatable Section Fields - Branch and Divisions

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics215_branch | Branch | Text | No | - | Branch name or identifier |
| ics215_division_group | Division, Group, or Other | Text | Yes | - | Division, Group or other location identifier |
| ics215_work_assignment | Work Assignment & Special Instructions | Text | Yes | Multi-line | Specific tasks and special instructions |

### Repeatable Section Fields - Resources

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics215_resource_type | Resource | Text | Yes | - | Category, kind, type of resource |
| ics215_resource_required | Required | Number | Yes | Non-negative | Number of resources required for assignment |
| ics215_resource_have | Have | Number | Yes | Non-negative | Number of resources available for assignment |
| ics215_resource_need | Need | Number | Yes | Non-negative | Number of additional resources needed |
| ics215_overhead_positions | Overhead Position(s) | Text | No | - | Supervisory positions not assigned to specific resources |
| ics215_special_equipment | Special Equipment & Supplies | Text | No | - | Special equipment/supplies needed for assignment |
| ics215_reporting_location | Reporting Location | Text | Yes | - | Where the resources should report |
| ics215_requested_arrival_time | Requested Arrival Time | Time | Yes | Valid time | When resources should arrive at location |

### Total Resources Section

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics215_total_resources_required | Total Resources Required | Number | Yes | Non-negative | Total number of resources required by category |
| ics215_total_resources_have | Total Resources Have on Hand | Number | Yes | Non-negative | Total number of resources available by category |
| ics215_total_resources_need | Total Resources Need To Order | Number | Yes | Non-negative | Total number of resources needed by category |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS215-01**: Incident Name must be provided
2. **R-ICS215-02**: Operational Period must be a valid date/time range
3. **R-ICS215-03**: At least one Division/Group must be specified with work assignment
4. **R-ICS215-04**: For each resource entry, Required, Have, and Need values must be provided
5. **R-ICS215-05**: For each resource category, Need = Required - Have
6. **R-ICS215-06**: Requested Arrival Time must be within the Operational Period
7. **R-ICS215-07**: Total Resources calculations must be accurate for each category
8. **R-ICS215-08**: Prepared By must include at minimum a name, position/title, and signature

### Form Lifecycle Rules

1. **L-ICS215-01**: The form is initiated by the Operations Section Chief during the Tactics Meeting
2. **L-ICS215-02**: The form is shared with the Command and General Staff during the Planning Meeting
3. **L-ICS215-03**: When assignments and resource allocations are agreed upon, the form is distributed to the Resources Unit
4. **L-ICS215-04**: The Resources Unit uses the form to prepare the Assignment Lists (ICS 204)
5. **L-ICS215-05**: The Logistics Section uses a copy for preparing resource requests
6. **L-ICS215-06**: All completed original forms must be given to the Documentation Unit

### Conditional Requirements

1. **C-ICS215-01**: If more than one Branch is used, clearly identify which Divisions/Groups belong to each Branch
2. **C-ICS215-02**: If a Strike Team or Task Force is to be created, indicate this in the resource area
3. **C-ICS215-03**: If additional pages are needed, use blank ICS 215 forms and repaginate as needed
4. **C-ICS215-04**: If special equipment or supplies are needed, specify in the designated field

## 4. User Interface Layout

### Section Definitions

1. **Header Section** - Contains incident identification and operational period
2. **Divisions and Work Assignments Section** - Lists divisions/groups and associated work assignments
3. **Resources Section** - Matrix of resource allocations by division/group
4. **Totals Section** - Summation of resource requirements and availability
5. **Footer Section** - Contains prepared by information

### Layout Specifications

- The form is designed as a one-page worksheet, possibly extending to multiple pages if needed
- Available in standard 8.5" x 11" format, as well as optional 8.5" x 14" (legal) and 11" x 17" formats
- Matrix design with divisions/work assignments listed vertically on the left
- Resource categories displayed horizontally across the top
- Resource requirements, availability, and needs displayed in cells of the matrix
- Totals calculated at the bottom of each resource column

### Field Groupings

- Incident identification fields grouped together in the header
- Operational period fields (from/to) grouped together
- Branch and Division/Group information grouped vertically
- Resource categorizations grouped horizontally
- Resource quantities (Required, Have, Need) grouped in sets of three
- Special resource requirements grouped together
- Totals grouped at the bottom of the worksheet

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 215 form during Tactics Meeting
2. **Update** - Modify resource allocations during Planning Meeting
3. **Calculate** - Determine resource needs based on requirements and availability
4. **Print** - Generate a printable version of the form
5. **Share** - Distribute to Resources Unit and Logistics Section
6. **Wall Mount** - Optionally display as a wall chart during meetings

### State Transitions

1. **Draft** → **Completed**: When the Operations Section Chief finalizes assignments and needs
2. **Completed** → **Agreed Upon**: When Command and General Staff concur during Planning Meeting
3. **Agreed Upon** → **Distributed**: When provided to Resources Unit and Logistics
4. **Distributed** → **Implemented**: When used to create ICS 204 forms and order resources
5. **Implemented** → **Archived**: When filed by Documentation Unit

### Access Control

1. Operations Section Chief: Create, Update
2. Command and General Staff: Review, Provide Input
3. Resources Unit: View, Use for Assignment Lists
4. Logistics Section: View, Use for Resource Ordering
5. Documentation Unit: Archive

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, times, and numeric values
2. Must maintain relationships between divisions and resource allocations
3. Should preserve all versions throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data
6. Should maintain calculation logic for resource needs

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Should support alternative sizes (8.5" x 14", 11" x 17")
3. Should support export to PDF and other common formats
4. Should maintain the matrix structure in all output formats
5. Should facilitate wall-mounted displays for meetings

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Should support matrix-style data entry with calculated fields
3. Should provide resource calculation automation
4. Should support rapid entry of division/group assignments
5. Should enable easy addition of resource categories
6. Should provide visual indicators for resource shortfalls

### Integration Requirements

1. Must integrate with Assignment Lists (ICS 204)
2. Should integrate with resource ordering systems
3. Should enable pre-population of incident information from existing data
4. Should support integration with Incident Action Plan Safety Analysis (ICS 215A)
5. Should allow for resource allocation visualization
6. Should support integration with resource tracking systems

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should support collaborative editing during meetings
4. Should include version control for updates
5. Must comply with accessibility standards
6. Should provide calculation validation
7. Must maintain data integrity during concurrent access
8. Should support large-format display for tactics meetings
9. Should provide templates for common incident types
