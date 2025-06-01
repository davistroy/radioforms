# ICS 221 - Demobilization Check-Out Analysis

## 1. Form Overview

### Form Name
ICS 221 - Demobilization Check-Out

### Purpose
The Demobilization Check-Out form ensures that resources checking out of the incident have completed all appropriate incident business and provides the Planning Section with information on resources released from the incident. It helps track the movement of resources and the completion of demobilization tasks.

### Primary Users
- Demobilization Unit Leader (preparer)
- Planning Section Chief (approver)
- Resources being demobilized
- Logistics Section (Supply Unit, Facilities Unit, Ground Support Unit)
- Finance/Administration Section (Time Unit, Claims Unit)
- Documentation Unit
- Supervisors of demobilizing resources

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics221_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics221_incident_number | Incident Number | Text | No | Max 50 chars | Number assigned to the incident |
| ics221_resource_number | Resource or Personnel Number | Text | Yes | - | Identifier for the resource being released |
| ics221_resource_info | Resource Information | Complex | Yes | - | Detailed information about the resource |
| ics221_checkout_points | Demobilization Checkout Points | Complex | Yes | - | Approval signatures from various sections and units |
| ics221_travel_information | Travel Information | Complex | Yes | - | Details about the resource's travel plan |
| ics221_prepared_by | Prepared By | Complex | Yes | - | Information about the person preparing the form |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics221_form_version | Form Version | Text | No | - | Version of the ICS 221 form being used |
| ics221_prepared_date_time | Preparation Date/Time | DateTime | Yes | Valid date/time | Date and time the form was prepared |

### Repeatable Section Fields - Resource Information

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics221_resource_type | Resource Type | Text | Yes | - | Type of resource being demobilized |
| ics221_resource_name | Resource Name | Text | Yes | - | Name or identifier of the resource |
| ics221_resource_kind | Resource Kind | Text | No | - | Category/kind of resource |
| ics221_last_assignment | Last Assignment | Text | Yes | - | Resource's final assignment on the incident |
| ics221_crew_leader_name | Crew/Leader Name | Text | Yes | - | Name of crew leader or individual |
| ics221_resource_contact | Contact Information | Text | Yes | - | Phone or other contact information |
| ics221_manifest | Manifest | Boolean | No | Yes/No | Indicates if a manifest is completed |
| ics221_manifest_number | Manifest Number | Text | No | - | Identification number of manifest |
| ics221_total_personnel | Total Number Personnel | Number | Yes | Positive integer | Number of personnel being released |

### Repeatable Section Fields - Demobilization Checkout Points

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics221_unit_leader_checklist | Unit/Leader Checklist | Complex | Yes | - | List of units that must sign off on demobilization |
| ics221_logistics_supply_unit | Supply Unit | Complex | Yes | - | Supply Unit checkout information |
| ics221_logistics_communications_unit | Communications Unit | Complex | No | - | Communications Unit checkout information |
| ics221_logistics_facilities_unit | Facilities Unit | Complex | No | - | Facilities Unit checkout information |
| ics221_logistics_ground_support_unit | Ground Support Unit | Complex | No | - | Ground Support Unit checkout information |
| ics221_planning_documentation_unit | Documentation Unit | Complex | Yes | - | Documentation Unit checkout information |
| ics221_finance_admin_time_unit | Finance/Administration (Time Unit) | Complex | Yes | - | Time Unit checkout information |
| ics221_other_checkout | Other Section/Unit | Complex | No | - | Other sections or units checkout information |
| ics221_remarks | Remarks | Text | No | Multi-line | Additional comments about checkout process |

### Repeatable Section Fields - Travel Information

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics221_actual_release_date | Actual Release Date/Time | DateTime | Yes | Valid date/time | When resource was released from incident |
| ics221_destination | Destination | Text | Yes | - | Where resource is traveling to |
| ics221_estimated_arrival_date | Estimated Time of Arrival | DateTime | Yes | Valid date/time | Expected arrival at destination |
| ics221_travel_method | Travel Method | Text | Yes | - | Mode of transportation |
| ics221_travel_contact | Travel Contact Information | Text | No | - | Contact information during travel |
| ics221_managed_rest_period | Action Required to Ensure Safe Travel and Rest Period | Boolean | Yes | Yes/No | Indicates if rest period needs management |
| ics221_rest_plan | Rest Period Action Plan | Text | No | - | Plan to ensure adequate rest |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS221-01**: Incident Name must be provided
2. **R-ICS221-02**: Resource Number must be provided
3. **R-ICS221-03**: Resource Name, Type, and Last Assignment must be provided
4. **R-ICS221-04**: Crew/Leader Name and Contact Information must be provided
5. **R-ICS221-05**: Total Number of Personnel must be provided and be a positive integer
6. **R-ICS221-06**: Required checkout points must have signatures (Supply Unit, Documentation Unit, Finance/Admin)
7. **R-ICS221-07**: Actual Release Date/Time must be a valid date and time
8. **R-ICS221-08**: Destination and Estimated Time of Arrival must be provided
9. **R-ICS221-09**: Travel Method must be specified
10. **R-ICS221-10**: Managed Rest Period question must be answered
11. **R-ICS221-11**: Prepared By must include at minimum a name, position/title, and signature

