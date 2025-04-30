#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility functions for batch processing operations in the DAO layer.

This module provides helper functions for common batch processing tasks
that leverage the bulk operation capabilities of the DAO classes.
"""

from typing import Any, Dict, List, Optional, Tuple, TypeVar, Generic, Union, Callable, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import csv
import io
from pathlib import Path
import json

from radioforms.database.dao.base_dao_bulk import BulkOperationsBaseDAO

# Generic type for entity objects
T = TypeVar('T')


class BatchProcessingResult:
    """
    Result object for batch processing operations.
    
    This class provides a standardized way to report on the results of batch
    processing operations, including success and failure counts, timing information,
    and detailed error tracking.
    """
    
    def __init__(self):
        """Initialize a new batch processing result object."""
        self.total_items = 0
        self.successful_items = 0
        self.failed_items = 0
        self.skipped_items = 0
        self.errors = []
        self.start_time = time.time()
        self.end_time = None
        self.processing_time = None
        
    def complete(self):
        """
        Mark the processing as complete and calculate processing time.
        
        Returns:
            self for method chaining
        """
        self.end_time = time.time()
        self.processing_time = self.end_time - self.start_time
        return self
        
    def add_success(self, count: int = 1):
        """
        Add a successful item count.
        
        Args:
            count: Number of successful items to add
            
        Returns:
            self for method chaining
        """
        self.successful_items += count
        self.total_items += count
        return self
        
    def add_failure(self, error: str, item: Any = None, count: int = 1):
        """
        Add a failed item and its error.
        
        Args:
            error: Error message or exception
            item: The item that failed (optional)
            count: Number of failed items to add
            
        Returns:
            self for method chaining
        """
        self.failed_items += count
        self.total_items += count
        self.errors.append((error, item))
        return self
        
    def add_skipped(self, count: int = 1):
        """
        Add a skipped item count.
        
        Args:
            count: Number of skipped items to add
            
        Returns:
            self for method chaining
        """
        self.skipped_items += count
        self.total_items += count
        return self
        
    def get_success_rate(self) -> float:
        """
        Get the success rate as a percentage.
        
        Returns:
            Percentage of successful items (0-100)
        """
        if self.total_items == 0:
            return 0.0
        return (self.successful_items / self.total_items) * 100
        
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the batch processing results.
        
        Returns:
            Dictionary with summary information
        """
        return {
            "total_items": self.total_items,
            "successful_items": self.successful_items,
            "failed_items": self.failed_items,
            "skipped_items": self.skipped_items,
            "success_rate": self.get_success_rate(),
            "processing_time": self.processing_time,
            "error_count": len(self.errors)
        }
        
    def __str__(self) -> str:
        """Get string representation of the results."""
        if not self.end_time:
            self.complete()
            
        summary = self.get_summary()
        return (
            f"Batch Processing Results:\n"
            f"  Total items: {summary['total_items']}\n"
            f"  Successful: {summary['successful_items']}\n"
            f"  Failed: {summary['failed_items']}\n"
            f"  Skipped: {summary['skipped_items']}\n"
            f"  Success rate: {summary['success_rate']:.2f}%\n"
            f"  Processing time: {summary['processing_time']:.2f} seconds\n"
            f"  Error count: {summary['error_count']}"
        )


