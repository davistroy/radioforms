# RadioForms Frequently Asked Questions (FAQ)

## General Questions

### What is RadioForms?

RadioForms is a desktop application designed specifically for emergency management personnel to create, manage, and transmit FEMA ICS (Incident Command System) forms. It focuses on the ICS-213 General Message form and operates completely offline for maximum reliability during emergencies.

### Do I need an internet connection to use RadioForms?

No! RadioForms is designed to work completely offline. This is intentional - during emergencies, internet connectivity may be unreliable or unavailable. All your data is stored locally on your computer.

### Is RadioForms free to use?

Yes, RadioForms is open-source software and free to use. There are no licensing fees, subscription costs, or usage limits.

### What operating systems does RadioForms support?

RadioForms runs on:
- **Windows 10 and newer**
- **macOS 10.14 (Mojave) and newer**
- **Linux distributions** (Ubuntu 18.04+ and equivalent)

### How much space does RadioForms require?

The application itself is approximately 50MB. For data storage, plan for:
- **Light use**: 10MB for hundreds of forms
- **Moderate use**: 100MB for thousands of forms
- **Heavy use**: 1GB+ for extensive incident documentation

## Installation and Setup

### Why does Windows show a security warning when I run RadioForms?

This is normal for downloaded applications. Windows doesn't recognize the publisher because RadioForms is open-source software. To run safely:
1. Click "More info" in the warning dialog
2. Click "Run anyway" 
3. The warning won't appear again

### Can I install RadioForms on multiple computers?

Yes! RadioForms is portable software. You can:
- Run it from a USB drive
- Install on multiple computers
- Copy the executable file anywhere
- No registration or activation required

### How do I update RadioForms to a new version?

1. Download the new version from the releases page
2. Close the current RadioForms application
3. Replace the old executable with the new one
4. Your data and settings are preserved automatically

### Can I run RadioForms from a USB drive?

Yes! RadioForms is fully portable. Copy the executable to a USB drive and run it directly. Your forms database will be created on the USB drive, making your data portable too.

## Using ICS-213 Forms

### What are the required fields for a valid ICS-213 form?

To pass validation, you must fill in:
- **To**: Recipient name and position
- **From**: Your name and position  
- **Subject**: Brief description of the message
- **Date**: When the message was created (YYYY-MM-DD format)
- **Time**: When the message was created (HH:MM format)
- **Message**: The actual message content

### How do I know if my form is valid?

Press **F5** or use **Form Menu > Validate Form**. The system will:
- Show a green checkmark if valid
- Display specific error messages for any problems
- Highlight problematic fields in red

### What's the difference between the priority levels?

- **Routine**: Normal operational messages, status updates, administrative communication
- **Urgent**: Time-sensitive operational messages, resource requests with deadlines
- **Immediate**: Life-safety emergencies, critical situations requiring immediate action

When in doubt, use Routine. Only use Immediate for true emergencies.

### Can I save incomplete forms?

Yes! You can save forms at any time, even if they're incomplete. This lets you:
- Work on forms over time
- Save drafts for later completion
- Preserve work if you need to close the application
- Collaborate with others on form content

### How do I correct a form after it's been sent?

Create a new form with:
- Subject: "CORRECTION - [Original Subject]"
- Reference to the original message
- Complete corrected information
- Clear indication of what was corrected

## Data Management

### Where are my forms stored?

Forms are stored in a local database on your computer:
- **Windows**: `%USERPROFILE%/Documents/RadioForms/`
- **macOS**: `~/Documents/RadioForms/`
- **Linux**: `~/Documents/RadioForms/`

### How do I backup my forms?

**Automatic backups** are created daily and stored in the backup folder.

**Manual backup**:
1. Use **File Menu > Export to JSON** for individual forms
2. Use **File Menu > Export All** for complete backup
3. Copy the entire RadioForms folder for full backup

### Can I share forms with other people?

Yes! Export forms to JSON format:
1. **File Menu > Export to JSON**
2. Choose a location and filename
3. Share the JSON file
4. Recipients can import using **File Menu > Import from JSON**

### What happens if my computer crashes while using RadioForms?

RadioForms includes crash protection:
- **Auto-save**: Forms are saved automatically
- **Database recovery**: SQLite database with corruption protection
- **Backup restoration**: Recent backups can restore lost data
- **Form recovery**: Unsaved changes may be recoverable

### Can I move my forms to a different computer?

Yes! Several methods:
1. **Export/Import**: Export all forms to JSON and import on new computer
2. **Database copy**: Copy the entire RadioForms folder to new computer
3. **USB drive**: Run RadioForms from USB drive with portable data

## Technical Issues

### RadioForms won't start - what should I do?

**On Windows**:
1. Right-click and "Run as Administrator"
2. Check Windows Defender hasn't quarantined it
3. Ensure you have latest Windows updates
4. Try downloading a fresh copy

**On macOS**:
1. Go to System Preferences > Security & Privacy
2. Click "Open Anyway" if RadioForms is listed
3. Or try right-clicking and selecting "Open"

**On Linux**:
1. Make sure the file is executable: `chmod +x RadioForms-Linux.AppImage`
2. Check you have required libraries installed
3. Try running from terminal to see error messages

### My forms won't save - what's wrong?

Check these common issues:
1. **Disk space**: Ensure you have available storage
2. **Permissions**: Make sure you can write to the RadioForms folder
3. **Antivirus**: Some antivirus software blocks database writes
4. **Form validation**: Invalid forms may not save (validate first)

### The application is running slowly - how can I fix this?

