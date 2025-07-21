#!/bin/bash
#
# Real-World Usage Simulator Runner
#
# Easy-to-use script for running realistic LLM usage patterns
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$PROJECT_DIR/venv"

echo -e "${PURPLE}🌍 Real-World LLM Usage Simulator${NC}"
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
    echo "  $0 start             - Start real-world simulation (3h intensive, 10min rest)"
    echo "  $0 test              - Quick test (30s intensive, 10s rest)"
    echo "  $0 custom [hours] [minutes]  - Custom intensive/rest periods"
    echo "  $0 status            - Check current simulation status"
    echo "  $0 logs              - View simulation logs"
    echo "  $0 stop              - Stop simulation"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 start                    # Standard simulation"
    echo "  $0 test                     # Quick test"
    echo "  $0 custom 2 5               # 2h intensive, 5min rest"
    echo "  $0 status                   # Check what's running"
}

# Function to check if simulator is running
check_running() {
    if pgrep -f "real_world_simulator.py" > /dev/null; then
        return 0  # Running
    else
        return 1  # Not running
    fi
}

# Parse command line arguments
case "${1:-help}" in
    "start")
        if check_running; then
            echo -e "${YELLOW}⚠️ Simulator already running. Stop it first with: $0 stop${NC}"
            exit 1
        fi
        echo -e "${GREEN}🚀 Starting Real-World Usage Simulation...${NC}"
        echo -e "${BLUE}📋 Pattern: 3 hours intensive (every 1 minute) → 10 minutes rest → repeat${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        python "$PROJECT_DIR/automation/real_world_simulator.py"
        ;;
    
    "test")
        if check_running; then
            echo -e "${YELLOW}⚠️ Simulator already running. Stop it first with: $0 stop${NC}"
            exit 1
        fi
        echo -e "${GREEN}🧪 Starting Test Simulation...${NC}"
        echo -e "${BLUE}📋 Pattern: 30 seconds intensive → 10 seconds rest → repeat${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        python "$PROJECT_DIR/automation/real_world_simulator.py" --test
        ;;
    
    "custom")
        if check_running; then
            echo -e "${YELLOW}⚠️ Simulator already running. Stop it first with: $0 stop${NC}"
            exit 1
        fi
        HOURS=${2:-3}
        MINUTES=${3:-10}
        echo -e "${GREEN}🔧 Starting Custom Simulation...${NC}"
        echo -e "${BLUE}📋 Pattern: ${HOURS} hours intensive → ${MINUTES} minutes rest → repeat${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
        python "$PROJECT_DIR/automation/real_world_simulator.py" --intensive-hours "$HOURS" --rest-minutes "$MINUTES"
        ;;
    
    "status")
        if check_running; then
            echo -e "${GREEN}✅ Real-World Simulator is running${NC}"
            PID=$(pgrep -f "real_world_simulator.py")
            echo -e "${BLUE}Process ID: $PID${NC}"
            
            # Show recent log entries
            if [ -f "$PROJECT_DIR/automation/real_world_simulator.log" ]; then
                echo -e "\n${BLUE}📋 Recent Activity:${NC}"
                tail -5 "$PROJECT_DIR/automation/real_world_simulator.log" | while read line; do
                    if [[ $line == *"✅"* ]]; then
                        echo -e "${GREEN}$line${NC}"
                    elif [[ $line == *"❌"* ]] || [[ $line == *"ERROR"* ]]; then
                        echo -e "${RED}$line${NC}"
                    elif [[ $line == *"⏳"* ]] || [[ $line == *"😴"* ]]; then
                        echo -e "${YELLOW}$line${NC}"
                    else
                        echo "$line"
                    fi
                done
            fi
        else
            echo -e "${RED}❌ Real-World Simulator is not running${NC}"
        fi
        ;;
    
    "logs")
        if [ -f "$PROJECT_DIR/automation/real_world_simulator.log" ]; then
            echo -e "${BLUE}📋 Real-World Simulator Logs:${NC}"
            tail -20 "$PROJECT_DIR/automation/real_world_simulator.log" | while read line; do
                if [[ $line == *"✅"* ]]; then
                    echo -e "${GREEN}$line${NC}"
                elif [[ $line == *"❌"* ]] || [[ $line == *"ERROR"* ]]; then
                    echo -e "${RED}$line${NC}"
                elif [[ $line == *"⏳"* ]] || [[ $line == *"😴"* ]]; then
                    echo -e "${YELLOW}$line${NC}"
                elif [[ $line == *"⚡"* ]] || [[ $line == *"🛌"* ]]; then
                    echo -e "${PURPLE}$line${NC}"
                else
                    echo "$line"
                fi
            done
        else
            echo -e "${RED}❌ No log file found${NC}"
        fi
        ;;
    
    "stop")
        if check_running; then
            echo -e "${YELLOW}🛑 Stopping Real-World Simulator...${NC}"
            pkill -f "real_world_simulator.py"
            sleep 2
            if check_running; then
                echo -e "${RED}❌ Failed to stop simulator gracefully. Force killing...${NC}"
                pkill -9 -f "real_world_simulator.py"
            else
                echo -e "${GREEN}✅ Simulator stopped successfully${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️ Simulator is not running${NC}"
        fi
        ;;
    
    "help"|*)
        show_usage
        ;;
esac 