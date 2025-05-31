# RadioForms Deployment Guide

## Overview

This document provides complete instructions for building, testing, and deploying RadioForms executables for Windows, macOS, and Linux platforms. RadioForms is packaged as single-file executables for maximum portability and ease of distribution.

## Quick Start

### For End Users (Installing RadioForms)

1. **Download**: Get the appropriate executable for your platform from the releases page
2. **Run**: Double-click the executable (no installation required)
3. **First Launch**: RadioForms will create its database and configuration files automatically

### For Developers (Building from Source)

1. **Clone Repository**: `git clone https://github.com/davistroy/radioforms.git`
2. **Run Build Script**: Use platform-specific script in `scripts/` directory
3. **Test**: Verify executable works on clean systems
4. **Distribute**: Share single executable file

## System Requirements

### Development Environment

**All Platforms:**
- Python 3.10 or newer
- 4GB RAM minimum, 8GB recommended
- 2GB free disk space for build process
- Internet connection for downloading dependencies

**Windows Additional:**
- Windows 10 or newer
- Microsoft Visual C++ Redistributable (usually pre-installed)
- PowerShell or Command Prompt

**macOS Additional:**
- macOS 10.14 (Mojave) or newer
- Xcode Command Line Tools
- Optional: Apple Developer Certificate for code signing

**Linux Additional:**
- GCC compiler and development headers
- X11 development libraries
- Mesa OpenGL libraries
- Distribution-specific package manager

### Target System Requirements

**End User Systems:**
- Windows 10+, macOS 10.14+, or modern Linux distribution
- 4GB RAM minimum
- 100MB free disk space
- Display with 1024x768 resolution or higher

## Building Executables

### Automated Build Process

RadioForms includes automated build scripts for each platform that handle all dependencies and configuration:

#### Windows Build

```batch
# From project root directory
scripts\build_windows.bat
```

**What the script does:**
1. Creates/activates Python virtual environment
2. Installs all dependencies including PyInstaller
3. Runs test suite to verify code quality
4. Builds single-file executable using PyInstaller
5. Tests the resulting executable
6. Reports file size and status

**Output:** `RadioForms-Windows.exe` (approximately 80-120MB)

#### macOS Build

```bash
# From project root directory
chmod +x scripts/build_macos.sh
./scripts/build_macos.sh
```

**What the script does:**
1. Verifies Python 3.10+ installation
2. Creates/activates Python virtual environment
3. Installs dependencies and PyInstaller
4. Runs comprehensive test suite
5. Builds application bundle or executable
6. Provides code signing and notarization guidance

**Output:** `RadioForms.app` bundle or `RadioForms-macOS` executable

#### Linux Build

```bash
# From project root directory
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
```

**What the script does:**
1. Checks system dependencies (X11, OpenGL libraries)
2. Sets up Python virtual environment
3. Installs all required packages
4. Runs test validation
5. Builds Linux executable
6. Optionally creates AppImage for better portability

**Output:** `RadioForms-Linux` executable and/or `RadioForms-Linux.AppImage`

### Manual Build Process

If automated scripts don't work for your environment:

#### Prerequisites

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt
pip install pyinstaller
```

#### Build Command

```bash
# Build using PyInstaller spec file
pyinstaller radioforms.spec
```

#### Customization

Edit `radioforms.spec` file to customize:
- Include/exclude specific modules
- Add additional data files
- Modify executable name or icon
- Adjust compression settings
- Platform-specific configurations

### Build Configuration

#### PyInstaller Specification

The build process uses `radioforms.spec` which includes:

**Included Data:**
- All documentation (user manual, getting started, FAQ)
- Architecture decision records (ADRs)
- API documentation
- Forms analysis documentation
- Development rules and guidelines

**Optimizations:**
- UPX compression for smaller file size
- Excluded unnecessary modules (matplotlib, numpy, etc.)
- Hidden imports for PySide6 modules
- Platform-specific icon and metadata

**Security:**
- No debug symbols in release builds
- No console window for GUI application
- Code signing hooks (when certificates available)

#### Version Information

Windows builds include detailed version information:
- Product name and version
- Company information
- File description
- Copyright notice
- Compatible with Windows version checking

## Testing Procedures

### Pre-Build Testing

Before building executables, ensure all tests pass:

```bash
# Run comprehensive test suite
python test_comprehensive_suite.py

