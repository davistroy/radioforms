#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Installation script for the fixed form model registry.

This script replaces the original form_model_registry.py with the fixed version
and runs tests to verify the fix works properly. This addresses the integration
issues between the form models and DAO layer described in task 0.1 of the
taskplan_updated.md.
"""

import sys
import os
import logging
import shutil
import subprocess
from pathlib import Path

# Add parent directory to path to import RadioForms modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def backup_original_file():
    """Back up the original form_model_registry.py file."""
    source_path = "radioforms/models/form_model_registry.py"
    backup_path = "radioforms/models/form_model_registry.py.bak"
    
    if os.path.exists(source_path):
        logger.info(f"Backing up original file to {backup_path}")
        shutil.copy2(source_path, backup_path)
        return True
    else:
        logger.error(f"Original file {source_path} not found")
        return False


def install_fixed_version():
    """Replace the original file with the fixed version."""
    source_path = "radioforms/models/form_model_registry_fixed.py"
    target_path = "radioforms/models/form_model_registry.py"
    
    if not os.path.exists(source_path):
        logger.error(f"Fixed version {source_path} not found")
        return False
        
    logger.info(f"Installing fixed version to {target_path}")
    shutil.copy2(source_path, target_path)
    return True


def run_tests():
    """Run the test script to validate the fix."""
    logger.info("Running tests to validate the fix")
    
    test_script = "scripts/test_fixed_form_registry.py"
    
    if not os.path.exists(test_script):
        logger.error(f"Test script {test_script} not found")
        return False
        
    try:
        result = subprocess.run([sys.executable, test_script], 
                                capture_output=True, text=True, check=False)
        
        logger.info("Test output:")
        print(result.stdout)
        
        if result.returncode != 0:
            logger.error("Tests failed:")
            print(result.stderr)
            return False
            
        logger.info("Tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return False


def main():
    """Run the installation script."""
    logger.info("Starting installation of fixed form model registry")
    
    # Backup original file
    if not backup_original_file():
        logger.error("Backup failed, aborting installation")
        return 1
        
    # Install fixed version
    if not install_fixed_version():
        logger.error("Installation failed")
        return 1
        
    # Run tests
    if not run_tests():
        logger.warning("Tests failed, but installation completed")
        logger.info("You can restore the original file using:")
        logger.info("  cp radioforms/models/form_model_registry.py.bak radioforms/models/form_model_registry.py")
        return 1
        
    logger.info("Installation completed successfully")
    logger.info("This fix addresses task 0.1 from the taskplan_updated.md:")
    logger.info("  'Fix form model registry and form DAO integration'")
    logger.info("The integration issues between form models and the database layer have been resolved.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
