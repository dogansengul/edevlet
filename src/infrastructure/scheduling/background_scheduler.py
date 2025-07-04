"""
Background Scheduler - Infrastructure Layer
Simple background task scheduler
"""
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Callable
import schedule


class BackgroundScheduler:
    """Simple background scheduler for periodic tasks."""
    
    def __init__(self):
        """Initialize scheduler."""
        self.logger = logging.getLogger("backend")
        self.is_running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.jobs = []
        
        self.logger.info("🕐 Background scheduler initialized")
    
    def schedule_job(self, job_function: Callable, interval_hours: int) -> None:
        """Schedule a job to run at specified intervals."""
        self.jobs.append((job_function, interval_hours))
        
        # Schedule the recurring job
        schedule.every(interval_hours).hours.do(job_function)
        
        self.logger.info(f"⏰ Job scheduled every {interval_hours} hours")
    
    def start(self) -> None:
        """Start the background scheduler."""
        if self.is_running:
            self.logger.warning("⚠️ Scheduler is already running")
            return
        
        self.logger.info("🚀 Starting background scheduler...")
        
        self.is_running = True
        self.stop_event.clear()
        
        # Start scheduler in background thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("✅ Background scheduler started successfully")
        if self.jobs:
            job_function, interval_hours = self.jobs[0]
            self.logger.info(f"🎯 Next execution: {datetime.now() + timedelta(hours=interval_hours)}")
    
    def stop(self) -> None:
        """Stop the background scheduler."""
        if not self.is_running:
            self.logger.warning("⚠️ Scheduler is not running")
            return
        
        self.logger.info("🛑 Stopping background scheduler...")
        
        self.is_running = False
        self.stop_event.set()
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("✅ Background scheduler stopped")
    
    def _run_scheduler(self) -> None:
        """Run the scheduler loop in background thread."""
        self.logger.info("🔄 Scheduler loop started")
        
        while self.is_running and not self.stop_event.is_set():
            try:
                schedule.run_pending()
                # Check every minute
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"💥 Scheduler loop error: {str(e)}", exc_info=True)
                time.sleep(60)  # Continue after error
        
        self.logger.info("🔄 Scheduler loop ended")
    
    def get_status(self) -> dict:
        """Get scheduler status information."""
        next_run = None
        if self.is_running and schedule.jobs:
            # Get next scheduled run time
            next_job = min(schedule.jobs, key=lambda job: job.next_run)
            next_run = next_job.next_run.isoformat() if next_job.next_run else None
        
        return {
            "is_running": self.is_running,
            "next_run": next_run,
            "jobs_count": len(schedule.jobs)
        } 