# Run specific test categories
python test_file_operations.py
python test_menu_system.py
```

### Post-Build Testing

#### Automated Testing

Build scripts include basic executable testing:
- Version information retrieval
- Application startup verification
- Clean shutdown testing

#### Manual Testing Checklist

**✅ Clean System Testing:**
- Test on system without Python installed
- Verify on system without development tools
- Test with minimal user permissions
- Check on different OS versions

**✅ Functionality Testing:**
- Create and validate ICS-213 forms
- Save and load forms from database
- Export and import JSON files
- Test all menu functions and keyboard shortcuts

**✅ Error Handling:**
- Test with invalid file permissions
- Verify behavior with full disk
- Check handling of corrupted data files
- Test application recovery after crashes

**✅ Performance Testing:**
- Measure startup time (should be <3 seconds)
- Test with large numbers of forms
- Verify memory usage stays reasonable
- Check for memory leaks during extended use

### Platform-Specific Testing

#### Windows Testing

```batch
# Test executable directly
RadioForms-Windows.exe --version

# Test installation in different locations
xcopy RadioForms-Windows.exe %USERPROFILE%\Desktop\
%USERPROFILE%\Desktop\RadioForms-Windows.exe

# Test with different user privileges
runas /user:testuser RadioForms-Windows.exe
```

#### macOS Testing

```bash
# Test executable
./RadioForms-macOS --version

# Test app bundle
open RadioForms.app

# Test on different macOS versions
# Verify Gatekeeper compatibility
# Check accessibility features
```

#### Linux Testing

```bash
# Test executable
./RadioForms-Linux --version

# Test AppImage
./RadioForms-Linux.AppImage --version

# Test on different distributions
# Verify library dependencies
ldd RadioForms-Linux
```

## Distribution

### Release Preparation

#### Version Management

1. **Update Version Numbers:**
   - `pyproject.toml`: Project version
   - `version_info.txt`: Windows version info
   - `radioforms.spec`: Application version
   - Documentation: Version references

2. **Tag Release:**
   ```bash
   git tag -a v1.0.0 -m "RadioForms v1.0.0 - Initial Release"
   git push origin v1.0.0
   ```

#### Release Notes

Create comprehensive release notes including:
- New features and capabilities
- Bug fixes and improvements
- Known issues and limitations
- Installation instructions
- Upgrade procedures (for future releases)

### File Naming Convention

Use consistent naming for all platforms:
- Windows: `RadioForms-v1.0.0-Windows.exe`
- macOS: `RadioForms-v1.0.0-macOS.app.zip`
- Linux: `RadioForms-v1.0.0-Linux.AppImage`

### Distribution Channels

#### GitHub Releases

Primary distribution method:
1. Create GitHub release with version tag
2. Upload platform-specific executables
3. Include release notes and installation instructions
4. Add checksums for file integrity verification

#### Alternative Distribution

**For Organizations:**
- Internal file servers
- Configuration management systems
- Software deployment tools
- USB drive distribution for air-gapped networks

**For Emergency Management:**
- State/regional EM websites
- Professional training materials
- Conference distribution
- Peer-to-peer sharing

### File Integrity

Generate and publish checksums:

```bash
# Windows
certutil -hashfile RadioForms-Windows.exe SHA256

# macOS/Linux
sha256sum RadioForms-Linux
sha256sum RadioForms-Linux.AppImage
```

Include checksums in release notes for verification.

## Installation Instructions

### End User Installation

#### Windows Installation

1. **Download:** Save `RadioForms-Windows.exe` to desired location
2. **Security Warning:** Click "More info" then "Run anyway" if Windows Defender blocks
3. **First Run:** Double-click executable to start
4. **Data Location:** Application creates `Documents/RadioForms/` folder automatically

**No traditional installation required** - executable is fully portable.

#### macOS Installation

1. **Download:** Save `RadioForms-macOS.app.zip` and extract
2. **Security:** Right-click app bundle and select "Open" to bypass Gatekeeper
3. **Optional:** Move to Applications folder for easier access
4. **First Run:** Application will request necessary permissions

#### Linux Installation

**AppImage (Recommended):**
1. Download `RadioForms-Linux.AppImage`
2. Make executable: `chmod +x RadioForms-Linux.AppImage`
3. Run: `./RadioForms-Linux.AppImage`

**Standard Executable:**
1. Download `RadioForms-Linux`
2. Make executable: `chmod +x RadioForms-Linux`
3. Run: `./RadioForms-Linux`

### System Administrator Deployment

#### Group Policy (Windows)

Deploy via Windows Group Policy:
1. Copy executable to network share
2. Create Group Policy Object
3. Add startup script or software installation policy
4. Deploy to target organizational units

#### Configuration Management

**Ansible Example:**
```yaml
- name: Deploy RadioForms
  copy:
    src: RadioForms-Linux
    dest: /usr/local/bin/radioforms
    mode: '0755'
  
- name: Create desktop shortcut
  template:
    src: radioforms.desktop.j2
    dest: /usr/share/applications/radioforms.desktop
