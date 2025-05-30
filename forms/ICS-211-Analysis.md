# ICS 211 - Incident Check-In List Analysis

## 1. Form Overview

### Form Name
ICS 211 - Incident Check-In List

### Purpose
The Incident Check-In List records arrival times at the incident of all overhead personnel and equipment. It serves several purposes: recording arrival times of resources, recording the initial location of personnel and equipment to facilitate subsequent assignments, and supporting demobilization by recording the home base, method of travel, etc., for resources checked in.

### Primary Users
- Check-in Recorders
- Resources Unit
- Personnel at various check-in locations:
  - Staging Areas
  - Base
  - Incident Command Post (ICP)
  - Helibase
- Incident Communications Center Manager
- Documentation Unit

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics211_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics211_incident_number | Incident Number | Text | No | Max 50 chars | Number assigned to the incident |
| ics211_check_in_location | Check-In Location | Complex | Yes | - | Location where check-in occurs |
| ics211_start_date_time | Start Date/Time | DateTime | Yes | Valid date/time | Date and time check-in began |
| ics211_resource_list | Resource List | Complex | Yes | - | List of resources being checked in |
| ics211_prepared_by | Prepared By | Complex | Yes | - | Information about the person preparing the form |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics211_form_version | Form Version | Text | No | - | Version of the ICS 211 form being used |
| ics211_prepared_date_time | Preparation Date/Time | DateTime | Yes | Valid date/time | Date and time the form was prepared |

### Repeatable Section Fields - Check-In Location

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics211_location_base | Base | Boolean | No | Checkbox | Indicates check-in at Base |
| ics211_location_staging_area | Staging Area | Boolean | No | Checkbox | Indicates check-in at Staging Area |
| ics211_location_icp | ICP | Boolean | No | Checkbox | Indicates check-in at Incident Command Post |
| ics211_location_helibase | Helibase | Boolean | No | Checkbox | Indicates check-in at Helibase |
| ics211_location_other | Other | Boolean | No | Checkbox | Indicates check-in at other location |
| ics211_location_details | Location Details | Text | No | - | Specific information about check-in location |

### Repeatable Section Fields - Resource List

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics211_single_overhead_option | List single resource personnel (overhead) by agency and name | Boolean | No | Checkbox | Option to list individual overhead personnel |
| ics211_list_resources_option | List resources by the following format | Boolean | No | Checkbox | Option to list resources by standard categorization |
| ics211_resource_state | State | Text | No | - | State identifier for the resource |
| ics211_resource_agency | Agency | Text | Yes | - | Agency name or designator |
| ics211_resource_category | Category | Text | No | - | Resource category per NIMS |
| ics211_resource_kind | Kind | Text | No | - | Resource kind per NIMS |
| ics211_resource_type | Type | Text | No | - | Resource type per NIMS |
| ics211_resource_name_id | Resource Name or Identifier | Text | Yes | - | Resource name or unique identifier |
| ics211_resource_st_tf | ST or TF | Text | No | - | Indicates if part of Strike Team or Task Force |
| ics211_order_request_number | Order Request # | Text | No | - | Order or request number assigned to resource |
| ics211_date_time_check_in | Date/Time Check-In | DateTime | Yes | Valid date/time | When resource arrived at incident |
| ics211_leaders_name | Leader's Name | Text | No | - | Name of resource leader if applicable |
| ics211_total_personnel | Total Number of Personnel | Number | Yes | Positive integer | Total number of personnel for the resource |
| ics211_incident_contact | Incident Contact Information | Text | No | - | Contact details (radio, cell, etc.) at incident |
| ics211_home_unit | Home Unit or Agency | Text | Yes | - | Home unit/agency to which resource is assigned |
| ics211_departure_point | Departure Point, Date and Time | Complex | Yes | - | Where and when resource departed |
| ics211_method_travel | Method of Travel | Text | Yes | - | Transportation method to incident |
| ics211_incident_assignment | Incident Assignment | Text | No | - | Assignment at time of dispatch |
| ics211_other_qualifications | Other Qualifications | Text | No | - | Additional relevant qualifications |
| ics211_sent_to_resources_unit | Data Provided to Resources Unit | Complex | Yes | - | Confirmation data was provided to Resources Unit |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS211-01**: Incident Name must be provided
2. **R-ICS211-02**: At least one Check-In Location must be checked
3. **R-ICS211-03**: Start Date/Time must be a valid date and time
4. **R-ICS211-04**: At least one resource must be listed
5. **R-ICS211-05**: Each resource must include at minimum Agency, Resource Name/ID, Date/Time Check-In, Total Personnel, Home Unit, Departure Point, and Method of Travel
6. **R-ICS211-06**: Prepared By must include at minimum a name, position/title, and signature
7. **R-ICS211-07**: For equipment, the operator's name should be entered as the Leader's Name
8. **R-ICS211-08**: For Strike Teams or Task Forces, the team leader's name should be included