### Form Lifecycle Rules

1. **L-ICS221-01**: The form is initiated by the Demobilization Unit when resource release is approved
2. **L-ICS221-02**: The resource carries the form to each checkout point for signature
3. **L-ICS221-03**: Each section/unit verifies that incident-related matters are resolved before signing
4. **L-ICS221-04**: After all signatures are obtained, the form is returned to the Demobilization Unit
5. **L-ICS221-05**: The Planning Section verifies that all sections are satisfied with demobilization
6. **L-ICS221-06**: The form is kept by the Documentation Unit in the incident files
7. **L-ICS221-07**: A copy may be given to the resource being demobilized

### Conditional Requirements

1. **C-ICS221-01**: If resource is being transported by aircraft, a manifest is required
2. **C-ICS221-02**: If manifest is required, the manifest number must be provided
3. **C-ICS221-03**: If "Yes" is checked for the rest period requirement, a rest plan must be provided
4. **C-ICS221-04**: If the resource used communications equipment, the Communications Unit must sign off
5. **C-ICS221-05**: If the resource used facilities, the Facilities Unit must sign off
6. **C-ICS221-06**: If the resource used vehicles or equipment, the Ground Support Unit must sign off
7. **C-ICS221-07**: If other sections had interactions with the resource, they should be included in checkout

## 4. User Interface Layout

### Section Definitions

1. **Header Section** - Contains incident identification and resource number
2. **Resource Information Section** - Contains details about the resource being demobilized
3. **Checkout Points Section** - Contains signature blocks for each incident unit
4. **Travel Information Section** - Contains details about travel plans
5. **Footer Section** - Contains prepared by information

### Layout Specifications

- The form is designed as a one-page document
- Header section appears at the top of the form
- Resource Information section appears below the header
- Checkout Points section appears in the middle of the form, with adequate space for signatures
- Travel Information section appears toward the bottom of the form
- Footer section appears at the bottom of the form

### Field Groupings

- Incident identification fields grouped together in the header
- Resource identification fields grouped together
- Checkout signature fields grouped by functional area (Logistics, Planning, Finance)
- Travel information fields grouped together
- Rest period management fields grouped together

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 221 form when resource is approved for release
2. **Update** - Add signatures as units approve the resource's demobilization
3. **Verify** - Ensure all required checkout points have signed off
4. **Complete** - Finalize the form when all signatures are obtained
5. **Print** - Generate a printable version of the form
6. **Share** - Provide copies to relevant parties
7. **Archive** - Store the completed form with Documentation Unit

### State Transitions

1. **Blank** → **Initiated**: When the Demobilization Unit creates the form
2. **Initiated** → **In Progress**: When the resource begins collecting signatures
3. **In Progress** → **Completed**: When all required signatures are obtained
4. **Completed** → **Verified**: When Planning Section confirms all checkouts
5. **Verified** → **Released**: When resource is allowed to depart
6. **Released** → **Archived**: When filed by Documentation Unit

### Access Control

1. Demobilization Unit: Create, Update, Verify
2. Resource Being Demobilized: Carry form, Collect signatures
3. Checkout Points: Update, Add signature
4. Planning Section: Verify, Approve
5. Documentation Unit: Archive

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, times, and boolean values
2. Must maintain relationships between resources and their checkout status
3. Should preserve all forms throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data
6. Should maintain historical record of demobilization activities

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Must maintain clear formatting for signature spaces
3. Should support export to PDF and other common formats
4. Should facilitate printing of copies for resource, Documentation Unit, and Demobilization Unit
5. Should support both electronic and physical signature processes

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Should support rapid creation of forms for multiple resources
3. Should provide clear indication of which signatures are still needed
4. Should support mobile access for resources moving between checkout points
5. Should provide status tracking of the demobilization process
6. Should alert to potential issues (e.g., missing signatures, travel safety)

### Integration Requirements

1. Should integrate with Resource Status Cards (ICS 219)
2. Should integrate with resource ordering and tracking systems
3. Should enable pre-population of resource information from existing data
4. Should support integration with time tracking systems
5. Should allow for data exchange with travel management systems
6. Should support integration with incident documentation systems

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should support digital signatures for checkout points
4. Should include version control for updates
5. Must comply with accessibility standards
6. Should enable tracking the physical location of forms in the checkout process
7. Must maintain data integrity during concurrent access
8. Should support barcode/QR code for resource identification
9. Should provide alerts for resources nearing planned demobilization
