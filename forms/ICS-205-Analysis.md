# ICS 205 - Incident Radio Communications Plan Analysis

## 1. Form Overview

### Form Name
ICS 205 - Incident Radio Communications Plan

### Purpose
The Incident Radio Communications Plan provides information on all radio frequency or trunked radio system talkgroup assignments for each operational period. It is a summary of information about available radio frequencies or talkgroups and their assignments, ensuring that incident responders can communicate effectively.

### Primary Users
- Communications Unit Leader (preparer)
- Planning Section Chief (reviewer)
- Incident Commander (approver)
- All personnel using radios at the incident
- Division/Group Supervisors
- Branch Directors
- Strike Team/Task Force Leaders

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics205_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics205_date_time_prepared | Date/Time Prepared | DateTime | Yes | Valid date/time | Date and time the form was prepared |
| ics205_operational_period | Operational Period | Complex | Yes | Valid date/time range | Time interval for which the form applies |
| ics205_basic_radio_channel_use | Basic Radio Channel Use | Complex | Yes | - | Detailed radio channel information |
| ics205_special_instructions | Special Instructions | Text | No | Multi-line | Additional information about radio usage |
| ics205_prepared_by | Prepared By | Complex | Yes | - | Information about the Communications Unit Leader |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics205_form_version | Form Version | Text | No | - | Version of the ICS 205 form being used |
| ics205_iap_page_number | IAP Page Number | Text | Yes | Format: "IAP Page ___" | Page number within the IAP |

### Repeatable Section Fields - Basic Radio Channel Use

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics205_zone_group | Zone Group | Text | No | - | Radio zone or group identifier |
| ics205_channel_number | Channel Number | Text | No | - | Channel number for incident radios |
| ics205_function | Function | Text | Yes | - | Net function (Command, Tactical, etc.) |
| ics205_channel_name | Channel Name/Talkgroup | Text | Yes | - | Common name for the channel or talkgroup |
| ics205_assignment | Assignment | Text | Yes | - | ICS Branch/Division/Group assignment |
| ics205_rx_freq | RX Frequency | Text | No | Format: xxx.xxxx N/W | Receive frequency with narrowband/wideband designation |
| ics205_rx_tone_nac | RX Tone/NAC | Text | No | - | Receive CTCSS tone or Network Access Code |
| ics205_tx_freq | TX Frequency | Text | No | Format: xxx.xxxx N/W | Transmit frequency with narrowband/wideband designation |
| ics205_tx_tone_nac | TX Tone/NAC | Text | No | - | Transmit CTCSS tone or Network Access Code |
| ics205_mode | Mode | Text | No | A, D, or M | Analog, Digital, or Mixed mode operation |
| ics205_remarks | Remarks | Text | No | - | Additional information about the channel |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS205-01**: Incident Name must be provided
2. **R-ICS205-02**: Date/Time Prepared must be a valid date and time
3. **R-ICS205-03**: Operational Period must be a valid date/time range
4. **R-ICS205-04**: At least one Radio Channel must be provided with Function, Channel Name, and Assignment
5. **R-ICS205-05**: If frequency information is provided, it must follow the specified format
6. **R-ICS205-06**: Mode must be one of: A (analog), D (digital), or M (mixed)
7. **R-ICS205-07**: Prepared By must include at minimum a name and signature
8. **R-ICS205-08**: All frequencies must be correctly formatted with N (narrowband) or W (wideband) designation if provided

### Form Lifecycle Rules

1. **L-ICS205-01**: The form is prepared by the Communications Unit Leader
2. **L-ICS205-02**: The form is given to the Planning Section Chief for inclusion in the IAP
3. **L-ICS205-03**: The form is duplicated and distributed with the IAP
4. **L-ICS205-04**: Information from the ICS 205 is placed on Assignment Lists (ICS 204)
5. **L-ICS205-05**: All completed original forms must be given to the Documentation Unit
6. **L-ICS205-06**: A new ICS 205 is created for each operational period or when there are significant changes to communications

### Conditional Requirements

1. **C-ICS205-01**: If a trunked radio system is being used, the form fields adapt to capture talkgroup information instead of conventional channel programming
2. **C-ICS205-02**: If using RX/TX frequencies, appropriate tone or NAC information should also be provided
3. **C-ICS205-03**: If special communications needs exist (e.g., cross-band repeaters, secure voice, encoders, private lines), they should be documented in Special Instructions
4. **C-ICS205-04**: If an incident within an incident exists, special instructions for handling those communications should be included

## 4. User Interface Layout

### Section Definitions

1. **Header Section** - Contains incident identification, preparation information, and operational period
2. **Radio Channel Table Section** - Tabular listing of all radio channel information
3. **Special Instructions Section** - Text area for additional communications instructions
4. **Footer Section** - Contains prepared by information

### Layout Specifications

- The form is designed as a one-page document, possibly extending to multiple pages if needed
- Radio Channel Table should be displayed as a table with multiple rows
- Radio Channel Table should accommodate several rows of channel information
- Special Instructions section should provide adequate space for detailed instructions

### Field Groupings

- Incident identification fields grouped together in the header
- Date/Time Prepared grouped with operational period fields
- Channel information grouped in rows in the Radio Channel table
- Technical parameters (frequencies, tones) grouped together within the table

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 205 form
2. **Update** - Modify information on an existing form
3. **Sign** - The Communications Unit Leader signs the completed form
4. **Print** - Generate a printable version of the form
5. **Share** - Distribute the form electronically
6. **Include in IAP** - Add to complete Incident Action Plan package
7. **Extract for ICS 204** - Transfer relevant communications information to Assignment Lists

### State Transitions

1. **Draft** → **Completed**: When the form is finished by Communications Unit Leader
2. **Completed** → **Published**: When included in distributed IAP
3. **Published** → **Archived**: When the operational period ends
4. **Any State** → **Superseded**: When replaced by a new version with updated information

### Access Control

1. Communications Unit Leader: Create, Update, Sign
2. Planning Section Chief: Review, Approve for IAP
3. Resources Unit Leader: View, Extract for ICS 204
4. Documentation Unit: Archive
5. IAP Recipients: View

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, times, and technical radio parameters
2. Must maintain relationship with other IAP components
3. Must preserve all versions throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data
6. Should maintain historical record of communications plans

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Must maintain consistent formatting across printed pages
3. Should support export to PDF and other common formats
4. Should support various output formats for inclusion in the IAP
5. Should provide a clear, readable format for radio operators in the field

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Should support quick entry of radio channel information
3. Should provide templates for common radio configurations
4. Should provide real-time validation of technical parameters
5. Should allow for cloning of similar channel entries
6. Should include frequency format validation
7. Should include channel/frequency conflict detection

### Integration Requirements

1. Should integrate with Assignment Lists (ICS 204)
2. Should integrate with Communications List (ICS 205A)
3. Should enable pre-population of incident information from existing data
4. Must support integration with other IAP components
5. Should support integration with radio programming software where applicable
6. Should allow for import/export of frequency databases

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should support digital signatures
4. Should include version control for communications plan updates
5. Must comply with accessibility standards
6. Should enable collaborative editing with appropriate access controls
7. Must maintain data integrity during concurrent access
8. Should support conversion between frequency formats (e.g., decimal MHz to channel numbers)
9. Should flag potential interference issues between assigned frequencies
