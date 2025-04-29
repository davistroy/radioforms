#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data Access Object (DAO) package for database operations.

This package contains DAO classes that provide a layer of abstraction between
the application logic and the database, implementing the DAO pattern for
each entity type in the system.
"""

from radioforms.database.dao.base_dao import BaseDAO, DAOException
from radioforms.database.dao.user_dao import UserDAO
from radioforms.database.dao.incident_dao import IncidentDAO
from radioforms.database.dao.form_dao import FormDAO
from radioforms.database.dao.attachment_dao import AttachmentDAO
from radioforms.database.dao.setting_dao import SettingDAO

__all__ = [
    'BaseDAO',
    'DAOException',
    'UserDAO',
    'IncidentDAO',
    'FormDAO',
    'AttachmentDAO',
    'SettingDAO'
]
