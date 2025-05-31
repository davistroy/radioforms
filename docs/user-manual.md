# RadioForms User Manual

## Table of Contents

1. [Introduction](#introduction)
2. [Application Overview](#application-overview)
3. [ICS-213 Form Guide](#ics-213-form-guide)
4. [Advanced Features](#advanced-features)
5. [Data Management](#data-management)
6. [Integration](#integration)
7. [Best Practices](#best-practices)
8. [Appendices](#appendices)

## Introduction

### About RadioForms

RadioForms is a professional desktop application designed specifically for emergency management personnel who need to create, manage, and transmit FEMA ICS (Incident Command System) forms. Built for reliability in emergency situations, RadioForms operates completely offline and provides the tools needed for effective incident communication.

### Key Benefits

**For Emergency Management Professionals:**
- ✅ **FEMA Compliance**: Forms meet official ICS-213 standards
- ✅ **Offline Reliability**: Works without internet connectivity
- ✅ **Professional Validation**: Prevents incomplete or invalid forms
- ✅ **Efficient Workflow**: Faster than paper forms, more reliable than generic software
- ✅ **Radio Integration**: Special encoding for radio transmission (upcoming)

**For Operations Teams:**
- ✅ **Quick Setup**: Start using in minutes
- ✅ **Intuitive Interface**: No training required for basic operations
- ✅ **Keyboard Shortcuts**: Fast data entry for experienced users
- ✅ **Data Persistence**: Never lose work due to application crashes

**For Command Staff:**
- ✅ **Standardized Communication**: Consistent format across all teams
- ✅ **Audit Trail**: Complete record of all messages
- ✅ **Export Capabilities**: Integration with other systems
- ✅ **Backup and Recovery**: Reliable data protection

### System Requirements

**Minimum Requirements:**
- **Operating System**: Windows 10, macOS 10.14, or Linux (Ubuntu 18.04+)
- **Memory**: 4GB RAM
- **Storage**: 100MB available space
- **Display**: 1024x768 resolution

**Recommended Requirements:**
- **Operating System**: Windows 11, macOS 12+, or recent Linux distribution
- **Memory**: 8GB RAM
- **Storage**: 1GB available space (for form storage)
- **Display**: 1920x1080 resolution or higher

## Application Overview

### Main Window Components

#### Menu Bar
The menu bar provides access to all application functions:

**File Menu:**
- New (Ctrl+N): Create a new form
- Save (Ctrl+S): Save current form
- Save As (Ctrl+Shift+S): Save with new name
- Import (Ctrl+I): Import form from JSON file
- Export (Ctrl+E): Export form to JSON file
- Recent Files: Quick access to recently used forms
- Exit (Ctrl+Q): Close application

**Edit Menu:**
- Validate (F5): Check form for errors
- Clear (Ctrl+L): Clear all form data

**Form Menu:**
- Approve (Ctrl+A): Approve form for transmission
- Add Reply (Ctrl+R): Add reply to received message
- Priority: Set message priority level

**View Menu:**
- Refresh (F5): Refresh current view
- Status Bar: Toggle status bar visibility

**Help Menu:**
- Documentation (F1): Open help system
- Keyboard Shortcuts: Show shortcut reference
- About: Application information

#### Form Area
The central area displays the current ICS-213 form with the following sections:

**Header Section:**
- Incident Name
- To (Recipient information)
- From (Sender information)
- Subject line
- Date and Time

**Message Section:**
- Priority level indicator
- Main message content area
- Reply requested checkbox

**Approval Section:**
- Approved by information
- Approval timestamp

**Reply Section:**
- Reply message content
- Replied by information
- Reply timestamp

#### Status Bar
The bottom status bar shows:
- Current operation status
- Form validation status
- Save status
- Application messages

### User Interface Themes

RadioForms supports multiple visual themes for different operational environments:

**Light Theme (Default):**
- High contrast for normal lighting conditions
- Professional appearance for office environments
- Easy reading on standard displays

**Dark Theme:**
- Reduced eye strain in low-light conditions
- Popular for emergency operations centers
- Better for extended use periods

**High Contrast Theme:**
- Maximum visibility for challenging conditions
- Accessibility compliance
- Essential for emergency lighting situations

*Theme selection: View Menu > Themes (planned for future release)*

## ICS-213 Form Guide

### Understanding ICS-213 Forms

The ICS-213 General Message form is a standardized communication tool used throughout the Incident Command System. It provides a structured format for:

- **Operational messages** between ICS positions
- **Status reports** from field units to command
- **Resource requests** for personnel, equipment, or supplies
- **Information sharing** between agencies and jurisdictions
- **Documentation** of important decisions and actions

### Required Fields

For a form to be valid and transmittable, the following fields must be completed:

#### To (Recipient) Information
- **Name**: Full name of the recipient
- **Position**: ICS position (e.g., "Incident Commander", "Operations Chief")

*Example: Name: "John Smith", Position: "Safety Officer"*

#### From (Sender) Information
- **Name**: Your full name
- **Position**: Your ICS position

*Example: Name: "Jane Doe", Position: "Communications Unit Leader"*

#### Message Details
- **Subject**: Clear, descriptive subject line
- **Date**: Message date in YYYY-MM-DD format
- **Time**: Message time in HH:MM format (24-hour)
- **Message**: The main message content

#### Optional Fields

**Incident Information:**
- **Incident Name**: Name of the incident (recommended for all messages)

**Contact Information:**
- **Signature**: Electronic signature or initials
- **Contact Info**: Radio frequency, phone number, or email

**Priority Information:**
- **Priority Level**: Routine, Urgent, or Immediate
- **Reply Requested**: Whether a response is needed

**Approval Information:**
- **Approved By**: Name and position of approving authority
- **Approval Date/Time**: When approval was granted

**Reply Information:**
- **Reply**: Response to the original message
- **Replied By**: Name and position of person providing reply
- **Reply Date/Time**: When reply was provided

### Priority Levels

Understanding and correctly setting priority levels is crucial for effective incident communication:

#### Routine Priority
**Use for:**
- Regular status updates
- Administrative messages
- Information sharing
- Non-urgent resource requests
- Documentation messages

**Examples:**
- "Daily status report for Division A"
- "Logistics meeting scheduled for 1400 hours"
- "Equipment inventory update"

#### Urgent Priority
**Use for:**
- Time-sensitive operational messages
- Resource requests with deadlines
- Weather or hazard updates
- Coordination messages
- Safety notifications

**Examples:**
- "Request immediate deployment of medical team"
- "Weather service issues high wind warning"
- "Evacuation route update for public information"

#### Immediate Priority
**Use for:**
- Life safety emergencies
- Critical resource failures
- Imminent danger notifications
- Emergency evacuations
- Major incident developments

**Examples:**
- "MAYDAY - Firefighter down, request immediate assistance"
- "Bridge collapse blocks primary evacuation route"
- "Chemical leak requires immediate area evacuation"

### Form Validation

RadioForms automatically validates your forms to ensure they meet ICS-213 standards:

#### Automatic Validation
- **Real-time checking**: Fields are validated as you type
- **Visual indicators**: Invalid fields are highlighted
- **Error messages**: Specific guidance for fixing issues

#### Manual Validation
- **F5 key**: Run complete validation check
- **Form Menu**: Select "Validate Form"
- **Pre-save validation**: Automatic check before saving

#### Common Validation Errors

**"Recipient must have both name and position"**
- Solution: Fill in both the To Name and To Position fields

**"Sender must have both name and position"**
- Solution: Fill in both the From Name and From Position fields

**"Subject is required"**
- Solution: Enter a descriptive subject line

**"Date is required"**
- Solution: Enter date in YYYY-MM-DD format

**"Time is required"**
- Solution: Enter time in HH:MM format (24-hour)

**"Message content is required"**
- Solution: Enter the main message text

### Form Lifecycle

Understanding the form lifecycle helps with proper workflow management:

#### 1. Draft Status
- Initial state for new forms
- Allows editing and modification
- Can be saved incomplete for later completion
- Not ready for transmission

#### 2. Validated Status
- Form passes all validation checks
- Ready for approval process
- Can be transmitted if no approval required
- Recommended before sending

#### 3. Approved Status
- Reviewed and approved by appropriate authority
- Ready for transmission
- Includes approver information
- Locked against major changes

#### 4. Transmitted Status
- Sent via communication channels
- Timestamp recorded
- Awaiting acknowledgment
- Part of official record

#### 5. Received Status
- Acknowledgment received
- Delivery confirmed
- Communication loop closed
- Archived for reference

#### 6. Replied Status
- Response provided
- Two-way communication complete
- Full documentation available
- Ready for archival

## Advanced Features

### Form Templates

*Note: Template functionality is planned for future releases*

**Personal Templates:**
- Save frequently used form structures
- Pre-filled sender information
- Common message types
- Quick form creation

**Organizational Templates:**
- Standardized formats for specific message types
- Department-specific information
- Compliance with local procedures
- Shared across team members

### Batch Operations

**Multiple Form Export:**
- Export all forms from an incident
- Create backup archives
- Share complete message logs
- Maintain audit trails

**Bulk Form Import:**
- Import forms from other systems
- Restore from backups
- Merge multiple databases
- Data migration support

### Search and Filtering

*Note: Search functionality is planned for future releases*

**Search Capabilities:**
- Full-text search across all forms
- Search by date range
- Filter by form status
- Find specific incidents

**Advanced Filters:**
- Priority level filtering
- Sender/recipient filtering
- Form type classification
- Time-based queries

### Keyboard Shortcuts

Master these shortcuts for efficient operation:

#### File Operations
- **Ctrl+N**: New form
- **Ctrl+S**: Save form
- **Ctrl+Shift+S**: Save as
- **Ctrl+I**: Import JSON
- **Ctrl+E**: Export JSON
- **Ctrl+Q**: Exit application

#### Form Operations
- **F5**: Validate form
- **Ctrl+L**: Clear form
- **Ctrl+A**: Approve form
- **Ctrl+R**: Add reply

#### Priority Setting
- **Ctrl+1**: Set to Routine
- **Ctrl+2**: Set to Urgent
- **Ctrl+3**: Set to Immediate

#### View Operations
- **F5**: Refresh view
- **F1**: Show help

#### Navigation
- **Tab**: Move to next field
- **Shift+Tab**: Move to previous field
- **Enter**: Confirm input in some fields

## Data Management

### Local Data Storage

RadioForms stores all data locally on your computer for maximum reliability and security:

**Database Location:**
- Windows: `%USERPROFILE%/Documents/RadioForms/`
- macOS: `~/Documents/RadioForms/`
- Linux: `~/Documents/RadioForms/`

**Database Format:**
- SQLite database with WAL mode
- Automatic corruption recovery
- Optimized for single-user access
- Cross-platform compatibility

### Backup and Recovery

#### Automatic Backups
- **Daily backups**: Automatic backup creation
- **Rotation policy**: Keeps last 30 days
- **Incremental backups**: Only changed data
- **Corruption protection**: Multiple backup copies

#### Manual Backup
1. **Export All Data**: File Menu > Export All Forms
2. **Choose Location**: Select backup directory
3. **JSON Format**: Human-readable backup files
4. **Verify Backup**: Test import on different system

#### Recovery Procedures
1. **Database Corruption**: Automatic recovery from WAL files
2. **Complete Loss**: Restore from JSON backups
3. **Partial Loss**: Selective form restoration
4. **Migration**: Move data between computers

### Data Export Options

#### JSON Export
**Single Form Export:**
- Complete form data and metadata
- Human-readable format
- Cross-platform compatibility
- Version information included

**Multiple Form Export:**
- Batch export for incidents
- Compressed archive option
- Metadata preservation
- Audit trail maintenance

#### Future Export Options
*Planned for upcoming releases:*
- **PDF Export**: Print-ready forms
- **CSV Export**: Spreadsheet compatibility
- **XML Export**: System integration
- **Radio Format**: Compressed transmission

### Data Import Capabilities

#### JSON Import
- **Single Form**: Import individual forms
- **Batch Import**: Multiple forms at once
- **Validation**: Automatic format checking
- **Merge Options**: Handle duplicate data

#### Migration Support
- **Database Upgrade**: Automatic schema migration
- **Version Compatibility**: Backward compatibility
- **Data Integrity**: Validation during import
- **Error Recovery**: Graceful failure handling

### Privacy and Security

#### Data Protection
- **Local-only storage**: No cloud transmission
- **No telemetry**: No usage data collection
- **Access control**: File system permissions
- **Secure deletion**: Complete data removal

#### Audit Trail
- **Form history**: Complete change tracking
- **User identification**: Creator and modifier tracking
- **Timestamp accuracy**: Precise time recording
- **Integrity verification**: Data consistency checks

## Integration

### System Integration

#### Emergency Management Systems
*Future integration capabilities:*
- **WebEOC integration**: Direct form transfer
- **GIS mapping**: Location-based messaging
- **CAD systems**: Incident linking
- **Resource management**: Status updates

#### Communication Systems
- **Radio integration**: Direct transmission capability
- **Email systems**: Form delivery via email
- **Messaging platforms**: Team communication
- **Mobile devices**: Cross-platform sync

### File Format Compatibility

#### Supported Import Formats
- **JSON**: Native RadioForms format
- **CSV**: Basic data import (planned)
- **XML**: System integration (planned)

#### Supported Export Formats
- **JSON**: Complete data export
- **PDF**: Print-ready forms (planned)
- **Radio encoding**: Transmission format (planned)

### API Capabilities

*Future API development:*
- **REST API**: External system integration
- **Webhook support**: Real-time notifications
- **Database access**: Direct data queries
- **Plugin architecture**: Custom extensions

## Best Practices

### Form Creation Guidelines

#### Message Structure
**Clear Subject Lines:**
- Use specific, descriptive subjects
- Include location when relevant
- Indicate action required
- Keep under 60 characters

*Examples:*
- "Status Update - Division A Sector 3"
- "Resource Request - Medical Team"
- "URGENT - Evacuation Route Blocked"

**Effective Message Content:**
- Start with most important information
- Use bullet points for lists
- Include specific details (times, locations, quantities)
- End with clear action items or next steps

#### Contact Information
**Complete Sender Information:**
- Always include your full name and position
- Add radio frequency or phone number
- Include backup contact method
- Update signature block regularly

**Accurate Recipient Information:**
- Verify recipient name and position
- Use correct ICS position titles
- Include contact information when available
- Copy appropriate personnel when needed

### Operational Procedures

#### During Incidents
1. **Establish Communication Plan**: Determine who needs what information
2. **Set Update Schedule**: Regular status reports at specified intervals
3. **Use Consistent Format**: Standardize message structure across team
4. **Maintain Message Log**: Keep complete record of all communications
5. **Backup Regularly**: Export forms at end of each operational period

#### Form Review Process
1. **Self-Review**: Check for completeness and accuracy
2. **Validation**: Run automatic validation check
3. **Peer Review**: Have colleague review important messages
4. **Approval**: Get supervisor approval for significant messages
5. **Distribution**: Send via appropriate channels

#### Quality Control
- **Spell Check**: Review for spelling and grammar errors
- **Fact Check**: Verify all information is accurate
- **Format Check**: Ensure consistent formatting
- **Priority Check**: Confirm appropriate priority level
- **Follow-up**: Track responses and acknowledgments

### Team Coordination

#### Standardization
**Message Templates:**
- Develop standard formats for common message types
- Share templates across team members
- Update templates based on experience
- Train team on proper usage

**Naming Conventions:**
- Use consistent incident naming
- Standardize position titles
- Establish contact information format
- Create reference guides

#### Training Recommendations
**Initial Training:**
- 30-minute application overview
- Practice with sample forms
- Review ICS-213 standards
- Hands-on exercises

**Ongoing Training:**
- Monthly refresher sessions
- Share lessons learned
- Update on new features
- Cross-training on different positions

## Appendices

### Appendix A: ICS Position Reference

Common ICS positions for the "Position" field:

**Command Staff:**
- Incident Commander (IC)
- Deputy Incident Commander
- Safety Officer (SO)
- Public Information Officer (PIO)
- Liaison Officer (LNO)

**Operations Section:**
- Operations Chief
- Deputy Operations Chief
- Division Supervisor
- Group Supervisor
- Task Force Leader
- Strike Team Leader
- Single Resource Boss

**Planning Section:**
- Planning Chief
- Deputy Planning Chief
- Resources Unit Leader
- Situation Unit Leader
- Documentation Unit Leader
- Demobilization Unit Leader
- Technical Specialists

**Logistics Section:**
- Logistics Chief
- Deputy Logistics Chief
- Service Branch Director
- Support Branch Director
- Communications Unit Leader
- Medical Unit Leader
- Food Unit Leader
- Supply Unit Leader
- Facilities Unit Leader
- Ground Support Unit Leader

**Finance/Administration Section:**
- Finance/Administration Chief
- Time Unit Leader
- Procurement Unit Leader
- Compensation/Claims Unit Leader
- Cost Unit Leader

### Appendix B: Common Message Types

#### Status Reports
**Purpose**: Regular updates on operational status
**Frequency**: As scheduled (typically hourly or by operational period)
**Priority**: Usually Routine
**Content**: Current status, resource needs, safety issues, next report time

#### Resource Requests
**Purpose**: Request personnel, equipment, or supplies
**Frequency**: As needed
**Priority**: Urgent (if time-sensitive) or Routine
**Content**: Specific resources needed, quantities, delivery location, timeline

#### Safety Messages
**Purpose**: Report safety concerns or incidents
**Frequency**: Immediate when issues arise
**Priority**: Urgent or Immediate (depending on severity)
**Content**: Nature of hazard, location, personnel affected, actions taken

#### Weather Updates
**Purpose**: Share weather information affecting operations
**Frequency**: When conditions change
**Priority**: Urgent (if operational impact) or Routine
**Content**: Current conditions, forecast, operational impacts

#### Evacuation Orders
**Purpose**: Coordinate evacuation activities
**Frequency**: As needed
**Priority**: Immediate
**Content**: Areas to evacuate, routes, timing, coordination points

### Appendix C: Troubleshooting Reference

#### Application Issues

**Application Won't Start:**
1. Check file permissions
2. Run as administrator (Windows)
3. Check system requirements
4. Restart computer
5. Re-download application

**Forms Won't Save:**
1. Check disk space
2. Verify write permissions
3. Close other applications
4. Check database integrity
5. Export data as backup

**Validation Errors:**
1. Review all required fields
2. Check field format requirements
3. Verify data completeness
4. Clear and re-enter problematic fields
5. Restart application if errors persist

#### Data Issues

**Missing Forms:**
1. Check form list/search
2. Verify database location
3. Check backup files
4. Review export files
5. Check other user accounts

**Corrupt Data:**
1. Close application
2. Restart application (automatic recovery)
3. Restore from backup
4. Export remaining data
5. Create new database

**Import Failures:**
1. Verify file format
2. Check file integrity
3. Review error messages
4. Try smaller batches
5. Validate source data

### Appendix D: Keyboard Shortcuts Reference

#### Quick Reference Card

**File Operations:**
- Ctrl+N: New form
- Ctrl+S: Save
- Ctrl+Shift+S: Save As
- Ctrl+I: Import
- Ctrl+E: Export
- Ctrl+Q: Exit

**Form Operations:**
- F5: Validate
- Ctrl+L: Clear
- Ctrl+A: Approve
- Ctrl+R: Add Reply

**Priority:**
- Ctrl+1: Routine
- Ctrl+2: Urgent  
- Ctrl+3: Immediate

**Help:**
- F1: Documentation

**Navigation:**
- Tab: Next field
- Shift+Tab: Previous field
- Enter: Confirm entry

### Appendix E: File Formats

#### JSON Export Format
```json
{
  "radioforms_export": {
    "format_version": "1.0",
    "export_timestamp": "2025-05-30T19:30:00Z",
    "form_type": "ICS-213"
  },
  "form": {
    "data": {
      "incident_name": "Wildfire Alpha",
      "to": {
        "name": "John Smith",
        "position": "Incident Commander"
      },
      "from_person": {
        "name": "Jane Doe", 
        "position": "Operations Chief"
      },
      "subject": "Status Update",
      "date": "2025-05-30",
      "time": "14:30",
      "message": "All teams deployed and operational.",
      "priority": "urgent"
    },
    "status": "approved",
    "created_at": "2025-05-30T14:30:00Z",
    "updated_at": "2025-05-30T14:32:00Z"
  }
}
```

---

**RadioForms User Manual v1.0**  
*For technical support, see the [FAQ](faq.md) and [Troubleshooting Guide](troubleshooting.md)*