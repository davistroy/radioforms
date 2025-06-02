# Code Signing Setup Guide
*Simple Code Signing for RadioForms*

## Overview

RadioForms supports basic code signing for Windows and macOS builds. Code signing is **optional** for development but **recommended** for distribution.

## Quick Setup

### Windows Code Signing

#### Prerequisites
- Code signing certificate (.p12 or .pfx file)
- Certificate password

#### Setup Steps
1. **Get certificate** - Purchase from trusted CA or use self-signed for testing
2. **Set environment variables:**
   ```bash
   export TAURI_SIGNING_PRIVATE_KEY="path/to/certificate.p12"
   export TAURI_SIGNING_PRIVATE_KEY_PASSWORD="your-password"
   ```
3. **Build signed executable:**
   ```bash
   npm run tauri build
   ```

#### Environment Variables
```bash
# Windows Code Signing
TAURI_SIGNING_PRIVATE_KEY=path/to/certificate.p12
TAURI_SIGNING_PRIVATE_KEY_PASSWORD=certificate-password
```

### macOS Code Signing

#### Prerequisites
- Apple Developer Account
- Code signing certificate in Keychain
- Application password for notarization

#### Setup Steps
1. **Install certificate** - Add to Keychain from Apple Developer portal
2. **Set environment variables:**
   ```bash
   export APPLE_CERTIFICATE_IDENTITY="Developer ID Application: Your Name"
   export APPLE_ID="your-apple-id@example.com"
   export APPLE_PASSWORD="app-specific-password"
   export APPLE_TEAM_ID="your-team-id"
   ```
3. **Build signed DMG:**
   ```bash
   npm run tauri build
   ```

#### Environment Variables
```bash
# macOS Code Signing & Notarization
APPLE_CERTIFICATE_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
APPLE_ID="your-apple-id@example.com"
APPLE_PASSWORD="app-specific-password"
APPLE_TEAM_ID="your-10-character-team-id"
```

## Testing Without Code Signing

### Development Builds
```bash
# Build without signing (faster for testing)
npm run tauri build --no-bundle
```

### Platform-Specific Testing
```bash
# Windows - test NSIS installer without signing
npm run tauri build -- --target nsis

# macOS - test DMG without notarization
npm run tauri build -- --target dmg

# Linux - AppImage doesn't require signing
npm run tauri build -- --target appimage
```

## CI/CD Integration

### GitHub Actions Environment Variables
Set these in repository secrets:

```yaml
# Windows
TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY }}
TAURI_SIGNING_PRIVATE_KEY_PASSWORD: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY_PASSWORD }}

# macOS
APPLE_CERTIFICATE_IDENTITY: ${{ secrets.APPLE_CERTIFICATE_IDENTITY }}
APPLE_ID: ${{ secrets.APPLE_ID }}
APPLE_PASSWORD: ${{ secrets.APPLE_PASSWORD }}
APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
```

### Build Script Integration
```bash
#!/bin/bash
# Simple build script with signing

echo "Building RadioForms with code signing..."

# Check for signing credentials
if [[ -n "$TAURI_SIGNING_PRIVATE_KEY" || -n "$APPLE_CERTIFICATE_IDENTITY" ]]; then
    echo "Code signing credentials found - building signed release"
    npm run tauri build
else
    echo "No signing credentials - building unsigned release"
    npm run tauri build --no-bundle
fi
```

## Certificate Management

### Windows Certificates
- **Self-signed (testing):** Use `makecert` or OpenSSL
- **Production:** Purchase from Digicert, Sectigo, or similar
- **Storage:** Keep .p12/.pfx files secure, use environment variables for passwords

### macOS Certificates
- **Development:** Use Xcode or Developer Portal
- **Distribution:** "Developer ID Application" certificate required
- **Notarization:** Requires Apple ID and app-specific password

## Common Issues

### Windows
❌ **"Certificate not found"**
✅ **Solution:** Check certificate path and password

❌ **"Timestamp server unavailable"**  
✅ **Solution:** Add timestampUrl to tauri.conf.json

### macOS
❌ **"Code signing failed"**
✅ **Solution:** Verify certificate identity name matches exactly

❌ **"Notarization failed"**
✅ **Solution:** Check Apple ID credentials and app-specific password

### Linux
✅ **No code signing required** - AppImage format doesn't require signing

## Security Notes

- **Never commit certificates** to version control
- **Use environment variables** for sensitive data
- **Rotate certificates** before expiration
- **Test signed builds** on clean systems

## Emergency Workaround

If code signing fails during build:

1. **Build unsigned version:**
   ```bash
   npm run tauri build --no-bundle
   ```

2. **Manual signing (if needed):**
   - Windows: Use `signtool` manually
   - macOS: Use `codesign` and `xcrun notarytool`

3. **Continue deployment** with unsigned builds for emergency releases

---

*Remember: Code signing improves user trust but shouldn't block emergency deployments. Unsigned builds work fine for internal use.*