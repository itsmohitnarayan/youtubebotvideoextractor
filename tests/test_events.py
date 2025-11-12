"""
Unit tests for Event Bus System
Tests pub/sub pattern, thread safety, and event history
"""
import pytest
import time
from datetime import datetime
from threading import Thread
from src.core.events import (
    EventBus, EventType, Event, get_event_bus,
    subscribe, unsubscribe, publish
)


class TestEventBus:
    """Test EventBus class"""
    
    def setup_method(self):
        """Setup for each test - create fresh event bus"""
        self.event_bus = EventBus()
        self.received_events = []
    
    def teardown_method(self):
        """Cleanup after each test"""
        self.event_bus.clear_all_subscribers()
        self.event_bus.clear_history()
        self.received_events.clear()
    
    def test_subscribe_and_publish(self):
        """Test basic subscribe and publish"""
        # Subscribe to event
        def callback(event):
            self.received_events.append(event)
        
        self.event_bus.subscribe(EventType.VIDEO_DETECTED, callback)
        
        # Publish event
        self.event_bus.publish(EventType.VIDEO_DETECTED, {
            'video_id': 'test123',
            'title': 'Test Video'
        }, source='test')
        
        # Verify event received
        assert len(self.received_events) == 1
        assert self.received_events[0].type == EventType.VIDEO_DETECTED
        assert self.received_events[0].data['video_id'] == 'test123'
        assert self.received_events[0].source == 'test'
    
    def test_multiple_subscribers(self):
        """Test multiple subscribers to same event"""
        received1 = []
        received2 = []
        
        def callback1(event):
            received1.append(event)
        
        def callback2(event):
            received2.append(event)
        
        # Subscribe both
        self.event_bus.subscribe(EventType.DOWNLOAD_STARTED, callback1)
        self.event_bus.subscribe(EventType.DOWNLOAD_STARTED, callback2)
        
        # Publish event
        self.event_bus.publish(EventType.DOWNLOAD_STARTED, {'video_id': 'abc'}, source='test')
        
        # Both should receive
        assert len(received1) == 1
        assert len(received2) == 1
        assert received1[0].data['video_id'] == 'abc'
        assert received2[0].data['video_id'] == 'abc'
    
    def test_unsubscribe(self):
        """Test unsubscribe functionality"""
        def callback(event):
            self.received_events.append(event)
        
        # Subscribe
        self.event_bus.subscribe(EventType.UPLOAD_COMPLETED, callback)
        
        # Publish - should receive
        self.event_bus.publish(EventType.UPLOAD_COMPLETED, {}, source='test')
        assert len(self.received_events) == 1
        
        # Unsubscribe
        self.event_bus.unsubscribe(EventType.UPLOAD_COMPLETED, callback)
        
        # Publish again - should NOT receive
        self.event_bus.publish(EventType.UPLOAD_COMPLETED, {}, source='test')
        assert len(self.received_events) == 1  # Still 1, not 2
    
    def test_different_event_types(self):
        """Test that different event types don't interfere"""
        received_video = []
        received_download = []
        
        def video_callback(event):
            received_video.append(event)
        
        def download_callback(event):
            received_download.append(event)
        
        # Subscribe to different events
        self.event_bus.subscribe(EventType.VIDEO_DETECTED, video_callback)
        self.event_bus.subscribe(EventType.DOWNLOAD_STARTED, download_callback)
        
        # Publish video event
        self.event_bus.publish(EventType.VIDEO_DETECTED, {}, source='test')
        
        # Publish download event
        self.event_bus.publish(EventType.DOWNLOAD_STARTED, {}, source='test')
        
        # Each should receive only their event
        assert len(received_video) == 1
        assert len(received_download) == 1
        assert received_video[0].type == EventType.VIDEO_DETECTED
        assert received_download[0].type == EventType.DOWNLOAD_STARTED
    
    def test_event_history(self):
        """Test event history tracking"""
        # Publish some events
        self.event_bus.publish(EventType.VIDEO_DETECTED, {'id': '1'}, source='test')
        self.event_bus.publish(EventType.DOWNLOAD_STARTED, {'id': '2'}, source='test')
        self.event_bus.publish(EventType.UPLOAD_COMPLETED, {'id': '3'}, source='test')
        
        # Get all history
        history = self.event_bus.get_event_history()
        assert len(history) == 3
        assert history[0].data['id'] == '1'
        assert history[1].data['id'] == '2'
        assert history[2].data['id'] == '3'
    
    def test_event_history_filtered(self):
        """Test filtered event history"""
        # Publish different events
        self.event_bus.publish(EventType.VIDEO_DETECTED, {'id': '1'}, source='test')
        self.event_bus.publish(EventType.DOWNLOAD_STARTED, {'id': '2'}, source='test')
        self.event_bus.publish(EventType.VIDEO_DETECTED, {'id': '3'}, source='test')
        
        # Get only VIDEO_DETECTED events
        history = self.event_bus.get_event_history(EventType.VIDEO_DETECTED)
        assert len(history) == 2
        assert all(e.type == EventType.VIDEO_DETECTED for e in history)
    
    def test_event_history_limit(self):
        """Test event history size limit"""
        # Publish many events (more than max_history)
        for i in range(1500):
            self.event_bus.publish(EventType.VIDEO_DETECTED, {'id': i}, source='test')
        
        # Should only keep last 1000
        history = self.event_bus.get_event_history()
        assert len(history) <= 1000
    
    def test_clear_history(self):
        """Test clearing event history"""
        # Publish some events
        self.event_bus.publish(EventType.VIDEO_DETECTED, {}, source='test')
        self.event_bus.publish(EventType.DOWNLOAD_STARTED, {}, source='test')
        
        assert len(self.event_bus.get_event_history()) == 2
        
        # Clear history
        self.event_bus.clear_history()
        
        assert len(self.event_bus.get_event_history()) == 0
    
    def test_get_subscribers_count(self):
        """Test getting subscriber count"""
        def callback1(event):
            pass
        
        def callback2(event):
            pass
        
        # Initially no subscribers
        assert self.event_bus.get_subscribers(EventType.ERROR_OCCURRED) == 0
        
        # Add subscribers
        self.event_bus.subscribe(EventType.ERROR_OCCURRED, callback1)
        assert self.event_bus.get_subscribers(EventType.ERROR_OCCURRED) == 1
        
        self.event_bus.subscribe(EventType.ERROR_OCCURRED, callback2)
        assert self.event_bus.get_subscribers(EventType.ERROR_OCCURRED) == 2
    
    def test_exception_in_callback(self):
        """Test that exception in one callback doesn't affect others"""
        received = []
        
        def bad_callback(event):
            raise ValueError("Intentional error")
        
        def good_callback(event):
            received.append(event)
        
        # Subscribe both
        self.event_bus.subscribe(EventType.VIDEO_DETECTED, bad_callback)
        self.event_bus.subscribe(EventType.VIDEO_DETECTED, good_callback)
        
        # Publish - should not crash, good callback should still receive
        self.event_bus.publish(EventType.VIDEO_DETECTED, {}, source='test')
        
        assert len(received) == 1
    
    def test_thread_safety(self):
        """Test thread-safe pub/sub"""
        received = []
        
        def callback(event):
            received.append(event)
        
        self.event_bus.subscribe(EventType.VIDEO_DETECTED, callback)
        
        # Publish from multiple threads
        def publish_events():
            for i in range(100):
                self.event_bus.publish(EventType.VIDEO_DETECTED, {'id': i}, source='test')
        
        threads = [Thread(target=publish_events) for _ in range(5)]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Should receive all 500 events (5 threads * 100 events)
        assert len(received) == 500
    
    def test_duplicate_subscription_prevention(self):
        """Test that subscribing same callback twice doesn't duplicate"""
        received = []
        
        def callback(event):
            received.append(event)
        
        # Subscribe twice
        self.event_bus.subscribe(EventType.VIDEO_DETECTED, callback)
        self.event_bus.subscribe(EventType.VIDEO_DETECTED, callback)
        
        # Publish event
        self.event_bus.publish(EventType.VIDEO_DETECTED, {}, source='test')
        
        # Should receive only once
        assert len(received) == 1


