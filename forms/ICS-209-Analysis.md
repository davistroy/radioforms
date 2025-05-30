# ICS 209 - Incident Status Summary Analysis

## 1. Form Overview

### Form Name
ICS 209 - Incident Status Summary

### Purpose
The Incident Status Summary provides decision makers with basic information about an incident situation and the resources allocated to it. The ICS 209 is designed to report significant incident status and operational information to incident management entities above the incident level, including the agency having jurisdiction and other multiagency coordination system (MACS) elements.

### Primary Users
- Situation Unit Leader/Planning Section Chief (preparers)
- Incident Commander/Unified Command (approvers)
- Agency administrators
- Multiagency Coordination Centers
- Emergency Operations Centers
- Agency dispatch centers
- Regional/geographic area command centers

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics209_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics209_incident_number | Incident Number | Text | No | Max 50 chars | Number assigned to the incident |
| ics209_report_version | Report Version | Enum | Yes | Initial/Update/Final | Indicates current version of the ICS 209 being submitted |
| ics209_report_number | Report # | Number | No | Positive integer | Report sequence number, if used |
| ics209_incident_commander | Incident Commander(s) & Agency or Organization | Text | Yes | - | Names and agencies of Incident Commander(s) |
| ics209_incident_management_org | Incident Management Organization | Text | No | - | Type of incident management organization (Type 1-3 IMT, UC, etc.) |
| ics209_incident_start_datetime | Incident Start Date/Time | DateTime | Yes | Valid date/time | When the incident began |
| ics209_incident_size_area | Current Incident Size or Area Involved | Text | No | - | Size or area with appropriate units |
| ics209_percent_contained | Percent (%) Contained/Completed | Number | No | 0-100 | Percentage of containment or completion |
| ics209_incident_definition | Incident Definition | Text | Yes | - | General definition of the incident |
| ics209_incident_complexity | Incident Complexity Level | Text | No | - | The complexity level of the incident |
| ics209_time_period | For Time Period | Complex | Yes | Valid date/time range | Time interval covered by this report |
| ics209_approval_routing | Approval and Routing Information | Complex | Yes | - | Information on preparation, approval, and submission |
| ics209_incident_location | Incident Location Information | Complex | Yes | - | Geographic location details of the incident |
| ics209_incident_summary | Incident Summary | Complex | Yes | - | Summary information about the incident situation |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics209_form_version | Form Version | Text | No | - | Version of the ICS 209 form being used |
| ics209_prepared_date_time | Preparation Date/Time | DateTime | Yes | Valid date/time | Date and time the form was prepared |
| ics209_submitted_date_time | Submission Date/Time | DateTime | Yes | Valid date/time | Date and time the form was submitted |
| ics209_sensitivity | Contains Sensitive Information | Boolean | No | Yes/No | Indicates if the form contains sensitive content |

### Repeatable Section Fields - Incident Location Information

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics209_state | State | Text | Yes* | - | State where incident originated |
| ics209_county | County/Parish/Borough | Text | Yes* | - | County/Parish/Borough where incident originated |
| ics209_city | City | Text | Yes* | - | City where incident originated |
| ics209_unit | Unit or Other | Text | No | - | Unit, sub-unit, or additional identifier |
| ics209_incident_jurisdiction | Incident Jurisdiction | Text | Yes* | - | Primary jurisdiction having responsibility for the incident |
| ics209_incident_location_ownership | Incident Location Ownership | Text | No | - | Ownership of the area where incident originated |
| ics209_longitude_latitude | Longitude/Latitude | Text | No | - | Geographic coordinates of the incident |
| ics209_us_national_grid | US National Grid Reference | Text | No | - | USNG reference of incident origin |
| ics209_legal_description | Legal Description | Text | No | - | Township, section, range information |
| ics209_short_location | Short Location or Area Description | Text | Yes | - | Brief description of incident location |
| ics209_utm_coordinates | UTM Coordinates | Text | No | - | Universal Transverse Mercator coordinates |
| ics209_geospatial_data | Electronic Geospatial Data | Text | No | - | Information about attached geospatial data |

### Repeatable Section Fields - Incident Summary

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics209_significant_events | Significant Events for the Time Period Reported | Text | Yes | Multi-line | Summary of significant progress, events, issues |
| ics209_primary_materials | Primary Materials or Hazards Involved | Text | No | - | Hazardous chemicals, fuel types, infectious agents, etc. |
| ics209_damage_assessment | Damage Assessment Information | Complex | No | - | Summary of damage to property or resources |

