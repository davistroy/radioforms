# RadioForms - ICS Forms Management Application

**Version**: 0.1.0 (Phase 1 MVP)  
**Status**: Development - Phase 1  
**Python**: 3.10+ required  
**GUI Framework**: PySide6 (Qt for Python)

## Overview

RadioForms is a standalone, offline-first desktop application for creating, managing, exporting, and archiving FEMA Incident Command System (ICS) forms. Built specifically for administrative staff and radio operators in emergency management.

### Phase 1 MVP Features
- **ICS-213 General Message** form creation and editing
- **Basic save/load** functionality with SQLite database
- **JSON export** for data portability
- **Simple, intuitive** user interface

## Quick Start

### Prerequisites
- Python 3.10 or higher
- Operating System: Windows, macOS, or Linux
- Minimum screen resolution: 1280x720

### Installation

1. **Clone or download** this repository
2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # Linux/Mac:
   source venv/bin/activate
   # Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e .[dev]
   ```

4. **Run the application**:
   ```bash
   python -m src.main
   ```

### Development Setup

1. **Install development dependencies**:
   ```bash
   pip install -e .[dev]
   ```

2. **Set up pre-commit hooks**:
   ```bash
   pre-commit install
   ```

3. **Run tests**:
   ```bash
   pytest
   ```

4. **Run code quality checks**:
   ```bash
   black src tests
   ruff check src tests
   mypy src
   ```

## Project Structure

```
radioforms/
├── src/                    # Source code
│   ├── app/               # Application core
│   ├── ui/                # User interface components
│   ├── models/            # Data models
│   ├── database/          # Database layer
│   └── main.py           # Application entry point
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── ui/               # UI tests
├── docs/                  # Documentation
├── pyproject.toml        # Project configuration
├── README.md             # This file
└── CLAUDE.md             # AI assistant guide
```

## Usage (Phase 1)

### Creating a New ICS-213 Form
1. Start the application
2. The main window displays an empty ICS-213 form
3. Fill in the required fields:
   - **To**: Message recipient
   - **From**: Message sender  
   - **Subject**: Message subject
   - **Message**: Message content
   - **Date**: Message date
   - **Time**: Message time
4. Use **File → Save** to save the form

### Opening an Existing Form
1. Use **File → Open** to browse for saved forms
2. Select a `.json` file to load the form data
3. Edit as needed and save changes

### Exporting Forms
1. Use **File → Export** to save form as JSON
2. Choose location and filename
3. JSON files can be shared or archived

## Technical Details

### Database
- **SQLite** database for local storage
- **WAL mode** for improved reliability
- **Automatic initialization** on first run
- **Location**: Same directory as application

### Data Format
- **JSON** for import/export
- **ISO 8601** date/time formatting
- **UTF-8** text encoding
- **Schema validation** for data integrity

## Development Guidelines

This project follows strict development principles:
- **Simple first**: Start with basic functionality
- **Incremental development**: One feature at a time
- **Test-driven**: >95% code coverage required
- **User-validated**: Features driven by real user needs

See `CLAUDE.md` for detailed development guidelines.

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py

# Run UI tests
pytest tests/ui/
```

### Test Requirements
- **Unit tests**: >95% coverage
- **Integration tests**: Complete workflows
- **UI tests**: User interactions
- **Performance tests**: Speed benchmarks

## Troubleshooting

### Common Issues

**Application won't start**
- Check Python version: `python --version` (must be 3.10+)
- Check dependencies: `pip list`
- Check error messages in console

**Database errors**
- Database file may be corrupted
- Delete database file to reset (data will be lost)
- Check file permissions in application directory

**Performance issues**
- Check available disk space
- Close other applications to free memory
- Restart application if sluggish

### Getting Help

1. **Check this README** for common solutions
2. **Review error messages** carefully
3. **Check logs** in the application directory
4. **Report issues** with detailed error information

## Future Phases

This is Phase 1 of a planned 6-phase development:
- **Phase 2**: Add ICS-214 form and multi-form management
- **Phase 3**: User-requested enhancements (dark theme, search, etc.)
- **Phase 4**: Additional ICS forms based on user demand
- **Phase 5**: Advanced features (ICS-DES encoding, plugins)
- **Phase 6**: Enterprise-grade deployment and security

## Contributing

This project follows the principles in `CLAUDE.md`:
1. **Simple solutions** over complex ones
2. **User validation** before feature addition
3. **Comprehensive testing** for all changes
4. **Clear documentation** for all code

## License

MIT License - See LICENSE file for details.

## Contact

For support or questions about RadioForms, please refer to the project documentation or submit an issue through the appropriate channels.

---

**RadioForms** - Simplifying incident documentation for emergency responders.