class TestGlobalEventBus:
    """Test global event bus singleton"""
    
    def setup_method(self):
        """Setup for each test"""
        # Clear global event bus
        get_event_bus().clear_all_subscribers()
        get_event_bus().clear_history()
    
    def test_get_event_bus_singleton(self):
        """Test that get_event_bus returns same instance"""
        bus1 = get_event_bus()
        bus2 = get_event_bus()
        
        assert bus1 is bus2
    
    def test_global_subscribe_publish(self):
        """Test global convenience functions"""
        received = []
        
        def callback(event):
            received.append(event)
        
        # Use global functions
        subscribe(EventType.VIDEO_DETECTED, callback)
        publish(EventType.VIDEO_DETECTED, {'test': 'data'}, source='global_test')
        
        assert len(received) == 1
        assert received[0].data['test'] == 'data'
    
    def test_global_unsubscribe(self):
        """Test global unsubscribe"""
        received = []
        
        def callback(event):
            received.append(event)
        
        subscribe(EventType.VIDEO_DETECTED, callback)
        publish(EventType.VIDEO_DETECTED, {}, source='test')
        
        assert len(received) == 1
        
        unsubscribe(EventType.VIDEO_DETECTED, callback)
        publish(EventType.VIDEO_DETECTED, {}, source='test')
        
        # Still 1, not 2
        assert len(received) == 1


