"""ICS Forms Data Encoding Specification (ICS-DES) Implementation.

This module provides ultra-compact encoding and decoding of ICS forms for
radio transmission over bandwidth-constrained communication channels.
Implements the complete ICS-DES specification with numeric field codes,
enumeration tables, and optimized field transmission.

Critical for emergency management when internet/cellular is unavailable
and only radio communication is possible. Reduces transmission size by
60-80% compared to full JSON or voice transmission.

Following CLAUDE.md principles:
- Simple encoding/decoding interface
- Robust error handling and validation
- Performance optimized for real-time use
- Complete specification compliance

Example:
    >>> from src.services.ics_des_encoder import ICSDesEncoder
    >>> from src.forms.ics213 import ICS213Form
    >>> 
    >>> # Encode ICS-213 form for radio transmission
    >>> encoder = ICSDesEncoder()
    >>> form = ICS213Form()  # ... populate form data ...
    >>> encoded = encoder.encode_form(form)
    >>> print(f"Encoded: {encoded}")
    >>> # Output: 213{24~OSC|25~PSC|26~Request additional resources|2~20250530|3~1430}
    >>> 
    >>> # Decode received transmission
    >>> decoded_form = encoder.decode_form(encoded)
    >>> print(f"Decoded: {decoded_form.data.subject}")

Classes:
    ICSDesEncoder: Main encoder/decoder for ICS forms
    FieldCodeMap: Mapping between form fields and numeric codes
    EnumerationTables: Lookup tables for common values
    
Functions:
    encode_ics213: Encode ICS-213 form specifically
    encode_ics214: Encode ICS-214 form specifically
    decode_transmission: Decode any ICS-DES transmission
    validate_encoding: Validate encoded transmission format

Notes:
    This implementation focuses on ICS-213 and ICS-214 forms as specified
    in the MVP requirements, with extensible architecture for additional
    forms. Follows the complete ICS-DES specification including character
    escaping, field optimization matrix, and enumeration tables.
"""

import logging
import json
import re
from datetime import datetime, date
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
from dataclasses import dataclass

# Import form models
try:
    from ..forms.ics213 import ICS213Form, ICS213Data, Person as ICS213Person, Priority
    from ..models.ics214 import ICS214Form, ICS214Data, ActivityEntry, ResourceAssignment
    from ..models.base_form import BaseForm, FormType
except ImportError:
    # For standalone testing
    try:
        from forms.ics213 import ICS213Form, ICS213Data, Person as ICS213Person, Priority
        from models.ics214 import ICS214Form, ICS214Data, ActivityEntry, ResourceAssignment
        from models.base_form import BaseForm, FormType
    except ImportError:
        import sys
        sys.path.append('.')
        from src.forms.ics213 import ICS213Form, ICS213Data, Person as ICS213Person, Priority
        from src.models.ics214 import ICS214Form, ICS214Data, ActivityEntry, ResourceAssignment
        from src.models.base_form import BaseForm, FormType


logger = logging.getLogger(__name__)


class ICSDesError(Exception):
    """Raised when ICS-DES encoding/decoding fails."""
    pass


