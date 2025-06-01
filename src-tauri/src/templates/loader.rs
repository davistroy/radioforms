/*!
 * Template Loader for Embedded Form Templates
 * 
 * This module handles loading and caching of form templates from embedded
 * resources. It provides efficient template loading with caching and
 * validation for production deployment.
 * 
 * Business Logic:
 * - Embedded template resource loading using include_str!
 * - Template caching for performance optimization
 * - Template validation on load with detailed error reporting
 * - Version compatibility checking and migration support
 * - Hot-reload support for development environments
 * 
 * Design Philosophy:
 * - Embedded resources for portable single-file deployment
 * - Aggressive caching for production performance
 * - Comprehensive error handling with detailed diagnostics
 * - Template validation on load for early error detection
 * - Extensible loader architecture for future enhancements
 */

use anyhow::{Result, Context, anyhow};
use std::collections::HashMap;
use log::{debug, info, warn, error};

use super::schema::*;
use super::parser::{TemplateParser, ValidationConfig};

/// Template loader for embedded form template resources.
/// 
/// Business Logic:
/// - Loads all embedded ICS form templates on initialization
/// - Provides caching for frequently accessed templates
/// - Validates templates on load with comprehensive error reporting
/// - Supports template versioning and compatibility checking
pub struct TemplateLoader {
    /// Parsed and validated templates cache
    templates: HashMap<String, FormTemplate>,
    
    /// Template parser with validation
    parser: TemplateParser,
    
    /// Loader configuration
    config: LoaderConfig,
    
    /// Version manager for template compatibility checking
    version_manager: VersionManager,
}

impl TemplateLoader {
    /// Creates a new template loader with default configuration.
    pub fn new() -> Result<Self> {
        Self::with_config(LoaderConfig::default())
    }
    
    /// Creates a template loader with custom configuration.
    pub fn with_config(config: LoaderConfig) -> Result<Self> {
        let parser = TemplateParser::with_config(config.validation_config.clone());
        
        let mut loader = Self {
            templates: HashMap::new(),
            parser,
            config,
            version_manager: VersionManager::new(),
        };
        
        loader.load_all_embedded_templates()?;
        Ok(loader)
    }
    
    /// Loads all embedded template resources.
    pub fn load_all_embedded_templates(&mut self) -> Result<()> {
        info!("Loading embedded form templates...");
        
        // Load all ICS form templates
        let template_definitions = self.get_embedded_template_definitions();
        let mut loaded_count = 0;
        let mut error_count = 0;
        
        for (form_type, template_content) in template_definitions {
            match self.load_template(&form_type, &template_content) {
                Ok(_) => {
                    loaded_count += 1;
                    debug!("Successfully loaded template: {}", form_type);
                },
                Err(e) => {
                    error_count += 1;
                    error!("Failed to load template {}: {}", form_type, e);
                    
                    if self.config.fail_on_template_error {
                        return Err(anyhow!("Template loading failed for {}: {}", form_type, e));
                    }
                }
            }
        }
        
        info!("Template loading completed: {} loaded, {} errors", loaded_count, error_count);
        
        if loaded_count == 0 {
            return Err(anyhow!("No templates were successfully loaded"));
        }
        
        Ok(())
    }
    
    /// Loads a single template from content.
    fn load_template(&mut self, form_type: &str, content: &str) -> Result<()> {
        let template = self.parser.parse_template(content)
            .with_context(|| format!("Failed to parse template for form type: {}", form_type))?;
        
        // Validate that the template form_type matches the expected form_type
        if template.form_type != form_type {
            return Err(anyhow!(
                "Template form_type '{}' does not match expected form_type '{}'",
                template.form_type,
                form_type
            ));
        }
        
        // Check template version compatibility
        match self.version_manager.validate_version_metadata(&template.version, &template.metadata.min_app_version) {
            Ok(validation_result) => {
                if !validation_result.is_compatible {
                    return Err(anyhow!("Template {} version {} is not compatible: {:?}", 
                                     template.form_type, template.version, validation_result.errors));
                }
                
                if !validation_result.warnings.is_empty() {
                    for warning in &validation_result.warnings {
                        warn!("Template {} version warning: {}", template.form_type, warning);
                    }
                }
                
                if validation_result.migration_required {
                    if let Some(ref recommended) = validation_result.recommended_version {
                        warn!("Template {} should be migrated from {} to {}", 
                              template.form_type, template.version, recommended);
                    }
                }
            },
            Err(e) => {
                warn!("Template {} version validation failed: {}", template.form_type, e);
            }
        }
        
        self.templates.insert(form_type.to_string(), template);
        Ok(())
    }
    
    /// Gets a template by form type.
    pub fn get_template(&self, form_type: &str) -> Option<&FormTemplate> {
        self.templates.get(form_type)
    }
    
    /// Gets a template by form type and version.
    pub fn get_template_version(&self, form_type: &str, version: &str) -> Option<&FormTemplate> {
        // For now, return the current template if version is compatible
        if let Some(template) = self.templates.get(form_type) {
            if self.version_manager.is_compatible(&template.version) {
                Some(template)
            } else {
                None
            }
        } else {
            None
        }
    }
    
    /// Gets the latest compatible version of a template.
    pub fn get_latest_template(&self, form_type: &str) -> Option<&FormTemplate> {
        // For now, this is the same as get_template since we only store one version
        // In the future, this would select the highest compatible version
        self.get_template(form_type)
    }
    
