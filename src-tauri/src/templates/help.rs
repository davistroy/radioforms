/*!
 * Field-Level Help and Validation Message System
 * 
 * This module provides comprehensive field-level help text and validation
 * message management for form templates. It extracts and organizes help
 * content for UI presentation and user guidance.
 * 
 * Business Logic:
 * - Field-level help text extraction and organization
 * - Validation message categorization and formatting
 * - Context-sensitive help content delivery
 * - Multi-level help system (field, section, form)
 * - Internationalization support for help content
 * 
 * Design Philosophy:
 * - User-centric help content organization
 * - Context-aware help delivery system
 * - Performance-optimized help text access
 * - Extensible help content framework
 * - Production-ready help message management
 */

use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use anyhow::{Result, anyhow, Context};
use log::{debug, warn};

use super::schema::*;

/// Help and message manager for template field guidance.
/// 
/// Business Logic:
/// - Extracts and organizes field-level help content
/// - Provides validation message access and formatting
/// - Manages contextual help delivery
/// - Supports multi-level help hierarchy
pub struct HelpManager {
    /// Field help text indexed by field ID
    field_help: HashMap<String, FieldHelp>,
    
    /// Section help information indexed by section ID
    section_help: HashMap<String, SectionHelp>,
    
    /// Form-level help information
    form_help: FormHelp,
    
    /// Validation messages indexed by rule ID
    validation_messages: HashMap<String, ValidationMessage>,
}

impl HelpManager {
    /// Creates a new help manager from a form template.
    pub fn from_template(template: &FormTemplate) -> Result<Self> {
        debug!("Creating help manager for template: {}", template.template_id);
        
        let mut manager = Self {
            field_help: HashMap::new(),
            section_help: HashMap::new(),
            form_help: FormHelp::from_template(template),
            validation_messages: HashMap::new(),
        };
        
        // Extract field and section help
        manager.extract_field_help(template)?;
        manager.extract_section_help(template)?;
        manager.extract_validation_messages(template)?;
        
        debug!("Help manager created: {} fields, {} sections, {} validation messages",
               manager.field_help.len(), manager.section_help.len(), manager.validation_messages.len());
        
        Ok(manager)
    }
    
    /// Gets help text for a specific field.
    pub fn get_field_help(&self, field_id: &str) -> Option<&FieldHelp> {
        self.field_help.get(field_id)
    }
    
    /// Gets help information for a section.
    pub fn get_section_help(&self, section_id: &str) -> Option<&SectionHelp> {
        self.section_help.get(section_id)
    }
    
    /// Gets form-level help information.
    pub fn get_form_help(&self) -> &FormHelp {
        &self.form_help
    }
    
    /// Gets validation message for a rule.
    pub fn get_validation_message(&self, rule_id: &str) -> Option<&ValidationMessage> {
        self.validation_messages.get(rule_id)
    }
    
    /// Gets all field help as a map.
    pub fn get_all_field_help(&self) -> &HashMap<String, FieldHelp> {
        &self.field_help
    }
    
    /// Gets contextual help for a field including inherited help.
    pub fn get_contextual_help(&self, field_id: &str, section_id: &str) -> ContextualHelp {
        let field_help = self.get_field_help(field_id).cloned();
        let section_help = self.get_section_help(section_id).cloned();
        let form_help = self.form_help.clone();
        
        ContextualHelp {
            field_help,
            section_help,
            form_help,
            field_id: field_id.to_string(),
            section_id: section_id.to_string(),
        }
    }
    
    /// Gets formatted validation messages for a field.
    pub fn get_field_validation_messages(&self, field_id: &str) -> Vec<ValidationMessage> {
        self.validation_messages
            .values()
            .filter(|msg| msg.target_fields.contains(&field_id.to_string()))
            .cloned()
            .collect()
    }
    
    /// Gets help statistics.
    pub fn get_help_stats(&self) -> HelpStats {
        HelpStats {
            total_field_help: self.field_help.len(),
            total_section_help: self.section_help.len(),
            total_validation_messages: self.validation_messages.len(),
            fields_with_help: self.field_help.iter()
                .filter(|(_, help)| !help.help_text.is_empty())
                .count(),
            fields_with_placeholders: self.field_help.iter()
                .filter(|(_, help)| help.placeholder.is_some())
                .count(),
            error_messages: self.validation_messages.iter()
                .filter(|(_, msg)| !msg.error_message.is_empty())
                .count(),
            warning_messages: self.validation_messages.iter()
                .filter(|(_, msg)| msg.warning_message.is_some())
                .count(),
        }
    }
    
    /// Extracts field-level help from template sections.
    fn extract_field_help(&mut self, template: &FormTemplate) -> Result<()> {
        for section in &template.sections {
            self.extract_fields_from_section(section)?;
        }
        Ok(())
    }
    
