#!/usr/bin/env python3
"""
Local Batch Evaluator Automation Scheduler

This script automates the batch evaluator to run at regular intervals
and upload results to GCS. Designed for local development and testing.
"""

import os
import sys
import time
import subprocess
import schedule
import logging
from datetime import datetime, timedelta
from typing import Optional
import signal
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class LocalBatchScheduler:
    """Local scheduler for batch evaluator with GCS upload"""
    
    def __init__(self, 
                 evaluation_script: str = "batch_evaluator.py",
                 log_file: str = "automation/batch_scheduler.log",
                 max_runtime_minutes: int = 30):
        """
        Initialize the scheduler
        
        Args:
            evaluation_script: Path to the batch evaluator script
            log_file: Path to log file
            max_runtime_minutes: Maximum runtime for each evaluation
        """
        self.evaluation_script = evaluation_script
        self.log_file = log_file
        self.max_runtime_minutes = max_runtime_minutes
        self.running = True
        self.execution_count = 0
        self.setup_logging()
        
        # Create automation directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
    def setup_logging(self):
        """Set up logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def run_batch_evaluation(self):
        """Run a single batch evaluation"""
        self.execution_count += 1
        start_time = datetime.now()
        
        self.logger.info(f"🚀 Starting batch evaluation #{self.execution_count}")
        self.logger.info(f"Start time: {start_time}")
        
        try:
            # Run the batch evaluator
            result = subprocess.run([
                sys.executable, self.evaluation_script
            ], 
            capture_output=True, 
            text=True, 
            timeout=self.max_runtime_minutes * 60,
            cwd=os.path.dirname(os.path.dirname(__file__))
            )
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            if result.returncode == 0:
                self.logger.info(f"✅ Batch evaluation #{self.execution_count} completed successfully")
                self.logger.info(f"Duration: {duration}")
                
                # Log key output lines
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if any(keyword in line for keyword in ['Uploaded', 'records saved', 'Success:', 'Error']):
                        self.logger.info(f"   {line}")
                        
            else:
                self.logger.error(f"❌ Batch evaluation #{self.execution_count} failed")
                self.logger.error(f"Return code: {result.returncode}")
                self.logger.error(f"STDERR: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"⏰ Batch evaluation #{self.execution_count} timed out after {self.max_runtime_minutes} minutes")
        except Exception as e:
            self.logger.error(f"💥 Batch evaluation #{self.execution_count} crashed: {str(e)}")
            
    def schedule_every_n_minutes(self, minutes: int):
        """Schedule evaluation every N minutes"""
        schedule.every(minutes).minutes.do(self.run_batch_evaluation)
        self.logger.info(f"📅 Scheduled to run every {minutes} minutes")
        
    def schedule_every_n_hours(self, hours: int):
        """Schedule evaluation every N hours"""
        schedule.every(hours).hours.do(self.run_batch_evaluation)
        self.logger.info(f"📅 Scheduled to run every {hours} hours")
        
    def schedule_daily_at(self, time_str: str):
        """Schedule evaluation daily at specific time (HH:MM format)"""
        schedule.every().day.at(time_str).do(self.run_batch_evaluation)
        self.logger.info(f"📅 Scheduled to run daily at {time_str}")
        
    def schedule_for_evaluation_period(self, 
                                     total_days: int = 4, 
                                     runs_per_12_hours: int = 14):
        """
        Schedule for evaluation period (e.g., 14 runs per 12 hours for 4 days)
        
        Args:
            total_days: Total number of days to run
            runs_per_12_hours: Number of runs every 12 hours
        """
        # Calculate interval in minutes
        interval_minutes = (12 * 60) // runs_per_12_hours
        
        self.logger.info(f"📅 Evaluation period schedule:")
        self.logger.info(f"   Duration: {total_days} days")
        self.logger.info(f"   Frequency: {runs_per_12_hours} runs per 12 hours")
        self.logger.info(f"   Interval: Every {interval_minutes} minutes")
        
        # Set end time
        self.end_time = datetime.now() + timedelta(days=total_days)
        self.logger.info(f"   End time: {self.end_time}")
        
        # Schedule the job
        schedule.every(interval_minutes).minutes.do(self.run_batch_evaluation)
        
    def run_immediate_test(self):
        """Run an immediate test evaluation"""
        self.logger.info("🧪 Running immediate test evaluation...")
        self.run_batch_evaluation()
        
    def start_scheduler(self):
        """Start the scheduler main loop"""
        self.logger.info("🏁 Starting batch evaluation scheduler...")
        self.logger.info(f"Log file: {os.path.abspath(self.log_file)}")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            while self.running:
                schedule.run_pending()
                
                # Check if evaluation period ended
                if hasattr(self, 'end_time') and datetime.now() > self.end_time:
                    self.logger.info("⏰ Evaluation period completed")
                    break
                    
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            self.logger.info("⚠️ Received keyboard interrupt")
        finally:
            self.stop_scheduler()
            
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        self.logger.info("🛑 Scheduler stopped")
        self.logger.info(f"📊 Total evaluations completed: {self.execution_count}")
        
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        self.logger.info(f"📡 Received signal {signum}")
        self.stop_scheduler()
        
    def get_status(self):
        """Get current scheduler status"""
        return {
            "running": self.running,
            "execution_count": self.execution_count,
            "next_run": schedule.next_run(),
            "jobs": len(schedule.jobs)
        }


def main():
    """Main function with CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Local Batch Evaluator Scheduler")
    parser.add_argument("--mode", choices=["test", "hourly", "evaluation-period"], 
                       default="test", help="Scheduling mode")
    parser.add_argument("--interval", type=int, default=60, 
                       help="Interval in minutes (for custom scheduling)")
    parser.add_argument("--hours", type=int, default=2, 
                       help="Interval in hours (for hourly mode)")
    parser.add_argument("--days", type=int, default=4, 
                       help="Total days for evaluation period")
    parser.add_argument("--runs-per-12h", type=int, default=14, 
                       help="Runs per 12 hours for evaluation period")
    parser.add_argument("--max-runtime", type=int, default=30, 
                       help="Maximum runtime per evaluation (minutes)")
    
    args = parser.parse_args()
    
    # Create scheduler
    scheduler = LocalBatchScheduler(max_runtime_minutes=args.max_runtime)
    
    # Configure based on mode
    if args.mode == "test":
        print("🧪 Running immediate test...")
        scheduler.run_immediate_test()
        return
        
    elif args.mode == "hourly":
        scheduler.schedule_every_n_hours(args.hours)
        
    elif args.mode == "evaluation-period":
        scheduler.schedule_for_evaluation_period(
            total_days=args.days,
            runs_per_12_hours=args.runs_per_12h
        )
    
    # Start the scheduler
    scheduler.start_scheduler()


if __name__ == "__main__":
    main() 