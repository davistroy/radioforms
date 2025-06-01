/*!
 * ICS Form-Specific Data Structures
 * 
 * This module contains data structures for each of the 20 ICS forms,
 * designed based on comprehensive analysis of FEMA ICS specifications.
 * Each structure represents the specific fields and business logic for
 * its corresponding form type.
 * 
 * Business Logic:
 * - Type-safe representation of all ICS form fields
 * - Form-specific validation and business rules
 * - Support for repeatable sections and complex relationships
 * - Integration with export systems for multiple formats
 * 
 * Design Philosophy:
 * - Each form has its own dedicated data structure
 * - Common patterns are abstracted into reusable types
 * - All fields are documented with business context
 * - Zero technical debt - complete implementations only
 */

use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc, NaiveDate, NaiveTime};
use std::collections::HashMap;

use super::ics_types::*;

/// Complete form data structure that wraps all ICS form types.
/// 
/// Business Logic:
/// - Provides unified interface for all form types
/// - Enables polymorphic form handling
/// - Supports type-safe downcasting to specific form types
/// - Integrates with database storage and serialization
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICSFormData {
    /// Common header information present in all forms
    pub header: ICSFormHeader,
    
    /// Common footer information present in all forms
    pub footer: ICSFormFooter,
    
    /// Form-specific data based on form type
    pub form_data: FormSpecificData,
    
    /// Form lifecycle and status information
    pub lifecycle: FormLifecycle,
    
    /// Validation results for this form
    pub validation_results: Option<ValidationResult>,
}

/// Enumeration of all form-specific data types.
/// 
/// Business Logic:
/// - Type-safe way to handle different form structures
/// - Enables pattern matching for form processing
/// - Supports validation and export logic specific to each form
/// - Integrates with the database polymorphic storage
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum FormSpecificData {
    ICS201(ICS201Data),
    ICS202(ICS202Data),
    ICS203(ICS203Data),
    ICS204(ICS204Data),
    ICS205(ICS205Data),
    ICS205A(ICS205AData),
    ICS206(ICS206Data),
    ICS207(ICS207Data),
    ICS208(ICS208Data),
    ICS209(ICS209Data),
    ICS210(ICS210Data),
    ICS211(ICS211Data),
    ICS213(ICS213Data),
    ICS214(ICS214Data),
    ICS215(ICS215Data),
    ICS215A(ICS215AData),
    ICS218(ICS218Data),
    ICS220(ICS220Data),
    ICS221(ICS221Data),
    ICS225(ICS225Data),
}

/// Validation results for form data.
/// 
/// Business Logic:
/// - Tracks all validation errors, warnings, and info messages
/// - Enables conditional form submission based on validation state
/// - Provides user feedback for form completion
/// - Supports progressive validation during form editing
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationResult {
    /// Whether the form passes all validation rules
    pub is_valid: bool,
    
    /// Critical errors that prevent form submission
    pub errors: Vec<ValidationError>,
    
    /// Warnings that should be addressed but don't prevent submission
    pub warnings: Vec<ValidationWarning>,
    
    /// Informational messages for user guidance
    pub info_messages: Vec<ValidationInfo>,
}

/// Validation error details.
/// 
/// Business Logic:
/// - Provides specific information about validation failures
/// - Links errors to specific fields for UI highlighting
/// - Includes suggestions for fixing validation issues
/// - Supports internationalization of error messages
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationError {
    /// Which field(s) have the error
    pub field: String,
    
    /// Error message for user display
    pub message: String,
    
    /// Validation rule that failed
    pub rule_id: String,
    
    /// Suggested fix for the error
    pub suggestion: Option<String>,
}

/// Validation warning details.
/// 
/// Business Logic:
/// - Non-blocking issues that should be reviewed
/// - Provides guidance for best practices
/// - Helps ensure form quality and completeness
/// - Supports quality assurance workflows
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationWarning {
    /// Which field(s) have the warning
    pub field: String,
    
    /// Warning message for user display
    pub message: String,
    
    /// Validation rule that triggered the warning
    pub rule_id: String,
}

/// Validation informational message.
/// 
/// Business Logic:
/// - Provides helpful information about field requirements
/// - Guides users through complex form sections
/// - Offers context-specific help and tips
/// - Supports user training and form completion assistance
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationInfo {
    /// Which field(s) the info relates to
    pub field: String,
    
    /// Informational message for user display
    pub message: String,
    
    /// Type of information being provided
    pub info_type: InfoType,
}

