/*!
 * Template Parser for JSON Form Templates
 * 
 * This module provides comprehensive parsing and validation of JSON form templates.
 * It converts raw JSON template data into validated, type-safe structures ready
 * for form generation and validation.
 * 
 * Business Logic:
 * - JSON template parsing with comprehensive error handling
 * - Template structure validation and integrity checking
 * - Field type validation and normalization
 * - Conditional logic validation and optimization
 * - Performance-optimized parsing for runtime use
 * 
 * Design Philosophy:
 * - Fail-fast validation with detailed error messages
 * - Type-safe parsing with comprehensive validation
 * - Performance-optimized for frequent template access
 * - Extensible parser architecture for new field types
 * - Production-ready error handling and logging
 */

use anyhow::{Result, Context, anyhow};
use serde_json;
use std::collections::{HashMap, HashSet};
use log::{debug, warn, error};

use super::schema::*;

/// Template parser for converting JSON to validated template structures.
/// 
/// Business Logic:
/// - Parses JSON templates with comprehensive validation
/// - Validates template structure and field definitions
/// - Checks conditional logic consistency
/// - Optimizes templates for runtime performance
pub struct TemplateParser {
    /// Validation configuration
    validation_config: ValidationConfig,
    
    /// Field type registry for extensibility
    field_type_registry: FieldTypeRegistry,
}

impl TemplateParser {
    /// Creates a new template parser with default configuration.
    pub fn new() -> Self {
        Self {
            validation_config: ValidationConfig::default(),
            field_type_registry: FieldTypeRegistry::default(),
        }
    }
    
    /// Creates a template parser with custom configuration.
    pub fn with_config(config: ValidationConfig) -> Self {
        Self {
            validation_config: config,
            field_type_registry: FieldTypeRegistry::default(),
        }
    }
    
    /// Parses a JSON template string into a validated FormTemplate.
    /// 
    /// Business Logic:
    /// - Deserializes JSON with comprehensive error handling
    /// - Validates template structure and content
    /// - Checks field type compatibility and configuration
    /// - Validates conditional logic consistency
    /// - Returns detailed error information for debugging
    pub fn parse_template(&self, json_content: &str) -> Result<FormTemplate> {
        debug!("Starting template parsing for {} bytes of JSON", json_content.len());
        
        // Parse JSON with detailed error context
        let template: FormTemplate = serde_json::from_str(json_content)
            .context("Failed to parse JSON template - check syntax and structure")?;
        
        // Validate template structure
        self.validate_template_structure(&template)
            .context("Template structure validation failed")?;
        
        // Validate fields and field types
        self.validate_template_fields(&template)
            .context("Template field validation failed")?;
        
        // Validate conditional logic
        self.validate_conditional_logic(&template)
            .context("Template conditional logic validation failed")?;
        
        // Validate cross-references
        self.validate_cross_references(&template)
            .context("Template cross-reference validation failed")?;
        
        debug!("Template parsing completed successfully for form type: {}", template.form_type);
        Ok(template)
    }
    
    /// Validates the overall template structure.
    fn validate_template_structure(&self, template: &FormTemplate) -> Result<()> {
        // Validate required fields
        if template.template_id.is_empty() {
            return Err(anyhow!("Template ID cannot be empty"));
        }
        
        if template.form_type.is_empty() {
            return Err(anyhow!("Form type cannot be empty"));
        }
        
        if template.version.is_empty() {
            return Err(anyhow!("Template version cannot be empty"));
        }
        
        if template.title.is_empty() {
            return Err(anyhow!("Template title cannot be empty"));
        }
        
        // Validate version format
        if !self.is_valid_version(&template.version) {
            return Err(anyhow!("Invalid version format: {}", template.version));
        }
        
        // Validate form type format
        if !self.is_valid_form_type(&template.form_type) {
            return Err(anyhow!("Invalid form type: {}", template.form_type));
        }
        
        // Validate sections exist
        if template.sections.is_empty() {
            return Err(anyhow!("Template must contain at least one section"));
        }
        
        Ok(())
    }
    
