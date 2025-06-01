# ICS 220 - Air Operations Summary Analysis

## 1. Form Overview

### Form Name
ICS 220 - Air Operations Summary

### Purpose
The Air Operations Summary provides information about the incident air operations. The form is used to inform and support the tactical use of aircraft in incident operations and communicates key logistical information regarding fueling, servicing, and resources for air operations.

### Primary Users
- Air Operations Branch Director (preparer)
- Operations Section Chief (approver)
- Air Tactical Group Supervisor
- Air Support Group Supervisor
- Helibase/Helispot Managers
- Fixed-Wing Base Managers
- Pilots and air crews
- Planning Section (Resources Unit)
- Logistics Section
- Ground personnel working with aircraft

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics220_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics220_operational_period | Operational Period | Complex | Yes | Valid date/time range | Time interval for which the form applies |
| ics220_sunrise | Sunrise | Time | No | Valid time | Time of sunrise at the incident location |
| ics220_sunset | Sunset | Time | No | Valid time | Time of sunset at the incident location |
| ics220_remarks | Remarks | Text | No | Multi-line | General remarks regarding air operations |
| ics220_medivac | Medivac | Text | No | - | Medical evacuation information for air resources |
| ics220_personnel_aircraft_hazard | Personnel/Aircraft Hazard | Text | No | - | Known hazards to personnel or aircraft |
| ics220_transportation | Transportation | Complex | No | - | Transportation plans and needs information |
| ics220_aircraft_information | Aircraft Information | Complex | Yes | - | Details of assigned aircraft |
| ics220_air_operations_org | Air Operations Organization | Complex | Yes | - | Organizational positions for air operations |
| ics220_fixed_wing_bases | Fixed-Wing Bases | Complex | No | - | Information about fixed-wing bases |
| ics220_helibase_helispot | Helibase/Helispot Information | Complex | No | - | Information about helibases and helispots |
| ics220_frequencies | Frequencies | Complex | Yes | - | Radio frequencies used in air operations |
| ics220_prepared_by | Prepared By | Complex | Yes | - | Information about the person preparing the form |
| ics220_approved_by | Approved By | Complex | Yes | - | Information about the Operations Section Chief |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics220_form_version | Form Version | Text | No | - | Version of the ICS 220 form being used |
| ics220_prepared_date_time | Preparation Date/Time | DateTime | Yes | Valid date/time | Date and time the form was prepared |

### Repeatable Section Fields - Aircraft Information

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics220_aircraft_designation | Aircraft Designation | Text | Yes | - | Identifier for the aircraft |
| ics220_aircraft_type | Aircraft Type | Text | Yes | - | Type of aircraft (e.g., helicopter type, fixed-wing type) |
| ics220_available | Available | Time | Yes | Valid time | Time when aircraft is available |
| ics220_est_departure | Estimated Departure | Time | No | Valid time | Estimated departure time |
| ics220_est_arrival | Estimated Arrival | Time | No | Valid time | Estimated arrival time |
| ics220_assigned | Assigned | Text | No | - | Assignment of the aircraft |
| ics220_aircraft_contact | Contact | Text | Yes | - | Contact information (frequency/phone) |
| ics220_remarks_notes | Remarks/Notes | Text | No | - | Additional information about the aircraft |

### Repeatable Section Fields - Air Operations Organization

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics220_air_ops_director | Air Operations Branch Director | Text | Yes | - | Name of the Air Operations Branch Director |
| ics220_air_ops_phone | Air Operations Branch Director Phone | Text | No | - | Phone number of the Air Operations Branch Director |
| ics220_air_tactical_group | Air Tactical Group Supervisor | Text | No | - | Name of the Air Tactical Group Supervisor |
| ics220_air_tactical_phone | Air Tactical Group Supervisor Phone | Text | No | - | Phone number of the Air Tactical Group Supervisor |
| ics220_air_support_group | Air Support Group Supervisor | Text | No | - | Name of the Air Support Group Supervisor |
| ics220_air_support_phone | Air Support Group Supervisor Phone | Text | No | - | Phone number of the Air Support Group Supervisor |

### Repeatable Section Fields - Fixed-Wing Bases

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics220_fixed_wing_base_name | Name | Text | Yes | - | Name of the fixed-wing base |
| ics220_fixed_wing_base_location | Location | Text | Yes | - | Geographic location of the base |
| ics220_fixed_wing_base_telephone | Telephone/Frequency | Text | Yes | - | Contact method for the base |

### Repeatable Section Fields - Helibase/Helispot Information

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics220_helibase_name | Name | Text | Yes | - | Name/designator of the helibase or helispot |
| ics220_helibase_location | Location | Text | Yes | - | Geographic location of the helibase/helispot |
| ics220_helibase_telephone | Telephone/Frequency | Text | Yes | - | Contact method for the helibase/helispot |

