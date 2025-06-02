# CI/CD Pipeline Documentation
*Simple GitHub Actions for RadioForms*

## Overview

RadioForms uses GitHub Actions for automated testing and building. The CI/CD system is designed to be simple, reliable, and to follow the MANDATORY.md principle: "If it fails, continue without it."

## Workflow Files

### 1. Test Workflow (.github/workflows/test.yml)
**Triggers:** Push to main, Pull requests
**Purpose:** Fast feedback on code quality
**Runtime:** ~3-5 minutes

**What it does:**
- Runs on every push and pull request
- Checks TypeScript compilation
- Runs ESLint linting
- Runs frontend tests
- Verifies frontend builds
- Checks Rust compilation
- Runs Rust tests

### 2. Build Workflow (.github/workflows/build.yml)
**Triggers:** Push to main, Pull requests, Manual releases
**Purpose:** Build cross-platform executables
**Runtime:** ~15-20 minutes per platform

**What it does:**
- Builds for Windows, macOS, and Linux
- Uses code signing if credentials are available
- Creates draft releases for manual review
- Uploads build artifacts

### 3. Release Workflow (.github/workflows/release.yml)
**Triggers:** Git tags starting with 'v' (e.g., v1.0.0)
**Purpose:** Automated releases
**Runtime:** ~15-20 minutes per platform

**What it does:**
- Builds production releases for all platforms
- Signs executables if certificates are configured
- Creates GitHub release automatically
- Uploads release assets

## Platform Support

### Windows
- **Target:** `windows-latest` (Windows Server 2022)
- **Output:** `.exe` installer (NSIS)
- **Code Signing:** Optional via TAURI_SIGNING_PRIVATE_KEY

### macOS
- **Target:** `macos-latest` (macOS 12+)
- **Output:** `.dmg` disk image (Universal Binary)
- **Code Signing:** Optional via Apple Developer certificates

### Linux
- **Target:** `ubuntu-22.04`
- **Output:** `.AppImage` portable application
- **Code Signing:** Not required

## Required Secrets

### Code Signing (Optional)
If you want signed releases, add these to GitHub repository secrets:

#### Windows Code Signing
```
TAURI_SIGNING_PRIVATE_KEY: <base64-encoded-certificate>
TAURI_SIGNING_PRIVATE_KEY_PASSWORD: <certificate-password>
```

#### macOS Code Signing
```
APPLE_CERTIFICATE_IDENTITY: Developer ID Application: Your Name (TEAM_ID)
APPLE_ID: your-apple-id@example.com
APPLE_PASSWORD: <app-specific-password>
APPLE_TEAM_ID: <10-character-team-id>
```

## How to Use

### Development Workflow
1. **Create feature branch**
2. **Make changes**
3. **Push to GitHub** - Test workflow runs automatically
4. **Create pull request** - Build workflow runs for verification
5. **Merge to main** - All workflows run

### Release Workflow
1. **Tag release:** `git tag v1.0.0`
2. **Push tag:** `git push origin v1.0.0`
3. **Release workflow runs** - Creates GitHub release automatically
4. **Download assets** - Windows/macOS/Linux builds available

### Manual Release
1. **Go to GitHub Actions**
2. **Select "Build RadioForms" workflow**
3. **Click "Run workflow"**
4. **Select branch and options**
5. **Check draft releases** for generated builds

## Build Artifacts

### Automatic Uploads
- **Draft releases** from build workflow
- **Final releases** from release workflow
- **Build logs** available in Actions tab

### File Naming
- `RadioForms_1.0.0_x64_en-US.msi` (Windows)
- `RadioForms_1.0.0_universal.dmg` (macOS)
- `radioforms_1.0.0_amd64.AppImage` (Linux)

## Troubleshooting

### Common Issues

#### ❌ Build fails with "npm install" error
✅ **Solution:** Check package.json and package-lock.json are committed

#### ❌ Rust compilation fails
✅ **Solution:** Check Cargo.toml and ensure all dependencies are compatible

#### ❌ Code signing fails
✅ **Solution:** Builds continue without signing - check certificate configuration

#### ❌ Frontend tests fail
✅ **Solution:** Run `npm test` locally to debug

### Debugging Steps
1. **Check Actions tab** in GitHub repository
2. **Click on failed workflow** to see details
3. **Expand failed step** to see error messages
4. **Fix locally first** then push again

### Emergency Bypass
If CI/CD is completely broken:
1. **Build locally** using `npm run tauri build`
2. **Create manual release** on GitHub
3. **Upload artifacts** directly to release

## Performance

### Optimization Features
- **Rust caching** with swatinem/rust-cache
- **npm caching** with setup-node cache
- **Parallel builds** across platforms
- **Fail-fast disabled** - one platform failure doesn't stop others

### Typical Times
- **Test workflow:** 3-5 minutes
- **Build workflow:** 15-20 minutes per platform
- **Release workflow:** 15-20 minutes per platform

## Monitoring

### Success Indicators
- ✅ Green checkmarks on commits
- ✅ Draft releases created automatically
- ✅ All platforms build successfully

### Failure Indicators
- ❌ Red X marks on commits
- ❌ Missing build artifacts
- ❌ Email notifications (if enabled)

## Configuration

### Workflow Triggers
- **test.yml:** Every push and PR
- **build.yml:** Main branch and manual
- **release.yml:** Only git tags

### Customization
Edit workflow files to:
- Change Node.js version
- Add new test steps
- Modify build targets
- Update release notes

## Security

### Repository Secrets
- **Never commit certificates** to repository
- **Use GitHub secrets** for sensitive data
- **Rotate secrets** regularly
- **Review access permissions**

### Build Security
- **Signed releases** when certificates available
- **Unsigned builds** still functional
- **No external dependencies** downloaded during build
- **Reproducible builds** from same source

---

*The CI/CD system is designed to be reliable and simple. If something breaks, you can always build locally and create releases manually.*