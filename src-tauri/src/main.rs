// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    // Test template system during development
    #[cfg(debug_assertions)]
    test_template_system();
    
    radioforms_lib::run()
}

/// Test function to verify template parsing system works correctly
#[cfg(debug_assertions)]
fn test_template_system() {
    use radioforms_lib::templates::TemplateLoader;
    
    println!("Testing template system...");
    
    match TemplateLoader::new() {
        Ok(loader) => {
            let stats = loader.get_template_stats();
            println!("✅ Template system initialized successfully");
            println!("📊 {}", stats.summary());
            
            // Test loading specific template
            if let Some(template) = loader.get_template("ICS-201") {
                println!("✅ ICS-201 template loaded: {} v{}", template.title, template.version);
                println!("   Sections: {}, Total fields: {}", 
                         template.sections.len(),
                         template.sections.iter().map(|s| s.fields.len()).sum::<usize>());
            } else {
                println!("⚠️  ICS-201 template not found");
            }
        },
        Err(e) => {
            println!("❌ Template system failed to initialize: {}", e);
        }
    }
    
    println!();
}