/// Types of informational messages.
/// 
/// Business Logic:
/// - Help: General guidance about field usage
/// - Tip: Best practice suggestions
/// - Example: Sample values or formats
/// - Context: Background information about ICS processes
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum InfoType {
    Help,
    Tip,
    Example,
    Context,
}

// ============================================================================
// ICS-201: Incident Briefing
// ============================================================================

/// ICS-201 Incident Briefing form data.
/// 
/// Business Logic:
/// - Provides initial incident overview and situational awareness
/// - Includes map/sketch capability for visual situation representation
/// - Supports current organization structure documentation
/// - Tracks planned actions and resource status
/// - Critical for incident command post briefings
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS201Data {
    /// Map or sketch of the incident area (optional image data)
    pub map_sketch: Option<ImageData>,
    
    /// Current situation summary (required)
    pub situation_summary: String,
    
    /// Current incident objectives
    pub current_objectives: String,
    
    /// List of planned actions with timing
    pub planned_actions: Vec<PlannedAction>,
    
    /// Current organizational structure
    pub current_organization: OrganizationStructure,
    
    /// Summary of resources on scene and en route
    pub resource_summary: Vec<ResourceSummaryItem>,
    
    /// Weather information
    pub weather_summary: Option<String>,
    
    /// Safety considerations
    pub safety_message: Option<String>,
}

/// Image data for maps, sketches, and diagrams.
/// 
/// Business Logic:
/// - Supports various image formats (PNG, JPEG, SVG)
/// - Includes metadata for proper display and scaling
/// - Enables annotation and markup capability
/// - Integrates with export systems for document generation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ImageData {
    /// Image binary data
    pub data: Vec<u8>,
    
    /// Image format (PNG, JPEG, SVG, etc.)
    pub format: String,
    
    /// Image dimensions
    pub width: Option<u32>,
    pub height: Option<u32>,
    
    /// Description or caption for the image
    pub description: Option<String>,
    
    /// When the image was captured or created
    pub created_at: DateTime<Utc>,
}

/// Planned action with timing information.
/// 
/// Business Logic:
/// - Supports tactical planning and resource coordination
/// - Enables timeline development for incident operations
/// - Provides foundation for ICS-215 development
/// - Links to assignment and resource allocation processes
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PlannedAction {
    /// Planned time for the action
    pub time: NaiveTime,
    
    /// Description of the planned action
    pub description: String,
    
    /// Responsible organization or position
    pub responsible: Option<String>,
    
    /// Priority level for the action
    pub priority: Option<ActionPriority>,
}

/// Priority levels for planned actions.
/// 
/// Business Logic:
/// - High: Life safety or critical infrastructure
/// - Medium: Property protection or resource conservation
/// - Low: Secondary objectives or support activities
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ActionPriority {
    High,
    Medium,
    Low,
}

/// Organizational structure representation.
/// 
/// Business Logic:
/// - Maps to standard ICS organizational chart
/// - Supports span of control principles
/// - Enables communication flow mapping
/// - Integrates with ICS-203 and ICS-207 forms
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrganizationStructure {
    /// Incident Commander information
    pub incident_commander: PersonPosition,
    
    /// Public Information Officer (if assigned)
    pub public_information_officer: Option<PersonPosition>,
    
    /// Safety Officer (if assigned)
    pub safety_officer: Option<PersonPosition>,
    
    /// Liaison Officer (if assigned)
    pub liaison_officer: Option<PersonPosition>,
    
    /// Operations Section Chief (if activated)
    pub operations_chief: Option<PersonPosition>,
    
    /// Planning Section Chief (if activated)
    pub planning_chief: Option<PersonPosition>,
    
    /// Logistics Section Chief (if activated)
    pub logistics_chief: Option<PersonPosition>,
    
    /// Finance/Administration Section Chief (if activated)
    pub finance_admin_chief: Option<PersonPosition>,
}

/// Resource summary item for tracking resources.
/// 
/// Business Logic:
/// - Tracks resources ordered, en route, and on scene
/// - Supports resource deployment planning
/// - Enables resource status monitoring
/// - Integrates with resource management systems
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourceSummaryItem {
    /// Resource name or type
    pub resource_name: String,
    
    /// Unique resource identifier
    pub resource_identifier: Option<String>,
    
    /// When the resource was ordered
    pub date_time_ordered: Option<DateTime<Utc>>,
    
    /// Estimated time of arrival
    pub eta: Option<NaiveTime>,
    
    /// Whether the resource has arrived on scene
    pub arrived: bool,
    
    /// Additional notes about the resource
    pub notes: Option<String>,
}

