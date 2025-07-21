#!/usr/bin/env python3
"""
Real-Time Dashboard for Real-World LLM Usage Simulator

Shows live statistics, current phase, and progress.
"""

import os
import sys
import time
import subprocess
from datetime import datetime, timedelta
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def get_simulator_status():
    """Check if simulator is running and get basic info"""
    try:
        result = subprocess.run(['pgrep', '-f', 'real_world_simulator.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            pid = result.stdout.strip()
            return {"running": True, "pid": pid}
        else:
            return {"running": False, "pid": None}
    except Exception:
        return {"running": False, "pid": None}

def parse_log_file():
    """Parse the simulator log file for current status"""
    log_file = "automation/real_world_simulator.log"
    
    if not os.path.exists(log_file):
        return None
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Parse log for current phase, cycle, and stats
        current_phase = "unknown"
        cycle_count = 0
        total_evaluations = 0
        successful_evaluations = 0
        failed_evaluations = 0
        last_evaluation_time = None
        phase_start_time = None
        
        for line in reversed(lines):  # Start from most recent
            if "Starting INTENSIVE phase" in line:
                current_phase = "intensive"
                if not phase_start_time:
                    # Extract timestamp
                    timestamp_str = line.split(' - ')[0]
                    try:
                        phase_start_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                    except:
                        pass
                # Extract cycle number
                if "[CYCLE" in line:
                    try:
                        cycle_part = line.split("[CYCLE ")[1].split("]")[0]
                        cycle_count = int(cycle_part)
                    except:
                        pass
                break
            elif "Switching to REST phase" in line:
                current_phase = "rest"
                if not phase_start_time:
                    timestamp_str = line.split(' - ')[0]
                    try:
                        phase_start_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                    except:
                        pass
                break
        
        # Count evaluations
        for line in lines:
            if "Starting evaluation #" in line:
                total_evaluations += 1
            elif "completed successfully" in line:
                successful_evaluations += 1
            elif "failed" in line and "evaluation" in line:
                failed_evaluations += 1
        
        # Get last evaluation time
        for line in reversed(lines):
            if "Starting evaluation #" in line:
                timestamp_str = line.split(' - ')[0]
                try:
                    last_evaluation_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                except:
                    pass
                break
        
        return {
            "current_phase": current_phase,
            "cycle_count": cycle_count,
            "total_evaluations": total_evaluations,
            "successful_evaluations": successful_evaluations,
            "failed_evaluations": failed_evaluations,
            "last_evaluation_time": last_evaluation_time,
            "phase_start_time": phase_start_time
        }
        
    except Exception as e:
        return {"error": str(e)}

def calculate_phase_progress(phase_start_time, current_phase):
    """Calculate progress within current phase"""
    if not phase_start_time:
        return 0, timedelta(0), timedelta(0)
    
    now = datetime.now()
    elapsed = now - phase_start_time
    
    if current_phase == "intensive":
        total_duration = timedelta(hours=3)
    else:  # rest
        total_duration = timedelta(minutes=10)
    
    remaining = total_duration - elapsed
    if remaining.total_seconds() < 0:
        remaining = timedelta(0)
    
    progress = min(100, (elapsed.total_seconds() / total_duration.total_seconds()) * 100)
    
    return progress, elapsed, remaining

def format_timedelta(td):
    """Format timedelta for display"""
    if td.total_seconds() < 0:
        return "0:00:00"
    
    hours, remainder = divmod(int(td.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}"

def create_progress_bar(progress, width=40):
    """Create a text progress bar"""
    filled = int(width * progress / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {progress:.1f}%"

def display_dashboard():
    """Display the main dashboard"""
    while True:
        clear_screen()
        
        print("🌍 REAL-WORLD LLM USAGE SIMULATOR DASHBOARD")
        print("=" * 60)
        print(f"🕐 Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check if simulator is running
        status = get_simulator_status()
        
        if not status["running"]:
            print("❌ SIMULATOR NOT RUNNING")
            print()
            print("Start with: automation/run_real_world_sim.sh start")
            print("Press Ctrl+C to exit dashboard")
            time.sleep(5)
            continue
        
        print(f"✅ SIMULATOR RUNNING (PID: {status['pid']})")
        print()
        
        # Parse log file for detailed status
        log_status = parse_log_file()
        
        if log_status and "error" not in log_status:
            # Current Phase
            phase = log_status["current_phase"].upper()
            if phase == "INTENSIVE":
                phase_emoji = "⚡"
                phase_color = "\033[92m"  # Green
            else:
                phase_emoji = "😴"
                phase_color = "\033[94m"  # Blue
            
            print(f"{phase_emoji} CURRENT PHASE: {phase_color}{phase}\033[0m")
            
            # Phase Progress
            if log_status["phase_start_time"]:
                progress, elapsed, remaining = calculate_phase_progress(
                    log_status["phase_start_time"], 
                    log_status["current_phase"]
                )
                
                print(f"📊 Progress: {create_progress_bar(progress)}")
                print(f"⏱️  Elapsed: {format_timedelta(elapsed)}")
                print(f"⏳ Remaining: {format_timedelta(remaining)}")
            
            print()
            
            # Cycle Information
            print(f"🔄 CYCLE: {log_status['cycle_count']}")
            
            # Statistics
            total = log_status["total_evaluations"]
            success = log_status["successful_evaluations"]
            failed = log_status["failed_evaluations"]
            success_rate = (success / total * 100) if total > 0 else 0
            
            print(f"📈 STATISTICS:")
            print(f"   Total Evaluations: {total}")
            print(f"   ✅ Successful: {success}")
            print(f"   ❌ Failed: {failed}")
            print(f"   🎯 Success Rate: {success_rate:.1f}%")
            
            # Last Evaluation
            if log_status["last_evaluation_time"]:
                last_eval_ago = datetime.now() - log_status["last_evaluation_time"]
                print(f"   🕐 Last Evaluation: {format_timedelta(last_eval_ago)} ago")
            
            print()
            
            # Next Action
            if log_status["current_phase"] == "intensive":
                print("🔜 NEXT: Evaluation in ~1 minute")
            else:
                if remaining.total_seconds() > 0:
                    print(f"🔜 NEXT: Intensive phase in {format_timedelta(remaining)}")
                else:
                    print("🔜 NEXT: Starting intensive phase...")
            
        else:
            print("⚠️  Could not parse log file")
            if log_status and "error" in log_status:
                print(f"Error: {log_status['error']}")
        
        print()
        print("─" * 60)
        print("📋 Commands:")
        print("   automation/run_real_world_sim.sh status")
        print("   automation/run_real_world_sim.sh logs")
        print("   automation/run_real_world_sim.sh stop")
        print()
        print("Press Ctrl+C to exit dashboard")
        
        # Wait 10 seconds before refresh
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            print("\n👋 Dashboard closed")
            break

if __name__ == "__main__":
    try:
        display_dashboard()
    except KeyboardInterrupt:
        print("\n�� Dashboard closed") 