def import_from_csv(dao: BulkOperationsBaseDAO[T], csv_file: Union[str, Path, io.TextIOWrapper], 
                  column_mapping: Dict[str, str] = None, batch_size: int = 100,
                  skip_header: bool = True) -> BatchProcessingResult:
    """
    Import data from a CSV file into the database using bulk operations.
    
    Args:
        dao: DAO instance to use for bulk operations
        csv_file: Path to CSV file or file-like object
        column_mapping: Mapping of CSV column names to database column names
        batch_size: Number of rows to process in each batch
        skip_header: Whether to skip the first row as a header
        
    Returns:
        BatchProcessingResult with import statistics
        
    Example:
        >>> result = import_from_csv(
        ...     user_dao, 
        ...     "path/to/users.csv",
        ...     column_mapping={"Name": "name", "Call Sign": "call_sign"}
        ... )
        >>> print(result)
    """
    result = BatchProcessingResult()
    
    # Prepare CSV file
    file_obj = None
    if isinstance(csv_file, (str, Path)):
        file_obj = open(csv_file, 'r', newline='')
    else:
        file_obj = csv_file
        
    try:
        reader = csv.reader(file_obj)
        
        # Skip header if needed
        header = None
        if skip_header:
            header = next(reader)
            
        # Use header for column mapping if not provided
        if not column_mapping and header:
            # Use the header columns as-is
            column_mapping = {col: col for col in header}
            
        # Read data in batches
        current_batch = []
        row_count = 0
        
        for row in reader:
            row_count += 1
            
            try:
                # Convert row to dictionary using column mapping
                if header:
                    row_dict = {}
                    for i, col_name in enumerate(header):
                        if i < len(row):
                            db_col = column_mapping.get(col_name, col_name)
                            row_dict[db_col] = row[i]
                else:
                    # If no header, use column mapping keys as indexes
                    row_dict = {}
                    for csv_idx, db_col in column_mapping.items():
                        try:
                            idx = int(csv_idx)
                            if idx < len(row):
                                row_dict[db_col] = row[idx]
                        except ValueError:
                            # If not an integer, ignore
                            pass
                
                # Add to current batch
                current_batch.append(row_dict)
                
                # Process batch if it's full
                if len(current_batch) >= batch_size:
                    try:
                        ids = dao.bulk_create(current_batch)
                        result.add_success(len(ids))
                    except Exception as e:
                        result.add_failure(str(e), current_batch, len(current_batch))
                    finally:
                        current_batch = []
                        
            except Exception as e:
                result.add_failure(f"Error processing row {row_count}: {str(e)}", row)
                
        # Process any remaining items in the batch
        if current_batch:
            try:
                ids = dao.bulk_create(current_batch)
                result.add_success(len(ids))
            except Exception as e:
                result.add_failure(str(e), current_batch, len(current_batch))
                
    finally:
        # Close file if we opened it
        if isinstance(csv_file, (str, Path)) and file_obj:
            file_obj.close()
            
    return result.complete()


def export_to_csv(dao: BulkOperationsBaseDAO[T], output_file: Union[str, Path, io.TextIOWrapper],
                column_mapping: Optional[Dict[str, str]] = None,
                filters: Optional[Dict[str, Any]] = None,
                include_header: bool = True,
                max_rows: Optional[int] = None) -> BatchProcessingResult:
    """
    Export data from the database to a CSV file.
    
    Args:
        dao: DAO instance to use for retrieving data
        output_file: Path to output CSV file or file-like object
        column_mapping: Mapping of database column names to CSV column names
        filters: Optional filters to apply when retrieving data
        include_header: Whether to include a header row
        max_rows: Maximum number of rows to export
        
    Returns:
        BatchProcessingResult with export statistics
        
    Example:
        >>> result = export_to_csv(
        ...     incident_dao, 
        ...     "incidents_export.csv",
        ...     column_mapping={"name": "Incident Name", "description": "Description"}
        ... )
        >>> print(f"Exported {result.successful_items} records")
    """
    result = BatchProcessingResult()
    
    # Get data to export
    try:
        limit = max_rows or 1000000  # Use a large default if not specified
        entities = dao.find_by_filter(filters or {}, limit=limit, as_dict=True)
        
        # Prepare CSV file
        file_obj = None
        if isinstance(output_file, (str, Path)):
            file_obj = open(output_file, 'w', newline='')
        else:
            file_obj = output_file
            
        try:
            writer = csv.writer(file_obj)
            
            # Determine columns to export
            if entities:
                # Get column names from first entity
                db_columns = list(entities[0].keys())
                
                # Apply column mapping if provided
                if column_mapping:
                    # Ensure all entity columns are in the mapping
                    for col in db_columns:
                        if col not in column_mapping:
                            column_mapping[col] = col
                    
                    # Convert db_columns to CSV column names
                    csv_columns = [column_mapping.get(col, col) for col in db_columns]
                else:
                    # Use entity columns as-is
                    csv_columns = db_columns
                    column_mapping = {col: col for col in db_columns}
                
                # Write header if requested
                if include_header:
                    writer.writerow(csv_columns)
                
                # Write data rows
                for entity in entities:
                    try:
                        # Extract values in the correct order
                        row = [entity.get(col) for col in db_columns]
                        writer.writerow(row)
                        result.add_success()
                    except Exception as e:
                        result.add_failure(f"Error writing entity: {str(e)}", entity)
                        
            else:
                # No entities to export
                if include_header and column_mapping:
                    # If we have a column mapping but no data, still write the header
                    writer.writerow(column_mapping.keys())
                        
        finally:
            # Close file if we opened it
            if isinstance(output_file, (str, Path)) and file_obj:
                file_obj.close()
                
    except Exception as e:
        result.add_failure(f"Error during export: {str(e)}")
        
    return result.complete()


