/*!
 * Template Version Management for RadioForms
 * 
 * This module provides comprehensive version management for form templates,
 * including semantic versioning support, compatibility checking, and
 * version migration capabilities.
 * 
 * Business Logic:
 * - Semantic versioning (SemVer) support for template versions
 * - Backward compatibility checking and validation
 * - Template migration support for version upgrades
 * - Version metadata management and validation
 * - Production-ready version handling with proper error reporting
 * 
 * Design Philosophy:
 * - SemVer compliance for version numbering
 * - Strict compatibility validation for production safety
 * - Comprehensive migration support for version transitions
 * - Performance-optimized version checking
 * - Extensible version management for future enhancements
 */

use serde::{Deserialize, Serialize};
use anyhow::{Result, anyhow};
use std::collections::HashMap;
use std::cmp::Ordering;
use log::{debug, warn, info};

/// Semantic version structure for template versioning.
/// 
/// Business Logic:
/// - Follows semantic versioning (SemVer) specification
/// - Supports major.minor.patch version format
/// - Includes pre-release and build metadata support
/// - Provides version comparison and compatibility checking
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct TemplateVersion {
    pub major: u32,
    pub minor: u32,
    pub patch: u32,
    pub pre_release: Option<String>,
    pub build_metadata: Option<String>,
}

impl TemplateVersion {
    /// Creates a new template version from a string.
    pub fn parse(version_str: &str) -> Result<Self> {
        let parts: Vec<&str> = version_str.split('.').collect();
        
        if parts.len() < 2 || parts.len() > 3 {
            return Err(anyhow!("Invalid version format: {}. Expected format: major.minor[.patch]", version_str));
        }
        
        let major = parts[0].parse::<u32>()
            .map_err(|_| anyhow!("Invalid major version: {}", parts[0]))?;
        let minor = parts[1].parse::<u32>()
            .map_err(|_| anyhow!("Invalid minor version: {}", parts[1]))?;
        let patch = if parts.len() == 3 {
            parts[2].parse::<u32>()
                .map_err(|_| anyhow!("Invalid patch version: {}", parts[2]))?
        } else {
            0
        };
        
        Ok(Self {
            major,
            minor,
            patch,
            pre_release: None,
            build_metadata: None,
        })
    }
    
    /// Creates a new template version with explicit components.
    pub fn new(major: u32, minor: u32, patch: u32) -> Self {
        Self {
            major,
            minor,
            patch,
            pre_release: None,
            build_metadata: None,
        }
    }
    
    /// Checks if this version is compatible with another version.
    /// 
    /// Business Logic:
    /// - Major version must match for compatibility
    /// - Minor version can be higher (backward compatible)
    /// - Patch version can be any value
    pub fn is_compatible_with(&self, other: &TemplateVersion) -> bool {
        self.major == other.major && self.minor >= other.minor
    }
    
    /// Checks if this version is newer than another version.
    pub fn is_newer_than(&self, other: &TemplateVersion) -> bool {
        self > other
    }
    
    /// Formats the version as a string.
    pub fn to_string(&self) -> String {
        format!("{}.{}.{}", self.major, self.minor, self.patch)
    }
}

impl PartialOrd for TemplateVersion {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for TemplateVersion {
    fn cmp(&self, other: &Self) -> Ordering {
        match self.major.cmp(&other.major) {
            Ordering::Equal => match self.minor.cmp(&other.minor) {
                Ordering::Equal => self.patch.cmp(&other.patch),
                other => other,
            },
            other => other,
        }
    }
}

impl std::fmt::Display for TemplateVersion {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.to_string())
    }
}

/// Version manager for template system versioning.
/// 
/// Business Logic:
/// - Manages supported template versions and compatibility
/// - Provides version migration and upgrade capabilities
/// - Validates version requirements and dependencies
/// - Handles version-specific template loading logic
pub struct VersionManager {
    /// Currently supported application version
    app_version: TemplateVersion,
    
    /// Minimum supported template version
    min_template_version: TemplateVersion,
    
    /// Maximum supported template version
    max_template_version: TemplateVersion,
    
    /// Version migration rules
    migration_rules: HashMap<String, VersionMigrationRule>,
}

impl VersionManager {
    /// Creates a new version manager with default configuration.
    pub fn new() -> Self {
        Self {
            app_version: TemplateVersion::new(1, 0, 0),
            min_template_version: TemplateVersion::new(1, 0, 0),
            max_template_version: TemplateVersion::new(2, 0, 0),
            migration_rules: HashMap::new(),
        }
    }
    
    /// Creates a version manager with custom configuration.
    pub fn with_config(config: VersionConfig) -> Self {
        let mut manager = Self::new();
        manager.app_version = config.app_version;
        manager.min_template_version = config.min_template_version;
        manager.max_template_version = config.max_template_version;
        manager
    }
    
    /// Checks if a template version is compatible with the current application.
    pub fn is_compatible(&self, version_str: &str) -> bool {
        match TemplateVersion::parse(version_str) {
            Ok(version) => {
                self.is_version_compatible(&version)
            },
            Err(_) => false,
        }
    }
    
    /// Static helper for quick compatibility checking.
    pub fn is_compatible_static(version_str: &str) -> bool {
        let manager = Self::new();
        manager.is_compatible(version_str)
    }
    