Performance optimization:
1. **Close other applications** to free memory
2. **Clean up old forms** by exporting and deleting
3. **Restart RadioForms** periodically
4. **Check available disk space** - low space slows everything down
5. **Run database maintenance** (planned for future versions)

### I accidentally deleted a form - can I recover it?

Recovery options:
1. **Check backups**: Look in the backups folder for recent copies
2. **Check exports**: You may have exported the form earlier
3. **Database recovery**: Some deleted data may be recoverable (contact support)
4. **Paper backup**: Check if you have paper copies

## Features and Functionality

### Can I print my forms?

Direct printing is planned for future versions. Currently:
1. Export to JSON
2. Copy text content to word processor
3. Format and print from word processor

PDF export with print-ready formatting is coming in a future release.

### Does RadioForms support other ICS forms besides ICS-213?

Currently, RadioForms focuses on ICS-213 General Message forms. Support for additional ICS forms (like ICS-214 Activity Log) is planned for future releases based on user feedback.

### Can I customize the form fields or add new ones?

The ICS-213 form follows FEMA standards, so core fields cannot be modified. However:
- **Custom templates** are planned for future versions
- **User-defined fields** may be added in advanced versions
- **Organization-specific information** can be included in signature blocks

### Is there a mobile version of RadioForms?

RadioForms is currently desktop-only. However:
- It works on laptops and tablets with Windows/macOS/Linux
- Mobile companion app is under consideration for future development
- Data can be synced via JSON export/import

### Can RadioForms integrate with our existing emergency management software?

Integration capabilities:
- **JSON export/import** works with most systems
- **Database access** possible for advanced users
- **API development** planned for future versions
- **Custom integration** may be possible (contact developers)

## Workflow and Best Practices

### How should our team use RadioForms during an incident?

**Recommended workflow**:
1. **Designate primary operator** for each location/position
2. **Establish communication schedule** (hourly updates, etc.)
3. **Use consistent naming** for incidents and positions
4. **Create message templates** for common scenarios
5. **Backup data** at end of each operational period

### Should I use RadioForms or paper forms?

**Use RadioForms when**:
- You have reliable power and computer access
- Electronic transmission is available or planned
- You need to maintain digital records
- Multiple people need access to the same information

**Use paper forms when**:
- Power or computer reliability is questionable
- You need immediate transmission via radio voice
- Backup documentation is required
- Working in harsh environmental conditions

### How do we train our team on RadioForms?

**Training approach**:
1. **Start with [Getting Started Guide](getting-started.md)** (15 minutes)
2. **Practice with sample scenarios** (30 minutes)
3. **Review ICS-213 standards** and your SOPs
4. **Conduct regular refresher training** (monthly recommended)

### What's the best way to organize forms during a long incident?

**Organization strategies**:
- **Use consistent incident naming** across all forms
- **Include time/date in subject lines** for chronological ordering
- **Export forms daily** for backup and archival
- **Create form logs** listing all messages sent/received
- **Use priority levels consistently** to filter important messages

## Integration and Compatibility

### Can I import forms from other software?

Currently supported:
- **JSON format**: Native RadioForms format
- **Manual entry**: Copy/paste from other applications

Planned for future versions:
- **CSV import**: From spreadsheet applications  
- **XML import**: From other emergency management systems
- **Direct integration**: With common EM software platforms

### Does RadioForms work with our radio system?

Radio integration features:
- **Current**: Forms can be read over radio voice communications
- **Planned**: Special radio encoding format for digital transmission
- **Future**: Direct integration with digital radio systems

### Can we use RadioForms with our agency's existing procedures?

Yes! RadioForms is designed to complement existing procedures:
- **Follows ICS standards** used by most agencies
- **Flexible enough** to adapt to local procedures
- **Export capabilities** integrate with existing documentation systems
- **No changes required** to your current ICS structure

## Support and Development

### How do I report a bug or request a feature?

**For bugs**:
1. Note exact error messages and steps to reproduce
2. Check this FAQ and [Troubleshooting Guide](troubleshooting.md)
3. Report via GitHub issues page
4. Include your operating system and RadioForms version

**For feature requests**:
1. Check existing feature requests on GitHub
2. Describe your use case and needs
3. Explain how it would improve your operations
4. Consider contributing to development

### Is there official support available?

RadioForms is open-source software with community support:
- **Documentation**: Comprehensive guides available
- **Community**: User forums and discussion groups
- **GitHub**: Issue tracking and feature requests
- **No formal support contract**: Software provided as-is

### Can our organization contribute to RadioForms development?

Absolutely! Contributions welcome:
- **Testing**: Report bugs and test new features
- **Documentation**: Improve guides and help content
- **Code**: Contribute programming improvements
- **Funding**: Support development of specific features

### Where can I get training or consulting services?

While RadioForms itself is free, third-party services may be available:
- **Training providers**: Emergency management trainers may offer RadioForms training
- **Consultants**: System integration specialists
- **User groups**: Local emergency management associations

### What's the development roadmap for RadioForms?

**Next version priorities** (based on user feedback):
1. PDF export and printing capabilities
2. ICS-214 Activity Log form support
3. Form templates and customization
4. Enhanced search and filtering
5. Mobile companion application

**Long-term goals**:
- Complete ICS form suite (201-225 series)
- Radio transmission integration
- Multi-user and synchronization capabilities
- GIS and mapping integration

---

## Need More Help?

If your question isn't answered here:

1. Check the [User Manual](user-manual.md) for detailed information
2. Review the [Troubleshooting Guide](troubleshooting.md) for technical issues
3. Search existing questions on the GitHub issues page
4. Contact the community via forums or discussion groups

**Remember**: During actual emergencies, always have paper backup procedures available in case of technical issues.