def import_from_json(dao: BulkOperationsBaseDAO[T], json_file: Union[str, Path, io.TextIOWrapper],
                   batch_size: int = 100, root_element: Optional[str] = None) -> BatchProcessingResult:
    """
    Import data from a JSON file into the database using bulk operations.
    
    Args:
        dao: DAO instance to use for bulk operations
        json_file: Path to JSON file or file-like object
        batch_size: Number of entities to process in each batch
        root_element: Optional root element name to extract data from
        
    Returns:
        BatchProcessingResult with import statistics
        
    Example:
        >>> result = import_from_json(
        ...     incident_dao, 
        ...     "incidents.json",
        ...     root_element="incidents"
        ... )
        >>> print(f"Imported {result.successful_items} incidents")
    """
    result = BatchProcessingResult()
    
    # Load JSON data
    try:
        if isinstance(json_file, (str, Path)):
            with open(json_file, 'r') as f:
                data = json.load(f)
        else:
            data = json.load(json_file)
        
        # Extract data from root element if specified
        if root_element and root_element in data:
            data = data[root_element]
            
        # Ensure data is a list
        if not isinstance(data, list):
            if isinstance(data, dict):
                # Convert single object to list
                data = [data]
            else:
                raise ValueError("JSON data is not a list or object")
                
        # Process data in batches
        dao.set_batch_size(batch_size)
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            
            try:
                ids = dao.bulk_create(batch)
                result.add_success(len(ids))
            except Exception as e:
                result.add_failure(f"Error processing batch: {str(e)}", batch, len(batch))
                
    except Exception as e:
        result.add_failure(f"Error during import: {str(e)}")
        
    return result.complete()


def bulk_upsert(dao: BulkOperationsBaseDAO[T], entities: List[Dict[str, Any]], 
             key_field: str, batch_size: Optional[int] = None) -> BatchProcessingResult:
    """
    Perform a bulk upsert operation (insert or update) based on a key field.
    
    This function efficiently handles mixed inserts and updates by determining
    which records already exist and separating them into create and update operations.
    
    Args:
        dao: DAO instance to use for bulk operations
        entities: List of entity dictionaries to insert or update
        key_field: Field name to use for determining if records exist
        batch_size: Number of entities to process in each batch
        
    Returns:
        BatchProcessingResult with upsert statistics
        
    Example:
        >>> users = [
        ...     {"call_sign": "ABC123", "name": "John Doe"},
        ...     {"call_sign": "XYZ789", "name": "Jane Smith"}
        ... ]
        >>> result = bulk_upsert(user_dao, users, "call_sign")
        >>> print(result)
    """
    result = BatchProcessingResult()
    
    if not entities:
        return result.complete()
        
    try:
        # Use custom batch size if provided
        if batch_size:
            dao.set_batch_size(batch_size)
            
        # Extract all key values
        key_values = [entity.get(key_field) for entity in entities if entity.get(key_field)]
        
        # Group entities by whether they have a key value
        entities_with_keys = []
        entities_without_keys = []
        
        for entity in entities:
            if entity.get(key_field):
                entities_with_keys.append(entity)
            else:
                entities_without_keys.append(entity)
                
        # Handle entities without key values (direct inserts)
        if entities_without_keys:
            try:
                create_ids = dao.bulk_create(entities_without_keys)
                result.add_success(len(create_ids))
            except Exception as e:
                result.add_failure(f"Error creating entities without keys: {str(e)}", 
                                 entities_without_keys, len(entities_without_keys))
                
        # For entities with keys, we need to determine which exist
        if entities_with_keys:
            # Get existing entities based on key field
            existing_query = f"SELECT {dao.pk_column}, {key_field} FROM {dao.table_name} WHERE {key_field} IN "
            
            # Process in batches to avoid large IN clauses
            existing_map = {}  # Maps key value to ID
            
            for i in range(0, len(key_values), dao.get_batch_size()):
                batch_keys = key_values[i:i+dao.get_batch_size()]
                placeholders = ", ".join(["?"] * len(batch_keys))
                query = f"{existing_query}({placeholders})"
                
                cursor = dao.db_manager.execute(query, batch_keys)
                for row in cursor.fetchall():
                    row_dict = dict(row)
                    existing_map[row_dict[key_field]] = row_dict[dao.pk_column]
                    
            # Separate entities for create and update operations
            entities_to_create = []
            entities_to_update = []
            
            for entity in entities_with_keys:
                key_value = entity.get(key_field)
                if key_value in existing_map:
                    # Entity exists, prepare for update
                    update_entity = entity.copy()
                    update_entity[dao.pk_column] = existing_map[key_value]
                    entities_to_update.append(update_entity)
                else:
                    # Entity doesn't exist, prepare for create
                    entities_to_create.append(entity)
                    
            # Perform bulk create operation
            if entities_to_create:
                try:
                    create_ids = dao.bulk_create(entities_to_create)
                    result.add_success(len(create_ids))
                except Exception as e:
                    result.add_failure(f"Error creating entities: {str(e)}", 
                                     entities_to_create, len(entities_to_create))
                                     
            # Perform bulk update operation
            if entities_to_update:
                try:
                    updated_count = dao.bulk_update(entities_to_update)
                    result.add_success(updated_count)
                except Exception as e:
                    result.add_failure(f"Error updating entities: {str(e)}", 
                                     entities_to_update, len(entities_to_update))
                    
    except Exception as e:
        result.add_failure(f"Error during bulk upsert: {str(e)}")
        
    return result.complete()