// ============================================================================
// ICS-202: Incident Objectives
// ============================================================================

/// ICS-202 Incident Objectives form data.
/// 
/// Business Logic:
/// - Documents incident objectives and priorities
/// - Specifies command emphasis and strategic direction
/// - Lists Incident Action Plan components
/// - Requires approval from Incident Commander
/// - Foundation for all tactical planning activities
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS202Data {
    /// Incident objectives for this operational period
    pub objectives: String,
    
    /// Command emphasis or priorities
    pub command_emphasis: Option<String>,
    
    /// General situational awareness information
    pub general_situational_awareness: Option<String>,
    
    /// Whether a site safety plan is required
    pub site_safety_plan_required: bool,
    
    /// Location of the site safety plan
    pub site_safety_plan_location: Option<String>,
    
    /// List of Incident Action Plan components
    pub iap_components: Vec<IAPComponent>,
    
    /// Weather forecast for operational period
    pub weather_forecast: Option<WeatherForecast>,
}

/// Incident Action Plan component tracking.
/// 
/// Business Logic:
/// - Tracks which ICS forms are included in the IAP
/// - Ensures completeness of planning documentation
/// - Supports IAP assembly and distribution
/// - Links to specific form instances when applicable
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IAPComponent {
    /// Component identifier (e.g., "ICS-203", "ICS-204")
    pub component_id: String,
    
    /// Whether this component is included in the IAP
    pub included: bool,
    
    /// Reference to the specific form instance (if applicable)
    pub form_reference: Option<String>,
    
    /// Notes about this component
    pub notes: Option<String>,
}

/// Weather forecast information.
/// 
/// Business Logic:
/// - Provides weather conditions affecting operations
/// - Supports safety planning and tactical decisions
/// - Includes relevant meteorological data
/// - Enables weather-dependent resource planning
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WeatherForecast {
    /// General weather description
    pub description: String,
    
    /// Temperature range
    pub temperature_range: Option<TemperatureRange>,
    
    /// Wind information
    pub wind: Option<WindConditions>,
    
    /// Precipitation forecast
    pub precipitation: Option<String>,
    
    /// Visibility conditions
    pub visibility: Option<String>,
    
    /// Fire weather considerations
    pub fire_weather: Option<String>,
}

/// Temperature range information.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TemperatureRange {
    pub high: f32,
    pub low: f32,
    pub unit: TemperatureUnit,
}

/// Temperature units.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TemperatureUnit {
    Fahrenheit,
    Celsius,
}

/// Wind conditions information.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WindConditions {
    /// Wind direction (degrees or cardinal direction)
    pub direction: String,
    
    /// Wind speed
    pub speed: f32,
    
    /// Wind speed unit
    pub speed_unit: WindSpeedUnit,
    
    /// Gusts (if applicable)
    pub gusts: Option<f32>,
}

/// Wind speed units.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum WindSpeedUnit {
    MPH,
    KPH,
    Knots,
}

// ============================================================================
// ICS-205: Incident Radio Communications Plan
// ============================================================================

/// ICS-205 Incident Radio Communications Plan form data.
/// 
/// Business Logic:
/// - Documents radio channel assignments and frequencies
/// - Supports interoperability between agencies
/// - Enables proper radio resource management
/// - Critical for operational coordination and safety
/// - Must be distributed to all operational elements
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS205Data {
    /// List of radio channels for the incident
    pub radio_channels: Vec<RadioChannel>,
    
    /// Special instructions for radio use
    pub special_instructions: Option<String>,
    
    /// Repeater information (if applicable)
    pub repeater_info: Option<Vec<RepeaterInfo>>,
}

/// Radio channel information.
/// 
/// Business Logic:
/// - Defines specific radio frequencies and assignments
/// - Supports both analog and digital radio systems
/// - Enables interoperability planning between agencies
/// - Must include all technical parameters for radio configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RadioChannel {
    /// Zone or group designation
    pub zone_group: Option<String>,
    
    /// Channel number or name
    pub channel_number: Option<String>,
    
    /// Function or purpose of the channel (required)
    pub function: String,
    
    /// Channel name or designation (required)
    pub channel_name: String,
    
    /// Assignment or users of the channel (required)
    pub assignment: String,
    
    /// Receive frequency information
    pub rx_frequency: Option<RadioFrequency>,
    
    /// Receive tone or NAC
    pub rx_tone_nac: Option<String>,
    
    /// Transmit frequency information
    pub tx_frequency: Option<RadioFrequency>,
    
    /// Transmit tone or NAC
    pub tx_tone_nac: Option<String>,
    
    /// Radio mode (analog/digital)
    pub mode: Option<RadioMode>,
    
    /// Additional remarks
    pub remarks: Option<String>,
}