    /// Validates all fields in the template.
    fn validate_template_fields(&self, template: &FormTemplate) -> Result<()> {
        let mut field_ids = HashSet::new();
        let mut section_ids = HashSet::new();
        
        for section in &template.sections {
            self.validate_section(section, &mut field_ids, &mut section_ids)?;
        }
        
        // Validate that all default values reference valid fields
        for (field_id, _) in &template.defaults {
            if !field_ids.contains(field_id) {
                return Err(anyhow!("Default value references unknown field: {}", field_id));
            }
        }
        
        Ok(())
    }
    
    /// Validates a single section and its fields.
    fn validate_section(
        &self,
        section: &FormSection,
        field_ids: &mut HashSet<String>,
        section_ids: &mut HashSet<String>,
    ) -> Result<()> {
        // Validate section ID uniqueness
        if section.section_id.is_empty() {
            return Err(anyhow!("Section ID cannot be empty"));
        }
        
        if section_ids.contains(&section.section_id) {
            return Err(anyhow!("Duplicate section ID: {}", section.section_id));
        }
        section_ids.insert(section.section_id.clone());
        
        // Validate section title
        if section.title.is_empty() {
            return Err(anyhow!("Section title cannot be empty for section: {}", section.section_id));
        }
        
        // Validate repetition settings
        if section.repeatable && section.max_repetitions.is_some() {
            let max_reps = section.max_repetitions.unwrap();
            if max_reps == 0 {
                return Err(anyhow!("Max repetitions must be greater than 0 for section: {}", section.section_id));
            }
        }
        
        // Validate fields
        for field in &section.fields {
            self.validate_field(field, field_ids)?;
        }
        
        // Validate subsections recursively
        for subsection in &section.subsections {
            self.validate_section(subsection, field_ids, section_ids)?;
        }
        
        Ok(())
    }
    
    /// Validates a single field.
    fn validate_field(&self, field: &FormField, field_ids: &mut HashSet<String>) -> Result<()> {
        // Validate field ID uniqueness
        if field.field_id.is_empty() {
            return Err(anyhow!("Field ID cannot be empty"));
        }
        
        if field_ids.contains(&field.field_id) {
            return Err(anyhow!("Duplicate field ID: {}", field.field_id));
        }
        field_ids.insert(field.field_id.clone());
        
        // Validate field label
        if field.label.is_empty() {
            return Err(anyhow!("Field label cannot be empty for field: {}", field.field_id));
        }
        
        // Validate field type
        self.validate_field_type(&field.field_type, &field.field_id)?;
        
        // Validate default value compatibility
        if let Some(ref default_value) = field.default_value {
            self.validate_field_value_compatibility(&field.field_type, default_value, &field.field_id)?;
        }
        
        // Validate validation rules
        for rule in &field.validation_rules {
            self.validate_validation_rule(rule, &field.field_type, &field.field_id)?;
        }
        
        Ok(())
    }
    
