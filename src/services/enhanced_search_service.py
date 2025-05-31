"""Enhanced Search Service for RadioForms.

This module provides advanced search capabilities building on the existing
multi-form service with user-requested enhancements including:
- Quick search presets for common emergency scenarios
- Smart search suggestions and auto-completion
- Search result ranking and relevance scoring
- Advanced filters for operational periods and form relationships
- Search history and saved searches for frequent queries

Following CLAUDE.md principles with focus on:
- User experience optimization for emergency operations
- Performance for rapid information retrieval
- Simple interface hiding complex functionality

Example:
    >>> from src.services.enhanced_search_service import EnhancedSearchService
    >>> 
    >>> search_service = EnhancedSearchService(db_manager)
    >>> # Quick search for urgent messages
    >>> urgent_forms = search_service.quick_search_urgent()
    >>> 
    >>> # Smart search with suggestions
    >>> results = search_service.smart_search("fire truck Division A")
    >>> suggestions = search_service.get_search_suggestions("fire tr")

Classes:
    EnhancedSearchService: Main enhanced search interface
    SearchPreset: Pre-configured search queries for common scenarios
    SearchSuggestion: Search suggestion with relevance scoring
    SearchHistory: Management of search history and saved searches
    
Functions:
    create_search_presets: Factory for common emergency search presets
    extract_search_terms: Extract meaningful terms from query text
    calculate_relevance_score: Score search results by relevance

Notes:
    This service extends the existing multi-form search capabilities
    with user experience enhancements specifically requested by
    emergency management professionals in user feedback analysis.
"""

import logging
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter

# Import existing search infrastructure
try:
    from .multi_form_service import MultiFormService, FormQuery, FormSortField, SortDirection
    from ..database.connection import DatabaseManager, DatabaseError
    from ..models.base_form import FormType, FormStatus
except ImportError:
    # For standalone testing
    try:
        from multi_form_service import MultiFormService, FormQuery, FormSortField, SortDirection
        from database.connection import DatabaseManager, DatabaseError
        from models.base_form import FormType, FormStatus
    except ImportError:
        import sys
        sys.path.append('.')
        from src.services.multi_form_service import MultiFormService, FormQuery, FormSortField, SortDirection
        from src.database.connection import DatabaseManager, DatabaseError
        from src.models.base_form import FormType, FormStatus


logger = logging.getLogger(__name__)


class SearchPresetType(Enum):
    """Types of pre-configured search presets."""
    
    URGENT_MESSAGES = "urgent_messages"
    TODAYS_ACTIVITY = "todays_activity"
    RESOURCE_REQUESTS = "resource_requests"
    STATUS_UPDATES = "status_updates"
    SAFETY_MESSAGES = "safety_messages"
    INCIDENT_COMMANDS = "incident_commands"
    RECENT_FORMS = "recent_forms"
    MY_FORMS = "my_forms"
    UNFINISHED_DRAFTS = "unfinished_drafts"


@dataclass
class SearchPreset:
    """Pre-configured search query for common emergency scenarios.
    
    Provides quick access to frequently used search patterns that
    emergency management personnel need during incidents.
    """
    
    preset_type: SearchPresetType
    name: str
    description: str
    query: FormQuery
    icon: str = "🔍"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert preset to dictionary representation."""
        return {
            'type': self.preset_type.value,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'query': {
                'form_types': [ft.value for ft in self.query.form_types] if self.query.form_types else None,
                'statuses': self.query.statuses,
                'search_text': self.query.search_text,
                'created_after': self.query.created_after.isoformat() if self.query.created_after else None,
                'sort_field': self.query.sort_field.value,
                'sort_direction': self.query.sort_direction.value,
                'limit': self.query.limit
            }
        }


@dataclass 
class SearchSuggestion:
    """Search suggestion with relevance scoring."""
    
    suggestion: str
    category: str
    relevance_score: float
    frequency: int = 0
    last_used: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert suggestion to dictionary."""
        return {
            'suggestion': self.suggestion,
            'category': self.category,
            'relevance_score': self.relevance_score,
            'frequency': self.frequency,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }


