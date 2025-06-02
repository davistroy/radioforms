/*!
 * Database module for RadioForms application
 * 
 * This module handles all database operations for the STANDALONE ICS Forms
 * Management Application. The database is a single SQLite file that travels
 * with the application for portable operation.
 * 
 * Following MANDATORY.md principles: simple functions, static SQL, basic error handling.
 */

// Simple database module - complex abstractions removed per SIMPLIFICATION PLAN

pub mod simple;
pub mod schema;

#[cfg(test)]
pub mod simple_tests;

#[cfg(test)]
pub mod integration_tests;