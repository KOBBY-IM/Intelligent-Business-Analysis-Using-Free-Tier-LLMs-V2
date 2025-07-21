# Local Batch Evaluator Automation

This directory contains automation tools for running batch LLM evaluations locally with automatic GCS upload.

## 🚀 Quick Start

### 1. **Test Run (Immediate)**
```bash
# Run a single evaluation immediately
automation/run_scheduler.sh test

# Or using Python directly
python automation/local_scheduler.py --mode test
```

### 2. **Hourly Schedule**
```bash
# Run every 2 hours (default)
automation/run_scheduler.sh hourly

# Run every hour
automation/run_scheduler.sh hourly 1

# Run every 6 hours
automation/run_scheduler.sh hourly 6
```

### 3. **Research Evaluation Schedule**
```bash
# 14 runs per 12 hours for 4 days (for research evaluation)
automation/run_scheduler.sh evaluation
```

### 4. **Custom Schedule**
```bash
# Run every 30 minutes
automation/run_scheduler.sh custom 30

# Run every 10 minutes (for testing)
automation/run_scheduler.sh custom 10
```

## 📊 Monitoring

### **Check Status**
```bash
# Full health check
python automation/monitor.py --status

# View recent logs
python automation/monitor.py --logs 20

# View statistics only
python automation/monitor.py --stats
```

### **What the Monitor Shows:**
- ✅ **Scheduler Process**: Whether automation is running
- 📁 **Local Files**: Last batch evaluation files
- 🔍 **GCS Status**: Cloud storage connectivity and latest uploads
- 📊 **Statistics**: Success rate, total runs, failures
- 📋 **Recent Logs**: Latest automation activity

## 📂 Files Generated

### **Log Files**
- `automation/batch_scheduler.log` - Main automation log
- `automation/batch_evaluator_service.log` - System service log (if using systemd)

### **Data Files**
- `data/batch_eval_metrics.json` - Latest evaluation results (JSON)
- `data/batch_eval_metrics.csv` - Latest evaluation results (CSV)

### **GCS Upload**
- `gs://your-bucket/batch_eval_metrics.json` - Cloud storage backup
- `gs://your-bucket/batch_eval_metrics.csv` - Cloud storage backup

## ⚙️ Configuration

### **Environment Variables**
The automation uses the same GCS credentials as the batch evaluator:
- Reads from `.streamlit/secrets.toml` automatically
- Creates temporary credential files as needed
- Uses `llm-eval-data-2025` bucket (or configured bucket)

### **Scheduling Options**

| Mode | Description | Use Case |
|------|-------------|----------|
| `test` | Single immediate run | Testing, debugging |
| `hourly` | Every N hours | Regular monitoring |
| `evaluation` | 14×/12h for 4 days | Research evaluation |
| `custom` | Every N minutes | Custom intervals |

## 🔧 Advanced Usage

### **Running as Background Service**

#### **Using nohup (Simple)**
```bash
# Run in background
nohup automation/run_scheduler.sh hourly 2 > automation/scheduler.out 2>&1 &

# Check if running
ps aux | grep local_scheduler

# Stop
pkill -f local_scheduler.py
```

#### **Using systemd (Linux)**
```bash
# Copy service file
sudo cp automation/batch-evaluator.service /etc/systemd/system/

# Edit paths in service file if needed
sudo nano /etc/systemd/system/batch-evaluator.service

# Enable and start
sudo systemctl enable batch-evaluator
sudo systemctl start batch-evaluator

# Check status
sudo systemctl status batch-evaluator

# View logs
sudo journalctl -u batch-evaluator -f
```

### **Python API Usage**
```python
from automation.local_scheduler import LocalBatchScheduler

# Create scheduler
scheduler = LocalBatchScheduler(max_runtime_minutes=30)

# Different scheduling options
scheduler.schedule_every_n_minutes(30)
scheduler.schedule_every_n_hours(2)
scheduler.schedule_daily_at("09:00")
scheduler.schedule_for_evaluation_period(days=4, runs_per_12_hours=14)

# Start (blocks until stopped)
scheduler.start_scheduler()
```

### **Monitoring API**
```python
from automation.monitor import BatchEvaluatorMonitor

monitor = BatchEvaluatorMonitor()
monitor.full_status_report()
monitor.get_evaluation_stats()
monitor.view_recent_logs(50)
```

## 🚨 Troubleshooting

### **Common Issues**

#### **"GCS credentials not set"**
- Check `.streamlit/secrets.toml` has `[gcs]` section with `service_account`
- Verify service account JSON is valid
- Run `python automation/monitor.py --status` to check GCS connectivity

#### **"Scheduler not running"**
- Process may have stopped due to error
- Check logs: `python automation/monitor.py --logs 50`
- Restart: `automation/run_scheduler.sh hourly`

#### **"Permission denied"**
```bash
chmod +x automation/run_scheduler.sh
```

#### **"Virtual environment not found"**
- Ensure you're in the project root directory
- Check `venv/` directory exists
- Recreate venv if needed

#### **High failure rate**
- Check API rate limits (LLM providers)
- Verify internet connectivity
- Check if datasets are accessible
- Review error logs for specific issues

### **Performance Tuning**

#### **Reduce API Pressure**
- Increase interval between runs
- Reduce number of questions per evaluation
- Add delays between LLM calls

#### **Improve Reliability**
- Increase `max_runtime_minutes` for slow networks
- Add retry logic for network failures
- Monitor resource usage

### **Logs Analysis**
```bash
# Find errors
grep -i error automation/batch_scheduler.log

# Success rate over time
grep "completed successfully" automation/batch_scheduler.log | wc -l

# Failed runs
grep "failed" automation/batch_scheduler.log

# Recent upload confirmations
grep "Uploaded.*to gs://" automation/batch_scheduler.log | tail -10
```

## 📈 Example Output

### **Successful Run**
```
2025-07-21 10:58:24,712 - INFO - 🚀 Starting batch evaluation #1
2025-07-21 11:00:46,107 - INFO - ✅ Batch evaluation #1 completed successfully
2025-07-21 11:00:46,107 - INFO - Duration: 0:02:21.394976
2025-07-21 11:00:46,110 - INFO -    Uploaded data/batch_eval_metrics.json to gs://llm-eval-data-2025/batch_eval_metrics.json
2025-07-21 11:00:46,110 - INFO -    Uploaded data/batch_eval_metrics.csv to gs://llm-eval-data-2025/batch_eval_metrics.csv
2025-07-21 11:00:46,111 - INFO -    Batch evaluation complete. 20 records saved.
```

### **Monitor Status**
```
🏥 Batch Evaluator Health Check
==================================================
✅ Scheduler running (PIDs: 12345)
✅ JSON: 11023 bytes, modified: 2025-07-21 11:00:41
✅ CSV: 4390 bytes, modified: 2025-07-21 11:00:41
✅ GCS bucket: llm-eval-data-2025
📊 Evaluation Statistics...
✅ Completed: 5
❌ Failed: 0
🎯 Success rate: 100.0%
```

## 🎯 Best Practices

1. **Start with test runs** to verify everything works
2. **Monitor logs regularly** to catch issues early
3. **Use appropriate intervals** to avoid rate limiting
4. **Keep credentials secure** and up to date
5. **Monitor GCS costs** if running frequently
6. **Set up alerts** for failed evaluations
7. **Back up important evaluation data**

## 🔗 Integration

The automation system integrates seamlessly with:
- **Streamlit Analysis Pages**: Real-time data display
- **GCS Storage**: Automatic cloud backup
- **Monitoring Tools**: Health checks and alerts
- **Manual Runs**: Can be combined with manual evaluations 