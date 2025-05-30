# ICS 205A - Communications List Analysis

## 1. Form Overview

### Form Name
ICS 205A - Communications List

### Purpose
The Communications List records methods of contact for incident personnel. While the Incident Radio Communications Plan (ICS 205) is used to provide information on radio frequencies, the ICS 205A indicates all methods of contact for personnel assigned to the incident (radio frequencies, phone numbers, pager numbers, etc.) and functions as an incident directory.

### Primary Users
- Communications Unit personnel (preparers)
- All incident personnel (end users)
- Command and General Staff
- Branch Directors
- Division/Group Supervisors
- Unit Leaders

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics205a_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics205a_operational_period | Operational Period | Complex | Yes | Valid date/time range | Time interval for which the form applies |
| ics205a_basic_local_comms_info | Basic Local Communications Information | Complex | Yes | - | Contact information for incident personnel |
| ics205a_prepared_by | Prepared By | Complex | Yes | - | Information about the person preparing the form |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics205a_form_version | Form Version | Text | No | - | Version of the ICS 205A form being used |
| ics205a_sensitive_info | Contains Sensitive Information | Boolean | No | Yes/No | Indicates if the form contains sensitive contact information |
| ics205a_prepared_date_time | Preparation Date/Time | DateTime | Yes | Valid date/time | Date and time the form was prepared |
| ics205a_iap_page_number | IAP Page Number | Text | No | Format: "IAP Page ___" | Page number within the IAP |

### Repeatable Section Fields - Basic Local Communications Information

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics205a_incident_assigned_position | Incident Assigned Position | Text | Yes | - | ICS position held by the individual |
| ics205a_name | Name | Text | Yes | - | Name of the person holding the position |
| ics205a_contact_methods | Method(s) of Contact | Text | Yes | - | Phone, pager, radio, etc. with appropriate details |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS205A-01**: Incident Name must be provided
2. **R-ICS205A-02**: Operational Period must be a valid date/time range
3. **R-ICS205A-03**: At least one contact entry must be provided
4. **R-ICS205A-04**: All contact entries must include Position, Name, and Method of Contact
5. **R-ICS205A-05**: Prepared By must include at minimum a name, position/title, and signature
6. **R-ICS205A-06**: If cell phone numbers are included, they should include area codes

### Form Lifecycle Rules

1. **L-ICS205A-01**: The form is filled out during check-in and maintained by Communications Unit personnel
2. **L-ICS205A-02**: The form is updated each operational period as personnel change
3. **L-ICS205A-03**: The form is distributed within the ICS organization by the Communications Unit
4. **L-ICS205A-04**: The form is posted as necessary for reference by incident personnel
5. **L-ICS205A-05**: All completed original forms must be given to the Documentation Unit
6. **L-ICS205A-06**: The form may be included in the IAP but is optional

### Conditional Requirements

1. **C-ICS205A-01**: If the form contains sensitive information (e.g., cell phone numbers), it should be clearly marked in the header
2. **C-ICS205A-02**: If sensitive information is included, the form should be marked as not for public release
3. **C-ICS205A-03**: If additional pages are needed, a blank ICS 205A can be used and repaginated
4. **C-ICS205A-04**: If used in conjunction with ICS 205, contact information relevant to radio communications should be consistent

## 4. User Interface Layout

### Section Definitions

1. **Header Section** - Contains incident identification, operational period, and sensitivity warnings
2. **Communications Information Section** - Tabular listing of all personnel contact information
3. **Footer Section** - Contains prepared by information

### Layout Specifications

- The form is designed as a one-page document, possibly extending to multiple pages
- Communications Information section should be displayed as a table with multiple alphabetized rows
- The table should accommodate numerous personnel entries
- If sensitive information is included, a clear notification should appear prominently

### Field Groupings

- Incident identification fields grouped together in the header
- Operational period fields (from/to) grouped together
- Personnel information grouped alphabetically in rows
- Contact methods grouped by type (phone, radio, etc.)

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 205A form
2. **Update** - Modify information on an existing form
3. **Print** - Generate a printable version of the form
4. **Share** - Distribute the form electronically
5. **Post** - Make the form available for reference at the incident
6. **Include in IAP** - Optionally add to Incident Action Plan package
7. **Mark Sensitive** - Flag the form as containing sensitive information

### State Transitions

1. **Draft** → **Active**: When the form is completed by Communications Unit personnel
2. **Active** → **Updated**: When personnel or contact information changes
3. **Active/Updated** → **Published**: When posted or distributed
4. **Published** → **Archived**: When the operational period ends
5. **Any State** → **Superseded**: When replaced by a new version

### Access Control

1. Communications Unit Personnel: Create, Update, Print
2. Planning Section Chief: Review
3. Command and General Staff: View
4. All Incident Personnel: View posted copies
5. Documentation Unit: Archive
6. Public: No access if contains sensitive information

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, and contact information
2. Must maintain relationship with other incident directory information
3. Must preserve all versions throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data
6. Should maintain security for sensitive contact information

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Must maintain consistent formatting across printed pages
3. Should support export to PDF and other common formats
4. Should support various output formats for posting and distribution
5. Should provide a clear, readable directory format

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Should support quick entry of contact information
3. Should support alphabetical sorting of entries
4. Should support sorting by position/role
5. Should provide validation of contact information formats
6. Should support search functionality for large directories
7. Should clearly indicate when updated versions are available

### Integration Requirements

1. Should integrate with Incident Radio Communications Plan (ICS 205)
2. Should enable pre-population of incident information from existing data
3. Should enable pre-population of personnel information from check-in records
4. Should support integration with other personnel tracking systems
5. Should allow export of contact information to other systems
6. Should support integration with digital directory services when available

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should include version control for updates
4. Must comply with accessibility standards
5. Should enable collaborative editing with appropriate access controls
6. Must maintain data integrity during concurrent access
7. Must implement appropriate security measures for sensitive information
8. Should support both digital and printed distribution and updates
9. Should support rapid updates as personnel change
