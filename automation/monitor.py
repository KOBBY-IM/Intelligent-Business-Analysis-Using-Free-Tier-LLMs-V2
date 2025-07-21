#!/usr/bin/env python3
"""
Batch Evaluator Monitor

Monitor the status of automated batch evaluations and view logs.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class BatchEvaluatorMonitor:
    """Monitor for batch evaluator automation"""
    
    def __init__(self):
        self.project_root = Path(os.path.dirname(os.path.dirname(__file__)))
        self.log_file = self.project_root / "automation" / "batch_scheduler.log"
        self.data_dir = self.project_root / "data"
        
    def check_gcs_status(self):
        """Check GCS upload status"""
        print("🔍 Checking GCS Status...")
        try:
            from google.cloud import storage
            from automation.local_scheduler import LocalBatchScheduler
            
            # Set up credentials like the scheduler does
            scheduler = LocalBatchScheduler()
            
            # Check environment variables
            gcp_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            gcs_bucket = os.environ.get('GCS_BUCKET', 'llm-evaluation-data')
            
            if not gcp_creds:
                print("⚠️  GOOGLE_APPLICATION_CREDENTIALS not set")
                return False
                
            # Test GCS connection
            client = storage.Client()
            bucket = client.bucket(gcs_bucket)
            
            if not bucket.exists():
                print(f"❌ Bucket {gcs_bucket} does not exist")
                return False
                
            # Check for recent files
            json_blob = bucket.blob("batch_eval_metrics.json")
            csv_blob = bucket.blob("batch_eval_metrics.csv")
            
            if json_blob.exists() and csv_blob.exists():
                print(f"✅ GCS bucket: {gcs_bucket}")
                print(f"   JSON: {json_blob.size} bytes, updated: {json_blob.updated}")
                print(f"   CSV: {csv_blob.size} bytes, updated: {csv_blob.updated}")
                return True
            else:
                print(f"⚠️  Files missing in bucket {gcs_bucket}")
                return False
                
        except Exception as e:
            print(f"❌ GCS check failed: {e}")
            return False
    
    def check_local_files(self):
        """Check local data files"""
        print("\n📁 Checking Local Files...")
        
        json_file = self.data_dir / "batch_eval_metrics.json"
        csv_file = self.data_dir / "batch_eval_metrics.csv"
        
        if json_file.exists():
            size = json_file.stat().st_size
            modified = datetime.fromtimestamp(json_file.stat().st_mtime)
            print(f"✅ JSON: {size} bytes, modified: {modified}")
        else:
            print("❌ JSON file not found")
            
        if csv_file.exists():
            size = csv_file.stat().st_size
            modified = datetime.fromtimestamp(csv_file.stat().st_mtime)
            print(f"✅ CSV: {size} bytes, modified: {modified}")
        else:
            print("❌ CSV file not found")
    
    def view_recent_logs(self, lines: int = 20):
        """View recent log entries"""
        print(f"\n📋 Recent Log Entries (last {lines} lines)...")
        
        if not self.log_file.exists():
            print("❌ Log file not found")
            return
            
        try:
            with open(self.log_file, 'r') as f:
                log_lines = f.readlines()
                
            # Show last N lines
            recent_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines
            
            for line in recent_lines:
                line = line.strip()
                if line:
                    # Color code log levels
                    if "ERROR" in line:
                        print(f"\033[0;31m{line}\033[0m")  # Red
                    elif "WARNING" in line or "WARN" in line:
                        print(f"\033[0;33m{line}\033[0m")  # Yellow
                    elif "✅" in line or "SUCCESS" in line:
                        print(f"\033[0;32m{line}\033[0m")  # Green
                    else:
                        print(line)
                        
        except Exception as e:
            print(f"❌ Error reading log file: {e}")
    
    def get_evaluation_stats(self):
        """Get evaluation statistics from logs"""
        print("\n📊 Evaluation Statistics...")
        
        if not self.log_file.exists():
            print("❌ Log file not found")
            return
            
        try:
            with open(self.log_file, 'r') as f:
                log_content = f.read()
                
            # Count evaluations
            completed_count = log_content.count("completed successfully")
            failed_count = log_content.count("failed")
            timeout_count = log_content.count("timed out")
            
            print(f"✅ Completed: {completed_count}")
            print(f"❌ Failed: {failed_count}")
            print(f"⏰ Timeouts: {timeout_count}")
            print(f"📈 Total attempts: {completed_count + failed_count + timeout_count}")
            
            # Success rate
            total = completed_count + failed_count + timeout_count
            if total > 0:
                success_rate = (completed_count / total) * 100
                print(f"🎯 Success rate: {success_rate:.1f}%")
                
        except Exception as e:
            print(f"❌ Error analyzing logs: {e}")
    
    def check_scheduler_process(self):
        """Check if scheduler is running"""
        print("\n🔍 Checking Scheduler Process...")
        
        import subprocess
        try:
            result = subprocess.run(['pgrep', '-f', 'local_scheduler.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                print(f"✅ Scheduler running (PIDs: {', '.join(pids)})")
                return True
            else:
                print("❌ Scheduler not running")
                return False
                
        except Exception as e:
            print(f"⚠️  Could not check process: {e}")
            return False
    
    def full_status_report(self):
        """Generate a comprehensive status report"""
        print("🏥 Batch Evaluator Health Check")
        print("=" * 50)
        
        self.check_scheduler_process()
        self.check_local_files()
        self.check_gcs_status()
        self.get_evaluation_stats()
        self.view_recent_logs(10)


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch Evaluator Monitor")
    parser.add_argument("--logs", type=int, default=20, help="Number of log lines to show")
    parser.add_argument("--stats", action="store_true", help="Show evaluation statistics")
    parser.add_argument("--status", action="store_true", help="Full status report")
    
    args = parser.parse_args()
    
    monitor = BatchEvaluatorMonitor()
    
    if args.status:
        monitor.full_status_report()
    elif args.stats:
        monitor.get_evaluation_stats()
    else:
        monitor.view_recent_logs(args.logs)


if __name__ == "__main__":
    main() 