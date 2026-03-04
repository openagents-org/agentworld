#!/bin/bash

# DeepSeek Benchmark Runner
# Runs tasks 1-45 and 75-100 using DeepSeek model
# Connects to game server 2 (port 7041)

OUTPUT_DIR="agents/logs/deepseek_v1.3"
AGENT_CONFIG="agents/configs/deepseek_agent.yaml"
TASK_DIR="data_v0.1_multi/v1.3_benchmark"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo "DeepSeek Benchmark Runner"
echo "Output: $OUTPUT_DIR"
echo "Agent Config: $AGENT_CONFIG"
echo "Game Server: http://localhost:7041"
echo "=============================================="

# Function to run tasks in a screen
run_screen() {
    local screen_name=$1
    local start_task=$2
    local end_task=$3
    local log_file="$OUTPUT_DIR/screen_${screen_name}.log"

    echo "Starting screen $screen_name: tasks $start_task to $end_task"

    screen -dmS "deepseek_s${screen_name}" bash -c '
        cd /home/ubuntu/works/agentworld
        LOG_FILE="'"$log_file"'"

        echo "===============================================" >> "$LOG_FILE"
        echo "Screen '"$screen_name"' started at $(date)" >> "$LOG_FILE"
        echo "Tasks: '"$start_task"' to '"$end_task"'" >> "$LOG_FILE"
        echo "===============================================" >> "$LOG_FILE"

        for i in $(seq '"$start_task"' '"$end_task"'); do
            TASK_NUM=$(printf "%02d" $i)
            TASK_FILE=$(ls '"$TASK_DIR"'/task_${TASK_NUM}_*.yaml 2>/dev/null | head -1)

            if [ -n "$TASK_FILE" ]; then
                echo "" >> "$LOG_FILE"
                echo ">>> Starting Task $TASK_NUM at $(date)" >> "$LOG_FILE"
                echo ">>> Task file: $TASK_FILE" >> "$LOG_FILE"

                python agents/run.py \
                    --task "$TASK_FILE" \
                    --agent '"$AGENT_CONFIG"' \
                    --output '"$OUTPUT_DIR"' \
                    --no-split-screen 2>&1 | tee -a "$LOG_FILE"

                echo ">>> Task $TASK_NUM completed with exit code $? at $(date)" >> "$LOG_FILE"
            else
                echo ">>> Skipping Task $TASK_NUM - file not found" >> "$LOG_FILE"
            fi
        done

        echo "===============================================" >> "$LOG_FILE"
        echo "Screen '"$screen_name"' completed all tasks at $(date)" >> "$LOG_FILE"
        echo "===============================================" >> "$LOG_FILE"
    '
}

# Launch 6 screens with task distributions:
# Screen 1: tasks 01-12 (12 tasks)
# Screen 2: tasks 13-24 (12 tasks)
# Screen 3: tasks 25-36 (12 tasks)
# Screen 4: tasks 37-45 (9 tasks)
# Screen 5: tasks 75-87 (13 tasks)
# Screen 6: tasks 88-100 (13 tasks)

run_screen 1 1 12
sleep 3
run_screen 2 13 24
sleep 3
run_screen 3 25 36
sleep 3
run_screen 4 37 45
sleep 3
run_screen 5 75 87
sleep 3
run_screen 6 88 100

echo ""
echo "=============================================="
echo "All 6 screens launched!"
echo "Monitor progress with: screen -ls"
echo "View logs in: $OUTPUT_DIR"
echo "Started at: $(date)"
echo "=============================================="
