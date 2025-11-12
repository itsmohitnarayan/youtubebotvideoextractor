"""
Event Bus System for Pub/Sub Communication
Provides centralized event handling between GUI and backend components
"""
from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
from threading import Lock


class EventType(Enum):
    """All supported event types in the application"""
    
    # Monitoring events
    MONITORING_STARTED = "monitoring_started"
    MONITORING_STOPPED = "monitoring_stopped"
    MONITORING_PAUSED = "monitoring_paused"
    MONITORING_RESUMED = "monitoring_resumed"
    
    # Video detection events
    VIDEO_DETECTED = "video_detected"
    VIDEO_QUEUED = "video_queued"
    
    # Download events
    DOWNLOAD_STARTED = "download_started"
    DOWNLOAD_PROGRESS = "download_progress"
    DOWNLOAD_COMPLETED = "download_completed"
    DOWNLOAD_FAILED = "download_failed"
    DOWNLOAD_CANCELLED = "download_cancelled"
    
    # Upload events
    UPLOAD_STARTED = "upload_started"
    UPLOAD_PROGRESS = "upload_progress"
    UPLOAD_COMPLETED = "upload_completed"
    UPLOAD_FAILED = "upload_failed"
    UPLOAD_CANCELLED = "upload_cancelled"
    
    # Status events
    STATUS_CHANGED = "status_changed"
    STATISTICS_UPDATED = "statistics_updated"
    
    # Error events
    ERROR_OCCURRED = "error_occurred"
    WARNING_OCCURRED = "warning_occurred"
    
    # Configuration events
    CONFIG_CHANGED = "config_changed"
    SETTINGS_SAVED = "settings_saved"
    
    # Application events
    APP_STARTED = "app_started"
    APP_SHUTDOWN = "app_shutdown"


@dataclass
class Event:
    """Event data structure"""
    type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    source: str = "unknown"
    
    def __repr__(self):
        return f"Event({self.type.value}, source={self.source}, data={self.data})"


class EventBus:
    """
    Thread-safe event bus implementing pub/sub pattern
    
    Usage:
        # Subscribe to events
        event_bus.subscribe(EventType.VIDEO_DETECTED, on_video_detected)
        
        # Publish events
        event_bus.publish(EventType.VIDEO_DETECTED, {
            'video_id': 'abc123',
            'title': 'New Video',
            'url': 'https://...'
        }, source='monitor')
        
        # Unsubscribe
        event_bus.unsubscribe(EventType.VIDEO_DETECTED, on_video_detected)
    """
    
    def __init__(self):
        """Initialize the event bus"""
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._lock = Lock()
        self._logger = logging.getLogger(__name__)
        self._event_history: List[Event] = []
        self._max_history = 1000  # Keep last 1000 events
        
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """
        Subscribe to an event type
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event is published
        """
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)
                self._logger.debug(f"Subscribed to {event_type.value}: {callback.__name__}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """
        Unsubscribe from an event type
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to remove
        """
        with self._lock:
            if event_type in self._subscribers:
                if callback in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(callback)
                    self._logger.debug(f"Unsubscribed from {event_type.value}: {callback.__name__}")
    
    def publish(self, event_type: EventType, data: Dict[str, Any] = None, source: str = "unknown") -> None:
        """
        Publish an event to all subscribers
        
        Args:
            event_type: Type of event
            data: Event data dictionary
            source: Source component that published the event
        """
        event = Event(
            type=event_type,
            timestamp=datetime.now(),
            data=data or {},
            source=source
        )
        
        # Add to history
        with self._lock:
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
        
        self._logger.debug(f"Publishing event: {event}")
        
        # Get subscribers (copy to avoid lock during callback execution)
        subscribers = []
        with self._lock:
            if event_type in self._subscribers:
                subscribers = self._subscribers[event_type].copy()
        
        # Call all subscribers
        for callback in subscribers:
            try:
                callback(event)
            except Exception as e:
                self._logger.error(f"Error in event callback {callback.__name__}: {e}", exc_info=True)
    
    def get_subscribers(self, event_type: EventType) -> int:
        """Get number of subscribers for an event type"""
        with self._lock:
            return len(self._subscribers.get(event_type, []))
    
    def get_event_history(self, event_type: EventType = None, limit: int = 100) -> List[Event]:
        """
        Get recent event history
        
        Args:
            event_type: Filter by event type (None = all events)
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        with self._lock:
            if event_type:
                filtered = [e for e in self._event_history if e.type == event_type]
                return filtered[-limit:]
            return self._event_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history"""
        with self._lock:
            self._event_history.clear()
            self._logger.debug("Event history cleared")
    
    def clear_all_subscribers(self) -> None:
        """Remove all subscribers (use for shutdown)"""
        with self._lock:
            self._subscribers.clear()
            self._logger.debug("All subscribers cleared")


# Global event bus instance
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus instance"""
    return _event_bus


# Convenience functions
def subscribe(event_type: EventType, callback: Callable[[Event], None]) -> None:
    """Subscribe to an event (convenience function)"""
    _event_bus.subscribe(event_type, callback)


def unsubscribe(event_type: EventType, callback: Callable[[Event], None]) -> None:
    """Unsubscribe from an event (convenience function)"""
    _event_bus.unsubscribe(event_type, callback)


def publish(event_type: EventType, data: Dict[str, Any] = None, source: str = "unknown") -> None:
    """Publish an event (convenience function)"""
    _event_bus.publish(event_type, data, source)
