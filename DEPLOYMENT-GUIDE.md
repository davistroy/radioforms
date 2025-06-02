# RadioForms Deployment Guide
*IT Staff Installation & Configuration*

## System Requirements

### Minimum Hardware
- **CPU:** Intel i3 or AMD equivalent (2015 or newer)
- **RAM:** 4GB (8GB recommended)
- **Storage:** 500MB free space (2GB recommended)
- **Display:** 1024x768 (1920x1080 recommended)

### Operating Systems
✅ **Supported:**
- Windows 10 (version 1909 or later)
- Windows 11 (all versions)
- macOS 10.15 Catalina or later
- Ubuntu 20.04 LTS or later
- Fedora 32 or later

❌ **Not Supported:**
- Windows 7/8/8.1
- macOS 10.14 or earlier
- 32-bit operating systems
- Windows Server (works but not tested)

### Network Requirements
- **Internet:** Not required for operation
- **Ports:** No inbound ports needed
- **Firewall:** No special configuration required
- **Proxy:** Works through corporate proxies

---

## Installation Methods

### Method 1: Single Executable (Recommended)

#### Windows Installation
1. **Download** `RadioForms-Setup.exe` from deployment folder
2. **Right-click** → Run as Administrator (if required)
3. **Follow** installation wizard
4. **Launch** from Start Menu or Desktop shortcut

#### macOS Installation
1. **Download** `RadioForms.dmg` file
2. **Double-click** to mount
3. **Drag** RadioForms to Applications folder
4. **First launch:** Right-click → Open (to bypass Gatekeeper)

#### Linux Installation
1. **Download** `RadioForms.AppImage` file
2. **Set executable:** `chmod +x RadioForms.AppImage`
3. **Run:** `./RadioForms.AppImage`
4. **Optional:** Install using package manager integration

### Method 2: Portable Installation

#### For USB Deployment or No-Install Environments
1. **Download** portable zip file for your OS
2. **Extract** to desired location (USB drive, network share)
3. **Run** RadioForms executable directly
4. **Data stored** in same folder as executable

#### Portable Deployment Benefits
✅ **No admin rights** required
✅ **Runs from USB** or network drive
✅ **Self-contained** - no system changes
✅ **Easy removal** - just delete folder

---

## Configuration

### First-Time Setup

#### Administrator Configuration
1. **Launch** RadioForms as admin
2. **Click** Settings → Admin Configuration
3. **Set:**
   - Default agency name
   - Default department
   - Standard operating procedures
   - Form templates
4. **Save** as system defaults

#### User Profile Setup
```json
{
  "defaultAgency": "Metro Fire Department",
  "defaultDepartment": "Operations",
  "defaultPosition": "Company Officer",
  "autoSaveInterval": 30,
  "formTemplates": ["Structure Fire", "EMS", "Hazmat"]
}
```

### Multi-User Environment

#### Shared Computer Setup
1. **Install** to Program Files (all users)
2. **Configure** individual user profiles
3. **Set** data storage to user documents
4. **Enable** automatic backup to network share

#### Department-Wide Deployment
```batch
# Windows batch deployment
@echo off
echo Installing RadioForms...
RadioForms-Setup.exe /S /D="C:\Program Files\RadioForms"
echo Configuring defaults...
copy department-config.json "C:\ProgramData\RadioForms\"
echo Installation complete.
```

---

## Network Deployment

### Group Policy Deployment (Windows)

#### MSI Package Creation
1. **Use** provided MSI or repackage EXE
2. **Test** on pilot machines first
3. **Deploy** via Group Policy Software Installation
4. **Configure** default settings via registry

#### Registry Settings
```reg
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\RadioForms]
"DefaultAgency"="Metro Fire Department"
"DefaultDepartment"="Operations"
"AutoSave"=dword:00000001
"BackupPath"="\\\\server\\share\\RadioForms\\Backup"
```

### Intune/MDM Deployment

#### Application Package
1. **Upload** .intunewin package
2. **Configure** installation command
3. **Set** detection rules
4. **Assign** to device groups

#### PowerShell Detection Script
```powershell
$AppPath = "C:\Program Files\RadioForms\RadioForms.exe"
if (Test-Path $AppPath) {
    $Version = (Get-ItemProperty $AppPath).VersionInfo.FileVersion
    if ($Version -ge "1.0.0") {
        Write-Output "Installed"
        exit 0
    }
}
exit 1
```

### macOS Enterprise Deployment

#### PKG Package Installation
1. **Create** PKG using packaging tool
2. **Sign** with developer certificate
3. **Deploy** via Jamf Pro or similar MDM
4. **Configure** launch agents for defaults

#### Configuration Profile
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>PayloadIdentifier</key>
    <string>com.radioforms.config</string>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>RadioFormsDefaults</key>
    <dict>
        <key>DefaultAgency</key>
        <string>Metro Fire Department</string>
        <key>AutoSave</key>
        <true/>
    </dict>
