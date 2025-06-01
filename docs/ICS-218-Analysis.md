# ICS 218 - Support Vehicle/Equipment Inventory Analysis

## 1. Form Overview

### Form Name
ICS 218 - Support Vehicle/Equipment Inventory

### Purpose
The Support Vehicle/Equipment Inventory provides an inventory of all transportation and support vehicles and equipment assigned to the incident. The information is used by the Ground Support Unit to maintain a record of the types and locations of vehicles and equipment on the incident, and the time they arrived and departed.

### Primary Users
- Ground Support Unit Leader (preparer)
- Facilities Unit
- Supply Unit
- Equipment Managers
- Logistics Section Chief
- Finance/Administration Section (for documentation of resources)
- Demobilization Unit

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics218_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics218_incident_number | Incident Number | Text | No | Max 50 chars | Number assigned to the incident |
| ics218_date_prepared | Date Prepared | Date | Yes | Valid date | Date the form was prepared |
| ics218_time_prepared | Time Prepared | Time | Yes | Valid time | Time the form was prepared |
| ics218_vehicle_equipment_information | Vehicle/Equipment Information | Complex | Yes | - | List of vehicles and equipment |
| ics218_prepared_by | Prepared By | Complex | Yes | - | Information about the person preparing the form |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics218_form_version | Form Version | Text | No | - | Version of the ICS 218 form being used |
| ics218_page_number | Page Number | Text | Yes | Format: "Page X of Y" | Page number information |

### Repeatable Section Fields - Vehicle/Equipment Information

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics218_order_request_number | Order Request Number | Text | No | - | Resource order request number |
| ics218_vehicle_equipment_type | Type | Text | Yes | - | Type of vehicle or equipment |
| ics218_vehicle_equipment_make | Make | Text | Yes | - | Make of vehicle or equipment |
| ics218_vehicle_id | ID/Lic | Text | Yes | - | ID number or license plate |
| ics218_vehicle_category | Category | Enum | Yes | Transport/Support/Other | Category of vehicle or equipment |
| ics218_datetime_checkin | Date/Time Check-In | DateTime | Yes | Valid date/time | When resource arrived at incident |
| ics218_driver_name | Driver Name | Text | No | - | Name of assigned driver |
| ics218_home_base | Home Base | Text | Yes | - | Location where vehicle is based |
| ics218_departure_datetime | Departure Date/Time | DateTime | No | Valid date/time | When resource left the incident |
| ics218_incident_assignment | Incident Assignment | Text | No | - | Assignment of vehicle at incident |
| ics218_notes | Notes | Text | No | - | Additional notes about resource |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS218-01**: Incident Name must be provided
2. **R-ICS218-02**: Date Prepared and Time Prepared must be valid
3. **R-ICS218-03**: At least one vehicle/equipment entry should be included
4. **R-ICS218-04**: Each vehicle/equipment entry must include Type, Make, ID/License, and Category
5. **R-ICS218-05**: Date/Time Check-In must be provided for each entry
6. **R-ICS218-06**: Home Base must be provided for each vehicle/equipment
7. **R-ICS218-07**: Prepared By must include at minimum a name, position/title, and signature
8. **R-ICS218-08**: Page numbers must be provided if multiple pages are used

### Form Lifecycle Rules

1. **L-ICS218-01**: The form is prepared by the Ground Support Unit Leader when vehicles/equipment arrive
2. **L-ICS218-02**: The form is updated as vehicles and equipment arrive and depart the incident
3. **L-ICS218-03**: The information is shared with the Facilities Unit and Supply Unit as needed
4. **L-ICS218-04**: The form may be shared with the Finance/Administration Section for documentation
5. **L-ICS218-05**: All completed original forms must be given to the Documentation Unit
6. **L-ICS218-06**: Copies may be provided to the Demobilization Unit to assist with resource release

### Conditional Requirements

1. **C-ICS218-01**: If the vehicle has an assigned driver, the driver's name should be provided
2. **C-ICS218-02**: If a vehicle/equipment departs the incident, the departure date/time should be recorded
3. **C-ICS218-03**: If additional pages are needed, use blank ICS 218, and repaginate as needed
4. **C-ICS218-04**: If vehicle is assigned within the incident, the assignment should be noted
5. **C-ICS218-05**: If special concerns exist for a vehicle or equipment, note in the Notes field

## 4. User Interface Layout

### Section Definitions

1. **Header Section** - Contains incident identification and form preparation information
2. **Vehicle/Equipment Information Section** - Tabular listing of all vehicles and equipment
3. **Footer Section** - Contains prepared by information

### Layout Specifications

- The form is designed as a one-page document, possibly extending to multiple pages
- Available in standard 8.5" x 11" format, as well as optionally in legal size (8.5" x 14")
- Vehicle/Equipment Information section should be displayed as a table with multiple rows
- Table columns should be appropriately sized based on data types
- Vehicle category indicators should be easily visible

### Field Groupings

- Incident identification fields grouped together in the header
- Date and time prepared grouped together
- Vehicle/equipment identification (Type, Make, ID) grouped together
- Vehicle status fields (check-in, departure) grouped together
- Personnel information (driver, home base) grouped together
- Assignment and notes grouped together

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 218 form
2. **Update** - Add additional vehicles/equipment as they arrive
3. **Record Departure** - Document when vehicles/equipment depart
4. **Print** - Generate a printable version of the form
5. **Share** - Distribute to other units as needed
6. **Query** - Search for specific vehicles/equipment

### State Transitions

1. **Blank** → **In Use**: When the form is initiated by Ground Support Unit
2. **In Use** → **Updated**: As vehicles/equipment arrive or depart
3. **Updated** → **Completed**: When all vehicles/equipment are documented for the operational period
4. **Completed** → **Archived**: When filed by Documentation Unit
5. **Any State** → **Extended**: When additional pages are added

### Access Control

1. Ground Support Unit Leader: Create, Update
2. Logistics Section Chief: View
3. Finance/Administration Section: View for cost tracking
4. Demobilization Unit: View for resource release planning
5. Documentation Unit: Archive

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, times, and enumerated values
2. Must maintain chronological record of vehicle/equipment status
3. Should preserve all forms throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data
6. Should maintain relationship to resource ordering system

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Should support alternative sizes (8.5" x 14")
3. Should support export to PDF and other common formats
4. Should maintain proper pagination for multi-page inventories
5. Should facilitate printing of partial inventories by category

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Should support rapid entry of vehicle/equipment information
3. Should provide check-in/departure process automation
4. Should support sorting and filtering by various criteria
5. Should allow for batch entry of multiple vehicles/equipment
6. Should facilitate tracking of vehicle assignments and locations

### Integration Requirements

1. Should integrate with resource ordering systems
2. Should integrate with ground support management systems
3. Should enable pre-population of vehicle information from existing data
4. Should support integration with demobilization planning
5. Should allow for data exchange with cost tracking systems
6. Should support integration with maintenance tracking systems

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should support barcode/RFID scanning for vehicle identification
4. Should include version control for updates
5. Must comply with accessibility standards
6. Should enable collaborative editing with appropriate access controls
7. Must maintain data integrity during concurrent access
8. Should support location-based tracking when available
9. Should provide alerts for vehicles nearing demobilization dates
