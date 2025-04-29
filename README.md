# RadioForms - ICS Forms Management Application

A desktop application for managing, creating, and sharing FEMA Incident Command System (ICS) forms, designed for efficient emergency management communications.

## Overview

RadioForms allows emergency management personnel to:

- Create and edit ICS forms (ICS-213, ICS-214, and more)
- Save and organize forms by incident
- Export forms to PDF format matching official FEMA layouts
- Export data in ICS-DES format for radio transmission
- Attach files to forms
- Track form versions and changes
- Work offline without internet connectivity

## Requirements

- Python 3.10 or higher
- SQLite (included with Python)
- 50MB disk space (plus space for your forms and attachments)
- Windows, macOS, or Linux operating system

## Installation

### Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/radioforms.git
   cd radioforms
   ```

2. Create and activate a virtual environment:
   ```
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the test script to verify setup:
   ```
   python -m radioforms.tests.test_setup
   ```

5. Run the Hello World application:
   ```
   python -m radioforms.tests.hello_world
   ```

6. Launch the application:
   ```
   python -m radioforms.main
   ```

## Project Structure

```
radioforms/
├── config/         # Application configuration
├── controllers/    # Application controllers
├── database/       # Database management and data access
├── forms/          # Form-specific implementations
├── models/         # Data models
├── resources/      # Static resources (icons, etc.)
├── tests/          # Test suite
├── utils/          # Utility functions
├── views/          # UI components
└── main.py         # Application entry point
```

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Add docstrings for all classes and methods
- Use descriptive variable names
- Write unit tests for all functionality

### Workflow

1. Create a new branch for each feature or bugfix
2. Write tests first where applicable
3. Implement functionality
4. Run tests to verify implementation
5. Submit a pull request

## Architecture

RadioForms uses a Model-View-Controller (MVC) architecture:

- **Models** (in `models/`): Data structures and business logic
- **Views** (in `views/`): User interface components built with PySide6
- **Controllers** (in `controllers/`): Coordinate between models and views

The application leverages SQLite with WAL mode for reliable database operations, ensuring data integrity even during power failures.

## Testing

Run the test suite:

```
python -m unittest discover -s radioforms/tests
```

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request