</dict>
</plist>
```

---

## USB Drive Deployment

### Emergency Response Vehicle Setup

#### USB Drive Preparation
1. **Format** USB drive (FAT32 for compatibility)
2. **Create** folder structure:
   ```
   RadioForms-Mobile/
   ├── RadioForms.exe (Windows)
   ├── RadioForms.app (macOS)
   ├── RadioForms.AppImage (Linux)
   ├── Templates/
   ├── Backup/
   └── Docs/
   ```
3. **Copy** portable versions for all platforms
4. **Test** on different computers

#### Auto-Run Configuration
```batch
# autorun.inf for Windows
[autorun]
label=RadioForms Emergency Response
icon=RadioForms.ico
open=start-radioforms.bat
action=Launch RadioForms
```

#### Cross-Platform Launcher
```bash
#!/bin/bash
# launch.sh - Works on macOS and Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    open RadioForms.app
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    ./RadioForms.AppImage
fi
```

### Vehicle Computer Integration

#### Rugged Computer Setup
1. **Install** to solid-state storage only
2. **Configure** automatic backup to USB
3. **Set** power management for vehicle use
4. **Test** with vehicle power fluctuations

#### Mobile Data Considerations
- **Offline operation** - No network required
- **Sync capabilities** - When network available
- **Battery backup** - Data preserved during power loss
- **Vibration resistance** - Solid-state storage recommended

---

## Security Configuration

### Data Protection

#### Local Data Encryption
- **Database:** SQLite with encryption extension
- **Backups:** AES-256 encrypted archives
- **Temp files:** Automatically cleared on exit
- **Memory:** Sensitive data cleared on close

#### Access Controls
```json
{
  "securitySettings": {
    "requireLogin": false,
    "autoLockMinutes": 30,
    "encryptBackups": true,
    "clearTempFiles": true,
    "auditTrail": true
  }
}
```

### Network Security

#### Firewall Configuration
- **Outbound:** No special requirements
- **Inbound:** No listening ports
- **Proxy:** Honors system proxy settings
- **VPN:** Works through VPN connections

#### Corporate Environment
1. **Whitelist** application executable
2. **Allow** data folders in user documents
3. **Permit** backup to network shares
4. **Test** with security software enabled

---

## Backup and Recovery

### Automated Backup Strategy

#### Daily Backup Configuration
```json
{
  "backupSettings": {
    "enabled": true,
    "interval": "daily",
    "retention": 30,
    "location": "Documents/RadioForms/Backup",
    "networkPath": "\\\\server\\share\\RadioForms\\UserBackups",
    "compression": true,
    "encryption": true
  }
}
```

#### Backup Verification
```powershell
# PowerShell backup verification script
$BackupPath = "$env:USERPROFILE\Documents\RadioForms\Backup"
$LatestBackup = Get-ChildItem $BackupPath | Sort LastWriteTime -Desc | Select -First 1
if ($LatestBackup.LastWriteTime -lt (Get-Date).AddDays(-2)) {
    Write-Warning "Backup is older than 2 days"
    # Send alert to IT
}
```

### Disaster Recovery

#### Complete System Recovery
1. **Install** RadioForms on new system
2. **Copy** backup files from network/USB
3. **Run** restore wizard in application
4. **Verify** all forms recovered correctly

#### Individual Form Recovery
1. **Open** RadioForms
2. **Click** File → Restore → From Backup
3. **Select** backup file or date range
4. **Choose** specific forms to restore
5. **Merge** with existing data or replace

---

## Troubleshooting

### Installation Issues

#### Windows Problems
❌ **"Installation failed"**
✅ **Solutions:**
1. Run as Administrator
2. Disable antivirus temporarily
3. Clear Windows Installer cache
4. Use MSI version instead of EXE

❌ **"App won't start after install"**
✅ **Solutions:**
1. Install Visual C++ Redistributable
2. Update Windows to latest version
3. Check Event Viewer for errors
4. Run in compatibility mode

#### macOS Problems
❌ **"App can't be opened because developer cannot be verified"**
✅ **Solutions:**
1. Right-click → Open (first time only)
2. System Preferences → Security → Allow
3. Use `sudo spctl --master-disable` (not recommended)
4. Contact vendor for signed version

❌ **"App damaged and can't be opened"**
✅ **Solutions:**
1. Re-download application
2. Clear quarantine: `xattr -cr RadioForms.app`
3. Verify download integrity
4. Check Gatekeeper status

#### Linux Problems
❌ **"Permission denied"**
✅ **Solutions:**
1. `chmod +x RadioForms.AppImage`
2. Check filesystem mount options
3. Disable SELinux temporarily for testing
4. Use package manager version

❌ **"Missing libraries"**
✅ **Solutions:**
1. Install FUSE for AppImage support
2. Update system packages
3. Install required dependencies
4. Use distribution-specific package

### Performance Issues

#### Slow Startup
❌ **App takes >10 seconds to start**
✅ **Solutions:**
1. Move to SSD storage
2. Exclude from antivirus scanning
3. Close unnecessary background apps
4. Check available RAM (need 4GB)

#### Database Performance
❌ **Forms take long time to save/load**
✅ **Solutions:**
1. Run database optimization in settings
2. Clear old backup files
3. Move database to faster storage
4. Limit concurrent form editing

### Network Issues

#### Backup to Network Share
❌ **"Cannot access network backup location"**
✅ **Solutions:**
1. Verify network connectivity
2. Check share permissions
3. Use UNC path instead of mapped drive
4. Test with different credentials

#### Proxy Environment
❌ **Updates or sync fail behind proxy**
✅ **Solutions:**
1. Configure proxy in system settings
2. Set proxy environment variables
3. Use direct connection for testing
4. Contact network administrator

---

## Monitoring and Maintenance

### Health Monitoring

#### Application Monitoring Script
```powershell
# Monitor RadioForms health
$ProcessName = "RadioForms"
$DataPath = "$env:USERPROFILE\Documents\RadioForms"