### Repeatable Section Fields - Additional Incident Decision Support Information

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics209_public_status | Public Status Summary | Complex | No | - | Information about civilians affected by the incident |
| ics209_responder_status | Responder Status Summary | Complex | No | - | Information about responders affected by the incident |
| ics209_life_safety | Life, Safety, and Health Status/Threat | Complex | No | - | Information about life safety issues |
| ics209_weather | Weather Concerns | Text | No | Multi-line | Synopsis of current and predicted weather |
| ics209_projected_activity | Projected Incident Activity, Potential, Movement, Escalation, or Spread | Text | No | Multi-line | Expected incident evolution in various timeframes |
| ics209_strategic_objectives | Strategic Objectives | Text | No | Multi-line | Defined planned end-state for the incident |
| ics209_current_threat | Current Incident Threat Summary and Risk Information | Text | No | Multi-line | Primary threats to life, property, communities, etc. |
| ics209_critical_resource_needs | Critical Resource Needs | Text | No | Multi-line | Specific resources needed in various timeframes |
| ics209_strategic_discussion | Strategic Discussion | Text | No | Multi-line | Explanation of overall strategy and concerns |
| ics209_planned_actions | Planned Actions for Next Operational Period | Text | No | Multi-line | Summary of actions planned for next period |
| ics209_projected_final_size | Projected Final Incident Size/Area | Text | No | - | Estimate of total area likely to be involved |
| ics209_anticipated_completion | Anticipated Incident Management Completion Date | Date | No | Valid date | Expected date when incident objectives will be met |
| ics209_projected_demob | Projected Significant Resource Demobilization Start Date | Date | No | Valid date | When significant demobilization may begin |
| ics209_estimated_costs | Estimated Incident Costs to Date | Currency | No | - | Estimated total incident costs to date |
| ics209_projected_final_costs | Projected Final Incident Cost Estimate | Currency | No | - | Estimate of total costs for the incident |
| ics209_remarks | Remarks | Text | No | Multi-line | Additional information or continuation of any blocks |

### Repeatable Section Fields - Incident Resource Commitment Summary

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics209_agency_organization | Agency or Organization | Text | No | - | Contributing agency/organization name |
| ics209_resources | Resources | Complex | No | - | Resources by category/kind/type with personnel counts |
| ics209_additional_personnel | Additional Personnel | Number | No | Non-negative | Personnel not assigned to a resource |
| ics209_total_personnel | Total Personnel | Number | No | Non-negative | Total personnel for the agency/organization |
| ics209_additional_cooperating | Additional Cooperating and Assisting Organizations Not Listed Above | Text | No | - | Other organizations providing support |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS209-01**: Incident Name must be provided
2. **R-ICS209-02**: Report Version must be specified (Initial, Update, or Final)
3. **R-ICS209-03**: Incident Commander(s) name and agency must be provided
4. **R-ICS209-04**: Incident Start Date/Time must be a valid date and time
5. **R-ICS209-05**: Time Period for the report must be specified with valid dates/times
6. **R-ICS209-06**: Incident Definition must be provided
7. **R-ICS209-07**: At least one incident location field (State, County, City, etc.) must be completed
8. **R-ICS209-08**: Short Location Description must be provided
9. **R-ICS209-09**: Significant Events for the Time Period must be provided
10. **R-ICS209-10**: Approval information must include name, position/title, and signature
11. **R-ICS209-11**: If Final report is checked, both Initial and Final should be checked
12. **R-ICS209-12**: Do not estimate any fatality information in status summaries
13. **R-ICS209-13**: If geospatial data is included, it should be simple (small file size)

### Form Lifecycle Rules

1. **L-ICS209-01**: The form is typically prepared by the Situation Unit Leader or Planning Section Chief
2. **L-ICS209-02**: The form must be approved by appropriate overhead (typically Planning Section Chief)
3. **L-ICS209-03**: The form is submitted according to jurisdiction or discipline-specific reporting requirements
4. **L-ICS209-04**: An initial ICS 209 is submitted when the incident reaches a pre-designated significance level
5. **L-ICS209-05**: Updates are typically submitted once daily or for each operational period
6. **L-ICS209-06**: A final ICS 209 is submitted when the incident requires only minor support
7. **L-ICS209-07**: All completed original forms must be given to the Documentation Unit
8. **L-ICS209-08**: Sensitive information should be handled with appropriate security measures

