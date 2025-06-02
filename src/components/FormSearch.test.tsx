/**
 * Simple tests for FormSearch component
 * 
 * Following MANDATORY.md: test basic functionality that emergency responders need.
 * Tests search functionality, error handling, and accessibility.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { FormSearch } from './FormSearch';
import { formService } from '../services/formService';

// Mock the form service
vi.mock('../services/formService', () => ({
  formService: {
    searchForms: vi.fn(),
  },
}));

const mockFormService = vi.mocked(formService);

describe('FormSearch', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render search form', () => {
    render(<FormSearch />);
    
    expect(screen.getByText('Search Forms')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Enter incident name to search/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Search Forms' })).toBeInTheDocument();
  });

  it('should display search results', async () => {
    // Arrange
    const mockResults = [
      {
        id: 1,
        incident_name: 'Test Fire Incident',
        form_type: 'ICS-201',
        status: 'draft',
        form_data: '{}',
        created_at: '2025-01-01T12:00:00Z',
        updated_at: '2025-01-01T12:00:00Z'
      }
    ];
    mockFormService.searchForms.mockResolvedValue(mockResults);

    // Act
    render(<FormSearch />);
    const searchInput = screen.getByPlaceholderText(/Enter incident name to search/);
    const searchButton = screen.getByRole('button', { name: 'Search Forms' });

    fireEvent.change(searchInput, { target: { value: 'Fire' } });
    fireEvent.click(searchButton);

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Search Results (1 forms found)')).toBeInTheDocument();
      expect(screen.getByText('Test Fire Incident')).toBeInTheDocument();
      expect(screen.getByText('Type: ICS-201')).toBeInTheDocument();
      expect(screen.getByText('Status: draft')).toBeInTheDocument();
    });

    expect(mockFormService.searchForms).toHaveBeenCalledWith('Fire');
  });

  it('should display no results message', async () => {
    // Arrange
    mockFormService.searchForms.mockResolvedValue([]);

    // Act
    render(<FormSearch />);
    const searchButton = screen.getByRole('button', { name: 'Search Forms' });
    fireEvent.click(searchButton);

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Search Results (0 forms found)')).toBeInTheDocument();
      expect(screen.getByText('No forms found')).toBeInTheDocument();
    });
  });

  it('should display error message on search failure', async () => {
    // Arrange
    mockFormService.searchForms.mockRejectedValue(new Error('Search failed'));

    // Act
    render(<FormSearch />);
    const searchButton = screen.getByRole('button', { name: 'Search Forms' });
    fireEvent.click(searchButton);

    // Assert
    await waitFor(() => {
      expect(screen.getByText('Error: Search failed')).toBeInTheDocument();
    });
  });

  it('should clear search results', async () => {
    // Arrange
    const mockResults = [
      {
        id: 1,
        incident_name: 'Test Incident',
        form_type: 'ICS-201',
        status: 'draft',
        form_data: '{}',
        created_at: '2025-01-01T12:00:00Z',
        updated_at: '2025-01-01T12:00:00Z'
      }
    ];
    mockFormService.searchForms.mockResolvedValue(mockResults);

    // Act
    render(<FormSearch />);
    const searchButton = screen.getByRole('button', { name: 'Search Forms' });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(screen.getByText('Search Results (1 forms found)')).toBeInTheDocument();
    });

    const clearButton = screen.getByRole('button', { name: 'Clear' });
    fireEvent.click(clearButton);

    // Assert
    expect(screen.queryByText('Search Results')).not.toBeInTheDocument();
  });

  it('should call onFormSelect when form is clicked', async () => {
    // Arrange
    const onFormSelect = vi.fn();
    const mockResults = [
      {
        id: 1,
        incident_name: 'Test Incident',
        form_type: 'ICS-201',
        status: 'draft',
        form_data: '{}',
        created_at: '2025-01-01T12:00:00Z',
        updated_at: '2025-01-01T12:00:00Z'
      }
    ];
    mockFormService.searchForms.mockResolvedValue(mockResults);

    // Act
    render(<FormSearch onFormSelect={onFormSelect} />);
    const searchButton = screen.getByRole('button', { name: 'Search Forms' });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(screen.getByText('Test Incident')).toBeInTheDocument();
    });

    const formItem = screen.getByText('Test Incident').closest('div');
    fireEvent.click(formItem!);

    // Assert
    expect(onFormSelect).toHaveBeenCalledWith(mockResults[0]);
  });

  it('should have proper accessibility attributes', () => {
    render(<FormSearch />);
    
    // Check ARIA attributes
    const searchForm = screen.getByLabelText('Search forms by incident name');
    expect(searchForm).toBeInTheDocument();
    
    const searchInput = screen.getByPlaceholderText(/Enter incident name to search/);
    expect(searchInput).toHaveAttribute('id', 'incident_name');
    
    const helpText = screen.getByText(/Leave empty to show all forms/);
    expect(helpText).toHaveAttribute('id', 'incident_name_help');
    expect(searchInput).toHaveAttribute('aria-describedby', 'incident_name_help');
  });
});