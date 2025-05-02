#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Database package for RadioForms.

This package provides database management, data access objects (DAOs),
and models for the RadioForms application.
"""

from radioforms.database.db_manager import DBManager

# Create and export the DatabaseManager alias for compatibility with existing code
class DatabaseManager(DBManager):
    """Alias for DBManager for compatibility with existing code."""
    pass
