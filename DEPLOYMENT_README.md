# RadioForms Deployment Package

## Quick Start

### Building Executables

**Windows:**
```batch
scripts\build_windows.bat
```

**macOS:**
```bash
./scripts/build_macos.sh
```

**Linux:**
```bash
./scripts/build_linux.sh
```

### Output Files

- **Windows**: `RadioForms-Windows.exe`
- **macOS**: `RadioForms.app` or `RadioForms-macOS`
- **Linux**: `RadioForms-Linux` and `RadioForms-Linux.AppImage`

## Requirements

- Python 3.10+ with pip
- 2GB free disk space
- Internet connection for dependencies

## Documentation

- **Complete Guide**: [docs/deployment.md](docs/deployment.md)
- **Release Process**: [docs/release-checklist.md](docs/release-checklist.md)
- **User Installation**: [docs/getting-started.md](docs/getting-started.md)

## Build Configuration

- **PyInstaller Spec**: `radioforms.spec`
- **Version Info**: `version_info.txt` (Windows)
- **Build Scripts**: `scripts/` directory

## Testing

Run comprehensive tests before building:
```bash
python test_comprehensive_suite.py
```

## Distribution

Built executables are single-file, portable applications requiring no installation. See [deployment documentation](docs/deployment.md) for complete distribution guidelines.

---

**RadioForms v1.0.0** - FEMA ICS Forms Management Application