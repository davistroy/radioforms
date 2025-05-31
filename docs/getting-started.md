# Getting Started with RadioForms

## Quick Start Guide

Welcome to RadioForms! This guide will help you start using the application in under 15 minutes. RadioForms is designed to make ICS form management simple and efficient for emergency management personnel.

## What is RadioForms?

RadioForms is a desktop application for creating, managing, and transmitting FEMA ICS (Incident Command System) forms. It works completely offline and provides:

- ✅ **Offline-first operation** - No internet required
- ✅ **ICS-213 General Message forms** - Full FEMA compliance
- ✅ **Radio transmission ready** - Special encoding for radio ops
- ✅ **Professional validation** - Prevents incomplete forms
- ✅ **Export capabilities** - JSON and PDF formats
- ✅ **Data persistence** - Never lose your work

## Installation

### Windows
1. Download `RadioForms-Windows.exe` from the releases page
2. Double-click to run (no installation required)
3. Windows may show a security warning - click "More info" then "Run anyway"

### macOS
1. Download `RadioForms-macOS.app` from the releases page
2. Drag to Applications folder or run directly
3. If blocked by security, go to System Preferences > Security & Privacy and click "Open Anyway"

### Linux
1. Download `RadioForms-Linux.AppImage` from the releases page
2. Make executable: `chmod +x RadioForms-Linux.AppImage`
3. Run: `./RadioForms-Linux.AppImage`

## First Launch

When you first start RadioForms:

1. **Welcome Screen**: You'll see the main application window
2. **Empty Form**: A blank ICS-213 form will be displayed
3. **Menu Bar**: File, Edit, Form, View, and Help menus are available
4. **Status Bar**: Shows application status at the bottom

## Creating Your First ICS-213 Form

### Step 1: Fill in Basic Information

1. **Incident Name**: Enter the name of your incident (e.g., "Wildfire Alpha Response")
2. **To Field**: 
   - Name: Enter recipient's name (e.g., "John Smith")
   - Position: Enter their position (e.g., "Incident Commander")
3. **From Field**:
   - Name: Enter your name (e.g., "Jane Doe")
   - Position: Enter your position (e.g., "Operations Chief")

### Step 2: Message Details

1. **Subject**: Enter a clear subject line (e.g., "Status Update - Sector 3")
2. **Date**: Enter today's date in YYYY-MM-DD format (e.g., "2025-05-30")
3. **Time**: Enter current time in HH:MM format (e.g., "14:30")
4. **Message**: Enter your message content

### Step 3: Set Priority

1. Click **Form** menu > **Priority**
2. Choose from:
   - **Routine**: Normal operational messages
   - **Urgent**: Time-sensitive messages
   - **Immediate**: Emergency or life-safety messages

### Step 4: Validate Your Form

1. Press **F5** or click **Form** menu > **Validate Form**
2. If errors are found, fix them (red text will show specific issues)
3. Green checkmark means your form is valid

### Step 5: Save Your Form

1. Press **Ctrl+S** or click **File** menu > **Save**
2. Your form is automatically saved to the local database
3. Status bar will confirm successful save

## Essential Features

### Keyboard Shortcuts
- **Ctrl+N**: New form
- **Ctrl+S**: Save form
- **Ctrl+I**: Import JSON file
- **Ctrl+E**: Export to JSON
- **F5**: Validate form
- **Ctrl+L**: Clear form
- **F1**: Show help

### Export Options

#### JSON Export (for backup/sharing)
1. Click **File** menu > **Export to JSON**
2. Choose location and filename
3. File includes all form data and metadata

#### Radio Transmission Format
*Coming in future versions*

### Form Management

#### Loading Previous Forms
1. Click **File** menu > **Open Recent** (when available)
2. Or use **File** menu > **Import from JSON**

#### Creating Multiple Forms
1. Use **Ctrl+N** to create a new form
2. Each form is saved independently
3. Form list shows all saved forms

## Common Tasks

### Sending a Status Update
1. Create new form (**Ctrl+N**)
2. Fill in To/From information
3. Subject: "Status Update - [Your Location/Unit]"
4. Set priority to **Urgent** if time-sensitive
5. Include:
   - Current status of your area/unit
   - Any resource needs
   - Safety concerns
   - Expected next update time
6. Validate (**F5**) and save (**Ctrl+S**)

### Requesting Resources
1. Create new form with subject "Resource Request"
2. Set priority to **Urgent**
3. In message, include:
   - Specific resources needed
   - Quantity required
   - Deployment location
   - Contact information
   - Urgency/timeline
4. Request reply by checking "Reply Requested" if available

### Reporting an Emergency
1. Create new form immediately
2. Set priority to **Immediate**
3. Subject: "EMERGENCY - [Brief Description]"
4. Include:
   - Exact location
   - Nature of emergency
   - Number of people involved
   - Resources responding
   - Contact information
5. Send immediately via available communication

## Best Practices

### Form Completion
- ✅ Always fill in required fields (marked with validation)
- ✅ Use clear, specific subject lines
- ✅ Include relevant details in message body
- ✅ Set appropriate priority level
- ✅ Validate before saving

### Message Content
- ✅ Be concise but complete
- ✅ Use standard ICS terminology
- ✅ Include location information
- ✅ Specify any actions needed
- ✅ Provide contact information

### Data Management
- ✅ Save forms regularly (**Ctrl+S**)
- ✅ Export important forms to JSON for backup
- ✅ Use descriptive incident names
- ✅ Keep subject lines consistent for related messages

## Troubleshooting Quick Fixes

### Form Won't Validate
- Check that To and From fields have both name and position
- Ensure Subject field is not empty
- Verify Date and Time are filled in
- Make sure Message content is provided

### Can't Save Form
- Check that you have write permissions in the application directory
- Ensure disk space is available
- Try validating the form first

### Application Won't Start
- Check that you have proper permissions to run the executable
- On Windows: Right-click and "Run as Administrator" if needed
- On macOS: Check Security & Privacy settings
- On Linux: Ensure the file is executable (`chmod +x`)

## Need Help?

### In-Application Help
- Press **F1** for keyboard shortcuts
- Check **Help** menu for documentation links
- Status bar shows current operation status

### Getting Support
- Review the [User Manual](user-manual.md) for detailed information
- Check the [FAQ](faq.md) for common questions
- See [Troubleshooting Guide](troubleshooting.md) for problem resolution

### Reporting Issues
If you encounter problems:
1. Note the exact error message
2. Record the steps that led to the issue
3. Check if you can reproduce the problem
4. Report via GitHub issues page

## Next Steps

Once you're comfortable with basic operations:

1. Read the [Complete User Manual](user-manual.md)
2. Learn about [Advanced Features](user-manual.md#advanced-features)
3. Review [ICS-213 Form Guidelines](user-manual.md#ics-213-guidelines)
4. Explore [Integration Options](user-manual.md#integration)

## Emergency Contact Information

For emergency situations where the application is critical to operations:

1. **First**: Try the troubleshooting steps above
2. **If urgent**: Use paper forms as backup
3. **Report issues**: Document problems for future improvement

---

**Welcome to RadioForms!** You're now ready to create professional ICS-213 forms efficiently and reliably.