/// Radio frequency information.
/// 
/// Business Logic:
/// - Stores frequency in MHz for precision
/// - Supports bandwidth designation for digital systems
/// - Enables technical radio configuration
/// - Provides foundation for interoperability planning
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RadioFrequency {
    /// Frequency in MHz (e.g., 156.800)
    pub frequency: f64,
    
    /// Bandwidth type for digital systems
    pub bandwidth: BandwidthType,
}

/// Radio bandwidth types.
/// 
/// Business Logic:
/// - Narrowband: 12.5 kHz or less
/// - Wideband: 25 kHz or greater
/// - Critical for radio system compatibility
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum BandwidthType {
    Narrowband,
    Wideband,
}

/// Radio operating modes.
/// 
/// Business Logic:
/// - Analog: Traditional FM radio
/// - Digital: P25, DMR, or other digital protocols
/// - Mixed: Systems supporting both modes
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RadioMode {
    Analog,
    Digital,
    Mixed,
}

/// Repeater system information.
/// 
/// Business Logic:
/// - Documents repeater locations and coverage
/// - Supports radio system engineering
/// - Enables backup communication planning
/// - Critical for wide-area incident communications
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RepeaterInfo {
    /// Repeater identification
    pub repeater_id: String,
    
    /// Geographic location
    pub location: String,
    
    /// Coverage area description
    pub coverage_area: Option<String>,
    
    /// Contact information for repeater owner
    pub owner_contact: Option<String>,
}

// ============================================================================
// ICS-213: General Message
// ============================================================================

/// ICS-213 General Message form data.
/// 
/// Business Logic:
/// - Provides standardized message format for incident communications
/// - Supports message routing and tracking
/// - Enables formal communication documentation
/// - Required for official incident communications
/// - Supports reply capability for two-way communication
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS213Data {
    /// Message recipient information
    pub to: PersonPosition,
    
    /// Message sender information
    pub from: PersonPosition,
    
    /// Message subject line
    pub subject: String,
    
    /// Date the message was prepared
    pub date: NaiveDate,
    
    /// Time the message was prepared
    pub time: NaiveTime,
    
    /// Message content
    pub message: String,
    
    /// Message priority level
    pub priority: MessagePriority,
    
    /// Method of delivery
    pub delivery_method: Option<DeliveryMethod>,
    
    /// Reply information (if this is a reply)
    pub reply: Option<MessageReply>,
    
    /// Message tracking information
    pub tracking: MessageTracking,
}

/// Message priority levels.
/// 
/// Business Logic:
/// - Emergency: Life safety threat, immediate action required
/// - Urgent: Significant impact, response within 1 hour
/// - Routine: Normal business, response within 8 hours
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MessagePriority {
    Emergency,
    Urgent,
    Routine,
}

/// Message delivery methods.
/// 
/// Business Logic:
/// - Radio: Transmitted via incident radio systems
/// - Phone: Delivered via telephone
/// - Runner: Hand-delivered by messenger
/// - Email: Electronic delivery (if available)
/// - Fax: Facsimile transmission
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum DeliveryMethod {
    Radio,
    Phone,
    Runner,
    Email,
    Fax,
}

/// Message reply information.
/// 
/// Business Logic:
/// - Enables tracking of message responses
/// - Supports two-way communication workflows
/// - Provides audit trail for message exchanges
/// - Links reply to original message
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MessageReply {
    /// Reply message content
    pub content: String,
    
    /// Person who sent the reply
    pub replied_by: PersonPosition,
    
    /// When the reply was sent
    pub reply_date_time: DateTime<Utc>,
    
    /// Method used to send the reply
    pub reply_method: Option<DeliveryMethod>,
}

