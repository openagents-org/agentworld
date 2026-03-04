#!/bin/bash

# Gemini Benchmark Runner
# Tasks 1-100 across 6 parallel screens
# Model: gemini-3-flash-preview
# Game Server: port 7041

OUTPUT_DIR="agents/logs/gemini_v1.3"
AGENT_CONFIG="agents/configs/gemini_agent.yaml"
TASK_DIR="data_v0.1_multi/v1.3_benchmark"

mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo "Gemini Benchmark Runner (gemini-3-flash-preview)"
echo "Tasks 1-100 across 6 screens"
echo "Game Server: http://localhost:7041"
echo "=============================================="

# Screen distribution (100 tasks / 6 screens):
# Screen 1: tasks 1-17   (17 tasks)
# Screen 2: tasks 18-34  (17 tasks)
# Screen 3: tasks 35-50  (16 tasks)
# Screen 4: tasks 51-67  (17 tasks)
# Screen 5: tasks 68-84  (17 tasks)
# Screen 6: tasks 85-100 (16 tasks)

run_screen() {
    local screen_num=$1
    local start=$2
    local end=$3
    local log_file="$OUTPUT_DIR/screen_${screen_num}.log"

    # Build task list
    task_list=""
    for i in $(seq $start $end); do
        task_list="$task_list $i"
    done

    echo "Starting gemini_s${screen_num}: tasks ${start}-${end}"

    screen -dmS "gemini_s${screen_num}" bash -c '
        cd /home/ubuntu/works/agentworld
        LOG_FILE="'"$log_file"'"
        AGENT_CONFIG="'"$AGENT_CONFIG"'"
        OUTPUT_DIR="'"$OUTPUT_DIR"'"
        TASK_DIR="'"$TASK_DIR"'"

        echo "===============================================" >> "$LOG_FILE"
        echo "Screen '"$screen_num"' started at $(date)" >> "$LOG_FILE"
        echo "Tasks: '"$start"'-'"$end"'" >> "$LOG_FILE"
        echo "===============================================" >> "$LOG_FILE"

        for i in '"$task_list"'; do
            TASK_NUM=$(printf "%02d" $i)
            TASK_FILE=$(ls "$TASK_DIR"/task_${TASK_NUM}_*.yaml 2>/dev/null | head -1)

            if [ -n "$TASK_FILE" ]; then
                echo "" >> "$LOG_FILE"
                echo ">>> Starting Task $TASK_NUM at $(date)" >> "$LOG_FILE"
                echo ">>> Task file: $TASK_FILE" >> "$LOG_FILE"

                python agents/run.py \
                    --task "$TASK_FILE" \
                    --agent "$AGENT_CONFIG" \
                    --output "$OUTPUT_DIR" \
                    --no-split-screen 2>&1 | tee -a "$LOG_FILE"

                echo ">>> Task $TASK_NUM completed with exit code $? at $(date)" >> "$LOG_FILE"
            else
                echo ">>> Skipping Task $TASK_NUM - file not found" >> "$LOG_FILE"
            fi
        done

        echo "===============================================" >> "$LOG_FILE"
        echo "Screen '"$screen_num"' completed all tasks at $(date)" >> "$LOG_FILE"
        echo "===============================================" >> "$LOG_FILE"
    '
}

run_screen 1 1 17
sleep 3
run_screen 2 18 34
sleep 3
run_screen 3 35 50
sleep 3
run_screen 4 51 67
sleep 3
run_screen 5 68 84
sleep 3
run_screen 6 85 100

echo ""
echo "=============================================="
echo "All 6 screens launched!"
echo "  gemini_s1: tasks 1-17"
echo "  gemini_s2: tasks 18-34"
echo "  gemini_s3: tasks 35-50"
echo "  gemini_s4: tasks 51-67"
echo "  gemini_s5: tasks 68-84"
echo "  gemini_s6: tasks 85-100"
echo "Monitor: screen -ls | grep gemini_s"
echo "Logs: $OUTPUT_DIR"
echo "Started at: $(date)"
echo "=============================================="
