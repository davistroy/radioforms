/*!
 * Services module for RadioForms application
 * 
 * This module contains business logic services that provide higher-level
 * functionality by orchestrating various components of the application.
 * 
 * Business Logic:
 * - Services encapsulate complex business workflows
 * - Each service focuses on a specific domain area
 * - Services coordinate between models, database, and external systems
 * - Proper error handling and transaction management
 * 
 * Design Philosophy:
 * - Keep services focused on business logic, not data access
 * - Services should be stateless where possible
 * - Comprehensive error handling with meaningful messages
 * - Services should be easily testable and mockable
 */

pub mod auto_save;

pub use auto_save::*;