class TestEvent:
    """Test Event dataclass"""
    
    def test_event_creation(self):
        """Test creating an Event"""
        now = datetime.now()
        event = Event(
            type=EventType.VIDEO_DETECTED,
            timestamp=now,
            data={'video_id': 'abc123'},
            source='test'
        )
        
        assert event.type == EventType.VIDEO_DETECTED
        assert event.timestamp == now
        assert event.data['video_id'] == 'abc123'
        assert event.source == 'test'
    
    def test_event_repr(self):
        """Test Event string representation"""
        event = Event(
            type=EventType.DOWNLOAD_STARTED,
            timestamp=datetime.now(),
            data={'id': '123'},
            source='downloader'
        )
        
        repr_str = repr(event)
        assert 'download_started' in repr_str
        assert 'downloader' in repr_str


class TestEventType:
    """Test EventType enum"""
    
    def test_all_event_types_exist(self):
        """Test that all expected event types are defined"""
        expected_types = [
            'MONITORING_STARTED', 'MONITORING_STOPPED', 'MONITORING_PAUSED', 'MONITORING_RESUMED',
            'VIDEO_DETECTED', 'VIDEO_QUEUED',
            'DOWNLOAD_STARTED', 'DOWNLOAD_PROGRESS', 'DOWNLOAD_COMPLETED', 'DOWNLOAD_FAILED', 'DOWNLOAD_CANCELLED',
            'UPLOAD_STARTED', 'UPLOAD_PROGRESS', 'UPLOAD_COMPLETED', 'UPLOAD_FAILED', 'UPLOAD_CANCELLED',
            'STATUS_CHANGED', 'STATISTICS_UPDATED',
            'ERROR_OCCURRED', 'WARNING_OCCURRED',
            'CONFIG_CHANGED', 'SETTINGS_SAVED',
            'APP_STARTED', 'APP_SHUTDOWN'
        ]
        
        for type_name in expected_types:
            assert hasattr(EventType, type_name), f"EventType.{type_name} not found"
    
    def test_event_type_values(self):
        """Test EventType enum values are strings"""
        assert EventType.VIDEO_DETECTED.value == 'video_detected'
        assert EventType.DOWNLOAD_STARTED.value == 'download_started'
        assert EventType.UPLOAD_COMPLETED.value == 'upload_completed'