### Conditional Requirements

1. **C-ICS209-01**: If "Initial" report version is checked and this is the final report, also check "Final"
2. **C-ICS209-02**: If "Report #" is used, follow the existing protocol for the jurisdiction
3. **C-ICS209-03**: If percent contained is provided, indicate if it's an estimate
4. **C-ICS209-04**: If there are fatalities, clear notifications must be made prior to form submission
5. **C-ICS209-05**: If precise geospatial information is included, clearly label the data format
6. **C-ICS209-06**: If an incident is in multiple jurisdictions, provide appropriate breakdown
7. **C-ICS209-07**: If resource numbers are estimates, indicate this in the form

## 4. User Interface Layout

### Section Definitions

1. **Header Information Section** - Contains basic incident identification (Page 1-4)
2. **Approval and Routing Section** - Information on preparation and approval (Page 1)
3. **Incident Location Section** - Detailed information about incident location (Page 1)
4. **Incident Summary Section** - Significant events and current situation (Page 1)
5. **Public and Responder Status Section** - Information on people affected (Page 2)
6. **Life Safety Section** - Current threats to life and safety (Page 2)
7. **Incident Projection Section** - Projected activity and planned actions (Pages 2-3)
8. **Resource Summary Section** - Detailed resource commitment information (Page 4)

### Layout Specifications

- The form is designed as a multi-page document (typically 4 pages)
- Resource Summary page can be duplicated if needed for multiple resources
- Each page should be clearly numbered and reference the incident
- Tables should be used for structured data like personnel counts and resources
- Status indicators should use checkboxes for clarity

### Field Groupings

- Incident identification fields grouped together on all pages
- Location information fields grouped geographically
- Status fields grouped by civilian/responder categories
- Resource fields grouped by agency/organization
- Time-based projections grouped by timeframe (12/24/48/72 hours)

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 209 form
2. **Update** - Modify information on an existing form
3. **Approve** - Obtain necessary signatures and approvals
4. **Submit** - Transmit to appropriate entities above the incident level
5. **Print** - Generate a printable version of the form
6. **Share** - Distribute the form electronically
7. **Secure** - Control access to sensitive information

### State Transitions

1. **Draft** → **Approved**: When the form is completed and signed
2. **Approved** → **Submitted**: When sent to recipients
3. **Submitted** → **Acknowledged**: When receipt is confirmed
4. **Any State** → **Updated**: When a new version is created
5. **Updated** → **Final**: When marked as the final report

### Access Control

1. Situation Unit Leader/Planning Section Chief: Create, Update, Print
2. Incident Commander: Review, Approve
3. Documentation Unit: Archive
4. Agency/EOC/MACS: View, Use for Support Decisions
5. Public Information Officer: View (for coordinating public information)
6. Intelligence/Investigations: Limited access based on sensitivity

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, times, numbers, and currency values
2. Must maintain versioning for updates to track incident progress
3. Must preserve all versions throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data
6. Should maintain security controls for sensitive information
7. Should support attachment of simple geospatial data files

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Must maintain consistent formatting across the multi-page form
3. Should support export to PDF and other common formats
4. Should support extraction of specific sections for specialized reports
5. Should support aggregation of data from multiple incidents

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Should support quick entry of common incident types and definitions
3. Should provide validation for critical fields like dates and coordinates
4. Should include warnings when entering potentially sensitive information
5. Should support duplication of previous reports for updates
6. Should clearly distinguish required vs. optional fields
7. Should provide help text for complex fields

### Integration Requirements

1. Should allow integration with incident management systems
2. Should support data exchange with EOCs and MACS
3. Should enable pre-population of incident information from existing data
4. Should support import/export to geospatial information systems
5. Should enable sharing of resource information with resource tracking systems
6. Should support secure transmission to authorized recipients

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should support digital signatures for approval fields
4. Should include version control for updates
5. Must comply with accessibility standards
6. Must implement appropriate security controls for sensitive information
7. Should support redaction of sensitive information for specific distribution
8. Must maintain appropriate audit trails for accountability
9. Should accommodate various jurisdictional reporting requirements and timeframes
