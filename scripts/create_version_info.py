#!/usr/bin/env python3
"""
Create version info file for Windows executable
Generates version_info.txt for PyInstaller
"""

import os
import sys
from pathlib import Path

def create_version_info():
    """Create version_info.txt for Windows executable."""
    
    # Version information
    version = "1.0.0"
    company_name = "RadioForms Project"
    product_name = "RadioForms"
    description = "FEMA ICS Forms Management Application"
    copyright_text = "© 2024 RadioForms Project"
    
    # Convert version to tuple format (major, minor, patch, build)
    version_parts = version.split('.')
    while len(version_parts) < 4:
        version_parts.append('0')
    
    version_tuple = f"({', '.join(version_parts)})"
    
    version_info_content = f'''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers={version_tuple},
    prodvers={version_tuple},
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{company_name}'),
        StringStruct(u'FileDescription', u'{description}'),
        StringStruct(u'FileVersion', u'{version}'),
        StringStruct(u'InternalName', u'{product_name}'),
        StringStruct(u'LegalCopyright', u'{copyright_text}'),
        StringStruct(u'OriginalFilename', u'RadioForms-Windows.exe'),
        StringStruct(u'ProductName', u'{product_name}'),
        StringStruct(u'ProductVersion', u'{version}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    # Write version info file
    output_path = Path("version_info.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(version_info_content)
    
    print(f"Version info file created: {output_path.absolute()}")
    print(f"Version: {version}")
    print(f"Product: {product_name}")

if __name__ == "__main__":
    create_version_info()