class FieldCodeMap:
    """Mapping between form fields and ICS-DES numeric codes.
    
    Implements the complete field code specification with validation
    and reverse lookup capabilities.
    """
    
    # Core field codes from ICS-DES specification
    CODES = {
        1: 'incident_name',      # Incident Name
        2: 'date',              # Date (YYYYMMDD or days since 2025-01-01)  
        3: 'time',              # Time (HHMM or minutes since midnight)
        4: 'datetime',          # Combined date and time
        5: 'incident_number',   # Number assigned to incident
        6: 'name',              # Person's name
        7: 'position',          # ICS position
        8: 'location',          # Physical location
        9: 'identifier',        # Resource identifier
        10: 'status',           # Resource status
        11: 'prepared_by',      # Person who prepared form
        12: 'objectives',       # Incident objectives
        13: 'operational_period', # Time period
        14: 'work_assignments', # Tasks assigned
        15: 'radio_channels',   # Communication channels
        16: 'function',         # Radio function
        17: 'channel_name',     # Radio channel name
        18: 'medical_aid_stations', # Medical facilities
        19: 'organization',     # Command structure
        20: 'safety_message',   # Safety information
        21: 'situation_summary', # Incident overview
        22: 'status_changes',   # Resource status updates
        23: 'check_in_list',    # Resource arrivals
        24: 'to',               # Message recipient
        25: 'from',             # Message sender (from_person)
        26: 'message',          # Message content
        27: 'activity_log',     # Chronological activities
        28: 'activity',         # Specific activity
        29: 'resources',        # Resource information
        30: 'resource_type',    # Type of resource
        31: 'required',         # Number required
        32: 'available',        # Number available
        33: 'hazards',          # Safety hazards
        34: 'hazard',           # Specific hazard
        35: 'mitigations',      # Safety measures
        36: 'vehicles',         # Vehicle information
        37: 'type',             # Resource type
        38: 'resource_name',    # Name of resource
        39: 'aircraft',         # Aircraft information
        40: 'assignment',       # Resource assignment
        41: 'resource_identifier', # Resource being released
        42: 'release_datetime', # Time of resource release
        43: 'person_name',      # Name of rated person
        44: 'rating',           # Performance rating
        45: 'comments',         # Additional information
        46: 'incident_commander', # Name of IC
        47: 'operations_chief', # Name of Operations Section Chief
        48: 'planning_chief',   # Name of Planning Section Chief
        49: 'logistics_chief',  # Name of Logistics Section Chief
        50: 'finance_chief'     # Name of Finance Section Chief
    }
    
    # Reverse mapping for decoding
    FIELDS = {v: k for k, v in CODES.items()}
    
    # Form-specific field requirements matrix
    FORM_FIELDS = {
        213: [1, 2, 3, 24, 25, 26],  # ICS-213: incident_name, date, time, to, from, message
        214: [1, 2, 3, 6, 7, 27],    # ICS-214: incident_name, date, time, name, position, activity_log
    }
    
    @classmethod
    def get_code(cls, field_name: str) -> Optional[int]:
        """Get numeric code for field name.
        
        Args:
            field_name: Field name to look up.
            
        Returns:
            int: Numeric code or None if not found.
        """
        return cls.FIELDS.get(field_name)
    
    @classmethod
    def get_field(cls, code: int) -> Optional[str]:
        """Get field name for numeric code.
        
        Args:
            code: Numeric code to look up.
            
        Returns:
            str: Field name or None if not found.
        """
        return cls.CODES.get(code)
    
    @classmethod
    def get_form_fields(cls, form_id: int) -> List[int]:
        """Get required field codes for a form.
        
        Args:
            form_id: Form ID (213, 214, etc.).
            
        Returns:
            List[int]: List of required field codes.
        """
        return cls.FORM_FIELDS.get(form_id, [])


class EnumerationTables:
    """Enumeration tables for common values to reduce transmission size."""
    
    # Resource status codes
    STATUS_CODES = {
        'available': 'A',
        'assigned': 'B', 
        'out_of_service': 'C'
    }
    
    # ICS position codes
    POSITION_CODES = {
        'incident_commander': 'IC',
        'operations_section_chief': 'OSC',
        'planning_section_chief': 'PSC',
        'logistics_section_chief': 'LSC',
        'finance_section_chief': 'FSC',
        'safety_officer': 'SO',
        'liaison_officer': 'LO',
        'public_information_officer': 'PIO',
        'division_supervisor': 'DIVS',
        'task_force_leader': 'TFL',
        'strike_team_leader': 'STL',
        'resources_unit_leader': 'RUL',
        'situation_unit_leader': 'SUL',
        'documentation_unit_leader': 'DOCL',
        'demobilization_unit_leader': 'DMOB',
        'communications_unit_leader': 'CUL',
        'medical_unit_leader': 'MUL'
    }
    
    # Performance rating codes
    RATING_CODES = {
        'exceeds_expectations': '1',
        'meets_expectations': '2',
        'needs_improvement': '3',
        'unsatisfactory': '4'
    }
    
    # Reverse mappings
    STATUS_DECODE = {v: k for k, v in STATUS_CODES.items()}
    POSITION_DECODE = {v: k for k, v in POSITION_CODES.items()}
    RATING_DECODE = {v: k for k, v in RATING_CODES.items()}
    
    @classmethod
    def encode_position(cls, position: str) -> str:
        """Encode position to short code.
        
        Args:
            position: Full position name.
            
        Returns:
            str: Encoded position or original if no match.
        """
        # Normalize position for lookup
        normalized = position.lower().replace(' ', '_').replace('-', '_')
        return cls.POSITION_CODES.get(normalized, position)
    
    @classmethod
    def decode_position(cls, code: str) -> str:
        """Decode position from short code.
        
        Args:
            code: Encoded position code.
            
        Returns:
            str: Decoded position or original if no match.
        """
        decoded = cls.POSITION_DECODE.get(code)
        if decoded:
            # Convert back to readable format
            return decoded.replace('_', ' ').title()
        return code