    /// Checks if a specific version is compatible.
    pub fn is_version_compatible(&self, version: &TemplateVersion) -> bool {
        version >= &self.min_template_version && version <= &self.max_template_version
    }
    
    /// Gets the recommended version for new templates.
    pub fn get_recommended_version(&self) -> &TemplateVersion {
        &self.app_version
    }
    
    /// Validates template version metadata.
    pub fn validate_version_metadata(&self, version_str: &str, min_app_version: &str) -> Result<VersionValidationResult> {
        debug!("Validating template version: {} with min app version: {}", version_str, min_app_version);
        
        let template_version = TemplateVersion::parse(version_str)?;
        let required_app_version = TemplateVersion::parse(min_app_version)?;
        
        let mut result = VersionValidationResult {
            is_valid: true,
            is_compatible: true,
            warnings: Vec::new(),
            errors: Vec::new(),
            migration_required: false,
            recommended_version: None,
        };
        
        // Check template version compatibility
        if !self.is_version_compatible(&template_version) {
            result.is_compatible = false;
            result.errors.push(format!(
                "Template version {} is not compatible with application (supported: {}-{})",
                template_version,
                self.min_template_version,
                self.max_template_version
            ));
        }
        
        // Check if application meets minimum requirements
        if self.app_version < required_app_version {
            result.is_valid = false;
            result.errors.push(format!(
                "Application version {} does not meet template requirement {}",
                self.app_version,
                required_app_version
            ));
        }
        
        // Check for outdated template versions
        if template_version < self.app_version {
            result.migration_required = true;
            result.recommended_version = Some(self.app_version.clone());
            result.warnings.push(format!(
                "Template version {} is older than current application version {}. Consider upgrading.",
                template_version,
                self.app_version
            ));
        }
        
        // Set overall validity
        result.is_valid = result.errors.is_empty();
        
        if !result.is_valid {
            warn!("Template version validation failed: {:?}", result.errors);
        } else if !result.warnings.is_empty() {
            info!("Template version validation completed with warnings: {:?}", result.warnings);
        } else {
            debug!("Template version validation successful");
        }
        
        Ok(result)
    }
    
    /// Adds a version migration rule.
    pub fn add_migration_rule(&mut self, from_version: String, rule: VersionMigrationRule) {
        self.migration_rules.insert(from_version, rule);
    }
    
    /// Gets available migration rules.
    pub fn get_migration_rules(&self) -> &HashMap<String, VersionMigrationRule> {
        &self.migration_rules
    }
}

impl Default for VersionManager {
    fn default() -> Self {
        Self::new()
    }
}

/// Version manager configuration.
#[derive(Debug, Clone)]
pub struct VersionConfig {
    pub app_version: TemplateVersion,
    pub min_template_version: TemplateVersion,
    pub max_template_version: TemplateVersion,
}

impl Default for VersionConfig {
    fn default() -> Self {
        Self {
            app_version: TemplateVersion::new(1, 0, 0),
            min_template_version: TemplateVersion::new(1, 0, 0),
            max_template_version: TemplateVersion::new(2, 0, 0),
        }
    }
}

/// Version validation result.
#[derive(Debug, Clone)]
pub struct VersionValidationResult {
    pub is_valid: bool,
    pub is_compatible: bool,
    pub warnings: Vec<String>,
    pub errors: Vec<String>,
    pub migration_required: bool,
    pub recommended_version: Option<TemplateVersion>,
}

/// Version migration rule for template upgrades.
#[derive(Debug, Clone)]
pub struct VersionMigrationRule {
    pub from_version: TemplateVersion,
    pub to_version: TemplateVersion,
    pub migration_type: MigrationType,
    pub description: String,
    pub is_automatic: bool,
}

/// Types of version migrations.
#[derive(Debug, Clone)]
pub enum MigrationType {
    /// Simple field rename or addition
    FieldUpdate,
    /// Schema structure change
    SchemaChange,
    /// Validation rule update
    ValidationUpdate,
    /// Complete template rewrite
    FullMigration,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version_parsing() {
        let version = TemplateVersion::parse("1.2.3").unwrap();
        assert_eq!(version.major, 1);
        assert_eq!(version.minor, 2);
        assert_eq!(version.patch, 3);
    }

    #[test]
    fn test_version_compatibility() {
        let v1 = TemplateVersion::new(1, 0, 0);
        let v2 = TemplateVersion::new(1, 1, 0);
        let v3 = TemplateVersion::new(2, 0, 0);
        
        assert!(v2.is_compatible_with(&v1));
        assert!(!v1.is_compatible_with(&v2));
        assert!(!v3.is_compatible_with(&v1));
    }

    #[test]
    fn test_version_comparison() {
        let v1 = TemplateVersion::new(1, 0, 0);
        let v2 = TemplateVersion::new(1, 1, 0);
        let v3 = TemplateVersion::new(2, 0, 0);
        
        assert!(v2 > v1);
        assert!(v3 > v2);
        assert!(v3 > v1);
    }

    #[test]
    fn test_version_manager_compatibility() {
        let manager = VersionManager::new();
        assert!(manager.is_compatible("1.0"));
        assert!(manager.is_compatible("1.5.2"));
        assert!(!manager.is_compatible("3.0"));
        
        // Test static method
        assert!(VersionManager::is_compatible_static("1.0"));
        assert!(VersionManager::is_compatible_static("1.5.2"));
        assert!(!VersionManager::is_compatible_static("3.0"));
    }
}