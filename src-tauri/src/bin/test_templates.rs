/*!
 * Template System Test Binary
 * 
 * This is a standalone test binary to verify the template system works
 * correctly without depending on the full application.
 */

use std::path::PathBuf;

// Simple template loader test that doesn't depend on the full application
fn main() {
    println!("🧪 Testing RadioForms Template System...");
    println!();
    
    // Test 1: Read the ICS-201 template file directly
    let template_path = PathBuf::from("templates/ics-201.json");
    
    match std::fs::read_to_string(&template_path) {
        Ok(content) => {
            println!("✅ Successfully read ICS-201 template file ({} bytes)", content.len());
            
            // Test 2: Parse as JSON
            match serde_json::from_str::<serde_json::Value>(&content) {
                Ok(json) => {
                    println!("✅ Template JSON is valid");
                    
                    // Extract basic information
                    if let Some(title) = json.get("title").and_then(|v| v.as_str()) {
                        println!("   📋 Title: {}", title);
                    }
                    if let Some(version) = json.get("version").and_then(|v| v.as_str()) {
                        println!("   🔢 Version: {}", version);
                    }
                    if let Some(sections) = json.get("sections").and_then(|v| v.as_array()) {
                        println!("   📑 Sections: {}", sections.len());
                        
                        let mut total_fields = 0;
                        for section in sections {
                            if let Some(fields) = section.get("fields").and_then(|v| v.as_array()) {
                                total_fields += fields.len();
                            }
                        }
                        println!("   🔤 Total fields: {}", total_fields);
                    }
                },
                Err(e) => {
                    println!("❌ Template JSON is invalid: {}", e);
                    std::process::exit(1);
                }
            }
        },
        Err(e) => {
            println!("❌ Failed to read template file: {}", e);
            println!("   Expected path: {:?}", template_path.canonicalize().unwrap_or(template_path));
            std::process::exit(1);
        }
    }
    
    println!();
    println!("🎉 Template system basic tests passed!");
    println!("   The template file can be read and parsed as valid JSON.");
    println!("   Ready for full template system integration.");
}