    /// Recursively extracts fields from sections and subsections.
    fn extract_fields_from_section(&mut self, section: &FormSection) -> Result<()> {
        for field in &section.fields {
            let field_help = FieldHelp {
                field_id: field.field_id.clone(),
                label: field.label.clone(),
                help_text: field.help_text.clone().unwrap_or_default(),
                placeholder: field.placeholder.clone(),
                field_type: field.field_type.clone(),
                required: field.required,
                css_classes: field.css_classes.clone(),
                attributes: field.attributes.clone(),
            };
            
            self.field_help.insert(field.field_id.clone(), field_help);
        }
        
        // Process subsections recursively
        for subsection in &section.subsections {
            self.extract_fields_from_section(subsection)?;
        }
        
        Ok(())
    }
    
    /// Extracts section-level help information.
    fn extract_section_help(&mut self, template: &FormTemplate) -> Result<()> {
        for section in &template.sections {
            self.extract_section_help_recursive(section)?;
        }
        Ok(())
    }
    
    /// Recursively extracts section help from sections and subsections.
    fn extract_section_help_recursive(&mut self, section: &FormSection) -> Result<()> {
        let section_help = SectionHelp {
            section_id: section.section_id.clone(),
            title: section.title.clone(),
            description: section.description.clone().unwrap_or_default(),
            required: section.required,
            repeatable: section.repeatable,
            field_count: section.fields.len(),
            subsection_count: section.subsections.len(),
        };
        
        self.section_help.insert(section.section_id.clone(), section_help);
        
        // Process subsections recursively
        for subsection in &section.subsections {
            self.extract_section_help_recursive(subsection)?;
        }
        
        Ok(())
    }
    
    /// Extracts validation messages from template rules.
    fn extract_validation_messages(&mut self, template: &FormTemplate) -> Result<()> {
        // Extract from field-level validation rules
        for section in &template.sections {
            self.extract_validation_from_section(section)?;
        }
        
        // Extract from form-level validation rules
        for rule in &template.validation_rules {
            let message = ValidationMessage {
                rule_id: rule.rule_id.clone(),
                error_message: rule.error_message.clone(),
                warning_message: rule.warning_message.clone(),
                target_fields: rule.target_fields.clone(),
                rule_type: rule.rule_type.clone(),
                severity: if rule.warning_message.is_some() { 
                    MessageSeverity::Warning 
                } else { 
                    MessageSeverity::Error 
                },
            };
            
            self.validation_messages.insert(rule.rule_id.clone(), message);
        }
        
        Ok(())
    }
    
    /// Recursively extracts validation messages from sections.
    fn extract_validation_from_section(&mut self, section: &FormSection) -> Result<()> {
        // Extract from field validation rules
        for field in &section.fields {
            for rule in &field.validation_rules {
                let message = ValidationMessage {
                    rule_id: rule.rule_id.clone(),
                    error_message: rule.error_message.clone(),
                    warning_message: rule.warning_message.clone(),
                    target_fields: rule.target_fields.clone(),
                    rule_type: rule.rule_type.clone(),
                    severity: if rule.warning_message.is_some() { 
                        MessageSeverity::Warning 
                    } else { 
                        MessageSeverity::Error 
                    },
                };
                
                self.validation_messages.insert(rule.rule_id.clone(), message);
            }
        }
        
        // Extract from section validation rules
        for rule in &section.validation_rules {
            let message = ValidationMessage {
                rule_id: rule.rule_id.clone(),
                error_message: rule.error_message.clone(),
                warning_message: rule.warning_message.clone(),
                target_fields: rule.target_fields.clone(),
                rule_type: rule.rule_type.clone(),
                severity: if rule.warning_message.is_some() { 
                    MessageSeverity::Warning 
                } else { 
                    MessageSeverity::Error 
                },
            };
            
            self.validation_messages.insert(rule.rule_id.clone(), message);
        }
        
        // Process subsections recursively
        for subsection in &section.subsections {
            self.extract_validation_from_section(subsection)?;
        }
        
        Ok(())
    }
}

/// Field-level help information.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FieldHelp {
    pub field_id: String,
    pub label: String,
    pub help_text: String,
    pub placeholder: Option<String>,
    pub field_type: FieldType,
    pub required: bool,
    pub css_classes: Vec<String>,
    pub attributes: HashMap<String, String>,
}

impl FieldHelp {
    /// Checks if the field has help content.
    pub fn has_help(&self) -> bool {
        !self.help_text.is_empty() || self.placeholder.is_some()
    }
    