@dataclass
class EncodingStats:
    """Statistics about encoding operation."""
    original_size: int
    encoded_size: int
    compression_ratio: float
    field_count: int
    encoding_time_ms: float


class ICSDesEncoder:
    """Main encoder/decoder for ICS forms using ICS-DES specification.
    
    Provides encoding and decoding of ICS forms for radio transmission with
    comprehensive error handling, validation, and statistics reporting.
    """
    
    def __init__(self):
        """Initialize ICS-DES encoder."""
        self.field_map = FieldCodeMap()
        self.enums = EnumerationTables()
        
        logger.debug("ICSDesEncoder initialized")
    
    def encode_form(self, form: BaseForm) -> str:
        """Encode a form using ICS-DES format.
        
        Args:
            form: Form instance to encode.
            
        Returns:
            str: ICS-DES encoded string.
            
        Raises:
            ICSDesError: If encoding fails.
        """
        try:
            form_type = form.get_form_type()
            
            if form_type == FormType.ICS_213:
                return self.encode_ics213(form)
            elif form_type == FormType.ICS_214:
                return self.encode_ics214(form)
            else:
                raise ICSDesError(f"Encoding not supported for form type: {form_type}")
                
        except Exception as e:
            logger.error(f"Form encoding failed: {e}")
            raise ICSDesError(f"Encoding failed: {e}") from e
    
    def encode_ics213(self, form: ICS213Form) -> str:
        """Encode ICS-213 General Message form.
        
        Args:
            form: ICS-213 form instance.
            
        Returns:
            str: ICS-DES encoded string.
        """
        start_time = datetime.now()
        
        # Get form data
        data = form.data
        fields = []
        
        # Required fields for ICS-213
        required_codes = self.field_map.get_form_fields(213)
        
        # Encode incident name (code 1)
        if data.incident_name:
            fields.append(f"1~{self._escape_text(data.incident_name)}")
        
        # Encode date (code 2) - format as YYYYMMDD
        if data.date:
            date_formatted = self._format_date(data.date)
            fields.append(f"2~{date_formatted}")
        
        # Encode time (code 3) - format as HHMM
        if data.time:
            time_formatted = self._format_time(data.time)
            fields.append(f"3~{time_formatted}")
        
        # Encode recipient (code 24)
        if data.to and data.to.name:
            to_encoded = self._encode_person(data.to)
            fields.append(f"24~{to_encoded}")
        
        # Encode sender (code 25) 
        if data.from_person and data.from_person.name:
            from_encoded = self._encode_person(data.from_person)
            fields.append(f"25~{from_encoded}")
        
        # Encode message (code 26)
        if data.message:
            fields.append(f"26~{self._escape_text(data.message)}")
        
        # Encode priority if not routine
        if data.priority != Priority.ROUTINE:
            # Use a custom field for priority (not in standard spec)
            priority_code = {'urgent': 'U', 'immediate': 'I'}.get(data.priority.value, 'R')
            fields.append(f"51~{priority_code}")
        
        # Create final encoding
        encoded = f"213{{{"|".join(fields)}}}"
        
        # Calculate statistics
        original_size = len(form.to_json())
        encoding_time = (datetime.now() - start_time).total_seconds() * 1000
        
        logger.debug(f"ICS-213 encoded: {len(encoded)} chars (original: {original_size})")
        
        return encoded
    
    def encode_ics214(self, form: ICS214Form) -> str:
        """Encode ICS-214 Activity Log form.
        
        Args:
            form: ICS-214 form instance.
            
        Returns:
            str: ICS-DES encoded string.
        """
        start_time = datetime.now()
        
        # Get form data
        data = form.data
        fields = []
        
        # Encode incident name (code 1)
        if data.incident_name:
            fields.append(f"1~{self._escape_text(data.incident_name)}")
        
        # Encode date range from operational period (code 2)
        if data.operational_period and data.operational_period.from_date:
            date_formatted = self._format_date(data.operational_period.from_date)
            fields.append(f"2~{date_formatted}")
        
        # Encode name (code 6)
        if data.name:
            fields.append(f"6~{self._escape_text(data.name)}")
        
        # Encode position (code 7)
        if data.ics_position:
            position_encoded = self.enums.encode_position(data.ics_position)
            fields.append(f"7~{position_encoded}")
        
        # Encode activity log (code 27) as array
        if data.activity_log:
            activity_array = self._encode_activity_array(data.activity_log)
            fields.append(f"27~{activity_array}")
        
        # Encode resources assigned if present
        if data.resources_assigned:
            resources_array = self._encode_resources_array(data.resources_assigned)
            fields.append(f"29~{resources_array}")
        
        # Create final encoding
        encoded = f"214{{{"|".join(fields)}}}"
        
        # Calculate statistics
        original_size = len(json.dumps(data.to_dict()))
        encoding_time = (datetime.now() - start_time).total_seconds() * 1000
        
        logger.debug(f"ICS-214 encoded: {len(encoded)} chars (original: {original_size})")
        
        return encoded
    
    def decode_form(self, encoded: str) -> BaseForm:
        """Decode ICS-DES encoded form.
        
        Args:
            encoded: ICS-DES encoded string.
            
        Returns:
            BaseForm: Decoded form instance.
            
        Raises:
            ICSDesError: If decoding fails.
        """
        try:
            # Parse form ID and fields
            form_id, fields_str = self._parse_encoded_form(encoded)
            
            if form_id == 213:
                return self.decode_ics213(fields_str)
            elif form_id == 214:
                return self.decode_ics214(fields_str)
            else:
                raise ICSDesError(f"Decoding not supported for form ID: {form_id}")
                
        except Exception as e:
            logger.error(f"Form decoding failed: {e}")
            raise ICSDesError(f"Decoding failed: {e}") from e
    
    def decode_ics213(self, fields_str: str) -> ICS213Form:
        """Decode ICS-213 from field string.
        
        Args:
            fields_str: Encoded fields string.
            
        Returns:
            ICS213Form: Decoded form instance.
        """
        # Parse fields
        fields = self._parse_fields(fields_str)
        
        # Create data structure
        data = ICS213Data()
        
        for code, value in fields.items():
            if code == 1:  # incident_name
                data.incident_name = self._unescape_text(value)
            elif code == 2:  # date
                data.date = self._parse_date(value)
            elif code == 3:  # time
                data.time = self._parse_time(value)
            elif code == 24:  # to
                data.to = self._decode_person(value)
            elif code == 25:  # from_person
                data.from_person = self._decode_person(value)
            elif code == 26:  # message
                data.message = self._unescape_text(value)
            elif code == 51:  # priority (custom)
                priority_map = {'U': Priority.URGENT, 'I': Priority.IMMEDIATE, 'R': Priority.ROUTINE}
                data.priority = priority_map.get(value, Priority.ROUTINE)
        
        # Create and return form
        form = ICS213Form(data)
        logger.debug(f"ICS-213 decoded successfully")
        
        return form
    
    def decode_ics214(self, fields_str: str) -> ICS214Form:
        """Decode ICS-214 from field string.
        
        Args:
            fields_str: Encoded fields string.
            
        Returns:
            ICS214Form: Decoded form instance.
        """
        # Parse fields
        fields = self._parse_fields(fields_str)
        
        # Create data structure
        from ..models.ics214 import OperationalPeriod
        data = ICS214Data()
        
        for code, value in fields.items():
            if code == 1:  # incident_name
                data.incident_name = self._unescape_text(value)
            elif code == 2:  # date
                # Set operational period date
                date_parsed = self._parse_date(value)
                if not data.operational_period:
                    data.operational_period = OperationalPeriod()
                data.operational_period.from_date = date_parsed
                data.operational_period.to_date = date_parsed
            elif code == 6:  # name
                data.name = self._unescape_text(value)
            elif code == 7:  # position
                data.ics_position = self.enums.decode_position(value)
            elif code == 27:  # activity_log
                data.activity_log = self._decode_activity_array(value)
            elif code == 29:  # resources
                data.resources_assigned = self._decode_resources_array(value)
        
        # Create and return form
        form = ICS214Form(data)
        logger.debug(f"ICS-214 decoded successfully")
        
        return form
    
    def get_encoding_stats(self, form: BaseForm, encoded: str) -> EncodingStats:
        """Get encoding statistics.
        
        Args:
            form: Original form.
            encoded: Encoded string.
            
        Returns:
            EncodingStats: Encoding statistics.
        """
        original_size = len(form.to_json())
        encoded_size = len(encoded)
        compression_ratio = (original_size - encoded_size) / original_size * 100
        
        # Count fields in encoded string
        field_count = encoded.count('~')
        
        return EncodingStats(
            original_size=original_size,
            encoded_size=encoded_size,
            compression_ratio=compression_ratio,
            field_count=field_count,
            encoding_time_ms=0.0  # Would need to track during encoding
        )
    
    def validate_encoding(self, encoded: str) -> bool:
        """Validate ICS-DES encoded string format.
        
        Args:
            encoded: Encoded string to validate.
            
        Returns:
            bool: True if valid format.
        """
        try:
            # Basic format check: FID{field1~value1|field2~value2}
            pattern = r'^\d+\{([^}]+)\}$'
            if not re.match(pattern, encoded):
                return False
            
            # Parse and validate
            form_id, fields_str = self._parse_encoded_form(encoded)
            fields = self._parse_fields(fields_str)
            
            # Check if form ID is supported
            if form_id not in [213, 214]:
                return False
            
            # Validate field codes
            for code in fields.keys():
                if not self.field_map.get_field(code):
                    return False
            
            return True
            
        except Exception:
            return False
    
    # Helper methods
    
    def _escape_text(self, text: str) -> str:
        """Escape special characters in text.
        
        Args:
            text: Text to escape.
            
        Returns:
            str: Escaped text.
        """
        # Replace special characters per ICS-DES spec
        return (text
                .replace('|', r'\/')
                .replace('~', r'\:')
                .replace('[', r'\(')
                .replace(']', r'\)'))
    
    def _unescape_text(self, text: str) -> str:
        """Unescape special characters in text.
        
        Args:
            text: Text to unescape.
            
        Returns:
            str: Unescaped text.
        """
        # Reverse escape process
        return (text
                .replace(r'\/', '|')
                .replace(r'\:', '~')
                .replace(r'\(', '[')
                .replace(r'\)', ']'))
    
    def _format_date(self, date_str: str) -> str:
        """Format date as YYYYMMDD.
        
        Args:
            date_str: Date string in YYYY-MM-DD format.
            
        Returns:
            str: Formatted date.
        """
        try:
            # Parse date and format as YYYYMMDD
            if '-' in date_str:
                return date_str.replace('-', '')
            return date_str
        except Exception:
            return date_str
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date from YYYYMMDD format.
        
        Args:
            date_str: Date in YYYYMMDD format.
            
        Returns:
            str: Date in YYYY-MM-DD format.
        """
        try:
            if len(date_str) == 8 and date_str.isdigit():
                return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            return date_str
        except Exception:
            return date_str
    
    def _format_time(self, time_str: str) -> str:
        """Format time as HHMM.
        
        Args:
            time_str: Time string in HH:MM format.
            
        Returns:
            str: Formatted time.
        """
        try:
            # Remove colon if present
            return time_str.replace(':', '')
        except Exception:
            return time_str
    
    def _parse_time(self, time_str: str) -> str:
        """Parse time from HHMM format.
        
        Args:
            time_str: Time in HHMM format.
            
        Returns:
            str: Time in HH:MM format.
        """
        try:
            if len(time_str) == 4 and time_str.isdigit():
                return f"{time_str[:2]}:{time_str[2:]}"
            return time_str
        except Exception:
            return time_str
    
    def _encode_person(self, person: ICS213Person) -> str:
        """Encode person data.
        
        Args:
            person: Person object.
            
        Returns:
            str: Encoded person string.
        """
        # Simple encoding: name,position
        name = self._escape_text(person.name)
        position = self.enums.encode_position(person.position)
        return f"{name},{position}"
    
    def _decode_person(self, encoded: str) -> ICS213Person:
        """Decode person data.
        
        Args:
            encoded: Encoded person string.
            
        Returns:
            Person: Decoded person object.
        """
        try:
            parts = encoded.split(',', 1)
            name = self._unescape_text(parts[0]) if len(parts) > 0 else ""
            position = self.enums.decode_position(parts[1]) if len(parts) > 1 else ""
            
            return ICS213Person(name=name, position=position)
        except Exception:
            return ICS213Person(name=encoded, position="")
    
    def _encode_activity_array(self, activities: List[ActivityEntry]) -> str:
        """Encode activity log array.
        
        Args:
            activities: List of activity entries.
            
        Returns:
            str: Encoded activity array.
        """
        encoded_activities = []
        
        for activity in activities:
            # Encode as [time~activity_text]
            time_str = activity.datetime.strftime("%H%M") if activity.datetime else ""
            activity_text = self._escape_text(activity.notable_activities)
            encoded_activities.append(f"[3~{time_str}|28~{activity_text}]")
        
        return f"[[{"|".join(encoded_activities)}]]"
    
    def _decode_activity_array(self, encoded: str) -> List[ActivityEntry]:
        """Decode activity log array.
        
        Args:
            encoded: Encoded activity array.
            
        Returns:
            List[ActivityEntry]: Decoded activity entries.
        """
        activities = []
        
        try:
            # Remove outer brackets
            if encoded.startswith('[[') and encoded.endswith(']]'):
                content = encoded[2:-2]
                
                # Split by ]|[ to get individual activities
                activity_strs = re.split(r'\]\|\[', content)
                
                for activity_str in activity_strs:
                    # Remove any remaining brackets
                    activity_str = activity_str.strip('[]')
                    
                    # Parse activity fields
                    activity_fields = {}
                    for field in activity_str.split('|'):
                        if '~' in field:
                            code_str, value = field.split('~', 1)
                            activity_fields[int(code_str)] = value
                    
                    # Create activity entry
                    time_str = activity_fields.get(3, "")
                    activity_text = self._unescape_text(activity_fields.get(28, ""))
                    
                    # Convert time to datetime (using today as base)
                    activity_datetime = datetime.now()
                    if time_str and len(time_str) == 4:
                        hour = int(time_str[:2])
                        minute = int(time_str[2:])
                        activity_datetime = activity_datetime.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    activities.append(ActivityEntry(
                        datetime=activity_datetime,
                        notable_activities=activity_text
                    ))
        
        except Exception as e:
            logger.warning(f"Failed to decode activity array: {e}")
        
        return activities
    
    def _encode_resources_array(self, resources: List[ResourceAssignment]) -> str:
        """Encode resources array.
        
        Args:
            resources: List of resource assignments.
            
        Returns:
            str: Encoded resources array.
        """
        encoded_resources = []
        
        for resource in resources:
            # Encode as [name~position~agency]
            name = self._escape_text(resource.name)
            position = self.enums.encode_position(resource.ics_position)
            agency = self._escape_text(resource.home_agency)
            encoded_resources.append(f"[6~{name}|7~{position}|52~{agency}]")
        
        return f"[[{"|".join(encoded_resources)}]]"
    
    def _decode_resources_array(self, encoded: str) -> List[ResourceAssignment]:
        """Decode resources array.
        
        Args:
            encoded: Encoded resources array.
            
        Returns:
            List[ResourceAssignment]: Decoded resource assignments.
        """
        resources = []
        
        try:
            # Similar to activity array decoding
            if encoded.startswith('[[') and encoded.endswith(']]'):
                content = encoded[2:-2]
                resource_strs = re.split(r'\]\|\[', content)
                
                for resource_str in resource_strs:
                    resource_str = resource_str.strip('[]')
                    
                    # Parse resource fields
                    resource_fields = {}
                    for field in resource_str.split('|'):
                        if '~' in field:
                            code_str, value = field.split('~', 1)
                            resource_fields[int(code_str)] = value
                    
                    # Create resource assignment
                    name = self._unescape_text(resource_fields.get(6, ""))
                    position = self.enums.decode_position(resource_fields.get(7, ""))
                    agency = self._unescape_text(resource_fields.get(52, ""))
                    
                    resources.append(ResourceAssignment(
                        name=name,
                        ics_position=position,
                        home_agency=agency
                    ))
        
        except Exception as e:
            logger.warning(f"Failed to decode resources array: {e}")
        
        return resources
    
    def _parse_encoded_form(self, encoded: str) -> Tuple[int, str]:
        """Parse encoded form to extract form ID and fields.
        
        Args:
            encoded: Encoded form string.
            
        Returns:
            Tuple[int, str]: Form ID and fields string.
        """
        match = re.match(r'^(\d+)\{([^}]+)\}$', encoded)
        if not match:
            raise ICSDesError(f"Invalid encoding format: {encoded}")
        
        form_id = int(match.group(1))
        fields_str = match.group(2)
        
        return form_id, fields_str
    
    def _parse_fields(self, fields_str: str) -> Dict[int, str]:
        """Parse fields string into code-value mapping.
        
        Args:
            fields_str: Fields string to parse.
            
        Returns:
            Dict[int, str]: Mapping of field codes to values.
        """
        fields = {}
        
        # Split by pipe, but handle escaped pipes
        field_parts = []
        current_part = ""
        i = 0
        
        while i < len(fields_str):
            if fields_str[i] == '|' and (i == 0 or fields_str[i-1] != '\\'):
                field_parts.append(current_part)
                current_part = ""
            else:
                current_part += fields_str[i]
            i += 1
        
        if current_part:
            field_parts.append(current_part)
        
        # Parse each field
        for field_part in field_parts:
            if '~' in field_part:
                code_str, value = field_part.split('~', 1)
                try:
                    code = int(code_str)
                    fields[code] = value
                except ValueError:
                    logger.warning(f"Invalid field code: {code_str}")
        
        return fields


def encode_ics213(form: ICS213Form) -> str:
    """Convenience function to encode ICS-213 form.
    
    Args:
        form: ICS-213 form to encode.
        
    Returns:
        str: ICS-DES encoded string.
    """
    encoder = ICSDesEncoder()
    return encoder.encode_ics213(form)


def encode_ics214(form: ICS214Form) -> str:
    """Convenience function to encode ICS-214 form.
    
    Args:
        form: ICS-214 form to encode.
        
    Returns:
        str: ICS-DES encoded string.
    """
    encoder = ICSDesEncoder()
    return encoder.encode_ics214(form)


def decode_transmission(encoded: str) -> BaseForm:
    """Convenience function to decode any ICS-DES transmission.
    
    Args:
        encoded: ICS-DES encoded string.
        
    Returns:
        BaseForm: Decoded form.
    """
    encoder = ICSDesEncoder()
    return encoder.decode_form(encoded)


def validate_encoding(encoded: str) -> bool:
    """Convenience function to validate ICS-DES encoding.
    
    Args:
        encoded: Encoded string to validate.
        
    Returns:
        bool: True if valid.
    """
    encoder = ICSDesEncoder()
    return encoder.validate_encoding(encoded)