### Form Lifecycle Rules

1. **L-ICS211-01**: The form is initiated at various check-in locations (Staging Area, Base, ICP, Helibase)
2. **L-ICS211-02**: Information may be recorded by overhead at check-in locations, Incident Communications Center Manager, or Resources Unit recorder
3. **L-ICS211-03**: Completed information is transmitted to the Resources Unit as soon as possible
4. **L-ICS211-04**: Resources Unit maintains master list of all equipment and personnel checked in
5. **L-ICS211-05**: All completed original forms must be given to the Documentation Unit
6. **L-ICS211-06**: The form may be copied for demobilization unit use and used to verify resources released from the incident

### Conditional Requirements

1. **C-ICS211-01**: If resource is a Strike Team or Task Force, indicate as such in the ST or TF field
2. **C-ICS211-02**: If "Other" is selected for check-in location, details must be provided
3. **C-ICS211-03**: If additional pages are needed, use a blank ICS 211 and repaginate as needed
4. **C-ICS211-04**: For mixed resource types, use separate pages for overhead personnel vs. equipment
5. **C-ICS211-05**: If colored paper is used to match Resource Status Card colors, follow the color coding system

## 4. User Interface Layout

### Section Definitions

1. **Header Section** - Contains incident identification, check-in location, and start date/time
2. **Check-In Information Section** - Tabular listing of all resources checking in
3. **Footer Section** - Contains prepared by information

### Layout Specifications

- The form is designed as a one-page document, possibly extending to multiple pages
- Available in standard 8.5" x 11" format, as well as optional 8.5" x 14" (legal) and 11" x 17" formats
- Check-In Information section should be displayed as a table with multiple rows
- Resource identification fields aligned to facilitate quick scanning
- Reverse side of form may be used for remarks or comments

### Field Groupings

- Incident identification fields grouped together in the header
- Check-in location options grouped together
- Resource information grouped in rows
- Resource identification fields (State, Agency, etc.) grouped together
- Resource status fields (check-in time, assignment, etc.) grouped together
- Travel information fields grouped together

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 211 form
2. **Update** - Add additional resources to an existing check-in list
3. **Print** - Generate a printable version of the form
4. **Share** - Transmit the form electronically to Resources Unit
5. **Color Code** - Optionally print on colored paper to match T-Card system
6. **Verify Resources** - Use during demobilization to verify resource departure

### State Transitions

1. **Blank** → **In Use**: When the form is placed at a check-in location
2. **In Use** → **Completed**: When all resources for that location/timeframe are recorded
3. **Completed** → **Transmitted**: When provided to Resources Unit
4. **Transmitted** → **Recorded**: When information is transferred to master resource list
5. **Recorded** → **Archived**: When filed by Documentation Unit
6. **Archived** → **Referenced**: When used during demobilization process

### Access Control

1. Check-in Recorders: Create, Update
2. Incident Communications Center Manager: Create, Update
3. Resources Unit: View, Record in master list
4. Demobilization Unit: View for verification
5. Documentation Unit: Archive

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, times, and numeric values
2. Must maintain relationship between check-in location and resources
3. Should preserve all forms throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data
6. Should maintain linkage to resource management system

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Should support alternative sizes (8.5" x 14", 11" x 17")
3. Should support export to PDF and other common formats
4. Should support color-coding options to match T-Card system
5. Should facilitate printing of multiple copies for various uses

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Should support rapid entry of resource information during busy check-in periods
3. Should provide validation of properly formatted resource identifiers
4. Should support barcode/RFID scanning of resource identification where available
5. Should support timestamp automation for check-in process
6. Should alert users to potentially duplicate check-ins

### Integration Requirements

1. Should integrate with Resource Status Cards (ICS 219)
2. Should integrate with master resource tracking system
3. Should enable pre-population of incident information from existing data
4. Should support integration with demobilization process
5. Should allow for import of pre-planned resource information
6. Should support data exchange with ordering systems

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should support batch processing of resources
4. Should include version control for updates
5. Must comply with accessibility standards
6. Should enable collaborative editing with appropriate access controls
7. Must maintain data integrity during concurrent access
8. Should support mobile check-in capabilities at remote locations
9. Should enable GPS/location tagging of check-in points when available