    /// Validates a field type configuration.
    fn validate_field_type(&self, field_type: &FieldType, field_id: &str) -> Result<()> {
        match field_type {
            FieldType::Text { max_length, min_length, .. } => {
                if let (Some(min), Some(max)) = (min_length, max_length) {
                    if min > max {
                        return Err(anyhow!("Min length cannot be greater than max length for field: {}", field_id));
                    }
                }
            },
            
            FieldType::Textarea { max_length, rows, cols } => {
                if let Some(max) = max_length {
                    if *max == 0 {
                        return Err(anyhow!("Max length must be greater than 0 for field: {}", field_id));
                    }
                }
                if let Some(r) = rows {
                    if *r == 0 {
                        return Err(anyhow!("Rows must be greater than 0 for field: {}", field_id));
                    }
                }
                if let Some(c) = cols {
                    if *c == 0 {
                        return Err(anyhow!("Cols must be greater than 0 for field: {}", field_id));
                    }
                }
            },
            
            FieldType::Number { min, max, step, decimal_places } => {
                if let (Some(min_val), Some(max_val)) = (min, max) {
                    if min_val > max_val {
                        return Err(anyhow!("Min value cannot be greater than max value for field: {}", field_id));
                    }
                }
                if let Some(step_val) = step {
                    if *step_val <= 0.0 {
                        return Err(anyhow!("Step must be greater than 0 for field: {}", field_id));
                    }
                }
                if let Some(decimal) = decimal_places {
                    if *decimal > 10 {
                        warn!("Decimal places > 10 may cause precision issues for field: {}", field_id);
                    }
                }
            },
            
            FieldType::Select { options, .. } => {
                if options.is_empty() {
                    return Err(anyhow!("Select field must have at least one option for field: {}", field_id));
                }
                
                let mut values = HashSet::new();
                for option in options {
                    if values.contains(&option.value) {
                        return Err(anyhow!("Duplicate option value '{}' for field: {}", option.value, field_id));
                    }
                    values.insert(&option.value);
                }
            },
            
            FieldType::Radio { options, .. } => {
                if options.is_empty() {
                    return Err(anyhow!("Radio field must have at least one option for field: {}", field_id));
                }
                
                let mut values = HashSet::new();
                for option in options {
                    if values.contains(&option.value) {
                        return Err(anyhow!("Duplicate option value '{}' for field: {}", option.value, field_id));
                    }
                    values.insert(&option.value);
                }
            },
            
            FieldType::Checkbox { options, .. } => {
                if options.is_empty() {
                    return Err(anyhow!("Checkbox field must have at least one option for field: {}", field_id));
                }
            },
            
            FieldType::File { max_size_mb, .. } => {
                if let Some(size) = max_size_mb {
                    if *size == 0 {
                        return Err(anyhow!("Max file size must be greater than 0 for field: {}", field_id));
                    }
                    if *size > 100 {
                        warn!("Large max file size ({} MB) for field: {}", size, field_id);
                    }
                }
            },
            
            FieldType::Table { columns, min_rows, max_rows } => {
                if columns.is_empty() {
                    return Err(anyhow!("Table field must have at least one column for field: {}", field_id));
                }
                
                if let (Some(min), Some(max)) = (min_rows, max_rows) {
                    if min > max {
                        return Err(anyhow!("Min rows cannot be greater than max rows for field: {}", field_id));
                    }
                }
                
                // Validate column IDs are unique
                let mut column_ids = HashSet::new();
                for column in columns {
                    if column_ids.contains(&column.column_id) {
                        return Err(anyhow!("Duplicate column ID '{}' for field: {}", column.column_id, field_id));
                    }
                    column_ids.insert(&column.column_id);
                }
            },
            
            _ => {} // Other field types are valid by default
        }
        
        Ok(())
    }
    
    /// Validates that a field value is compatible with the field type.
    fn validate_field_value_compatibility(
        &self,
        field_type: &FieldType,
        value: &FieldValue,
        field_id: &str,
    ) -> Result<()> {
        match (field_type, value) {
            (FieldType::Text { .. }, FieldValue::String(_)) => Ok(()),
            (FieldType::Textarea { .. }, FieldValue::String(_)) => Ok(()),
            (FieldType::Number { .. }, FieldValue::Number(_)) => Ok(()),
            (FieldType::BooleanCheckbox { .. }, FieldValue::Boolean(_)) => Ok(()),
            (FieldType::Select { multiple: true, .. }, FieldValue::Array(_)) => Ok(()),
            (FieldType::Select { multiple: false, .. }, FieldValue::String(_)) => Ok(()),
            (FieldType::Checkbox { .. }, FieldValue::Array(_)) => Ok(()),
            (FieldType::Radio { .. }, FieldValue::String(_)) => Ok(()),
            (FieldType::Email { .. }, FieldValue::String(_)) => Ok(()),
            (FieldType::Phone { .. }, FieldValue::String(_)) => Ok(()),
            (FieldType::Date { .. }, FieldValue::String(_)) => Ok(()),
            (FieldType::Time { .. }, FieldValue::String(_)) => Ok(()),
            (FieldType::DateTime { .. }, FieldValue::String(_)) => Ok(()),
            (FieldType::Table { .. }, FieldValue::Array(_)) => Ok(()),
            (_, FieldValue::Null) => Ok(()), // Null is always compatible
            _ => Err(anyhow!(
                "Default value type incompatible with field type for field: {}",
                field_id
            )),
        }
    }
    
