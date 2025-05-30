# ICS 206 - Medical Plan Analysis

## 1. Form Overview

### Form Name
ICS 206 - Medical Plan

### Purpose
The Medical Plan provides information on incident medical aid stations, transportation services, hospitals, and medical emergency procedures. It ensures that appropriate medical support is available for incident personnel and outlines procedures for managing medical emergencies.

### Primary Users
- Medical Unit Leader (preparer)
- Safety Officer (reviewer)
- Planning Section Chief
- Logistics Section Chief
- All incident personnel
- Division/Group Supervisors
- Branch Directors

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics206_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics206_operational_period | Operational Period | Complex | Yes | Valid date/time range | Time interval for which the form applies |
| ics206_medical_aid_stations | Medical Aid Stations | Complex | No | - | Information on incident medical aid stations |
| ics206_transportation | Transportation | Complex | No | - | Information on medical transport capabilities |
| ics206_hospitals | Hospitals | Complex | No | - | Information on receiving medical facilities |
| ics206_special_medical_emergency_procedures | Special Medical Emergency Procedures | Text | No | Multi-line | Detailed emergency instructions and procedures |
| ics206_aviation_assets | Aviation Assets Utilized for Rescue | Boolean | No | Checkbox | Indicates if aviation assets are used for rescue |
| ics206_prepared_by | Prepared By | Complex | Yes | - | Information about the Medical Unit Leader |
| ics206_approved_by | Approved By | Complex | Yes | - | Information about the Safety Officer |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics206_form_version | Form Version | Text | No | - | Version of the ICS 206 form being used |
| ics206_prepared_date_time | Preparation Date/Time | DateTime | Yes | Valid date/time | Date and time the form was prepared |
| ics206_iap_page_number | IAP Page Number | Text | Yes | Format: "IAP Page ___" | Page number within the IAP |

### Repeatable Section Fields - Medical Aid Stations

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics206_aid_station_name | Name | Text | Yes | - | Name of the medical aid station |
| ics206_aid_station_location | Location | Text | Yes | - | Location of the medical aid station |
| ics206_aid_station_contact | Contact Number(s)/Frequency | Text | Yes | - | Contact information for the medical aid station |
| ics206_aid_station_paramedics | Paramedics On Site | Boolean | Yes | Yes/No | Indicates if paramedics are at the station |

### Repeatable Section Fields - Transportation

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics206_ambulance_service | Ambulance Service | Text | Yes | - | Name of ambulance service |
| ics206_ambulance_location | Location | Text | Yes | - | Location of the ambulance service |
| ics206_ambulance_contact | Contact Number(s)/Frequency | Text | Yes | - | Contact information for the ambulance service |
| ics206_ambulance_level | Level of Service | Enum | Yes | ALS/BLS | Advanced Life Support or Basic Life Support |

### Repeatable Section Fields - Hospitals

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics206_hospital_name | Hospital Name | Text | Yes | - | Name of the hospital |
| ics206_hospital_address | Address, Latitude & Longitude if Helipad | Text | Yes | - | Location details for the hospital |
| ics206_hospital_contact | Contact Number(s)/Frequency | Text | Yes | - | Contact information for the hospital |
| ics206_hospital_travel_time_air | Travel Time Air | Text | No | - | Estimated air travel time to hospital |
| ics206_hospital_travel_time_ground | Travel Time Ground | Text | No | - | Estimated ground travel time to hospital |
| ics206_hospital_trauma_center | Trauma Center | Boolean | Yes | Yes/No | Indicates if hospital is a trauma center |
| ics206_hospital_trauma_level | Trauma Level | Text | No | - | Level of trauma center if applicable |
| ics206_hospital_burn_center | Burn Center | Boolean | Yes | Yes/No | Indicates if hospital has a burn center |
| ics206_hospital_helipad | Helipad | Boolean | Yes | Yes/No | Indicates if hospital has a helipad |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS206-01**: Incident Name must be provided
2. **R-ICS206-02**: Operational Period must be a valid date/time range
3. **R-ICS206-03**: At least one medical aid station, transportation service, or hospital should be listed
4. **R-ICS206-04**: If a medical aid station is listed, it must include Name, Location, Contact, and Paramedics status
5. **R-ICS206-05**: If a transportation service is listed, it must include Service Name, Location, Contact, and Level
6. **R-ICS206-06**: If a hospital is listed, it must include Name, Address, Contact, and status fields
7. **R-ICS206-07**: If "Aviation Assets Utilized for Rescue" is checked, it must be coordinated with Air Operations
8. **R-ICS206-08**: Prepared By must include at minimum the Medical Unit Leader's name and signature
9. **R-ICS206-09**: Approved By must include at minimum the Safety Officer's name and signature