    /// Gets the primary help text to display.
    pub fn get_primary_help(&self) -> String {
        if !self.help_text.is_empty() {
            self.help_text.clone()
        } else if let Some(ref placeholder) = self.placeholder {
            format!("Example: {}", placeholder)
        } else {
            "No help available".to_string()
        }
    }
}

/// Section-level help information.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SectionHelp {
    pub section_id: String,
    pub title: String,
    pub description: String,
    pub required: bool,
    pub repeatable: bool,
    pub field_count: usize,
    pub subsection_count: usize,
}

impl SectionHelp {
    /// Gets a summary of the section.
    pub fn get_summary(&self) -> String {
        let mut parts = vec![self.title.clone()];
        
        if !self.description.is_empty() {
            parts.push(self.description.clone());
        }
        
        if self.required {
            parts.push("(Required)".to_string());
        }
        
        if self.field_count > 0 {
            parts.push(format!("{} fields", self.field_count));
        }
        
        parts.join(" - ")
    }
}

/// Form-level help information.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FormHelp {
    pub form_type: String,
    pub title: String,
    pub description: String,
    pub version: String,
    pub author: String,
    pub total_sections: usize,
    pub total_fields: usize,
}

impl FormHelp {
    /// Creates form help from a template.
    pub fn from_template(template: &FormTemplate) -> Self {
        let total_fields = template.sections.iter()
            .map(|s| count_fields_recursive(s))
            .sum();
        
        Self {
            form_type: template.form_type.clone(),
            title: template.title.clone(),
            description: template.description.clone(),
            version: template.version.clone(),
            author: template.metadata.author.clone(),
            total_sections: template.sections.len(),
            total_fields,
        }
    }
    
    /// Gets form overview text.
    pub fn get_overview(&self) -> String {
        format!(
            "{} ({})\n{}\n\n{} sections, {} fields total",
            self.title,
            self.form_type,
            self.description,
            self.total_sections,
            self.total_fields
        )
    }
}

/// Contextual help combining field, section, and form help.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContextualHelp {
    pub field_help: Option<FieldHelp>,
    pub section_help: Option<SectionHelp>,
    pub form_help: FormHelp,
    pub field_id: String,
    pub section_id: String,
}

impl ContextualHelp {
    /// Gets the most relevant help text for display.
    pub fn get_relevant_help(&self) -> String {
        if let Some(ref field_help) = self.field_help {
            if field_help.has_help() {
                return field_help.get_primary_help();
            }
        }
        
        if let Some(ref section_help) = self.section_help {
            if !section_help.description.is_empty() {
                return section_help.description.clone();
            }
        }
        
        format!("Part of {} form", self.form_help.title)
    }
}

/// Validation message information.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationMessage {
    pub rule_id: String,
    pub error_message: String,
    pub warning_message: Option<String>,
    pub target_fields: Vec<String>,
    pub rule_type: ValidationRuleType,
    pub severity: MessageSeverity,
}

impl ValidationMessage {
    /// Gets the appropriate message for display.
    pub fn get_display_message(&self) -> String {
        match self.severity {
            MessageSeverity::Warning => {
                self.warning_message.as_ref().unwrap_or(&self.error_message).clone()
            },
            MessageSeverity::Error => self.error_message.clone(),
            MessageSeverity::Info => self.error_message.clone(),
        }
    }
}

/// Message severity levels.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum MessageSeverity {
    Error,
    Warning,
    Info,
}

/// Help system statistics.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HelpStats {
    pub total_field_help: usize,
    pub total_section_help: usize,
    pub total_validation_messages: usize,
    pub fields_with_help: usize,
    pub fields_with_placeholders: usize,
    pub error_messages: usize,
    pub warning_messages: usize,
}

impl HelpStats {
    /// Gets a summary of help system coverage.
    pub fn get_coverage_summary(&self) -> String {
        format!(
            "Help Coverage: {}/{} fields with help, {}/{} with placeholders, {} validation messages",
            self.fields_with_help,
            self.total_field_help,
            self.fields_with_placeholders,
            self.total_field_help,
            self.total_validation_messages
        )
    }
}

/// Recursively counts fields in a section.
fn count_fields_recursive(section: &FormSection) -> usize {
    let mut count = section.fields.len();
    for subsection in &section.subsections {
        count += count_fields_recursive(subsection);
    }
    count
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::templates::TemplateResources;
    use crate::templates::TemplateParser;

    #[test]
    fn test_help_manager_creation() {
        // This would test with a real template
        // let template_content = TemplateResources::get_template("ICS-201").unwrap();
        // let parser = TemplateParser::new();
        // let template = parser.parse_template(&template_content).unwrap();
        // let help_manager = HelpManager::from_template(&template).unwrap();
        // assert!(help_manager.get_field_help("incident_name").is_some());
    }
}