```

**Puppet/Chef:** Similar patterns for configuration management systems

## Maintenance and Updates

### Update Procedures

#### For End Users

1. **Download** new version executable
2. **Close** current RadioForms application
3. **Replace** old executable with new one
4. **Start** new version (data is preserved automatically)

#### For Developers

1. **Test** new version thoroughly
2. **Update** version numbers in all files
3. **Build** new executables for all platforms
4. **Test** upgrade path from previous version
5. **Release** with clear upgrade instructions

### Rollback Procedures

If issues occur with new version:

1. **Stop** new version of application
2. **Replace** executable with previous version
3. **Restart** application
4. **Verify** data integrity
5. **Report** issues to development team

### Data Migration

RadioForms automatically handles data migration between versions:
- Database schema updates are applied automatically
- Configuration files are upgraded in place
- Backup copies are created before major changes

## Troubleshooting

### Common Build Issues

#### Python Version Mismatch

**Problem:** Build fails with Python version error
**Solution:** Install Python 3.10 or newer, update PATH

#### Missing Dependencies

**Problem:** PyInstaller can't find modules
**Solution:** Install all requirements-dev.txt dependencies

#### Permission Errors

**Problem:** Can't write to build directories
**Solution:** Run build script with appropriate permissions

#### Large File Size

**Problem:** Executable is unexpectedly large
**Solution:** Check for unnecessary included files in spec file

### Deployment Issues

#### Security Warnings

**Problem:** OS blocks execution of downloaded executable
**Solution:** Add code signing (developers) or security exceptions (users)

#### Missing Libraries

**Problem:** Application won't start on target system
**Solution:** Ensure all dependencies are included in build

#### Performance Issues

**Problem:** Slow startup or operation
**Solution:** Test on target hardware, optimize build settings

## Security Considerations

### Code Signing

#### Windows Code Signing

```bash
# With certificate file
signtool sign /f certificate.pfx /p password /t http://timestamp.comodoca.com RadioForms-Windows.exe

# With certificate store
signtool sign /n "Certificate Name" /t http://timestamp.comodoca.com RadioForms-Windows.exe
```

#### macOS Code Signing

```bash
# Sign executable
codesign --force --deep --sign "Developer ID Application: Your Name" RadioForms.app

# Verify signature
codesign --verify --verbose RadioForms.app

# Notarize for macOS 10.15+
xcrun notarytool submit RadioForms.zip --apple-id your-id --password app-password --team-id TEAM_ID
```

### Distribution Security

- **Checksums:** Always provide SHA256 checksums
- **HTTPS:** Distribute only via HTTPS connections
- **Verification:** Encourage users to verify checksums
- **Source:** Maintain clear chain of custody from source code to binary

## Platform-Specific Notes

### Windows

- **Antivirus:** Some antivirus software may quarantine unsigned executables
- **UAC:** Application doesn't require administrator privileges
- **Dependencies:** All required DLLs are included in executable
- **Registry:** No registry modifications required

### macOS

- **Gatekeeper:** Unsigned applications require user approval
- **Notarization:** Required for macOS 10.15+ distribution
- **Permissions:** Application may request file system access
- **Universal Binary:** Consider building for both Intel and Apple Silicon

### Linux

- **Dependencies:** System libraries must be compatible
- **Desktop Integration:** AppImage provides better desktop integration
- **Package Managers:** Consider creating .deb/.rpm packages
- **Distribution Testing:** Test on multiple Linux distributions

## Continuous Integration

### Automated Builds

Example GitHub Actions workflow:

```yaml
name: Build RadioForms
on:
  push:
    tags: ['v*']
  
jobs:
  build:
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Build executable
        run: |
          pip install -r requirements-dev.txt
          pyinstaller radioforms.spec
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: radioforms-${{ matrix.os }}
          path: dist/
```

### Quality Gates

Before releasing:
- ✅ All tests pass on all platforms
- ✅ Executables run on clean test systems
- ✅ Performance benchmarks meet requirements
- ✅ Security scan passes
- ✅ Documentation is current
- ✅ Version numbers are consistent

---

## Support and Resources

### Documentation
- [User Manual](user-manual.md) - Complete user guide
- [Getting Started](getting-started.md) - Quick start instructions
- [FAQ](faq.md) - Common questions and answers
- [Troubleshooting](troubleshooting.md) - Problem resolution

### Development Resources
- [API Documentation](api/) - Code reference
- [Architecture Decisions](adr/) - Technical decisions
- [CLAUDE.md](../CLAUDE.md) - Development guidelines

### Community
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Community support and ideas
- Release Notes: Version history and changes

---

**Note:** This deployment guide is for RadioForms v1.0.0. Check for updates and newer versions regularly.