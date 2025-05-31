# RadioForms Installation Guide

## Quick Start

RadioForms is distributed as a single executable file that requires no installation or dependencies. Simply download and run!

### Windows Installation

1. **Download**: Get `RadioForms-Windows.exe` from the releases page
2. **Run**: Double-click the executable to start RadioForms
3. **First Launch**: The application will create a database and configuration files automatically
4. **Optional**: Create a desktop shortcut for easy access

**System Requirements:**
- Windows 10 or newer (64-bit)
- No additional software required

### macOS Installation

1. **Download**: Get `RadioForms.app` or `RadioForms-macOS` from the releases page
2. **Install**: 
   - For `.app` bundle: Drag to Applications folder
   - For executable: Place in a convenient location
3. **Security**: You may need to right-click and select "Open" on first launch (Gatekeeper)
4. **Run**: Launch from Applications or by double-clicking

**System Requirements:**
- macOS 10.14 (Mojave) or newer
- No additional software required

### Linux Installation

#### Option 1: AppImage (Recommended)
1. **Download**: Get `RadioForms-Linux.AppImage`
2. **Make Executable**: `chmod +x RadioForms-Linux.AppImage`
3. **Run**: `./RadioForms-Linux.AppImage`
4. **Integration**: AppImage can integrate with your desktop automatically

#### Option 2: Standalone Executable
1. **Download**: Get `RadioForms-Linux`
2. **Make Executable**: `chmod +x RadioForms-Linux`
3. **Run**: `./RadioForms-Linux`

**System Requirements:**
- Linux with X11 (most desktop distributions)
- glibc 2.17 or newer
- Basic GUI libraries (usually pre-installed)

**Tested Distributions:**
- Ubuntu 18.04+
- Debian 10+
- CentOS 7+
- Fedora 30+
- openSUSE Leap 15+

## Detailed Installation Instructions

### Database Location

RadioForms stores its database in the following locations:

- **Windows**: `%APPDATA%\RadioForms\forms.db`
- **macOS**: `~/Library/Application Support/RadioForms/forms.db`
- **Linux**: `~/.local/share/RadioForms/forms.db`

The database is created automatically on first launch.

### Configuration Files

Application settings are stored in:

- **Windows**: `%APPDATA%\RadioForms\settings.ini`
- **macOS**: `~/Library/Preferences/com.radioforms.radioforms.plist`
- **Linux**: `~/.config/RadioForms/settings.ini`

### Backup and Recovery

#### Creating Backups
1. Launch RadioForms
2. Go to File → Export → Backup Database
3. Choose a location to save the backup file
4. The backup includes all forms and settings

#### Restoring from Backup
1. Close RadioForms if running
2. Replace the database file with your backup
3. Restart RadioForms

#### Manual Backup
Simply copy the database file from the location above to a safe place.

### Uninstallation

Since RadioForms is a portable application:

1. **Delete the executable file**
2. **Optionally delete user data**:
   - Database file (see locations above)
   - Configuration files (see locations above)

### Troubleshooting

#### Windows

**Problem**: "Windows protected your PC" message
- **Solution**: Click "More info" then "Run anyway"
- **Cause**: Executable is not digitally signed

**Problem**: Application won't start
- **Solution**: Right-click executable and "Run as administrator"
- **Alternative**: Check Windows Defender exclusions

#### macOS

**Problem**: "Cannot be opened because it is from an unidentified developer"
- **Solution**: Right-click → Open → Open (confirm twice)
- **Alternative**: System Preferences → Security → Allow anyway

**Problem**: Application appears damaged
- **Solution**: Try: `xattr -cr RadioForms.app` in Terminal
- **Cause**: Quarantine attribute from download

#### Linux

**Problem**: "No such file or directory" error
- **Solution**: Install missing GUI libraries:
  ```bash
  # Ubuntu/Debian
  sudo apt install libgl1-mesa-glx libglib2.0-0 libxcb-xinerama0
  
  # CentOS/RHEL
  sudo yum install mesa-libGL glib2 libxcb
  
  # Fedora
  sudo dnf install mesa-libGL glib2 libxcb
  ```

**Problem**: AppImage won't run
- **Solution**: Install FUSE: `sudo apt install fuse` (Ubuntu/Debian)
- **Alternative**: Extract AppImage: `./RadioForms-Linux.AppImage --appimage-extract`

### Network and Security

#### Network Requirements
- **None**: RadioForms works completely offline
- **No internet connection required**
- **No data transmission to external servers**

#### Security Features
- **Local data only**: All information stays on your computer
- **Encrypted storage**: Option to encrypt sensitive data
- **Audit logging**: Track all data modifications
- **Secure deletion**: Permanently remove sensitive forms

### Performance Optimization

#### Hardware Recommendations
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 100MB free space minimum
- **Display**: 1024x768 minimum resolution

#### Performance Tips
1. **Close other applications** when working with large incidents
2. **Regular backups** prevent database corruption
3. **Archive old forms** to maintain performance
4. **Use search filters** for faster form location

### Enterprise Deployment

#### Silent Installation
RadioForms can be deployed silently in enterprise environments:

1. **Copy executable** to desired location
2. **Pre-configure settings** by copying configuration files
3. **Set database location** via environment variables
4. **Create desktop shortcuts** programmatically

#### Group Policy (Windows)
- Deploy via Group Policy Software Installation
- Use environment variables for standardized paths
- Configure security policies as needed

#### System Administration
- **Centralized database**: Use shared network storage (with care)
- **User permissions**: Standard user rights sufficient
- **Backup strategy**: Include in regular backup procedures
- **Update management**: Replace executable for updates

### Development and Advanced Usage

#### Command Line Options
```bash
# Display version information
./RadioForms --version

# Specify custom database location
./RadioForms --database /path/to/database.db

# Enable debug logging
./RadioForms --debug

# Run in headless mode (batch operations)
./RadioForms --headless --batch-import forms.json
```

#### Environment Variables
- `RADIOFORMS_DB_PATH`: Custom database location
- `RADIOFORMS_CONFIG_PATH`: Custom configuration location
- `RADIOFORMS_DEBUG`: Enable debug logging
- `RADIOFORMS_HEADLESS`: Force headless mode

### Support and Updates

#### Getting Help
1. **User Manual**: See `docs/USER_MANUAL.md`
2. **FAQ**: See `docs/faq.md`
3. **Troubleshooting**: See `docs/troubleshooting.md`
4. **Bug Reports**: Submit to project repository

#### Updates
- **Check for updates** in Help menu
- **Backup data** before updating
- **Download new version** and replace executable
- **Database migration** happens automatically

#### Version Compatibility
- **Forward compatible**: Newer versions read older databases
- **Backup recommended**: Before major version upgrades
- **Settings preserved**: Configuration carries forward

---

*For technical support or questions, please refer to the documentation or submit an issue to the project repository.*