# Check if app is running
if (!(Get-Process $ProcessName -ErrorAction SilentlyContinue)) {
    Write-Warning "RadioForms not running"
}

# Check database integrity
$DbPath = "$DataPath\radioforms.db"
if (Test-Path $DbPath) {
    $DbSize = (Get-Item $DbPath).Length
    if ($DbSize -eq 0) {
        Write-Error "Database file is empty"
    }
}

# Check backup recency
$BackupPath = "$DataPath\Backup"
$LatestBackup = Get-ChildItem $BackupPath | Sort LastWriteTime -Desc | Select -First 1
if ($LatestBackup.LastWriteTime -lt (Get-Date).AddDays(-1)) {
    Write-Warning "Backup is older than 1 day"
}
```

### Update Management

#### Automatic Updates
```json
{
  "updateSettings": {
    "checkForUpdates": true,
    "downloadAutomatically": false,
    "installAutomatically": false,
    "updateChannel": "stable",
    "checkInterval": "weekly"
  }
}
```

#### Manual Update Process
1. **Download** new version from deployment folder
2. **Test** on pilot machines first
3. **Export** user data before upgrade
4. **Install** new version over existing
5. **Verify** data migration completed
6. **Deploy** to production machines

### Maintenance Tasks

#### Weekly Maintenance
- [ ] Check backup completion logs
- [ ] Verify application startup on sample machines
- [ ] Review error logs for patterns
- [ ] Test network backup accessibility
- [ ] Update antivirus exclusions if needed

#### Monthly Maintenance
- [ ] Update application to latest version
- [ ] Clean old backup files (>30 days)
- [ ] Run database optimization
- [ ] Review storage usage trends
- [ ] Test disaster recovery procedures

#### Quarterly Maintenance
- [ ] Full security audit
- [ ] Performance benchmarking
- [ ] User training refresher
- [ ] Documentation updates
- [ ] Hardware compatibility testing

---

## User Training

### IT Staff Training

#### Technical Training Topics
1. **Installation procedures** - All deployment methods
2. **Configuration management** - Default settings, templates
3. **Backup and recovery** - Full disaster recovery procedures
4. **Troubleshooting** - Common issues and solutions
5. **Security** - Data protection and access controls

#### End User Training

#### Basic Training Curriculum (2 hours)
1. **Application basics** - Starting, navigation, interface
2. **Form creation** - ICS-201, ICS-202, ICS-213 essentials
3. **Data management** - Saving, searching, organizing
4. **Export and sharing** - PDF creation, printing
5. **Emergency procedures** - What to do when technology fails

#### Advanced Training Curriculum (4 hours)
1. **All form types** - Complete ICS form suite
2. **Advanced features** - Templates, automation, shortcuts
3. **Incident workflows** - Start to finish documentation
4. **Integration** - Other emergency management systems
5. **Troubleshooting** - Self-service problem resolution

---

## Documentation and Support

### Documentation Package
- **USER-MANUAL.md** - Complete user guide
- **QUICK-START.md** - Emergency reference card
- **TROUBLESHOOTING.md** - Problem resolution guide
- **DEPLOYMENT-GUIDE.md** - This document

### Support Resources
- **Internal wiki** - Department-specific procedures
- **Video tutorials** - Screen recordings of common tasks
- **FAQ database** - Common questions and answers
- **Contact information** - IT help desk and emergency contacts

### Change Management
1. **Version control** - Track all configuration changes
2. **Testing procedures** - Validate changes before deployment
3. **Rollback plans** - Quick recovery from failed updates
4. **Communication** - Notify users of changes and training

---

*This deployment guide ensures RadioForms can be reliably deployed and maintained in emergency response environments where reliability is critical.*