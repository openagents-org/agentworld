#!/bin/bash

# DeepSeek R1-70B - Augmented Benchmark (v2 tasks only)
# 2 parallel screens, 50 tasks each

OUTPUT_DIR="agents/logs/deepseek_augmented"
AGENT_CONFIG="agents/configs/deepseek_agent.yaml"
TASK_DIR="data_v0.1_multi/v1.3_augmented"

mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo "DeepSeek R1-70B - Augmented Benchmark (v2)"
echo "Output: $OUTPUT_DIR"
echo "Agent Config: $AGENT_CONFIG"
echo "Screen 1: tasks 1-50"
echo "Screen 2: tasks 51-100"
echo "=============================================="

run_screen() {
    local screen_name=$1
    local start_task=$2
    local end_task=$3
    local log_file="$OUTPUT_DIR/screen_${screen_name}.log"

    echo "Starting screen $screen_name: tasks $start_task to $end_task"

    screen -dmS "deepseek_aug_s${screen_name}" bash -c '
        cd /home/ubuntu/works/agentworld
        LOG_FILE="'"$log_file"'"

        echo "===============================================" >> "$LOG_FILE"
        echo "Screen '"$screen_name"' started at $(date)" >> "$LOG_FILE"
        echo "Tasks: '"$start_task"' to '"$end_task"'" >> "$LOG_FILE"
        echo "===============================================" >> "$LOG_FILE"

        for i in $(seq '"$start_task"' '"$end_task"'); do
            TASK_NUM=$(printf "%02d" $i)
            TASK_FILE=$(ls '"$TASK_DIR"'/task_${TASK_NUM}_*_v2.yaml 2>/dev/null | head -1)

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
                echo ">>> Skipping Task $TASK_NUM - v2 file not found" >> "$LOG_FILE"
            fi
        done

        echo "===============================================" >> "$LOG_FILE"
        echo "Screen '"$screen_name"' completed all tasks at $(date)" >> "$LOG_FILE"
        echo "===============================================" >> "$LOG_FILE"
    '
}

run_screen 1 1 50
sleep 5
run_screen 2 51 100

echo ""
echo "=============================================="
echo "Both screens launched!"
echo "Monitor: screen -ls"
echo "Logs: $OUTPUT_DIR"
echo "Started at: $(date)"
echo "=============================================="
