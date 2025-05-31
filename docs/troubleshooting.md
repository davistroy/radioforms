# RadioForms Troubleshooting Guide

## Quick Diagnosis

### Emergency Checklist

If RadioForms is not working during an emergency:

1. **✅ Immediate Action**: Switch to paper forms
2. **✅ Save work**: Export any unsaved forms to JSON
3. **✅ Restart**: Close and restart RadioForms
4. **✅ Verify data**: Check that forms are still accessible
5. **✅ Document issue**: Note exactly what happened for later troubleshooting

### Common Solutions

**90% of issues are resolved by:**
- ✅ Restarting the application
- ✅ Checking file permissions
- ✅ Validating forms before saving
- ✅ Ensuring adequate disk space
- ✅ Running as administrator (Windows)

## Application Issues

### RadioForms Won't Start

#### Symptoms
- Double-clicking does nothing
- Error message appears immediately
- Application starts then crashes
- "File not found" or permission errors

#### Windows Solutions

**Security/Permission Issues:**
1. **Run as Administrator**:
   - Right-click on RadioForms.exe
   - Select "Run as administrator"
   - Check if application starts normally

2. **Windows Defender/Antivirus**:
   - Check Windows Defender quarantine
   - Add RadioForms folder to antivirus exclusions
   - Temporarily disable real-time protection for testing

3. **File Association Issues**:
   - Download fresh copy of RadioForms
   - Ensure file isn't corrupted during download
   - Check file properties for "Unblock" option

**System Requirements:**
1. **Check Windows Version**:
   - RadioForms requires Windows 10 or newer
   - Ensure latest Windows updates are installed
   - Check system architecture (64-bit recommended)

2. **Missing Dependencies**:
   - Install Microsoft Visual C++ Redistributable
   - Update .NET Framework if required
   - Install latest Windows updates

#### macOS Solutions

**Security Settings:**
1. **Gatekeeper Bypass**:
   - Go to System Preferences > Security & Privacy
   - Look for RadioForms in blocked applications
   - Click "Open Anyway"

2. **Alternative Method**:
   - Right-click on RadioForms.app
   - Select "Open" from context menu
   - Click "Open" in security dialog

**Permission Issues:**
1. **File Permissions**:
   - Check that RadioForms.app has execute permissions
   - Try moving to Applications folder
   - Ensure user has admin rights

#### Linux Solutions

**Execute Permissions:**
```bash
chmod +x RadioForms-Linux.AppImage
```

**Missing Libraries:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install libc6 libstdc++6 libgcc1

# CentOS/RHEL/Fedora  
sudo yum install glibc libstdc++ gcc
```

**FUSE for AppImage:**
```bash
# Ubuntu/Debian
sudo apt install fuse

