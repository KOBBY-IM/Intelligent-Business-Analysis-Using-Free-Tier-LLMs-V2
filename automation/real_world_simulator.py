#!/usr/bin/env python3
"""
Real-World Usage Simulator for LLM Evaluation

Simulates realistic API usage patterns:
- Intensive period: API calls every minute for 3 hours  
- Rest period: 10 minutes break
- Repeat cycle continuously
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Optional
import signal
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class RealWorldSimulator:
    """Real-world usage pattern simulator for batch evaluator"""
    
    def __init__(self, 
                 evaluation_script: str = "batch_evaluator.py",
                 log_file: str = "automation/real_world_simulator.log",
                 max_runtime_minutes: int = 10,
                 intensive_duration_hours: int = 3,
                 rest_duration_minutes: int = 10):
        """
        Initialize the real-world simulator
        
        Args:
            evaluation_script: Path to the batch evaluator script
            log_file: Path to log file
            max_runtime_minutes: Maximum runtime for each evaluation
            intensive_duration_hours: Hours of intensive usage (default: 3)
            rest_duration_minutes: Minutes of rest period (default: 10)
        """
        self.evaluation_script = evaluation_script
        self.log_file = log_file
        self.max_runtime_minutes = max_runtime_minutes
        self.intensive_duration = timedelta(hours=intensive_duration_hours)
        self.rest_duration = timedelta(minutes=rest_duration_minutes)
        self.running = True
        self.execution_count = 0
        self.cycle_count = 0
        self.current_phase = "intensive"  # "intensive" or "rest"
        self.phase_start_time = None
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
        
        self.logger.info(f"🚀 [CYCLE {self.cycle_count}] Starting evaluation #{self.execution_count} ({self.current_phase} phase)")
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
                self.logger.info(f"✅ Evaluation #{self.execution_count} completed successfully")
                self.logger.info(f"Duration: {duration}")
                
                # Log key output lines
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if any(keyword in line for keyword in ['Uploaded', 'records saved', 'Success:', 'Error']):
                        self.logger.info(f"   {line}")
                        
            else:
                self.logger.error(f"❌ Evaluation #{self.execution_count} failed")
                self.logger.error(f"Return code: {result.returncode}")
                self.logger.error(f"STDERR: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"⏰ Evaluation #{self.execution_count} timed out after {self.max_runtime_minutes} minutes")
        except Exception as e:
            self.logger.error(f"💥 Evaluation #{self.execution_count} crashed: {str(e)}")
    
    def should_switch_phase(self):
        """Check if it's time to switch phases"""
        if not self.phase_start_time:
            return False
            
        elapsed = datetime.now() - self.phase_start_time
        
        if self.current_phase == "intensive":
            return elapsed >= self.intensive_duration
        else:  # rest phase
            return elapsed >= self.rest_duration
    
    def switch_phase(self):
        """Switch between intensive and rest phases"""
        if self.current_phase == "intensive":
            self.current_phase = "rest"
            self.logger.info(f"🛌 [CYCLE {self.cycle_count}] Switching to REST phase for {self.rest_duration}")
        else:
            self.current_phase = "intensive"
            self.cycle_count += 1
            self.logger.info(f"⚡ [CYCLE {self.cycle_count}] Switching to INTENSIVE phase for {self.intensive_duration}")
        
        self.phase_start_time = datetime.now()
    
    def get_next_run_time(self):
        """Calculate when the next evaluation should run"""
        if self.current_phase == "intensive":
            return datetime.now() + timedelta(minutes=1)  # Every minute during intensive
        else:
            # During rest, return when the next intensive phase starts
            time_until_next_phase = self.rest_duration - (datetime.now() - self.phase_start_time)
            return datetime.now() + time_until_next_phase
    
    def start_simulator(self):
        """Start the real-world simulation"""
        self.logger.info("🌍 Starting Real-World Usage Simulator...")
        self.logger.info(f"📋 Configuration:")
        self.logger.info(f"   Intensive phase: {self.intensive_duration} (every 1 minute)")
        self.logger.info(f"   Rest phase: {self.rest_duration}")
        self.logger.info(f"   Log file: {os.path.abspath(self.log_file)}")
        
        # Start with intensive phase
        self.current_phase = "intensive"
        self.cycle_count = 1
        self.phase_start_time = datetime.now()
        self.logger.info(f"⚡ [CYCLE {self.cycle_count}] Starting INTENSIVE phase for {self.intensive_duration}")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            while self.running:
                # Check if we should switch phases
                if self.should_switch_phase():
                    self.switch_phase()
                
                # Run evaluation if in intensive phase
                if self.current_phase == "intensive":
                    self.run_batch_evaluation()
                    
                    # Wait 1 minute before next evaluation
                    self.logger.info(f"⏳ Waiting 60 seconds until next evaluation...")
                    for i in range(60):
                        if not self.running:
                            break
                        time.sleep(1)
                else:
                    # In rest phase, just wait and check periodically
                    time_until_next_phase = self.rest_duration - (datetime.now() - self.phase_start_time)
                    if time_until_next_phase.total_seconds() > 0:
                        wait_seconds = min(30, time_until_next_phase.total_seconds())  # Check every 30 seconds max
                        self.logger.info(f"😴 Rest phase - {time_until_next_phase} remaining...")
                        time.sleep(wait_seconds)
                
        except KeyboardInterrupt:
            self.logger.info("⚠️ Received keyboard interrupt")
        finally:
            self.stop_simulator()
    
    def stop_simulator(self):
        """Stop the simulator"""
        self.running = False
        self.logger.info("🛑 Real-World Simulator stopped")
        self.logger.info(f"📊 Final Statistics:")
        self.logger.info(f"   Total cycles: {self.cycle_count}")
        self.logger.info(f"   Total evaluations: {self.execution_count}")
        self.logger.info(f"   Current phase: {self.current_phase}")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        self.logger.info(f"📡 Received signal {signum}")
        self.stop_simulator()
    
    def get_status(self):
        """Get current simulator status"""
        phase_elapsed = datetime.now() - self.phase_start_time if self.phase_start_time else timedelta(0)
        
        if self.current_phase == "intensive":
            phase_remaining = self.intensive_duration - phase_elapsed
        else:
            phase_remaining = self.rest_duration - phase_elapsed
        
        return {
            "running": self.running,
            "execution_count": self.execution_count,
            "cycle_count": self.cycle_count,
            "current_phase": self.current_phase,
            "phase_elapsed": str(phase_elapsed),
            "phase_remaining": str(phase_remaining),
            "next_evaluation": "1 minute" if self.current_phase == "intensive" else str(phase_remaining)
        }


def main():
    """Main function with CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Real-World LLM Usage Simulator")
    parser.add_argument("--intensive-hours", type=int, default=3, 
                       help="Hours of intensive usage (default: 3)")
    parser.add_argument("--rest-minutes", type=int, default=10, 
                       help="Minutes of rest period (default: 10)")
    parser.add_argument("--max-runtime", type=int, default=10, 
                       help="Maximum runtime per evaluation (minutes)")
    parser.add_argument("--test", action="store_true", 
                       help="Test mode: 30 seconds intensive, 10 seconds rest")
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 Running in TEST mode (30s intensive, 10s rest)")
        # For testing: 30 seconds intensive, 10 seconds rest
        simulator = RealWorldSimulator(
            intensive_duration_hours=30/3600,  # 30 seconds
            rest_duration_minutes=10/60,       # 10 seconds
            max_runtime_minutes=args.max_runtime
        )
    else:
        # Normal mode
        simulator = RealWorldSimulator(
            intensive_duration_hours=args.intensive_hours,
            rest_duration_minutes=args.rest_minutes,
            max_runtime_minutes=args.max_runtime
        )
    
    # Start the simulator
    simulator.start_simulator()


if __name__ == "__main__":
    main() 