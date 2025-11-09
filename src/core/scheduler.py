"""
Task Scheduler
Wrapper around APScheduler for managing periodic tasks.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, time
from typing import Callable, Optional
import logging


class TaskScheduler:
    """Manages scheduled tasks for the application."""
    
    def __init__(self, timezone: str = 'UTC'):
        """
        Initialize task scheduler.
        
        Args:
            timezone: Timezone for scheduling (default: UTC)
        """
        self.scheduler = BackgroundScheduler(timezone=timezone)
        self.logger = logging.getLogger(__name__)
        self.active_hours: Optional[tuple[time, time]] = None
        self._monitoring_job_id: Optional[str] = None
    
    def start(self) -> None:
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            self.logger.info("Scheduler started")
    
    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.logger.info("Scheduler shut down")
    
    def set_active_hours(self, start_time: str, end_time: str) -> None:
        """
        Set active hours for task execution.
        
        Args:
            start_time: Start time in HH:MM format
            end_time: End time in HH:MM format
        """
        start_hour, start_min = map(int, start_time.split(':'))
        end_hour, end_min = map(int, end_time.split(':'))
        
        self.active_hours = (
            time(start_hour, start_min),
            time(end_hour, end_min)
        )
        
        self.logger.info(f"Active hours set: {start_time} - {end_time}")
    
    def is_within_active_hours(self) -> bool:
        """
        Check if current time is within active hours.
        
        Returns:
            True if within active hours or no active hours set, False otherwise
        """
        if not self.active_hours:
            return True
        
        current_time = datetime.now().time()
        start_time, end_time = self.active_hours
        
        if start_time <= end_time:
            # Normal case: e.g., 10:00 - 22:00
            return start_time <= current_time <= end_time
        else:
            # Crosses midnight: e.g., 22:00 - 06:00
            return current_time >= start_time or current_time <= end_time
    
    def add_interval_job(
        self,
        func: Callable,
        minutes: int,
        job_id: str,
        **kwargs
    ) -> None:
        """
        Add a job that runs at regular intervals.
        
        Args:
            func: Function to execute
            minutes: Interval in minutes
            job_id: Unique job identifier
            **kwargs: Additional arguments to pass to function
        """
        try:
            self.scheduler.add_job(
                func=self._wrap_with_active_hours_check(func),
                trigger=IntervalTrigger(minutes=minutes),
                id=job_id,
                kwargs=kwargs,
                replace_existing=True
            )
            self.logger.info(f"Interval job added: {job_id} (every {minutes} min)")
        except Exception as e:
            self.logger.error(f"Error adding interval job {job_id}: {e}")
    
    def add_cron_job(
        self,
        func: Callable,
        hour: int,
        minute: int,
        job_id: str,
        **kwargs
    ) -> None:
        """
        Add a job that runs at specific time daily.
        
        Args:
            func: Function to execute
            hour: Hour (0-23)
            minute: Minute (0-59)
            job_id: Unique job identifier
            **kwargs: Additional arguments to pass to function
        """
        try:
            self.scheduler.add_job(
                func=func,
                trigger=CronTrigger(hour=hour, minute=minute),
                id=job_id,
                kwargs=kwargs,
                replace_existing=True
            )
            self.logger.info(f"Cron job added: {job_id} (daily at {hour:02d}:{minute:02d})")
        except Exception as e:
            self.logger.error(f"Error adding cron job {job_id}: {e}")
    
    def remove_job(self, job_id: str) -> None:
        """
        Remove a scheduled job.
        
        Args:
            job_id: Job identifier to remove
        """
        try:
            self.scheduler.remove_job(job_id)
            self.logger.info(f"Job removed: {job_id}")
        except Exception as e:
            self.logger.error(f"Error removing job {job_id}: {e}")
    
    def pause_job(self, job_id: str) -> None:
        """
        Pause a scheduled job.
        
        Args:
            job_id: Job identifier to pause
        """
        try:
            self.scheduler.pause_job(job_id)
            self.logger.info(f"Job paused: {job_id}")
        except Exception as e:
            self.logger.error(f"Error pausing job {job_id}: {e}")
    
    def resume_job(self, job_id: str) -> None:
        """
        Resume a paused job.
        
        Args:
            job_id: Job identifier to resume
        """
        try:
            self.scheduler.resume_job(job_id)
            self.logger.info(f"Job resumed: {job_id}")
        except Exception as e:
            self.logger.error(f"Error resuming job {job_id}: {e}")
    
    def _wrap_with_active_hours_check(self, func: Callable) -> Callable:
        """
        Wrap a function to only execute within active hours.
        
        Args:
            func: Function to wrap
        
        Returns:
            Wrapped function
        """
        def wrapper(*args, **kwargs):
            if self.is_within_active_hours():
                return func(*args, **kwargs)
            else:
                self.logger.debug(
                    f"Skipping job '{func.__name__}' - outside active hours"
                )
        
        return wrapper
    
    def get_job_status(self, job_id: str) -> Optional[dict]:
        """
        Get status of a scheduled job.
        
        Args:
            job_id: Job identifier
        
        Returns:
            Job information dictionary or None
        """
        job = self.scheduler.get_job(job_id)
        if job:
            return {
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time,
                'trigger': str(job.trigger)
            }
        return None