### Form Lifecycle Rules

1. **L-ICS206-01**: The form is prepared by the Medical Unit Leader
2. **L-ICS206-02**: The form must be reviewed and approved by the Safety Officer
3. **L-ICS206-03**: The form is duplicated and attached to the ICS 202 as part of the IAP
4. **L-ICS206-04**: Information from the plan is noted on relevant Assignment Lists (ICS 204)
5. **L-ICS206-05**: All completed original forms must be given to the Documentation Unit
6. **L-ICS206-06**: A new ICS 206 is created for each operational period or when there are significant changes to medical support

### Conditional Requirements

1. **C-ICS206-01**: If trauma centers are listed, their level should be specified
2. **C-ICS206-02**: If multiple pages are needed, additional pages can be used
3. **C-ICS206-03**: If aviation assets are used for rescue, this should be coordinated with Air Operations
4. **C-ICS206-04**: If latitude and longitude are provided for hospitals with helipads, they must be in a format that complements medical evacuation helicopters and air resources

## 4. User Interface Layout

### Section Definitions

1. **Header Section** - Contains incident identification and operational period
2. **Medical Aid Stations Section** - Tabular listing of all incident medical aid stations
3. **Transportation Section** - Tabular listing of ambulance services and other medical transport
4. **Hospitals Section** - Tabular listing of area hospitals and their capabilities
5. **Special Procedures Section** - Text area for detailed emergency procedures
6. **Approval Section** - Contains prepared by and approved by information

### Layout Specifications

- The form is designed as a one-page document, possibly extending to multiple pages if needed
- Medical Aid Stations section should be displayed as a table with multiple rows
- Transportation section should be displayed as a table with multiple rows
- Hospitals section should be displayed as a table with multiple rows
- Special Procedures section should provide adequate space for detailed instructions

### Field Groupings

- Incident identification fields grouped together in the header
- Operational period fields (from/to) grouped together
- Medical Aid Station information grouped in rows
- Transportation information grouped in rows
- Hospital information grouped in rows with capability indicators clearly visible
- Approval fields grouped by role (prepared by, approved by)

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 206 form
2. **Update** - Modify information on an existing form
3. **Review** - Safety Officer reviews the medical plan
4. **Approve** - Safety Officer approves the medical plan
5. **Print** - Generate a printable version of the form
6. **Share** - Distribute the form electronically
7. **Include in IAP** - Add to complete Incident Action Plan package
8. **Extract for ICS 204** - Transfer relevant medical information to Assignment Lists

### State Transitions

1. **Draft** → **Reviewed**: When the form is reviewed by Safety Officer
2. **Reviewed** → **Approved**: When approved by Safety Officer
3. **Approved** → **Published**: When included in distributed IAP
4. **Published** → **Archived**: When the operational period ends
5. **Any State** → **Superseded**: When replaced by a new version

### Access Control

1. Medical Unit Leader: Create, Update, Print
2. Safety Officer: Review, Approve
3. Planning Section Chief: View, Include in IAP
4. All Incident Personnel: View published plan
5. Division/Group Supervisors: View, Extract relevant information
6. Documentation Unit: Archive

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, and boolean values
2. Must maintain relationship with other IAP components
3. Must preserve all versions throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data
6. Should maintain historical record of medical resources

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Must maintain consistent formatting across printed pages
3. Should support export to PDF and other common formats
4. Should support various output formats for inclusion in the IAP
5. Should provide a clear, readable format for medical information
6. Should support printing of maps showing medical facility locations

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Should support quick entry of medical resources
3. Should provide templates for common medical plan components
4. Should provide real-time validation of entered data
5. Should support map-based entry of facility locations
6. Should clearly indicate trauma levels and other critical capabilities
7. Should support clear organization of emergency procedures

### Integration Requirements

1. Should integrate with Assignment Lists (ICS 204)
2. Should integrate with Air Operations Summary (ICS 220) if aviation assets are used
3. Should enable pre-population of incident information from existing data
4. Must support integration with other IAP components
5. Should enable integration with mapping/GIS systems for facility locations
6. Should support integration with local emergency medical services databases

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should support digital signatures for approval fields
4. Should include version control for medical plan updates
5. Must comply with accessibility standards
6. Should enable collaborative editing with appropriate access controls
7. Must maintain data integrity during concurrent access
8. Should provide emergency quick-reference format for field use
9. Should comply with relevant health information privacy requirements