# CentOS/RHEL
sudo yum install fuse
```

**Run from Terminal** (to see error messages):
```bash
./RadioForms-Linux.AppImage
```

### Application Crashes During Use

#### Symptoms
- Application closes unexpectedly
- "Application has stopped working" messages
- Frozen interface requiring force-quit
- Data loss after restart

#### Immediate Recovery
1. **Restart Application**:
   - Close all RadioForms windows
   - Wait 30 seconds
   - Restart application
   - Check for recovered data

2. **Check Auto-Recovery**:
   - RadioForms may recover unsaved forms
   - Look for "Recovered Forms" in file menu
   - Export recovered forms immediately

#### Prevention and Diagnosis

**System Resources:**
1. **Memory Issues**:
   - Close other applications to free memory
   - Restart computer if system is sluggish
   - Check Task Manager for memory usage

2. **Disk Space**:
   - Ensure at least 1GB free space
   - Clean temporary files
   - Check database folder size

**Software Conflicts:**
1. **Antivirus Interference**:
   - Add RadioForms to antivirus exclusions
   - Temporarily disable real-time scanning
   - Check antivirus logs for blocked actions

2. **Other Software**:
   - Close other database applications
   - Disable screen savers/power management
   - Check for Windows updates

### Slow Performance

#### Symptoms
- Long delays when opening forms
- Slow saving operations
- UI freezes temporarily
- High CPU or memory usage

#### Performance Solutions

**Database Optimization:**
1. **Export and Cleanup**:
   - Export old forms to JSON
   - Delete unnecessary forms from database
   - Restart application after cleanup

2. **File System Issues**:
   - Run disk cleanup utility
   - Check for hard drive errors
   - Ensure database folder isn't on network drive

**System Optimization:**
1. **Resource Management**:
   - Close unnecessary applications
   - Restart computer regularly
   - Check for malware/viruses

2. **Hardware Considerations**:
   - Ensure adequate RAM (4GB minimum, 8GB recommended)
   - Use SSD instead of traditional hard drive
   - Keep system updated

## Data and Database Issues

### Forms Won't Save

#### Symptoms
- "Save failed" error messages
- Forms appear to save but aren't in database
- Permission denied errors
- Database corruption warnings

#### File Permission Solutions

**Windows:**
1. **Check Folder Permissions**:
   - Navigate to Documents/RadioForms folder
   - Right-click > Properties > Security
   - Ensure your user has "Full Control"
   - Apply permissions to subfolders

2. **Run as Administrator**:
   - Start RadioForms as administrator
   - Try saving forms
   - Check if permission issue is resolved

**macOS/Linux:**
1. **Check Directory Permissions**:
   ```bash
   ls -la ~/Documents/RadioForms/
   chmod 755 ~/Documents/RadioForms/
   ```

2. **Ownership Issues**:
   ```bash
   sudo chown -R $USER:$USER ~/Documents/RadioForms/
   ```

#### Database Issues

**Database Corruption:**
1. **Automatic Recovery**:
   - Close RadioForms
   - Restart application
   - SQLite will attempt automatic recovery

2. **Manual Recovery**:
   - Locate backup files in backups/ folder
   - Copy most recent backup to main folder
   - Rename backup file to replace corrupted database

**Disk Space Issues:**
1. **Check Available Space**:
   - Ensure at least 100MB free space
   - Clean temporary files
   - Move large files to external storage

2. **Database Size Management**:
   - Export old forms and delete from database
   - Compress backup files
   - Monitor database growth

### Missing Forms

#### Symptoms
- Previously saved forms don't appear
- Form count decreased unexpectedly
- Search results missing expected forms
- Import/export issues

#### Recovery Procedures

**Check Backup Files:**
1. **Automatic Backups**:
   - Look in Documents/RadioForms/backups/
   - Find most recent backup before forms went missing
   - Import backup data using File > Import

2. **Manual Exports**:
   - Check Downloads folder for exported JSON files
   - Look in email attachments if forms were shared
   - Check external storage devices

**Database Investigation:**
1. **Database Location**:
   - Verify you're looking in correct database location
   - Check if multiple users have separate databases
   - Look for database files with different names

2. **Filter/Search Issues**:
   - Clear any active filters
   - Check date range settings
   - Verify search terms are correct

### Import/Export Problems

#### Export Issues

**JSON Export Failures:**
1. **File Permission Problems**:
   - Choose different export location
   - Ensure write permissions to destination
   - Try exporting to desktop first

2. **Form Validation**:
   - Validate forms before export
   - Fix any validation errors
   - Try exporting individual forms

**Large Export Problems:**
1. **Memory Issues**:
   - Export smaller batches of forms
   - Close other applications
   - Restart RadioForms before large exports

#### Import Issues

**JSON Import Failures:**
1. **File Format Validation**:
   - Verify JSON file is valid RadioForms format
   - Check file wasn't corrupted during transfer
   - Try importing a single known-good form first

2. **Version Compatibility**:
   - Ensure JSON was exported from compatible version
   - Check format version in JSON file
   - Update RadioForms if needed

**Data Conflicts:**
1. **Duplicate Forms**:
   - RadioForms may refuse to import duplicates
   - Delete existing forms if re-importing is needed
   - Check import logs for specific errors

## Form Validation Issues

### Common Validation Errors

#### "Recipient must have both name and position"
**Solution:**
- Fill in both "To Name" and "To Position" fields
- Ensure fields contain actual text, not just spaces
- Check for hidden characters (copy/paste issues)

#### "Sender must have both name and position"  
**Solution:**
- Fill in both "From Name" and "From Position" fields
- Use your actual name and ICS position
- Verify spelling and format

#### "Subject is required"
**Solution:**
- Enter descriptive subject line
- Subject should be specific to message content
- Avoid using only spaces or special characters

#### "Date is required" / "Time is required"
**Solution:**
- Date format: YYYY-MM-DD (e.g., "2025-05-30")
- Time format: HH:MM (24-hour, e.g., "14:30")
- Ensure both fields are completely filled

#### "Message content is required"
**Solution:**
- Enter actual message text in message field
- Message should contain meaningful content
- Avoid using only spaces or line breaks

### Advanced Validation Issues

#### Forms Validate But Won't Approve
**Causes:**
- Form status prevents approval
- Missing approver information
- Database permission issues

**Solutions:**
1. Check form status is "Draft"
2. Ensure approver has both name and position
3. Restart application and try again

#### Validation Seems Incorrect
**Troubleshooting:**
1. **Clear Form and Re-enter**:
   - Use Ctrl+L to clear form
   - Re-enter all information carefully
   - Check for copy/paste formatting issues

2. **Character Encoding Issues**:
   - Avoid special characters in names
   - Type directly instead of copy/paste
   - Check for hidden Unicode characters

## Integration and File Format Issues

### JSON File Problems

#### Can't Open Exported JSON Files
**Solutions:**
1. **File Association**:
   - Right-click JSON file > Open With > Text Editor
   - Use Notepad (Windows), TextEdit (macOS), or gedit (Linux)
   - JSON files are human-readable text

2. **File Corruption**:
   - Check file size (should be > 1KB for typical form)
   - Look for complete JSON structure
   - Re-export if file appears truncated

#### JSON Import Errors
**Common Issues:**
1. **Invalid JSON Format**:
   - File may be corrupted
   - Editing may have introduced errors
   - Use JSON validator online to check format

2. **Wrong Version**:
   - File may be from different version of RadioForms
   - Check "format_version" in JSON file
   - Update RadioForms if needed

### Database Transfer Issues

#### Moving Between Computers
**Complete Database Transfer:**
1. **Export Method** (Recommended):
   - Export all forms to JSON on source computer
   - Install RadioForms on destination computer
   - Import all JSON files

2. **File Copy Method**:
   - Close RadioForms on source computer
   - Copy entire Documents/RadioForms folder
   - Paste to same location on destination computer
   - Ensure file permissions are correct

**Partial Transfer Issues:**
- Some forms missing after transfer
- Database corruption during copy
- Permission issues on destination

**Solutions:**
- Always close RadioForms before copying database files
- Use export/import method for critical data
- Verify data integrity after transfer

## System-Specific Issues

### Windows-Specific Problems

#### Windows Defender Quarantine
**Symptoms:**
- RadioForms suddenly stops working
- "File not found" errors
- Recently downloaded version won't run

**Solution:**
1. Open Windows Defender Security Center
2. Go to Virus & threat protection
3. Check quarantine/history
4. Restore RadioForms if quarantined
5. Add to exclusions list

#### Windows Updates Breaking RadioForms
**Solutions:**
1. Download latest version of RadioForms
2. Check compatibility with new Windows version
3. Run Windows Update troubleshooter
4. Restore from backup if needed

### macOS-Specific Problems

#### "App is damaged and can't be opened"
**Solution:**
```bash
sudo xattr -r -d com.apple.quarantine RadioForms.app
```

#### Catalina+ Security Issues
**Solution:**
1. System Preferences > Security & Privacy
2. Privacy tab > Full Disk Access
3. Add RadioForms to allowed applications

### Linux-Specific Problems

#### AppImage Won't Run
**Solutions:**
1. **Install FUSE**:
   ```bash
   sudo apt install fuse libfuse2
   ```

2. **Extract and Run**:
   ```bash
   ./RadioForms-Linux.AppImage --appimage-extract
   ./squashfs-root/AppRun
   ```

#### Missing Libraries
**Common Missing Dependencies:**
```bash
# Ubuntu/Debian
sudo apt install libxcb-xinerama0 libxcb-cursor0

