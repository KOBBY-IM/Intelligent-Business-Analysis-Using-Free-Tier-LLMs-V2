#!/bin/bash
#
# Local Batch Evaluator Scheduler Runner
#
# Easy-to-use scripts for running automated batch evaluations locally.
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$PROJECT_DIR/venv"

echo -e "${BLUE}🚀 Local Batch Evaluator Scheduler${NC}"
echo "Project directory: $PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Virtual environment not found at $VENV_PATH${NC}"
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Function to show usage
show_usage() {
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 test              - Run immediate test"
    echo "  $0 hourly [hours]    - Run every N hours (default: 2)"
    echo "  $0 evaluation        - Run evaluation period (14×/12h for 4 days)"
    echo "  $0 custom [minutes]  - Run every N minutes"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 test                    # Test run"
    echo "  $0 hourly 1                # Every hour"
    echo "  $0 evaluation              # Research evaluation schedule"
    echo "  $0 custom 30               # Every 30 minutes"
}

# Parse command line arguments
case "${1:-help}" in
    "test")
        echo -e "${GREEN}🧪 Running immediate test evaluation...${NC}"
        python "$PROJECT_DIR/automation/local_scheduler.py" --mode test
        ;;
    
    "hourly")
        HOURS=${2:-2}
        echo -e "${GREEN}⏰ Scheduling to run every $HOURS hours...${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        python "$PROJECT_DIR/automation/local_scheduler.py" --mode hourly --hours "$HOURS"
        ;;
    
    "evaluation")
        echo -e "${GREEN}📊 Starting evaluation period (14 runs per 12 hours for 4 days)...${NC}"
        echo -e "${YELLOW}This will run for 4 days. Press Ctrl+C to stop early.${NC}"
        python "$PROJECT_DIR/automation/local_scheduler.py" --mode evaluation-period
        ;;
    
    "custom")
        MINUTES=${2:-60}
        echo -e "${GREEN}🔄 Scheduling to run every $MINUTES minutes...${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        python -c "
import sys
sys.path.insert(0, '$PROJECT_DIR')
from automation.local_scheduler import LocalBatchScheduler
scheduler = LocalBatchScheduler()
scheduler.schedule_every_n_minutes($MINUTES)
scheduler.start_scheduler()
"
        ;;
    
    "help"|*)
        show_usage
        ;;
esac 