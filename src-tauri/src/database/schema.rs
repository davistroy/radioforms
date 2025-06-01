/*!
 * Database schema definitions for RadioForms
 * 
 * This module contains the database schema for the STANDALONE ICS Forms
 * Management Application. The schema is designed for simplicity and follows
 * the "simpler is better" principle.
 * 
 * Business Logic:
 * - Simple table structure for easy maintenance
 * - JSON storage for form data flexibility
 * - Minimal foreign keys to reduce complexity
 * - Optimized for single-user operation
 * 
 * Design Decisions:
 * - Form data stored as JSON blob for flexibility
 * - Status enum ensures data consistency
 * - Timestamps for audit trail and sorting
 * - No complex relationships to maintain simplicity
 */

use sqlx::FromRow;
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use std::collections::HashMap;

/// Form status enumeration.
/// Represents the lifecycle of an ICS form from creation to finalization.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum FormStatus {
    /// Form is being created or edited
    Draft,
    /// Form has been completed but not finalized
    Completed,
    /// Form has been finalized and is read-only
    Final,
}

impl std::fmt::Display for FormStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            FormStatus::Draft => write!(f, "draft"),
            FormStatus::Completed => write!(f, "completed"),
            FormStatus::Final => write!(f, "final"),
        }
    }
}

impl std::str::FromStr for FormStatus {
    type Err = anyhow::Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "draft" => Ok(FormStatus::Draft),
            "completed" => Ok(FormStatus::Completed),
            "final" => Ok(FormStatus::Final),
            _ => Err(anyhow::anyhow!("Invalid form status: {}", s)),
        }
    }
}

impl TryFrom<String> for FormStatus {
    type Error = anyhow::Error;

    fn try_from(value: String) -> Result<Self, Self::Error> {
        value.parse()
    }
}

/// ICS Form type enumeration.
/// Represents the different types of ICS forms supported by the application.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum ICSFormType {
    ICS201, ICS202, ICS203, ICS204, ICS205, ICS205A, ICS206, ICS207,
    ICS208, ICS209, ICS210, ICS211, ICS213, ICS214, ICS215, ICS215A,
    ICS218, ICS220, ICS221, ICS225,
}

impl std::fmt::Display for ICSFormType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ICSFormType::ICS201 => write!(f, "ICS-201"),
            ICSFormType::ICS202 => write!(f, "ICS-202"),
            ICSFormType::ICS203 => write!(f, "ICS-203"),
            ICSFormType::ICS204 => write!(f, "ICS-204"),
            ICSFormType::ICS205 => write!(f, "ICS-205"),
            ICSFormType::ICS205A => write!(f, "ICS-205A"),
            ICSFormType::ICS206 => write!(f, "ICS-206"),
            ICSFormType::ICS207 => write!(f, "ICS-207"),
            ICSFormType::ICS208 => write!(f, "ICS-208"),
            ICSFormType::ICS209 => write!(f, "ICS-209"),
            ICSFormType::ICS210 => write!(f, "ICS-210"),
            ICSFormType::ICS211 => write!(f, "ICS-211"),
            ICSFormType::ICS213 => write!(f, "ICS-213"),
            ICSFormType::ICS214 => write!(f, "ICS-214"),
            ICSFormType::ICS215 => write!(f, "ICS-215"),
            ICSFormType::ICS215A => write!(f, "ICS-215A"),
            ICSFormType::ICS218 => write!(f, "ICS-218"),
            ICSFormType::ICS220 => write!(f, "ICS-220"),
            ICSFormType::ICS221 => write!(f, "ICS-221"),
            ICSFormType::ICS225 => write!(f, "ICS-225"),
        }
    }
}

