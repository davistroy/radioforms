# ICS 225 - Incident Personnel Performance Rating Analysis

## 1. Form Overview

### Form Name
ICS 225 - Incident Personnel Performance Rating

### Purpose
The Incident Personnel Performance Rating form provides a mechanism to evaluate performance of assigned incident personnel for the specified operational period, using a standardized assessment system with defined rating categories. It is primarily used for personnel assigned in supervisory positions and documents both satisfactory and unsatisfactory performance.

### Primary Users
- Supervisors (preparers)
- Incident personnel being evaluated
- Incident Commander/Unified Command
- Planning Section (Documentation Unit)
- Agency-specific personnel departments
- Home unit supervisors

## 2. Data Model

### Core Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics225_incident_name | Incident Name | Text | Yes | Max 100 chars | Name assigned to the incident |
| ics225_incident_number | Incident Number | Text | No | Max 50 chars | Number assigned to the incident |
| ics225_operational_period | Operational Period | Complex | Yes | Valid date/time range | Time interval for which the evaluation applies |
| ics225_individual_info | Individual Information | Complex | Yes | - | Information about the person being evaluated |
| ics225_position_info | Position Information | Complex | Yes | - | Details about the position held during evaluation |
| ics225_ratings | Performance Ratings | Complex | Yes | - | Evaluation ratings across multiple categories |
| ics225_narrative | Narrative Evaluation | Text | Yes | Multi-line | Descriptive assessment of performance |
| ics225_prepared_by | Prepared By | Complex | Yes | - | Information about the evaluator |
| ics225_individual_rated | Individual Rated | Complex | Yes | - | Acknowledgment by the person being evaluated |

### Metadata Fields

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics225_form_version | Form Version | Text | No | - | Version of the ICS 225 form being used |
| ics225_prepared_date_time | Preparation Date/Time | DateTime | Yes | Valid date/time | Date and time the form was prepared |

### Repeatable Section Fields - Individual Information

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics225_name | Name | Text | Yes | - | Full name of the individual being evaluated |
| ics225_home_unit | Home Unit/Agency | Text | Yes | - | The individual's normal work organization |
| ics225_home_position | Position Held on Home Unit | Text | Yes | - | Normal position at home unit/agency |
| ics225_home_phone | Phone Number | Text | Yes | - | Contact information for follow-up |

### Repeatable Section Fields - Position Information

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics225_incident_position | Incident Position | Text | Yes | - | Position held during incident assignment |
| ics225_incident_date_from | Date(s) of Assignment (From) | Date | Yes | Valid date | Start date of assignment |
| ics225_incident_date_to | Date(s) of Assignment (To) | Date | Yes | Valid date | End date of assignment |
| ics225_incident_activity | Incident Activity Description | Text | No | Multi-line | Brief description of incident activity |

### Repeatable Section Fields - Performance Ratings

| Field ID | Name | Data Type | Required | Constraints | Description |
|----------|------|-----------|----------|------------|-------------|
| ics225_knowledge_position | Knowledge of the Job/ Professional Competence | Enum | Yes | 0-5 scale | Rating of job knowledge |
| ics225_ability_objectives | Ability to Obtain Performance/Results | Enum | Yes | 0-5 scale | Rating of performance outcomes |
| ics225_ability_work | Ability to Work on a Team | Enum | Yes | 0-5 scale | Rating of teamwork ability |
| ics225_attitude | Attitude | Enum | Yes | 0-5 scale | Rating of attitude toward assignment |
| ics225_compliance_work | Compliance with Work Schedule | Enum | Yes | 0-5 scale | Rating of attendance and punctuality |
| ics225_communication_skills | Communication Skills | Enum | Yes | 0-5 scale | Rating of communication effectiveness |
| ics225_ability_supervise | Ability to Supervise Others | Enum | No | 0-5 scale | Rating of supervisory skills if applicable |
| ics225_judgment_decisions | Judgment/Decisions Under Stress | Enum | Yes | 0-5 scale | Rating of decision-making under pressure |
| ics225_consideration_safety | Consideration for Personnel Welfare/Safety | Enum | Yes | 0-5 scale | Rating of safety consciousness |
| ics225_equipment_use | Equipment Use | Enum | No | 0-5 scale | Rating of equipment usage if applicable |
| ics225_other_rating | Other | Complex | No | - | Additional rating category if needed |
| ics225_other_rating_explanation | Other Rating Explanation | Text | No | - | Description of other rating category |

## 3. Business Rules and Validation

### Validation Rules

1. **R-ICS225-01**: Incident Name must be provided
2. **R-ICS225-02**: Operational Period must be a valid date/time range
3. **R-ICS225-03**: Individual's Name, Home Unit, Position, and Phone must be provided
4. **R-ICS225-04**: Incident Position and Dates of Assignment must be provided
5. **R-ICS225-05**: Performance Ratings must be provided for all required categories
6. **R-ICS225-06**: Rating values must be within the defined scale (0-5 or N/A)
7. **R-ICS225-07**: Narrative Evaluation must be provided with substantive content
8. **R-ICS225-08**: Prepared By must include at minimum a name, position/title, and signature
9. **R-ICS225-09**: Ratings of 1 or 5 should be explained in the narrative
10. **R-ICS225-10**: If "Other" rating category is used, an explanation must be provided

