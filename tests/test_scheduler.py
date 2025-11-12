"""
Test suite for task scheduler.
"""

import pytest
from pathlib import Path
import sys
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.scheduler import TaskScheduler


class TestTaskScheduler:
    """Tests for TaskScheduler class."""
    
    @pytest.fixture
    def scheduler(self):
        """Create TaskScheduler instance."""
        sched = TaskScheduler(timezone='UTC')
        yield sched
        # Cleanup
        if sched.scheduler.running:
            sched.shutdown()
    
    def test_scheduler_initialization(self, scheduler):
        """Test scheduler initialization."""
        assert scheduler.scheduler is not None
        assert scheduler.active_hours is None
        assert scheduler.scheduler.running is False
    
    def test_start_scheduler(self, scheduler):
        """Test starting the scheduler."""
        scheduler.start()
        assert scheduler.scheduler.running is True
    
    def test_shutdown_scheduler(self, scheduler):
        """Test shutting down the scheduler."""
        scheduler.start()
        assert scheduler.scheduler.running is True
        
        scheduler.shutdown()
        assert scheduler.scheduler.running is False
    
    def test_start_already_running(self, scheduler):
        """Test starting scheduler when already running."""
        scheduler.start()
        assert scheduler.scheduler.running is True
        
        # Start again - should not raise error
        scheduler.start()
        assert scheduler.scheduler.running is True
    
    def test_shutdown_not_running(self, scheduler):
        """Test shutting down scheduler when not running."""
        assert scheduler.scheduler.running is False
        
        # Shutdown when not running - should not raise error
        scheduler.shutdown()
        assert scheduler.scheduler.running is False
    
    def test_set_active_hours(self, scheduler):
        """Test setting active hours."""
        scheduler.set_active_hours("10:00", "22:00")
        
        assert scheduler.active_hours is not None
        start_time, end_time = scheduler.active_hours
        
        assert start_time.hour == 10
        assert start_time.minute == 0
        assert end_time.hour == 22
        assert end_time.minute == 0
    
    def test_set_active_hours_with_minutes(self, scheduler):
        """Test setting active hours with minutes."""
        scheduler.set_active_hours("09:30", "17:45")
        
        start_time, end_time = scheduler.active_hours
        
        assert start_time.hour == 9
        assert start_time.minute == 30
        assert end_time.hour == 17
        assert end_time.minute == 45
    
    def test_is_within_active_hours_no_hours_set(self, scheduler):
        """Test active hours check when no hours are set."""
        # Should return True when no active hours set
        assert scheduler.is_within_active_hours() is True
    
    @patch('core.scheduler.datetime')
    def test_is_within_active_hours_inside(self, mock_datetime, scheduler):
        """Test active hours check when inside active hours."""
        # Set active hours 10:00 - 22:00
        scheduler.set_active_hours("10:00", "22:00")
        
        # Mock current time to 15:30 (inside active hours)
        mock_now = Mock()
        mock_now.time.return_value = datetime(2025, 11, 10, 15, 30).time()
        mock_datetime.now.return_value = mock_now
        
        assert scheduler.is_within_active_hours() is True
    
    @patch('core.scheduler.datetime')
    def test_is_within_active_hours_outside_before(self, mock_datetime, scheduler):
        """Test active hours check when before active hours."""
        scheduler.set_active_hours("10:00", "22:00")
        
        # Mock current time to 08:00 (before active hours)
        mock_now = Mock()
        mock_now.time.return_value = datetime(2025, 11, 10, 8, 0).time()
        mock_datetime.now.return_value = mock_now
        
        assert scheduler.is_within_active_hours() is False
    
    @patch('core.scheduler.datetime')
    def test_is_within_active_hours_outside_after(self, mock_datetime, scheduler):
        """Test active hours check when after active hours."""
        scheduler.set_active_hours("10:00", "22:00")
        
        # Mock current time to 23:00 (after active hours)
        mock_now = Mock()
        mock_now.time.return_value = datetime(2025, 11, 10, 23, 0).time()
        mock_datetime.now.return_value = mock_now
        
        assert scheduler.is_within_active_hours() is False
    
    @patch('core.scheduler.datetime')
    def test_is_within_active_hours_at_start(self, mock_datetime, scheduler):
        """Test active hours check at exact start time."""
        scheduler.set_active_hours("10:00", "22:00")
        
        # Mock current time to 10:00 (exact start)
        mock_now = Mock()
        mock_now.time.return_value = datetime(2025, 11, 10, 10, 0).time()
        mock_datetime.now.return_value = mock_now
        
        assert scheduler.is_within_active_hours() is True
    
    @patch('core.scheduler.datetime')
    def test_is_within_active_hours_at_end(self, mock_datetime, scheduler):
        """Test active hours check at exact end time."""
        scheduler.set_active_hours("10:00", "22:00")
        
        # Mock current time to 22:00 (exact end)
        mock_now = Mock()
        mock_now.time.return_value = datetime(2025, 11, 10, 22, 0).time()
        mock_datetime.now.return_value = mock_now
        
        assert scheduler.is_within_active_hours() is True
    
    @patch('core.scheduler.datetime')
    def test_is_within_active_hours_crosses_midnight(self, mock_datetime, scheduler):
        """Test active hours that cross midnight (e.g., 22:00 - 06:00)."""
        scheduler.set_active_hours("22:00", "06:00")
        
        # Test at 23:00 (should be inside)
        mock_now = Mock()
        mock_now.time.return_value = datetime(2025, 11, 10, 23, 0).time()
        mock_datetime.now.return_value = mock_now
        assert scheduler.is_within_active_hours() is True
        
        # Test at 02:00 (should be inside)
        mock_now.time.return_value = datetime(2025, 11, 10, 2, 0).time()
        assert scheduler.is_within_active_hours() is True
        
        # Test at 12:00 (should be outside)
        mock_now.time.return_value = datetime(2025, 11, 10, 12, 0).time()
        assert scheduler.is_within_active_hours() is False
    
    def test_add_interval_job(self, scheduler):
        """Test adding an interval job."""
        mock_func = Mock()
        
        scheduler.add_interval_job(
            func=mock_func,
            minutes=5,
            job_id="test_job"
        )
        
        # Check job was added
        job = scheduler.scheduler.get_job("test_job")
        assert job is not None
        assert job.id == "test_job"
    
    def test_add_interval_job_with_args(self, scheduler):
        """Test adding interval job with arguments."""
        mock_func = Mock()
        
        scheduler.add_interval_job(
            func=mock_func,
            minutes=10,
            job_id="test_job_with_args",
            arg1="value1",
            arg2=42
        )
        
        job = scheduler.scheduler.get_job("test_job_with_args")
        assert job is not None
    
    def test_add_interval_job_replace_existing(self, scheduler):
        """Test replacing existing interval job."""
        mock_func1 = Mock()
        mock_func2 = Mock()
        
        # Add first job
        scheduler.add_interval_job(
            func=mock_func1,
            minutes=5,
            job_id="replace_test"
        )
        
        # Replace with second job
        scheduler.add_interval_job(
            func=mock_func2,
            minutes=10,
            job_id="replace_test"
        )
        
        # Should only have one job with this ID
        job = scheduler.scheduler.get_job("replace_test")
        assert job is not None
    
    def test_add_cron_job(self, scheduler):
        """Test adding a cron job."""
        mock_func = Mock()
        
        scheduler.add_cron_job(
            func=mock_func,
            hour=10,
            minute=30,
            job_id="cron_test"
        )
        
        job = scheduler.scheduler.get_job("cron_test")
        assert job is not None
        assert job.id == "cron_test"
    
    def test_add_cron_job_with_kwargs(self, scheduler):
        """Test adding cron job with keyword arguments."""
        mock_func = Mock()
        
        scheduler.add_cron_job(
            func=mock_func,
            hour=14,
            minute=0,
            job_id="cron_with_kwargs",
            channel_id="UC123",
            notify=True
        )
        
        job = scheduler.scheduler.get_job("cron_with_kwargs")
        assert job is not None
    
    def test_remove_job(self, scheduler):
        """Test removing a job."""
        mock_func = Mock()
        
        scheduler.add_interval_job(
            func=mock_func,
            minutes=5,
            job_id="job_to_remove"
        )
        
        # Verify job exists
        assert scheduler.scheduler.get_job("job_to_remove") is not None
        
        # Remove job
        scheduler.remove_job("job_to_remove")
        
        # Verify job is gone
        assert scheduler.scheduler.get_job("job_to_remove") is None
    
    def test_remove_nonexistent_job(self, scheduler):
        """Test removing non-existent job doesn't raise error."""
        # Should not raise error
        scheduler.remove_job("nonexistent_job")
    
    def test_pause_job(self, scheduler):
        """Test pausing a job."""
        mock_func = Mock()
        
        scheduler.add_interval_job(
            func=mock_func,
            minutes=5,
            job_id="job_to_pause"
        )
        
        # Pause job
        scheduler.pause_job("job_to_pause")
        
        # Job should still exist but be paused
        job = scheduler.scheduler.get_job("job_to_pause")
        assert job is not None
        # Note: APScheduler doesn't have a direct 'paused' property we can check easily
    
    def test_resume_job(self, scheduler):
        """Test resuming a paused job."""
        mock_func = Mock()
        
        scheduler.add_interval_job(
            func=mock_func,
            minutes=5,
            job_id="job_to_resume"
        )
        
        scheduler.pause_job("job_to_resume")
        scheduler.resume_job("job_to_resume")
        
        # Job should exist and be running
        job = scheduler.scheduler.get_job("job_to_resume")
        assert job is not None
    
    def test_pause_nonexistent_job(self, scheduler):
        """Test pausing non-existent job doesn't raise error."""
        scheduler.pause_job("nonexistent")
    
    def test_resume_nonexistent_job(self, scheduler):
        """Test resuming non-existent job doesn't raise error."""
        scheduler.resume_job("nonexistent")
    
    def test_get_job_status_existing(self, scheduler):
        """Test getting status of existing job."""
        mock_func = Mock()
        
        scheduler.add_interval_job(
            func=mock_func,
            minutes=5,
            job_id="status_test"
        )
        
        status = scheduler.get_job_status("status_test")
        
        assert status is not None
        assert status['id'] == "status_test"
        assert 'next_run_time' in status
        assert 'trigger' in status
        assert 'name' in status
    
    def test_get_job_status_nonexistent(self, scheduler):
        """Test getting status of non-existent job."""
        status = scheduler.get_job_status("nonexistent")
        assert status is None
    
    @patch('core.scheduler.datetime')
    def test_active_hours_wrapper_inside_hours(self, mock_datetime, scheduler):
        """Test that jobs execute inside active hours."""
        scheduler.set_active_hours("10:00", "22:00")
        
        # Mock current time to 15:00 (inside active hours)
        mock_now = Mock()
        mock_now.time.return_value = datetime(2025, 11, 10, 15, 0).time()
        mock_datetime.now.return_value = mock_now
        
        mock_func = Mock()
        wrapped_func = scheduler._wrap_with_active_hours_check(mock_func)
        
        # Call wrapped function
        wrapped_func()
        
        # Function should have been called
        mock_func.assert_called_once()
    
    @patch('core.scheduler.datetime')
    def test_active_hours_wrapper_outside_hours(self, mock_datetime, scheduler):
        """Test that jobs skip execution outside active hours."""
        scheduler.set_active_hours("10:00", "22:00")
        
        # Mock current time to 08:00 (outside active hours)
        mock_now = Mock()
        mock_now.time.return_value = datetime(2025, 11, 10, 8, 0).time()
        mock_datetime.now.return_value = mock_now
        
        mock_func = Mock()
        wrapped_func = scheduler._wrap_with_active_hours_check(mock_func)
        
        # Call wrapped function
        wrapped_func()
        
        # Function should NOT have been called
        mock_func.assert_not_called()
    
    def test_interval_job_execution(self, scheduler):
        """Test that interval job actually executes."""
        execution_flag = {'called': False}
        
        def test_job():
            execution_flag['called'] = True
        
        scheduler.start()
        
        # Add job with 1 second interval
        scheduler.add_interval_job(
            func=test_job,
            minutes=1/60,  # 1 second
            job_id="execution_test"
        )
        
        # Wait for job to execute
        time.sleep(1.5)
        
        # Check if job was called
        assert execution_flag['called'] is True
    
    def test_multiple_jobs(self, scheduler):
        """Test adding multiple different jobs."""
        mock_func1 = Mock()
        mock_func2 = Mock()
        mock_func3 = Mock()
        
        scheduler.add_interval_job(mock_func1, minutes=5, job_id="job1")
        scheduler.add_interval_job(mock_func2, minutes=10, job_id="job2")
        scheduler.add_cron_job(mock_func3, hour=10, minute=0, job_id="job3")
        
        # All jobs should exist
        assert scheduler.scheduler.get_job("job1") is not None
        assert scheduler.scheduler.get_job("job2") is not None
        assert scheduler.scheduler.get_job("job3") is not None
    
    def test_scheduler_timezone(self):
        """Test scheduler with different timezone."""
        sched = TaskScheduler(timezone='America/New_York')
        assert sched.scheduler.timezone.zone == 'America/New_York'
        sched.shutdown()
