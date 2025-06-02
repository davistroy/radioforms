/*!
 * Form Template System for RadioForms
 * 
 * This module provides the complete form template system for all 20 ICS forms
 * with JSON-based template definitions, validation rules, and runtime parsing.
 * 
 * Business Logic:
 * - Dynamic form generation from JSON templates
 * - Complete field type support for all ICS form types
 * - Validation rules and conditional logic
 * - Template versioning and migration support
 * - Embedded template resources for portable deployment
 * 
 * Design Philosophy:
 * - JSON-based templates for maximum flexibility
 * - Type-safe template parsing and validation
 * - Template versioning for future compatibility
 * - Comprehensive field type support
 * - Production-ready template loading and caching
 */

pub mod schema;
pub mod parser;
pub mod loader;
pub mod validator;
pub mod version;
pub mod resources;
pub mod help;

pub use schema::*;
pub use parser::*;
pub use loader::*;
pub use validator::*;
pub use version::*;
pub use resources::*;
pub use help::*;

use std::collections::HashMap;
use anyhow::Result;

/// Template system manager for loading and managing form templates.
/// 
/// Business Logic:
/// - Manages all form templates for the application
/// - Provides template loading and caching
/// - Supports template versioning and migration
/// - Validates template integrity on load
pub struct TemplateManager {
    templates: HashMap<String, FormTemplate>,
    cache: HashMap<String, ParsedTemplate>,
    version_compatibility: VersionManager,
}

impl TemplateManager {
    /// Creates a new template manager and loads all embedded templates.
    pub fn new() -> Result<Self> {
        let mut manager = Self {
            templates: HashMap::new(),
            cache: HashMap::new(),
            version_compatibility: VersionManager::new(),
        };
        
        manager.load_embedded_templates()?;
        Ok(manager)
    }
    
    /// Loads all embedded template resources.
    fn load_embedded_templates(&mut self) -> Result<()> {
        // Will implement template loading in subsequent tasks
        Ok(())
    }
    
    /// Gets a template by form type.
    pub fn get_template(&self, form_type: &str) -> Option<&FormTemplate> {
        self.templates.get(form_type)
    }
    
    /// Gets a parsed template (cached) by form type.
    pub fn get_parsed_template(&mut self, form_type: &str) -> Result<&ParsedTemplate> {
        if !self.cache.contains_key(form_type) {
            if let Some(template) = self.templates.get(form_type) {
                let parsed = ParsedTemplate::from_template(template)?;
                self.cache.insert(form_type.to_string(), parsed);
            } else {
                return Err(anyhow::anyhow!("Template not found: {}", form_type));
            }
        }
        
        Ok(self.cache.get(form_type).unwrap())
    }
}

/// Parsed and validated template ready for form generation.
/// 
/// Business Logic:
/// - Optimized structure for runtime form generation
/// - Pre-validated field types and constraints
/// - Cached validation rules for performance
/// - Ready-to-use field configurations
#[derive(Debug, Clone)]
pub struct ParsedTemplate {
    pub template_id: String,
    pub form_type: String,
    pub version: String,
    pub title: String,
    pub description: String,
    pub sections: Vec<FormSection>,
    pub validation_rules: Vec<ValidationRule>,
    pub conditional_logic: Vec<ConditionalRule>,
    pub metadata: TemplateMetadata,
}

impl ParsedTemplate {
    /// Creates a parsed template from a raw template definition.
    pub fn from_template(template: &FormTemplate) -> Result<Self> {
        // Will implement template parsing in subsequent tasks
        Ok(ParsedTemplate {
            template_id: template.template_id.clone(),
            form_type: template.form_type.clone(),
            version: template.version.clone(),
            title: template.title.clone(),
            description: template.description.clone(),
            sections: Vec::new(),
            validation_rules: Vec::new(),
            conditional_logic: Vec::new(),
            metadata: template.metadata.clone(),
        })
    }
}

/// Version compatibility manager for template migrations.
/// 
/// Business Logic:
/// - Manages template version compatibility
/// - Supports template migration between versions
/// - Validates version constraints
/// - Provides version upgrade paths
#[derive(Debug, Clone)]
pub struct VersionManager {
    supported_versions: Vec<String>,
    migration_paths: HashMap<String, String>,
}

impl VersionManager {
    pub fn new() -> Self {
        Self {
            supported_versions: vec!["1.0".to_string()],
            migration_paths: HashMap::new(),
        }
    }
    
    /// Checks if a template version is supported.
    pub fn is_version_supported(&self, version: &str) -> bool {
        self.supported_versions.contains(&version.to_string())
    }
}