### Repeatable Section Fields - Frequencies

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics220_frequency_function | Function | Text | Yes | - | Purpose of the frequency |
| ics220_frequency_channel | Channel/Frequency | Text | Yes | - | The actual frequency or channel number |
| ics220_frequency_assignment | Assignment | Text | No | - | Who is assigned to use the frequency |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS220-01**: Incident Name must be provided
2. **R-ICS220-02**: Operational Period must be a valid date/time range
3. **R-ICS220-03**: At least one aircraft should be listed
4. **R-ICS220-04**: Each aircraft entry must include Designation, Type, Available time, and Contact information
5. **R-ICS220-05**: Air Operations Branch Director information must be provided
6. **R-ICS220-06**: At least one frequency must be included in the Frequencies section
7. **R-ICS220-07**: If fixed-wing bases are used, their name, location, and contact information must be provided
8. **R-ICS220-08**: If helibases/helispots are used, their name, location, and contact information must be provided
9. **R-ICS220-09**: Prepared By must include at minimum a name, position/title, and signature
10. **R-ICS220-10**: Approved By must include at minimum the Operations Section Chief name and signature

### Form Lifecycle Rules

1. **L-ICS220-01**: The form is prepared by the Air Operations Branch Director for each operational period
2. **L-ICS220-02**: The completed form must be approved by the Operations Section Chief
3. **L-ICS220-03**: The form is distributed to air tactical and air support personnel
4. **L-ICS220-04**: The form is duplicated and attached to the Incident Action Plan if relevant
5. **L-ICS220-05**: Updates may be made during the operational period as aircraft assignments change
6. **L-ICS220-06**: All completed original forms must be given to the Documentation Unit

### Conditional Requirements

1. **C-ICS220-01**: If air medical evacuation is part of air operations, Medivac information must be completed
2. **C-ICS220-02**: If known hazards exist, the Personnel/Aircraft Hazard field must be completed
3. **C-ICS220-03**: If special transportation plans exist, the Transportation field must be completed
4. **C-ICS220-04**: If sunrise/sunset times are relevant to operations, they should be included
5. **C-ICS220-05**: If additional pages are needed, use blank ICS 220 forms and repaginate as needed

## 4. User Interface Layout

### Section Definitions

1. **Header Section** - Contains incident identification, operational period, and sunrise/sunset times
2. **Comments Section** - Contains remarks, medivac information, hazards, and transportation plans
3. **Organization Section** - Contains air operations organization information
4. **Aircraft Information Section** - Tabular listing of assigned aircraft and their details
5. **Base Information Section** - Contains information about fixed-wing bases and helibases/helispots
6. **Frequencies Section** - Tabular listing of radio frequencies used in air operations
7. **Footer Section** - Contains prepared by and approved by information

### Layout Specifications

- The form is designed as a one-page document, possibly extending to multiple pages if needed
- Aircraft Information section should be displayed as a multi-column table
- Frequencies section should be displayed as a three-column table
- Organization information should be displayed with names and phone numbers clearly visible
- Base information should be grouped by type (fixed-wing vs. helicopter)

### Field Groupings

- Incident identification fields grouped together in the header
- Operational period fields (from/to) grouped together
- General information fields (remarks, medivac, hazards, transportation) grouped together
- Air operations organization positions grouped together
- Aircraft information grouped in rows
- Base information grouped by type
- Frequency information grouped in rows

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 220 form for an operational period
2. **Update** - Modify aircraft assignments or other information as needed
3. **Approve** - Operations Section Chief reviews and approves the form
4. **Print** - Generate a printable version of the form
5. **Share** - Distribute to air tactical and air support personnel
6. **Include in IAP** - Attach to Incident Action Plan when relevant

### State Transitions

1. **Draft** → **Completed**: When the Air Operations Branch Director finalizes the form
2. **Completed** → **Approved**: When signed by the Operations Section Chief
3. **Approved** → **Distributed**: When provided to relevant air operations personnel
4. **Distributed** → **Included in IAP**: When attached to the Incident Action Plan
5. **Any State** → **Updated**: When aircraft assignments or other information changes
6. **Any State** → **Archived**: When filed by Documentation Unit

### Access Control

1. Air Operations Branch Director: Create, Update
2. Operations Section Chief: Review, Approve
3. Air Tactical and Air Support Personnel: View
4. Planning Section: View, Include in IAP
5. Documentation Unit: Archive

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, times, and contact information
2. Must maintain relationships between aircraft and their assignments
3. Should preserve all versions throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data
6. Should maintain historical record of air operations for each operational period

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Must maintain consistent formatting across printed pages
3. Should support export to PDF and other common formats
4. Should support various output formats for inclusion in the IAP
5. Should facilitate printing of multiple copies for distribution to air crews

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Should support rapid entry of aircraft information
3. Should provide templates for common aircraft configurations
4. Should support quick duplication of information from previous operational periods
5. Should provide validation of frequency information
6. Should clearly highlight safety information (hazards, medivac)

### Integration Requirements

1. Should integrate with ICS 203 (Organization Assignment List)
2. Should integrate with ICS 205 (Radio Communications Plan)
3. Should integrate with ICS 206 (Medical Plan) for medivac information
4. Should enable pre-population of incident information from existing data
5. Should support integration with aviation resource tracking systems
6. Should integrate with weather services for sunrise/sunset information

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should support digital signatures for approval fields
4. Should include version control for updates
5. Must comply with accessibility standards
6. Should enable collaborative editing with appropriate access controls
7. Must maintain data integrity during concurrent access
8. Should support mapping integration for helibase/helispot locations
9. Should provide templates for common air operations configurations