def multi_threaded_batch_process(dao: BulkOperationsBaseDAO[T], entities: List[Any],
                               process_func: Callable[[List[Any]], Any],
                               max_workers: int = 4, batch_size: Optional[int] = None) -> BatchProcessingResult:
    """
    Process a large list of entities in parallel using multiple threads.
    
    This function divides the workload into batches and processes them
    concurrently using a thread pool for improved performance.
    
    Args:
        dao: DAO instance to use for operations
        entities: List of entities to process
        process_func: Function that processes a batch of entities
        max_workers: Maximum number of worker threads
        batch_size: Number of entities in each batch
        
    Returns:
        BatchProcessingResult with processing statistics
        
    Example:
        >>> def process_form_batch(forms):
        ...     results = []
        ...     for form in forms:
        ...         # Process each form...
        ...         results.append(success)
        ...     return sum(results)  # Return count of successful operations
        >>> 
        >>> result = multi_threaded_batch_process(
        ...     form_dao, all_forms, process_form_batch, max_workers=8
        ... )
        >>> print(f"Processed {result.total_items} forms with {result.successful_items} successes")
    """
    result = BatchProcessingResult()
    
    if not entities:
        return result.complete()
        
    # Use provided batch size or default from DAO
    chunk_size = batch_size or dao.get_batch_size()
    
    # Split entities into batches
    batches = list(dao._chunk_list(entities, chunk_size))
    
    # Process batches in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all batches for processing
        future_to_batch = {
            executor.submit(process_func, batch): batch
            for batch in batches
        }
        
        # Process results as they complete
        for future in as_completed(future_to_batch):
            batch = future_to_batch[future]
            try:
                # Get the result of the future (return value of process_func)
                batch_result = future.result()
                
                # Interpret the result based on its type
                if isinstance(batch_result, int):
                    # If an integer, treat as count of successful items
                    result.add_success(batch_result)
                    
                    # If some items failed, add them as failures
                    if batch_result < len(batch):
                        result.add_failure("Some items in batch failed", None, len(batch) - batch_result)
                elif isinstance(batch_result, tuple) and len(batch_result) == 2:
                    # If a tuple of (success_count, error_count), record both
                    success_count, error_count = batch_result
                    result.add_success(success_count)
                    if error_count > 0:
                        result.add_failure("Batch contained errors", None, error_count)
                elif isinstance(batch_result, dict) and "success" in batch_result:
                    # If a dictionary with success/failure counts
                    result.add_success(batch_result.get("success", 0))
                    result.add_failure(
                        batch_result.get("error", "Batch error"),
                        None,
                        batch_result.get("failure", 0)
                    )
                    result.add_skipped(batch_result.get("skipped", 0))
                elif batch_result:
                    # If a truthy value, consider the whole batch successful
                    result.add_success(len(batch))
                else:
                    # If a falsy value, consider the whole batch failed
                    result.add_failure("Batch processing failed", batch, len(batch))
            except Exception as e:
                # If the future raised an exception, record all items as failures
                result.add_failure(f"Error processing batch: {str(e)}", batch, len(batch))
                
    return result.complete()