    /// Validates a validation rule.
    fn validate_validation_rule(
        &self,
        rule: &ValidationRule,
        field_type: &FieldType,
        field_id: &str,
    ) -> Result<()> {
        if rule.rule_id.is_empty() {
            return Err(anyhow!("Validation rule ID cannot be empty for field: {}", field_id));
        }
        
        if rule.error_message.is_empty() {
            return Err(anyhow!("Validation rule error message cannot be empty for rule: {}", rule.rule_id));
        }
        
        // Validate rule type compatibility with field type
        match (&rule.rule_type, field_type) {
            (ValidationRuleType::MinLength { .. }, FieldType::Text { .. }) => Ok(()),
            (ValidationRuleType::MinLength { .. }, FieldType::Textarea { .. }) => Ok(()),
            (ValidationRuleType::MaxLength { .. }, FieldType::Text { .. }) => Ok(()),
            (ValidationRuleType::MaxLength { .. }, FieldType::Textarea { .. }) => Ok(()),
            (ValidationRuleType::Range { .. }, FieldType::Number { .. }) => Ok(()),
            (ValidationRuleType::Email, FieldType::Email { .. }) => Ok(()),
            (ValidationRuleType::Phone, FieldType::Phone { .. }) => Ok(()),
            (ValidationRuleType::Date, FieldType::Date { .. }) => Ok(()),
            (ValidationRuleType::Time, FieldType::Time { .. }) => Ok(()),
            (ValidationRuleType::DateTime, FieldType::DateTime { .. }) => Ok(()),
            (ValidationRuleType::Required, _) => Ok(()), // Required is compatible with all types
            (ValidationRuleType::Pattern { .. }, FieldType::Text { .. }) => Ok(()),
            (ValidationRuleType::Pattern { .. }, FieldType::Textarea { .. }) => Ok(()),
            (ValidationRuleType::Custom { .. }, _) => Ok(()), // Custom rules are always allowed
            _ => Err(anyhow!(
                "Validation rule type {:?} is not compatible with field type for field: {}",
                rule.rule_type,
                field_id
            )),
        }
    }
    
    /// Validates conditional logic consistency.
    fn validate_conditional_logic(&self, template: &FormTemplate) -> Result<()> {
        // Collect all field IDs for reference validation
        let mut all_field_ids = HashSet::new();
        let mut all_section_ids = HashSet::new();
        
        self.collect_field_and_section_ids(template, &mut all_field_ids, &mut all_section_ids);
        
        // Validate global conditional rules
        for rule in &template.conditional_logic {
            self.validate_conditional_rule(rule, &all_field_ids, &all_section_ids)?;
        }
        
        Ok(())
    }
    
    /// Validates cross-references between template components.
    fn validate_cross_references(&self, template: &FormTemplate) -> Result<()> {
        // Collect all field IDs
        let mut all_field_ids = HashSet::new();
        let mut all_section_ids = HashSet::new();
        
        self.collect_field_and_section_ids(template, &mut all_field_ids, &all_section_ids);
        
        // Validate validation rule target fields
        for rule in &template.validation_rules {
            for target_field in &rule.target_fields {
                if !all_field_ids.contains(target_field) {
                    return Err(anyhow!(
                        "Validation rule '{}' references unknown field: {}",
                        rule.rule_id,
                        target_field
                    ));
                }
            }
        }
        
        Ok(())
    }
    
    /// Collects all field and section IDs from the template.
    fn collect_field_and_section_ids(
        &self,
        template: &FormTemplate,
        field_ids: &mut HashSet<String>,
        section_ids: &mut HashSet<String>,
    ) {
        for section in &template.sections {
            self.collect_section_ids(section, field_ids, section_ids);
        }
    }
    
    /// Recursively collects field and section IDs from a section.
    fn collect_section_ids(
        &self,
        section: &FormSection,
        field_ids: &mut HashSet<String>,
        section_ids: &mut HashSet<String>,
    ) {
        section_ids.insert(section.section_id.clone());
        
        for field in &section.fields {
            field_ids.insert(field.field_id.clone());
        }
        
        for subsection in &section.subsections {
            self.collect_section_ids(subsection, field_ids, section_ids);
        }
    }
    
    /// Validates a conditional rule.
    fn validate_conditional_rule(
        &self,
        rule: &ConditionalRule,
        field_ids: &HashSet<String>,
        section_ids: &HashSet<String>,
    ) -> Result<()> {
        if rule.rule_id.is_empty() {
            return Err(anyhow!("Conditional rule ID cannot be empty"));
        }
        
        self.validate_condition(&rule.condition, field_ids)?;
        
        for action in &rule.actions {
            self.validate_conditional_action(action, field_ids, section_ids)?;
        }
        
        Ok(())
    }
    
