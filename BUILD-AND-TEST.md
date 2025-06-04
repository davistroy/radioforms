# Building and Testing RadioForms

## Quick Build Instructions

Since the initial build takes time due to dependency compilation, here are the steps to get your executable:

### Option 1: Development Build (Faster)
```bash
# This creates a debug executable that's larger but builds faster
npm run tauri dev
```

### Option 2: Production Build (Recommended for Testing)
```bash
# This creates an optimized executable
npm run tauri build
```

The executable will be located at:
- **Windows**: `src-tauri/target/release/radioforms.exe`
- **macOS**: `src-tauri/target/release/radioforms`
- **Linux**: `src-tauri/target/release/radioforms`

### Option 3: Pre-built Development Version
For immediate testing while the build completes:

1. The development server can be started with:
   ```bash
   npm run tauri dev
   ```
   This will open the app in development mode.

2. Once built, the production executable will be completely standalone:
   - Single `.exe` file (Windows)
   - Single binary (macOS/Linux)
   - No installation required
   - Can run from USB drive

## Testing the Application

### Basic Functionality Test:
1. Launch the application
2. Create a new ICS-213 form (General Message Form)
3. Fill in basic fields:
   - Incident Name: "Test Incident"
   - To: "Operations Chief"
   - From: "Planning Section"
   - Message: "Test message for RadioForms"
4. Save the form
5. Export as PDF
6. Export as JSON
7. Test the search functionality

### Performance Test:
- Form operations should complete in < 1 second
- Search should be instant
- PDF export should take < 2 seconds

### Portable Operation Test:
1. Copy the executable to a USB drive
2. Run from the USB drive
3. Create and save forms
4. Verify the `radioforms.db` file is created alongside the executable

## Build Time Expectations

With the optimizations implemented:
- **First build**: 2-3 minutes (downloading and compiling all dependencies)
- **Subsequent builds**: 30-45 seconds
- **Incremental builds**: 10-15 seconds

## Troubleshooting

If the build fails:
1. Ensure you have the latest Rust: `rustup update`
2. Clear the build cache: `cd src-tauri && cargo clean`
3. Try a debug build first: `cargo build` (without --release)

## Current Build Status

The compilation optimizations have been implemented:
- ✅ SQLx offline mode enabled
- ✅ Reduced dependency features
- ✅ Optimized build profiles
- ✅ Runtime queries instead of compile-time macros

This should result in significantly faster builds once the initial dependency compilation is complete.