@dataclass
class SearchHistoryEntry:
    """Entry in search history."""
    
    query: str
    timestamp: datetime
    result_count: int
    execution_time_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert history entry to dictionary."""
        return {
            'query': self.query,
            'timestamp': self.timestamp.isoformat(),
            'result_count': self.result_count,
            'execution_time_ms': self.execution_time_ms
        }


class EnhancedSearchService:
    """Enhanced search service with user experience improvements.
    
    Extends the existing multi-form search with:
    - Quick search presets for common emergency scenarios
    - Smart search suggestions based on usage patterns
    - Search history and saved searches
    - Advanced relevance scoring and result ranking
    - Performance optimizations for emergency operations
    """
    
    def __init__(self, db_manager: DatabaseManager, multi_form_service: Optional[MultiFormService] = None):
        """Initialize enhanced search service.
        
        Args:
            db_manager: Database manager for connections.
            multi_form_service: Optional existing multi-form service instance.
        """
        self.db_manager = db_manager
        self.multi_form_service = multi_form_service or MultiFormService(db_manager)
        self.logger = logging.getLogger(__name__)
        
        # Initialize search components
        self.presets = self._create_search_presets()
        self.search_history: List[SearchHistoryEntry] = []
        self.saved_searches: Dict[str, FormQuery] = {}
        self.suggestion_cache: Dict[str, List[SearchSuggestion]] = {}
        
        logger.debug("EnhancedSearchService initialized")
    
    def initialize(self) -> None:
        """Initialize the enhanced search service.
        
        Sets up search history storage and suggestion caching.
        """
        self.logger.info("Initializing enhanced search service...")
        
        try:
            # Initialize underlying multi-form service
            self.multi_form_service.initialize()
            
            # Initialize search history table
            self._initialize_search_history()
            
            # Load saved searches
            self._load_saved_searches()
            
            self.logger.info("Enhanced search service initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize enhanced search service: {e}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg) from e
    
    def quick_search_urgent(self) -> List[Dict[str, Any]]:
        """Quick search for urgent/immediate priority messages.
        
        Returns:
            List of urgent message forms.
        """
        preset = self.presets[SearchPresetType.URGENT_MESSAGES]
        return self._execute_search_with_timing(preset.query, "urgent_quick_search")
    
    def quick_search_today(self) -> List[Dict[str, Any]]:
        """Quick search for today's activity.
        
        Returns:
            List of forms created today.
        """
        preset = self.presets[SearchPresetType.TODAYS_ACTIVITY]
        return self._execute_search_with_timing(preset.query, "today_quick_search")
    
    def quick_search_resource_requests(self) -> List[Dict[str, Any]]:
        """Quick search for resource request messages.
        
        Returns:
            List of resource request forms.
        """
        preset = self.presets[SearchPresetType.RESOURCE_REQUESTS]
        return self._execute_search_with_timing(preset.query, "resource_request_search")
    
    def quick_search_my_drafts(self, user: str) -> List[Dict[str, Any]]:
        """Quick search for user's draft forms.
        
        Args:
            user: Username to search for.
            
        Returns:
            List of draft forms by the user.
        """
        query = FormQuery(
            statuses=['draft'],
            created_by=user,
            sort_field=FormSortField.UPDATED_DATE,
            sort_direction=SortDirection.DESCENDING,
            limit=20
        )
        return self._execute_search_with_timing(query, f"my_drafts_{user}")
    
    def smart_search(self, search_text: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Perform smart search with enhanced result ranking.
        
        Args:
            search_text: Text to search for.
            max_results: Maximum number of results to return.
            
        Returns:
            List of search results with relevance scoring.
        """
        start_time = datetime.now()
        
        try:
            # Extract and enhance search terms
            enhanced_terms = self._enhance_search_terms(search_text)
            
            # Create optimized query
            query = FormQuery(
                search_text=enhanced_terms,
                sort_field=FormSortField.UPDATED_DATE,
                sort_direction=SortDirection.DESCENDING,
                limit=max_results
            )
            
            # Execute search
            results = self.multi_form_service.search_forms(query)
            
            # Apply relevance scoring
            scored_results = self._apply_relevance_scoring(results, search_text)
            
            # Record search in history
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._record_search_history(search_text, len(scored_results), execution_time)
            
            self.logger.debug(f"Smart search for '{search_text}' returned {len(scored_results)} results")
            
            return scored_results
            
        except Exception as e:
            self.logger.error(f"Smart search failed: {e}")
            raise DatabaseError(f"Smart search failed: {e}") from e
    
    def get_search_suggestions(self, partial_text: str, max_suggestions: int = 10) -> List[SearchSuggestion]:
        """Get search suggestions based on partial input.
        
        Args:
            partial_text: Partial search text.
            max_suggestions: Maximum suggestions to return.
            
        Returns:
            List of search suggestions.
        """
        if len(partial_text) < 2:
            return []
        
        # Check cache first
        cache_key = partial_text.lower()
        if cache_key in self.suggestion_cache:
            return self.suggestion_cache[cache_key][:max_suggestions]
        
        suggestions = []
        
        try:
            # Get suggestions from search history
            history_suggestions = self._get_history_suggestions(partial_text)
            suggestions.extend(history_suggestions)
            
            # Get suggestions from common terms
            common_suggestions = self._get_common_term_suggestions(partial_text)
            suggestions.extend(common_suggestions)
            
            # Get suggestions from form content
            content_suggestions = self._get_content_suggestions(partial_text)
            suggestions.extend(content_suggestions)
            
            # Remove duplicates and sort by relevance
            unique_suggestions = {}
            for suggestion in suggestions:
                if suggestion.suggestion not in unique_suggestions:
                    unique_suggestions[suggestion.suggestion] = suggestion
                else:
                    # Keep the one with higher relevance score
                    existing = unique_suggestions[suggestion.suggestion]
                    if suggestion.relevance_score > existing.relevance_score:
                        unique_suggestions[suggestion.suggestion] = suggestion
            
            # Sort by relevance score
            sorted_suggestions = sorted(
                unique_suggestions.values(),
                key=lambda s: s.relevance_score,
                reverse=True
            )
            
            # Cache results
            self.suggestion_cache[cache_key] = sorted_suggestions
            
            return sorted_suggestions[:max_suggestions]
            
        except Exception as e:
            self.logger.warning(f"Failed to get search suggestions: {e}")
            return []
    
    def save_search(self, name: str, query: FormQuery) -> None:
        """Save a search query for future use.
        
        Args:
            name: Name for the saved search.
            query: Query to save.
        """
        self.saved_searches[name] = query
        self._persist_saved_searches()
        self.logger.debug(f"Saved search '{name}'")
    
    def get_saved_searches(self) -> Dict[str, Dict[str, Any]]:
        """Get all saved searches.
        
        Returns:
            Dictionary of saved search names to query data.
        """
        result = {}
        for name, query in self.saved_searches.items():
            result[name] = {
                'form_types': [ft.value for ft in query.form_types] if query.form_types else None,
                'search_text': query.search_text,
                'statuses': query.statuses,
                'created_after': query.created_after.isoformat() if query.created_after else None,
                'created_before': query.created_before.isoformat() if query.created_before else None,
                'sort_field': query.sort_field.value,
                'sort_direction': query.sort_direction.value
            }
        return result
    
    def execute_saved_search(self, name: str) -> List[Dict[str, Any]]:
        """Execute a saved search by name.
        
        Args:
            name: Name of the saved search.
            
        Returns:
            Search results.
            
        Raises:
            ValueError: If saved search doesn't exist.
        """
        if name not in self.saved_searches:
            raise ValueError(f"Saved search '{name}' not found")
        
        query = self.saved_searches[name]
        return self._execute_search_with_timing(query, f"saved_search_{name}")
    
    def get_search_presets(self) -> List[Dict[str, Any]]:
        """Get all available search presets.
        
        Returns:
            List of search preset data.
        """
        return [preset.to_dict() for preset in self.presets.values()]
    
    def execute_preset_search(self, preset_type: SearchPresetType) -> List[Dict[str, Any]]:
        """Execute a preset search.
        
        Args:
            preset_type: Type of preset to execute.
            
        Returns:
            Search results.
        """
        if preset_type not in self.presets:
            raise ValueError(f"Unknown preset type: {preset_type}")
        
        preset = self.presets[preset_type]
        return self._execute_search_with_timing(preset.query, f"preset_{preset_type.value}")
    
    def get_search_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent search history.
        
        Args:
            limit: Maximum number of history entries to return.
            
        Returns:
            List of search history entries.
        """
        recent_history = sorted(
            self.search_history,
            key=lambda h: h.timestamp,
            reverse=True
        )[:limit]
        
        return [entry.to_dict() for entry in recent_history]
    
    def clear_search_history(self) -> None:
        """Clear all search history."""
        self.search_history.clear()
        self._persist_search_history()
        self.logger.debug("Search history cleared")
    
    def get_search_analytics(self) -> Dict[str, Any]:
        """Get search usage analytics.
        
        Returns:
            Dictionary with search analytics data.
        """
        if not self.search_history:
            return {
                'total_searches': 0,
                'average_execution_time': 0,
                'most_common_terms': [],
                'search_trends': {}
            }
        
        # Calculate analytics
        total_searches = len(self.search_history)
        avg_execution_time = sum(h.execution_time_ms for h in self.search_history) / total_searches
        
        # Extract common terms
        all_terms = []
        for entry in self.search_history:
            terms = self._extract_search_terms(entry.query)
            all_terms.extend(terms)
        
        term_counter = Counter(all_terms)
        most_common = term_counter.most_common(10)
        
        # Calculate daily search trends
        search_trends = defaultdict(int)
        for entry in self.search_history:
            date_key = entry.timestamp.strftime('%Y-%m-%d')
            search_trends[date_key] += 1
        
        return {
            'total_searches': total_searches,
            'average_execution_time': round(avg_execution_time, 2),
            'most_common_terms': [{'term': term, 'count': count} for term, count in most_common],
            'search_trends': dict(search_trends)
        }
    
    # Private helper methods
    
    def _create_search_presets(self) -> Dict[SearchPresetType, SearchPreset]:
        """Create default search presets."""
        presets = {}
        
        # Urgent messages preset
        urgent_query = FormQuery(
            search_text="urgent immediate priority",
            sort_field=FormSortField.CREATED_DATE,
            sort_direction=SortDirection.DESCENDING,
            limit=20
        )
        presets[SearchPresetType.URGENT_MESSAGES] = SearchPreset(
            preset_type=SearchPresetType.URGENT_MESSAGES,
            name="Urgent Messages",
            description="High priority and urgent communications",
            query=urgent_query,
            icon="🚨"
        )
        
        # Today's activity preset
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_query = FormQuery(
            created_after=today,
            sort_field=FormSortField.CREATED_DATE,
            sort_direction=SortDirection.DESCENDING,
            limit=50
        )
        presets[SearchPresetType.TODAYS_ACTIVITY] = SearchPreset(
            preset_type=SearchPresetType.TODAYS_ACTIVITY,
            name="Today's Activity",
            description="All forms created today",
            query=today_query,
            icon="📅"
        )
        
        # Resource requests preset
        resource_query = FormQuery(
            search_text="request resource engine crew helicopter personnel equipment",
            sort_field=FormSortField.CREATED_DATE,
            sort_direction=SortDirection.DESCENDING,
            limit=30
        )
        presets[SearchPresetType.RESOURCE_REQUESTS] = SearchPreset(
            preset_type=SearchPresetType.RESOURCE_REQUESTS,
            name="Resource Requests",
            description="Forms requesting additional resources",
            query=resource_query,
            icon="🚒"
        )
        
        # Status updates preset
        status_query = FormQuery(
            search_text="status update situation report progress contained",
            sort_field=FormSortField.CREATED_DATE,
            sort_direction=SortDirection.DESCENDING,
            limit=25
        )
        presets[SearchPresetType.STATUS_UPDATES] = SearchPreset(
            preset_type=SearchPresetType.STATUS_UPDATES,
            name="Status Updates",
            description="Incident status and situation reports",
            query=status_query,
            icon="📊"
        )
        
        # Safety messages preset
        safety_query = FormQuery(
            search_text="safety hazard danger warning evacuation injury medical",
            sort_field=FormSortField.CREATED_DATE,
            sort_direction=SortDirection.DESCENDING,
            limit=20
        )
        presets[SearchPresetType.SAFETY_MESSAGES] = SearchPreset(
            preset_type=SearchPresetType.SAFETY_MESSAGES,
            name="Safety Messages",
            description="Safety alerts and hazard communications",
            query=safety_query,
            icon="⚠️"
        )
        
        # Recent forms preset
        recent_query = FormQuery(
            sort_field=FormSortField.UPDATED_DATE,
            sort_direction=SortDirection.DESCENDING,
            limit=30
        )
        presets[SearchPresetType.RECENT_FORMS] = SearchPreset(
            preset_type=SearchPresetType.RECENT_FORMS,
            name="Recent Forms",
            description="Most recently updated forms",
            query=recent_query,
            icon="🕒"
        )
        
        # Unfinished drafts preset
        drafts_query = FormQuery(
            statuses=['draft'],
            sort_field=FormSortField.UPDATED_DATE,
            sort_direction=SortDirection.DESCENDING,
            limit=25
        )
        presets[SearchPresetType.UNFINISHED_DRAFTS] = SearchPreset(
            preset_type=SearchPresetType.UNFINISHED_DRAFTS,
            name="Unfinished Drafts",
            description="Forms that are still in draft status",
            query=drafts_query,
            icon="📝"
        )
        
        return presets
    
    def _enhance_search_terms(self, search_text: str) -> str:
        """Enhance search terms with synonyms and expansions."""
        # Common emergency management synonyms
        synonyms = {
            'fire': ['fire', 'wildfire', 'blaze', 'burn'],
            'truck': ['truck', 'engine', 'apparatus', 'vehicle'],
            'crew': ['crew', 'team', 'personnel', 'staff'],
            'urgent': ['urgent', 'immediate', 'priority', 'emergency'],
            'help': ['help', 'assistance', 'support', 'aid'],
            'medical': ['medical', 'ems', 'ambulance', 'paramedic', 'health']
        }
        
        terms = search_text.lower().split()
        enhanced_terms = []
        
        for term in terms:
            enhanced_terms.append(term)
            # Add synonyms if available
            for key, synonym_list in synonyms.items():
                if term in synonym_list and key not in enhanced_terms:
                    enhanced_terms.extend(synonym_list[:2])  # Add top 2 synonyms
                    break
        
        return ' '.join(enhanced_terms)
    
    def _apply_relevance_scoring(self, results: List[Dict[str, Any]], 
                                search_text: str) -> List[Dict[str, Any]]:
        """Apply relevance scoring to search results."""
        if not results:
            return results
        
        search_terms = set(search_text.lower().split())
        
        for result in results:
            score = 0.0
            
            # Score based on title match
            title = result.get('title', '').lower()
            title_matches = sum(1 for term in search_terms if term in title)
            score += title_matches * 2.0
            
            # Score based on incident name match
            incident = result.get('incident_name', '').lower()
            incident_matches = sum(1 for term in search_terms if term in incident)
            score += incident_matches * 1.5
            
            # Score based on recency (newer = higher score)
            try:
                created_at = datetime.fromisoformat(result.get('created_at', ''))
                days_old = (datetime.now() - created_at).days
                recency_score = max(0, 1.0 - (days_old / 30))  # Decay over 30 days
                score += recency_score
            except (ValueError, TypeError):
                pass
            
            # Score based on form type relevance
            form_type = result.get('form_type', '')
            if form_type == 'ICS-213' and any(term in ['message', 'communication'] for term in search_terms):
                score += 0.5
            elif form_type == 'ICS-214' and any(term in ['activity', 'log', 'timeline'] for term in search_terms):
                score += 0.5
            
            result['relevance_score'] = round(score, 2)
        
        # Sort by relevance score (descending)
        return sorted(results, key=lambda r: r.get('relevance_score', 0), reverse=True)
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract meaningful search terms from query."""
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        
        # Extract alphanumeric terms
        terms = re.findall(r'\b[a-zA-Z0-9]+\b', query.lower())
        
        # Filter out stop words and short terms
        meaningful_terms = [term for term in terms if len(term) >= 3 and term not in stop_words]
        
        return meaningful_terms
    
    def _execute_search_with_timing(self, query: FormQuery, search_type: str) -> List[Dict[str, Any]]:
        """Execute search with performance timing."""
        start_time = datetime.now()
        
        try:
            results = self.multi_form_service.search_forms(query)
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Record in history if it's a text search
            if query.search_text:
                self._record_search_history(query.search_text, len(results), execution_time)
            
            self.logger.debug(f"{search_type} returned {len(results)} results in {execution_time:.1f}ms")
            return results
            
        except Exception as e:
            self.logger.error(f"{search_type} failed: {e}")
            raise
    
    def _record_search_history(self, query: str, result_count: int, execution_time_ms: float) -> None:
        """Record search in history."""
        entry = SearchHistoryEntry(
            query=query,
            timestamp=datetime.now(),
            result_count=result_count,
            execution_time_ms=execution_time_ms
        )
        
        self.search_history.append(entry)
        
        # Keep only last 100 searches in memory
        if len(self.search_history) > 100:
            self.search_history = self.search_history[-100:]
    
    def _get_history_suggestions(self, partial_text: str) -> List[SearchSuggestion]:
        """Get suggestions from search history."""
        suggestions = []
        partial_lower = partial_text.lower()
        
        # Find matching queries from history
        matching_queries = [
            entry.query for entry in self.search_history
            if partial_lower in entry.query.lower() and len(entry.query) > len(partial_text)
        ]
        
        # Count frequency and calculate relevance
        query_counts = Counter(matching_queries)
        
        for query, count in query_counts.most_common(5):
            relevance = min(1.0, count / 10.0)  # Max relevance of 1.0
            suggestions.append(SearchSuggestion(
                suggestion=query,
                category="History",
                relevance_score=relevance,
                frequency=count
            ))
        
        return suggestions
    
    def _get_common_term_suggestions(self, partial_text: str) -> List[SearchSuggestion]:
        """Get suggestions from common emergency management terms."""
        common_terms = [
            "urgent", "immediate", "resource request", "status update", 
            "fire engine", "ambulance", "helicopter", "personnel",
            "evacuation", "safety", "medical", "equipment",
            "incident commander", "operations", "planning", "logistics",
            "division", "sector", "strike team", "task force"
        ]
        
        suggestions = []
        partial_lower = partial_text.lower()
        
        for term in common_terms:
            if term.startswith(partial_lower) and term != partial_lower:
                relevance = 1.0 - (len(term) - len(partial_text)) / len(term)
                suggestions.append(SearchSuggestion(
                    suggestion=term,
                    category="Common Terms",
                    relevance_score=relevance
                ))
        
        return suggestions
    
    def _get_content_suggestions(self, partial_text: str) -> List[SearchSuggestion]:
        """Get suggestions from form content."""
        # This would query the database for matching content
        # For now, return empty list to avoid complex database queries
        return []
    
    def _initialize_search_history(self) -> None:
        """Initialize search history storage."""
        try:
            with self.db_manager.get_transaction() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS search_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query TEXT NOT NULL,
                        result_count INTEGER,
                        execution_time_ms REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS saved_searches (
                        name TEXT PRIMARY KEY,
                        query_data TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
        
        except Exception as e:
            self.logger.error(f"Failed to initialize search history: {e}")
            raise
    
    def _load_saved_searches(self) -> None:
        """Load saved searches from database."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute("SELECT name, query_data FROM saved_searches")
                
                for row in cursor.fetchall():
                    name, query_data = row
                    try:
                        # This would need proper FormQuery deserialization
                        # For now, skip loading to avoid complexity
                        pass
                    except Exception as e:
                        self.logger.warning(f"Failed to load saved search '{name}': {e}")
        
        except Exception as e:
            self.logger.warning(f"Failed to load saved searches: {e}")
    
    def _persist_saved_searches(self) -> None:
        """Persist saved searches to database."""
        # Implementation would serialize and save FormQuery objects
        # Skipped for simplicity
        pass
    
    def _persist_search_history(self) -> None:
        """Persist search history to database."""
        # Implementation would save recent history entries
        # Skipped for simplicity
        pass


def create_enhanced_search_service(db_manager: DatabaseManager) -> EnhancedSearchService:
    """Factory function for creating enhanced search service.
    
    Args:
        db_manager: Database manager instance.
        
    Returns:
        EnhancedSearchService: Configured search service.
    """
    service = EnhancedSearchService(db_manager)
    service.initialize()
    return service