# CentOS/RHEL
sudo yum install xcb-util-cursor
```

## Emergency Procedures

### Data Loss Prevention

#### Before Troubleshooting
1. **Export Current Data**:
   - Export all accessible forms to JSON
   - Copy database files to safe location
   - Document current state and errors

2. **Backup Strategy**:
   - Use external storage for backups
   - Export to multiple formats if possible
   - Keep backups in different locations

#### During Emergencies
1. **Immediate Fallback**:
   - Switch to paper forms immediately
   - Continue operations without interruption
   - Document technical issues for later

2. **Quick Recovery**:
   - Try restart first (solves 80% of issues)
   - Use backup data if available
   - Import from recent exports

### Contact Information

#### Self-Help Resources
1. **Documentation**: Review user manual and FAQ
2. **Community**: Check GitHub issues and discussions
3. **Testing**: Use sample data to reproduce issues

#### Reporting Critical Issues
**For emergency-critical bugs:**
1. Document exact steps to reproduce
2. Note operating system and version
3. Include error messages or screenshots
4. Report via GitHub issues with "emergency" label

**Include in Bug Reports:**
- RadioForms version number
- Operating system and version
- Exact error messages
- Steps to reproduce the problem
- Sample data that triggers the issue (if safe to share)

---

## Prevention Tips

### Regular Maintenance
- **Weekly**: Export important forms to JSON
- **Monthly**: Restart RadioForms and computer
- **Quarterly**: Clean up old forms and run updates
- **Before major incidents**: Verify all systems working

### Best Practices
- **Always validate** forms before saving
- **Keep backups** of critical data
- **Test regularly** to catch issues early
- **Have paper backup** procedures ready
- **Train team** on basic troubleshooting

### System Health
- **Monitor disk space** (keep >1GB free)
- **Keep OS updated** but test RadioForms after updates
- **Use antivirus exclusions** for RadioForms folder
- **Regular system restarts** to clear memory issues

---

**Remember**: In actual emergencies, your mission comes first. Use paper forms if RadioForms isn't working, and troubleshoot technical issues after the emergency is resolved.