impl std::str::FromStr for ICSFormType {
    type Err = anyhow::Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_uppercase().as_str() {
            "ICS-201" | "ICS201" => Ok(ICSFormType::ICS201),
            "ICS-202" | "ICS202" => Ok(ICSFormType::ICS202),
            "ICS-203" | "ICS203" => Ok(ICSFormType::ICS203),
            "ICS-204" | "ICS204" => Ok(ICSFormType::ICS204),
            "ICS-205" | "ICS205" => Ok(ICSFormType::ICS205),
            "ICS-205A" | "ICS205A" => Ok(ICSFormType::ICS205A),
            "ICS-206" | "ICS206" => Ok(ICSFormType::ICS206),
            "ICS-207" | "ICS207" => Ok(ICSFormType::ICS207),
            "ICS-208" | "ICS208" => Ok(ICSFormType::ICS208),
            "ICS-209" | "ICS209" => Ok(ICSFormType::ICS209),
            "ICS-210" | "ICS210" => Ok(ICSFormType::ICS210),
            "ICS-211" | "ICS211" => Ok(ICSFormType::ICS211),
            "ICS-213" | "ICS213" => Ok(ICSFormType::ICS213),
            "ICS-214" | "ICS214" => Ok(ICSFormType::ICS214),
            "ICS-215" | "ICS215" => Ok(ICSFormType::ICS215),
            "ICS-215A" | "ICS215A" => Ok(ICSFormType::ICS215A),
            "ICS-218" | "ICS218" => Ok(ICSFormType::ICS218),
            "ICS-220" | "ICS220" => Ok(ICSFormType::ICS220),
            "ICS-221" | "ICS221" => Ok(ICSFormType::ICS221),
            "ICS-225" | "ICS225" => Ok(ICSFormType::ICS225),
            _ => Err(anyhow::anyhow!("Unknown ICS form type: {}", s)),
        }
    }
}

impl TryFrom<String> for ICSFormType {
    type Error = anyhow::Error;

    fn try_from(value: String) -> Result<Self, Self::Error> {
        value.parse()
    }
}

/// Main form record structure.
/// 
/// Business Logic:
/// - Represents a single ICS form instance
/// - Form data stored as JSON for flexibility
/// - Simple status tracking for workflow management
/// - Timestamps for sorting and audit purposes
/// 
/// Design Notes:
/// - ID is auto-incrementing primary key
/// - JSON data field contains all form-specific fields
/// - Status enum ensures valid state transitions
/// - Notes field for user annotations
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Form {
    /// Unique identifier for the form (auto-increment primary key)
    pub id: i64,
    
    /// Type of ICS form (ICS-201, ICS-202, etc.) - stored as string
    form_type: String,
    
    /// Name of the incident this form relates to
    pub incident_name: String,
    
    /// Optional incident number for cross-referencing
    pub incident_number: Option<String>,
    
    /// Current status of the form (draft, completed, final) - stored as string
    status: String,
    
    /// Complete form data as JSON
    /// Contains all field values specific to the form type
    pub data: String, // JSON string
    
    /// Optional notes or comments about the form
    pub notes: Option<String>,
    
    /// Name of the person who prepared the form
    pub preparer_name: Option<String>,
    
    /// When the form was first created
    pub created_at: DateTime<Utc>,
    
    /// When the form was last modified
    pub updated_at: DateTime<Utc>,
}

impl Form {
    /// Gets the form type as an enum
    pub fn form_type(&self) -> anyhow::Result<ICSFormType> {
        self.form_type.parse()
    }
    
    /// Sets the form type from an enum
    pub fn set_form_type(&mut self, form_type: ICSFormType) {
        self.form_type = form_type.to_string();
    }
    
    /// Gets the status as an enum
    pub fn status(&self) -> anyhow::Result<FormStatus> {
        self.status.parse()
    }
    
    /// Sets the status from an enum
    pub fn set_status(&mut self, status: FormStatus) {
        self.status = status.to_string();
    }

    /// Parses the JSON data field into a structured HashMap.
    /// 
    /// Business Logic:
    /// - Provides type-safe access to form field data
    /// - Handles JSON parsing errors gracefully
    /// - Returns HashMap for flexible field access
    pub fn parse_data(&self) -> anyhow::Result<HashMap<String, serde_json::Value>> {
        serde_json::from_str(&self.data)
            .map_err(|e| anyhow::anyhow!("Failed to parse form data: {}", e))
    }

    /// Sets the form data from a HashMap.
    /// 
    /// Business Logic:
    /// - Converts structured data back to JSON string
    /// - Ensures data is properly serialized for storage
    /// - Updates the updated_at timestamp
    pub fn set_data(&mut self, data: HashMap<String, serde_json::Value>) -> anyhow::Result<()> {
        self.data = serde_json::to_string(&data)
            .map_err(|e| anyhow::anyhow!("Failed to serialize form data: {}", e))?;
        self.updated_at = Utc::now();
        Ok(())
    }