### Form Lifecycle Rules

1. **L-ICS225-01**: The form is completed by a supervisor who directly observed the individual
2. **L-ICS225-02**: The form is normally completed near the end of the individual's assignment
3. **L-ICS225-03**: The evaluation is discussed with the individual being rated
4. **L-ICS225-04**: The Individual Rated section is signed by the person being evaluated
5. **L-ICS225-05**: A copy may be provided to the individual being evaluated
6. **L-ICS225-06**: The original form is given to the Documentation Unit
7. **L-ICS225-07**: A copy may be forwarded to the individual's home agency or supervisor
8. **L-ICS225-08**: The form may become part of the individual's personnel record

### Conditional Requirements

1. **C-ICS225-01**: If a rating of 1 (Unacceptable) is given, specific explanation is required in the narrative
2. **C-ICS225-02**: If a rating of 5 (Exceeded Expectations) is given, specific examples should be included
3. **C-ICS225-03**: If "Ability to Supervise Others" is rated, the individual must have had supervisory duties
4. **C-ICS225-04**: If "Equipment Use" is rated, the individual must have used equipment in their position
5. **C-ICS225-05**: If "N/A" is marked for any category, explanation should be included in the narrative
6. **C-ICS225-06**: If individual disagrees with the evaluation, they may note this when signing

## 4. User Interface Layout

### Section Definitions

1. **Header Section** - Contains incident identification and operational period
2. **Individual Information Section** - Contains details about the person being evaluated
3. **Position Information Section** - Contains information about the incident assignment
4. **Rating Scale Section** - Contains explanation of the rating scale
5. **Performance Rating Section** - Contains tabular ratings across categories
6. **Narrative Section** - Contains text evaluation of performance
7. **Signature Section** - Contains evaluator and evaluated person's signatures

### Layout Specifications

- The form is designed as a two-page document
- Header section appears at the top of the first page
- Individual and Position Information sections appear below the header
- Rating Scale explanation appears before the Performance Rating section
- Performance Rating section should be displayed as a tabular format with rating options
- Narrative section should provide adequate space for detailed comments
- Signature section appears at the bottom of the form

### Field Groupings

- Incident identification fields grouped together in the header
- Operational period fields (from/to) grouped together
- Individual identification fields grouped together
- Position and assignment information grouped together
- Performance ratings grouped by category
- Signatures grouped at the bottom of the form

## 5. Actions and Operations

### Available Operations

1. **Create** - Initialize a new ICS 225 form for a specific individual
2. **Complete Ratings** - Fill in performance ratings for all categories
3. **Document Narrative** - Provide detailed comments about performance
4. **Discuss** - Review the evaluation with the individual being rated
5. **Sign** - Obtain signatures from both evaluator and individual
6. **Print** - Generate a printable version of the form
7. **Share** - Distribute copies to appropriate parties
8. **Archive** - Store the completed form with Documentation Unit

### State Transitions

1. **Blank** → **In Progress**: When a supervisor begins the evaluation
2. **In Progress** → **Completed**: When all ratings and narrative are completed
3. **Completed** → **Reviewed**: When discussed with the individual
4. **Reviewed** → **Signed**: When both parties have signed the form
5. **Signed** → **Distributed**: When copies are provided to appropriate parties
6. **Distributed** → **Archived**: When filed by Documentation Unit

### Access Control

1. Supervisor/Evaluator: Create, Complete Ratings, Document Narrative
2. Individual Being Evaluated: Review, Sign (acknowledge)
3. Incident Commander: View
4. Documentation Unit: Archive
5. Home Unit/Agency: Receive copy if forwarded

## 6. Technology-Agnostic Requirements

### Data Storage Requirements

1. Must support structured storage of text, dates, and numeric rating values
2. Must maintain relationship between evaluation and individual
3. Should preserve all forms throughout incident lifecycle
4. Should support both online and offline access to form data
5. Must support backup and recovery of form data
6. Should maintain confidentiality appropriate for personnel evaluations

### Print and Export Requirements

1. Must generate standard 8.5" x 11" printable output
2. Must maintain clear formatting of rating scale and categories
3. Should support export to PDF and other common formats
4. Should facilitate printing of copies for individual, Documentation Unit, and home unit
5. Should support physical signatures or secure electronic signature alternatives

### User Experience Requirements

1. Must provide intuitive data entry interface for all fields
2. Should support consistent application of rating scale
3. Should provide clear indicators for required fields
4. Should provide adequate space for narrative comments
5. Should facilitate discussion of the evaluation
6. Should provide guidance for completing evaluations effectively

### Integration Requirements

1. Should integrate with incident personnel tracking systems
2. Should enable pre-population of individual and incident information
3. Should support integration with agency personnel systems when appropriate
4. Should allow for aggregated analysis of performance data at the incident level
5. Should support secure transmission to home units when needed
6. Should integrate with Documentation Unit records management

### Implementation Considerations

1. Must support multiple platforms (mobile, tablet, desktop)
2. Should function in limited-connectivity environments
3. Should support digital signatures with appropriate security
4. Should include version control for updates
5. Must comply with accessibility standards
6. Must comply with applicable privacy regulations
7. Should maintain data confidentiality during transmission
8. Should provide templates or guidance for writing effective evaluations
9. Should enable supervisors to save draft evaluations