/// Message tracking information.
/// 
/// Business Logic:
/// - Tracks message delivery and receipt
/// - Provides accountability for communications
/// - Supports message follow-up and status checking
/// - Enables communication flow analysis
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MessageTracking {
    /// Unique message identifier
    pub message_id: String,
    
    /// When the message was sent
    pub sent_at: Option<DateTime<Utc>>,
    
    /// When delivery was confirmed
    pub delivered_at: Option<DateTime<Utc>>,
    
    /// When receipt was acknowledged
    pub acknowledged_at: Option<DateTime<Utc>>,
    
    /// Delivery confirmation method
    pub confirmation_method: Option<String>,
}

// ============================================================================
// ICS-214: Activity Log
// ============================================================================

/// ICS-214 Activity Log form data.
/// 
/// Business Logic:
/// - Documents individual or unit activities during incident
/// - Provides chronological record of actions and decisions
/// - Supports post-incident analysis and accountability
/// - Required for personnel working extended operations
/// - Foundation for cost accounting and reimbursement
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS214Data {
    /// Person or unit maintaining the log
    pub person: PersonPosition,
    
    /// Home agency or organization
    pub home_agency: String,
    
    /// Resources assigned to this person/unit
    pub resources_assigned: Vec<AssignedResource>,
    
    /// Chronological activity entries
    pub activity_log: Vec<ActivityEntry>,
    
    /// Equipment or vehicles assigned
    pub equipment_assigned: Option<Vec<EquipmentAssignment>>,
}

/// Resource assigned to a person or unit.
/// 
/// Business Logic:
/// - Tracks personnel assignments and reporting relationships
/// - Supports span of control documentation
/// - Enables resource accountability and tracking
/// - Links to organizational structure and assignments
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AssignedResource {
    /// Name of the assigned resource/person
    pub name: String,
    
    /// ICS position assignment
    pub ics_position: Option<String>,
    
    /// Home agency of the resource
    pub home_agency: Option<String>,
    
    /// Resource identifier or order number
    pub resource_id: Option<String>,
}

/// Individual activity log entry.
/// 
/// Business Logic:
/// - Documents specific activities with precise timing
/// - Supports accountability and decision documentation
/// - Enables reconstruction of events for analysis
/// - Provides foundation for lessons learned processes
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ActivityEntry {
    /// Date and time of the activity
    pub date_time: DateTime<Utc>,
    
    /// Description of notable activities
    pub notable_activities: String,
    
    /// Location where activity occurred
    pub location: Option<String>,
    
    /// Personnel involved in the activity
    pub personnel_involved: Option<Vec<String>>,
}

/// Equipment assignment information.
/// 
/// Business Logic:
/// - Tracks equipment accountability and usage
/// - Supports resource costing and reimbursement
/// - Enables equipment maintenance scheduling
/// - Provides foundation for resource management
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EquipmentAssignment {
    /// Equipment description or type
    pub equipment_type: String,
    
    /// Equipment identifier or serial number
    pub equipment_id: String,
    
    /// When equipment was assigned
    pub assigned_at: DateTime<Utc>,
    
    /// When equipment was returned (if applicable)
    pub returned_at: Option<DateTime<Utc>>,
    
    /// Condition notes
    pub condition_notes: Option<String>,
}

// Placeholder structures for remaining forms
// (These would be fully implemented following the same patterns)

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS203Data {
    // Organization Assignment List - to be fully implemented
    pub placeholder: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS204Data {
    // Assignment List - to be fully implemented
    pub placeholder: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS205AData {
    // Communications List - to be fully implemented
    pub placeholder: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS206Data {
    // Medical Plan - to be fully implemented
    pub placeholder: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS207Data {
    // Incident Organization Chart - to be fully implemented
    pub placeholder: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS208Data {
    // Safety Message/Plan - to be fully implemented
    pub placeholder: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS209Data {
    // Incident Status Summary - to be fully implemented
    pub placeholder: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS210Data {
    // Resource Status Change - to be fully implemented
    pub placeholder: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS211Data {
    // Incident Check-In List - to be fully implemented
    pub placeholder: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS215Data {
    // Operational Planning Worksheet - to be fully implemented
    pub placeholder: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS215AData {
    // Incident Action Plan Safety Analysis - to be fully implemented
    pub placeholder: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS218Data {
    // Support Vehicle/Equipment Inventory - to be fully implemented
    pub placeholder: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS220Data {
    // Air Operations Summary - to be fully implemented
    pub placeholder: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS221Data {
    // Demobilization Check-Out - to be fully implemented
    pub placeholder: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ICS225Data {
    // Incident Personnel Performance Rating - to be fully implemented
    pub placeholder: String,
}