    /// Validates a condition.
    fn validate_condition(&self, condition: &Condition, field_ids: &HashSet<String>) -> Result<()> {
        match condition {
            Condition::FieldEquals { field, .. } |
            Condition::FieldNotEquals { field, .. } |
            Condition::FieldEmpty { field } |
            Condition::FieldNotEmpty { field } |
            Condition::FieldGreaterThan { field, .. } |
            Condition::FieldLessThan { field, .. } |
            Condition::FieldContains { field, .. } => {
                if !field_ids.contains(field) {
                    return Err(anyhow!("Condition references unknown field: {}", field));
                }
            },
            Condition::And { conditions } |
            Condition::Or { conditions } => {
                for cond in conditions {
                    self.validate_condition(cond, field_ids)?;
                }
            },
            Condition::Not { condition } => {
                self.validate_condition(condition, field_ids)?;
            },
        }
        
        Ok(())
    }
    
    /// Validates a conditional action.
    fn validate_conditional_action(
        &self,
        action: &ConditionalAction,
        field_ids: &HashSet<String>,
        section_ids: &HashSet<String>,
    ) -> Result<()> {
        match action {
            ConditionalAction::ShowField { field } |
            ConditionalAction::HideField { field } |
            ConditionalAction::RequireField { field } |
            ConditionalAction::UnrequireField { field } |
            ConditionalAction::SetFieldValue { field, .. } => {
                if !field_ids.contains(field) {
                    return Err(anyhow!("Conditional action references unknown field: {}", field));
                }
            },
            ConditionalAction::ShowSection { section } |
            ConditionalAction::HideSection { section } => {
                if !section_ids.contains(section) {
                    return Err(anyhow!("Conditional action references unknown section: {}", section));
                }
            },
        }
        
        Ok(())
    }
    
    /// Validates version format.
    fn is_valid_version(&self, version: &str) -> bool {
        // Simple semantic version validation
        let parts: Vec<&str> = version.split('.').collect();
        if parts.len() < 2 || parts.len() > 3 {
            return false;
        }
        
        parts.iter().all(|part| part.parse::<u32>().is_ok())
    }
    
    /// Validates form type format.
    fn is_valid_form_type(&self, form_type: &str) -> bool {
        // ICS form type validation (ICS-XXX format)
        form_type.starts_with("ICS-") && form_type.len() >= 5
    }
}

/// Configuration for template validation.
#[derive(Debug, Clone)]
pub struct ValidationConfig {
    pub strict_mode: bool,
    pub max_sections: u32,
    pub max_fields_per_section: u32,
    pub max_validation_rules_per_field: u32,
    pub max_conditional_rules: u32,
}

impl Default for ValidationConfig {
    fn default() -> Self {
        Self {
            strict_mode: true,
            max_sections: 50,
            max_fields_per_section: 100,
            max_validation_rules_per_field: 10,
            max_conditional_rules: 100,
        }
    }
}

/// Registry for field type validation and parsing.
#[derive(Debug, Clone)]
pub struct FieldTypeRegistry {
    supported_types: HashSet<String>,
}

impl Default for FieldTypeRegistry {
    fn default() -> Self {
        let mut supported_types = HashSet::new();
        supported_types.insert("text".to_string());
        supported_types.insert("textarea".to_string());
        supported_types.insert("number".to_string());
        supported_types.insert("date".to_string());
        supported_types.insert("time".to_string());
        supported_types.insert("datetime".to_string());
        supported_types.insert("select".to_string());
        supported_types.insert("radio".to_string());
        supported_types.insert("checkbox".to_string());
        supported_types.insert("boolean_checkbox".to_string());
        supported_types.insert("email".to_string());
        supported_types.insert("phone".to_string());
        supported_types.insert("coordinates".to_string());
        supported_types.insert("radio_frequency".to_string());
        supported_types.insert("file".to_string());
        supported_types.insert("signature".to_string());
        supported_types.insert("ics_position".to_string());
        supported_types.insert("person_info".to_string());
        supported_types.insert("address".to_string());
        supported_types.insert("table".to_string());
        
        Self { supported_types }
    }
}