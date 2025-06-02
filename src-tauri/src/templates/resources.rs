/*!
 * Embedded Template Resources for RadioForms
 * 
 * This module provides embedded template resources that are compiled into
 * the binary at build time for portable deployment. Templates are embedded
 * using the include_str! macro for zero-runtime-cost access.
 * 
 * Business Logic:
 * - Compile-time template embedding for portable deployment
 * - Zero-overhead template access through static string references
 * - Development mode file system fallback for rapid iteration
 * - Centralized template resource management
 * - Complete template catalog for all 20 ICS forms
 * 
 * Design Philosophy:
 * - Compile-time embedding for production efficiency
 * - Development-time flexibility with file system fallback
 * - Static template definitions for memory efficiency
 * - Centralized resource management for maintainability
 * - Future-ready architecture for template expansion
 */

use log::{debug, info, warn};

/// Template resource manager for embedded template access.
/// 
/// Business Logic:
/// - Provides compile-time embedded template access
/// - Manages template resource catalog and metadata
/// - Supports development mode file system fallback
/// - Centralizes template resource organization
pub struct TemplateResources;

impl TemplateResources {
    /// Gets all embedded template definitions.
    /// 
    /// Returns a vector of (form_type, template_content) tuples for all
    /// available embedded templates. In debug mode, attempts to load from
    /// file system first for development convenience.
    pub fn get_all_embedded_templates() -> Vec<(String, String)> {
        let mut templates = Vec::new();
        
        // ICS-201: Incident Briefing
        templates.push(("ICS-201".to_string(), Self::get_ics_201_template()));
        
        // TODO: Add remaining 19 ICS forms as they are implemented
        // templates.push(("ICS-202".to_string(), Self::get_ics_202_template()));
        // templates.push(("ICS-203".to_string(), Self::get_ics_203_template()));
        // templates.push(("ICS-204".to_string(), Self::get_ics_204_template()));
        // templates.push(("ICS-205".to_string(), Self::get_ics_205_template()));
        // templates.push(("ICS-205A".to_string(), Self::get_ics_205a_template()));
        // templates.push(("ICS-206".to_string(), Self::get_ics_206_template()));
        // templates.push(("ICS-207".to_string(), Self::get_ics_207_template()));
        // templates.push(("ICS-208".to_string(), Self::get_ics_208_template()));
        // templates.push(("ICS-209".to_string(), Self::get_ics_209_template()));
        // templates.push(("ICS-210".to_string(), Self::get_ics_210_template()));
        // templates.push(("ICS-211".to_string(), Self::get_ics_211_template()));
        // templates.push(("ICS-213".to_string(), Self::get_ics_213_template()));
        // templates.push(("ICS-214".to_string(), Self::get_ics_214_template()));
        // templates.push(("ICS-215".to_string(), Self::get_ics_215_template()));
        // templates.push(("ICS-215A".to_string(), Self::get_ics_215a_template()));
        // templates.push(("ICS-218".to_string(), Self::get_ics_218_template()));
        // templates.push(("ICS-220".to_string(), Self::get_ics_220_template()));
        // templates.push(("ICS-221".to_string(), Self::get_ics_221_template()));
        // templates.push(("ICS-225".to_string(), Self::get_ics_225_template()));
        
        info!("Loaded {} embedded templates", templates.len());
        templates
    }
    
    /// Gets a specific template by form type.
    pub fn get_template(form_type: &str) -> Option<String> {
        match form_type {
            "ICS-201" => Some(Self::get_ics_201_template()),
            // TODO: Add cases for remaining forms
            _ => {
                warn!("Template {} not found in embedded resources", form_type);
                None
            }
        }
    }
    
    /// Gets available template form types.
    pub fn get_available_form_types() -> Vec<String> {
        vec![
            "ICS-201".to_string(),
            // TODO: Add remaining form types as implemented
        ]
    }
    
    /// Gets template resource metadata.
    pub fn get_resource_info() -> TemplateResourceInfo {
        TemplateResourceInfo {
            total_templates: 1, // Update as more templates are added
            embedded_size_bytes: Self::get_ics_201_template().len(),
            supported_forms: Self::get_available_form_types(),
            version: "1.0.0".to_string(),
        }
    }
    
    // ===================
    // EMBEDDED TEMPLATES
    // ===================
    
    /// Gets the embedded ICS-201 Incident Briefing template.
    /// 
    /// In debug mode, attempts to load from file system first.
    /// In release mode, always uses the embedded template.
    fn get_ics_201_template() -> String {
        if cfg!(debug_assertions) {
            // Development mode: try file system first for rapid iteration
            match std::fs::read_to_string("templates/ics-201.json") {
                Ok(content) => {
                    debug!("Loaded ICS-201 template from file system ({} bytes)", content.len());
                    content
                },
                Err(_) => {
                    debug!("Loading ICS-201 template from embedded resources");
                    Self::get_embedded_ics_201().to_string()
                }
            }
        } else {
            // Production mode: always use embedded template
            debug!("Loading ICS-201 template from embedded resources");
            Self::get_embedded_ics_201().to_string()
        }
    }
    
    /// Gets the compile-time embedded ICS-201 template.
    /// 
    /// This template is embedded into the binary at compile time using
    /// include_str! for zero-runtime overhead and portable deployment.
    fn get_embedded_ics_201() -> &'static str {
        include_str!("../../templates/ics-201.json")
    }
    
    // TODO: Add embedded template methods for remaining 19 forms
    /*
    fn get_ics_202_template() -> String { ... }
    fn get_embedded_ics_202() -> &'static str { include_str!("../../templates/ics-202.json") }
    
    fn get_ics_203_template() -> String { ... }
    fn get_embedded_ics_203() -> &'static str { include_str!("../../templates/ics-203.json") }
    
    ... etc for all 20 forms
    */
}

/// Template resource information and metadata.
#[derive(Debug, Clone)]
pub struct TemplateResourceInfo {
    pub total_templates: usize,
    pub embedded_size_bytes: usize,
    pub supported_forms: Vec<String>,
    pub version: String,
}

impl TemplateResourceInfo {
    /// Gets a summary of the template resources.
    pub fn summary(&self) -> String {
        format!(
            "Embedded Templates: {} forms, {} KB total, version {}",
            self.total_templates,
            self.embedded_size_bytes / 1024,
            self.version
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_embedded_template_access() {
        let ics_201 = TemplateResources::get_template("ICS-201");
        assert!(ics_201.is_some());
        
        let content = ics_201.unwrap();
        assert!(!content.is_empty());
        assert!(content.contains("Incident Briefing"));
    }
    
    #[test]
    fn test_resource_info() {
        let info = TemplateResources::get_resource_info();
        assert!(info.total_templates > 0);
        assert!(info.embedded_size_bytes > 0);
        assert!(!info.supported_forms.is_empty());
    }
    
    #[test]
    fn test_available_form_types() {
        let forms = TemplateResources::get_available_form_types();
        assert!(forms.contains(&"ICS-201".to_string()));
    }
}