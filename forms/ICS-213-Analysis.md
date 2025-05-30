# ICS 213 - General Message Analysis

## 1. Form Overview

### Form Name
ICS 213 - General Message

### Purpose
The General Message form is used by incident dispatchers to record incoming messages that cannot be orally transmitted to the intended recipients. It is also used by the Incident Command Post and other incident personnel to transmit messages to the Incident Communications Center for transmission via radio or telephone to the addressee. This form is used to send any message or notification to incident personnel that requires hard-copy delivery.

### Primary Users
- Incident Dispatchers
- Incident Command Post personnel
- Command and General Staff
- All incident personnel needing to send written messages
- Incident Communications Center personnel
- Documentation Unit

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics213_incident_name | Incident Name | Text | No | Max 100 chars | Name assigned to the incident (optional on this form) |
| ics213_to | To | Complex | Yes | - | Recipient's name and position |
| ics213_from | From | Complex | Yes | - | Sender's name and position |
| ics213_subject | Subject | Text | Yes | - | Subject of the message |
| ics213_date | Date | Date | Yes | Valid date | Date the message was created |
| ics213_time | Time | Time | Yes | Valid time | Time the message was created |
| ics213_message | Message | Text | Yes | Multi-line | Content of the message |
| ics213_approved_by | Approved by | Complex | Yes | - | Information about the person approving the message |
| ics213_reply | Reply | Text | No | Multi-line | Response to the original message |
| ics213_replied_by | Replied by | Complex | No | - | Information about the person replying to the message |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics213_form_version | Form Version | Text | No | - | Version of the ICS 213 form being used |
| ics213_replied_date_time | Reply Date/Time | DateTime | No | Valid date/time | Date and time of the reply |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS213-01**: To (recipient) must be provided with at minimum a name and position
2. **R-ICS213-02**: From (sender) must be provided with at minimum a name and position
3. **R-ICS213-03**: Subject must be provided to clearly identify the purpose of the message
4. **R-ICS213-04**: Date and Time must be provided and valid
5. **R-ICS213-05**: Message content must be provided
6. **R-ICS213-06**: Approved by must include at minimum a name, position/title, and signature
7. **R-ICS213-07**: If a reply is provided, the Replied by field should include at minimum a name, position/title, and signature

### Form Lifecycle Rules

1. **L-ICS213-01**: The form may be initiated by incident dispatchers or any incident personnel
2. **L-ICS213-02**: The form is a three-part form, typically using carbon paper
3. **L-ICS213-03**: The sender completes Part 1 of the form and sends Parts 2 and 3 to the recipient
4. **L-ICS213-04**: The recipient completes Part 2 (reply) and returns Part 3 to the sender
5. **L-ICS213-05**: A copy of the ICS 213 should be sent to and maintained within the Documentation Unit
6. **L-ICS213-06**: Messages may be delivered physically or transmitted via radio or telephone by the Incident Communications Center

### Conditional Requirements

1. **C-ICS213-01**: If the message requires approval before transmission, the Approved by section should be completed
2. **C-ICS213-02**: If a reply is expected, the reply section should be completed by the recipient
3. **C-ICS213-03**: If the form is used for resource orders, additional contact information for sender and receiver may be added
4. **C-ICS213-04**: If the Incident Name is not provided, it should be clear from context which incident the message relates to

## 4. User Interface Layout

### Section Definitions

1. **Header Section** - Contains optional incident name, recipient and sender information, subject, date and time
2. **Message Section** - Contains the message content and approval information
3. **Reply Section** - Contains the reply content and reply signature information

### Layout Specifications

- The form is designed as a single-page document
- The form is typically a three-part carbon copy form
- Header section appears at the top of the form
- Message section occupies the middle portion of the form
- Reply section appears at the bottom of the form
- Adequate space should be provided for the message and reply

### Field Groupings

- Incident identification appears at the top
- Recipient and sender information grouped together
- Subject and date/time grouped together
- Approval information appears at the end of the message section
- Reply information and signature appear at the end of the reply section

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 213 form
2. **Complete Message** - Fill in the message portion of the form
3. **Approve** - Obtain approval signature if required
4. **Transmit** - Send the message to the recipient
5. **Reply** - Complete the reply section (by recipient)
6. **Return** - Return the completed form to the sender
7. **Document** - File a copy with the Documentation Unit

### State Transitions

1. **Blank** → **Message Drafted**: When message content is entered
2. **Message Drafted** → **Approved**: When signed by the approver (if required)
3. **Approved** → **Transmitted**: When sent to the recipient
4. **Transmitted** → **Received**: When received by the intended recipient
5. **Received** → **Replied**: When reply is completed by recipient
6. **Replied** → **Returned**: When returned to original sender
7. **Any State** → **Documented**: When copy is filed with Documentation Unit

### Access Control

1. Message Originator: Create, Complete Message
2. Approving Authority: Approve (when required)
3. Communications Center: Transmit
4. Recipient: Reply
5. Documentation Unit: Document/Archive

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, and times
2. Should maintain relationship between original message and reply
3. Should preserve all forms throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data
6. Should maintain record of message transmission and receipt

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Should support multi-part form printing (for carbon copy effect)
3. Should support export to PDF and other common formats
4. Should facilitate electronic transmission when appropriate
5. Should support fax or other alternative delivery methods when needed

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Should support rapid message creation during incident operations
3. Should provide clear distinction between message and reply sections
4. Should indicate when replies are pending
5. Should support electronic delivery tracking where applicable
6. Should provide templates for common message types

### Integration Requirements

1. Should integrate with incident communications systems
2. Should enable pre-population of incident information from existing data
3. Should support integration with electronic messaging systems when available
4. Should allow for tracking of message status (sent, delivered, replied)
5. Should integrate with Documentation Unit record-keeping system
6. Should support integration with Resource Request systems when used for that purpose

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should support digital signatures for approval fields
4. Should include version control for updates
5. Must comply with accessibility standards
6. Should provide both physical and electronic workflow options
7. Must maintain data integrity during transmission
8. Should support attachments or reference to other documents when needed
9. Should support urgent message flagging/prioritization