    /// Gets a specific field value from the form data.
    /// 
    /// Business Logic:
    /// - Provides convenient access to individual form fields
    /// - Returns None if field doesn't exist
    /// - Handles JSON parsing transparently
    pub fn get_field(&self, field_name: &str) -> anyhow::Result<Option<serde_json::Value>> {
        let data = self.parse_data()?;
        Ok(data.get(field_name).cloned())
    }

    /// Sets a specific field value in the form data.
    /// 
    /// Business Logic:
    /// - Allows updating individual fields without replacing all data
    /// - Automatically updates the updated_at timestamp
    /// - Preserves other field values
    pub fn set_field(&mut self, field_name: &str, value: serde_json::Value) -> anyhow::Result<()> {
        let mut data = self.parse_data()?;
        data.insert(field_name.to_string(), value);
        self.set_data(data)
    }

    /// Validates that required fields are present for the form type.
    /// 
    /// Business Logic:
    /// - Ensures form meets ICS standards before completion
    /// - Returns list of missing required fields
    /// - Form-type specific validation rules
    pub fn validate_required_fields(&self) -> anyhow::Result<Vec<String>> {
        let data = self.parse_data()?;
        let mut missing_fields = Vec::new();

        // Basic required fields for all forms
        let basic_required = vec!["incident_name", "date_prepared", "time_prepared"];
        
        for field in basic_required {
            if !data.contains_key(field) || data[field].is_null() {
                missing_fields.push(field.to_string());
            }
        }

        // Form-type specific validation could be added here
        // This would reference the ICS form specifications

        Ok(missing_fields)
    }

    /// Checks if the form can transition to the specified status.
    /// 
    /// Business Logic:
    /// - Enforces proper workflow transitions
    /// - Draft -> Completed -> Final (no backwards transitions)
    /// - Validates required fields before status changes
    pub fn can_transition_to(&self, new_status: &FormStatus) -> anyhow::Result<bool> {
        let current_status = self.status()?;
        match (&current_status, new_status) {
            // Can always stay in same status
            (current, new) if current == new => Ok(true),
            
            // Forward transitions
            (FormStatus::Draft, FormStatus::Completed) => {
                // Check if required fields are filled
                let missing = self.validate_required_fields()?;
                Ok(missing.is_empty())
            },
            (FormStatus::Completed, FormStatus::Final) => Ok(true),
            (FormStatus::Draft, FormStatus::Final) => {
                // Direct draft to final requires validation
                let missing = self.validate_required_fields()?;
                Ok(missing.is_empty())
            },
            
            // Backwards transitions not allowed
            _ => Ok(false),
        }
    }
}

/// Application settings storage.
/// 
/// Business Logic:
/// - Simple key-value storage for application preferences
/// - Used for user settings, default values, etc.
/// - Keeps settings portable with the application
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Setting {
    /// Setting key (unique identifier)
    pub key: String,
    
    /// Setting value (stored as JSON for flexibility)
    pub value: String,
    
    /// When the setting was last updated
    pub updated_at: DateTime<Utc>,
}

impl Setting {
    /// Creates a new setting with the given key and value.
    pub fn new(key: String, value: serde_json::Value) -> anyhow::Result<Self> {
        Ok(Self {
            key,
            value: serde_json::to_string(&value)?,
            updated_at: Utc::now(),
        })
    }

    /// Gets the setting value as a typed value.
    pub fn get_value<T>(&self) -> anyhow::Result<T> 
    where 
        T: for<'de> Deserialize<'de>
    {
        serde_json::from_str(&self.value)
            .map_err(|e| anyhow::anyhow!("Failed to deserialize setting value: {}", e))
    }

    /// Sets the setting value from a typed value.
    pub fn set_value<T>(&mut self, value: T) -> anyhow::Result<()>
    where 
        T: Serialize
    {
        self.value = serde_json::to_string(&value)?;
        self.updated_at = Utc::now();
        Ok(())
    }
}