    /// Gets all loaded templates.
    pub fn get_all_templates(&self) -> &HashMap<String, FormTemplate> {
        &self.templates
    }
    
    /// Gets available form types.
    pub fn get_available_form_types(&self) -> Vec<String> {
        self.templates.keys().cloned().collect()
    }
    
    /// Checks if a template exists for the given form type.
    pub fn has_template(&self, form_type: &str) -> bool {
        self.templates.contains_key(form_type)
    }
    
    /// Gets embedded resource information.
    pub fn get_resource_info(&self) -> TemplateResourceInfo {
        TemplateResources::get_resource_info()
    }
    
    /// Gets available embedded form types.
    pub fn get_embedded_form_types(&self) -> Vec<String> {
        TemplateResources::get_available_form_types()
    }
    
    /// Checks if running in embedded mode (release) or file system mode (debug).
    pub fn is_embedded_mode(&self) -> bool {
        !cfg!(debug_assertions)
    }
    
    /// Gets template statistics.
    pub fn get_template_stats(&self) -> TemplateStats {
        let mut stats = TemplateStats {
            total_templates: self.templates.len(),
            total_sections: 0,
            total_fields: 0,
            total_validation_rules: 0,
            form_types: Vec::new(),
            version_info: Vec::new(),
            resource_info: TemplateResources::get_resource_info(),
        };
        
        for (form_type, template) in &self.templates {
            stats.form_types.push(form_type.clone());
            stats.version_info.push((form_type.clone(), template.version.clone()));
            stats.total_sections += template.sections.len();
            stats.total_validation_rules += template.validation_rules.len();
            
            for section in &template.sections {
                stats.total_fields += self.count_section_fields(section);
            }
        }
        
        stats
    }
    
    /// Counts fields in a section recursively.
    fn count_section_fields(&self, section: &FormSection) -> usize {
        let mut count = section.fields.len();
        for subsection in &section.subsections {
            count += self.count_section_fields(subsection);
        }
        count
    }
    
    /// Checks template version compatibility.
    fn is_template_version_compatible(&self, template: &FormTemplate) -> bool {
        // Use the version manager for compatibility checking
        self.version_manager.is_compatible(&template.version)
    }
    
    /// Gets embedded template definitions.
    /// 
    /// Uses the TemplateResources module for compile-time embedded access.
    /// Templates are embedded into the binary using include_str! macro.
    fn get_embedded_template_definitions(&self) -> Vec<(String, String)> {
        TemplateResources::get_all_embedded_templates()
    }
    
    /// Gets a minimal ICS-201 template for testing when file loading fails.
    fn get_minimal_ics_201_template(&self) -> String {
        r#"{
            "template_id": "ics-201-minimal",
            "form_type": "ICS-201",
            "version": "1.0",
            "title": "Incident Briefing (Minimal)",
            "description": "Minimal ICS-201 template for testing",
            "metadata": {
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "author": "System",
                "compatibility_version": "1.0",
                "min_app_version": "1.0.0",
                "tags": ["test"],
                "status": "draft",
                "custom_metadata": {}
            },
            "sections": [
                {
                    "section_id": "basic_info",
                    "title": "Basic Information",
                    "description": "Essential incident information",
                    "order": 1,
                    "required": true,
                    "repeatable": false,
                    "max_repetitions": null,
                    "fields": [
                        {
                            "field_id": "incident_name",
                            "label": "Incident Name",
                            "field_type": {
                                "type": "text",
                                "max_length": 100
                            },
                            "required": true,
                            "default_value": null,
                            "placeholder": "Enter incident name",
                            "help_text": "Name of the incident",
                            "validation_rules": [],
                            "conditional_display": null,
                            "order": 1,
                            "readonly": false,
                            "css_classes": [],
                            "attributes": {}
                        }
                    ],
                    "subsections": [],
                    "validation_rules": [],
                    "conditional_display": null
                }
            ],
            "validation_rules": [],
            "conditional_logic": [],
            "defaults": {}
        }"#.to_string()
    }
}

/// Template loader configuration.
#[derive(Debug, Clone)]
pub struct LoaderConfig {
    /// Validation configuration for template parsing
    pub validation_config: ValidationConfig,
    
    /// Whether to fail completely if any template fails to load
    pub fail_on_template_error: bool,
    
    /// Whether to enable template caching
    pub enable_caching: bool,
    
    /// Maximum number of templates to cache
    pub max_cache_size: usize,
}

impl Default for LoaderConfig {
    fn default() -> Self {
        Self {
            validation_config: ValidationConfig::default(),
            fail_on_template_error: false,
            enable_caching: true,
            max_cache_size: 100,
        }
    }
}

/// Template loading statistics.
#[derive(Debug, Clone)]
pub struct TemplateStats {
    pub total_templates: usize,
    pub total_sections: usize,
    pub total_fields: usize,
    pub total_validation_rules: usize,
    pub form_types: Vec<String>,
    pub version_info: Vec<(String, String)>, // (form_type, version)
    pub resource_info: TemplateResourceInfo,
}

impl TemplateStats {
    /// Gets a summary string of the template statistics.
    pub fn summary(&self) -> String {
        format!(
            "Templates: {}, Sections: {}, Fields: {}, Validation Rules: {}",
            self.total_templates,
            self.total_sections,
            self.total_fields,
            self.total_validation_rules
        )
    }
}