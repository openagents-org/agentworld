#!/bin/bash

# Claude 4.5 Haiku Rerun - Failed Tasks Only
# 2 parallel screens to avoid rate limiting

OUTPUT_DIR="agents/logs/claude_haiku45_rerun"
AGENT_CONFIG="agents/configs/claude_haiku_45_agent.yaml"
TASK_DIR="data_v0.1_multi/v1.3_benchmark"

# Failed tasks split into 2 groups (~32 each)
SCREEN1_TASKS=(2 4 6 7 9 11 12 15 17 18 20 21 22 23 25 30 32 33 34 36 38 42 44 45 46 47 49 52 54 55 56 57)
SCREEN2_TASKS=(58 59 60 61 62 63 65 66 68 69 71 72 73 74 75 78 80 81 83 86 87 88 89 90 91 93 94 95 98 99 100)

mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo "Claude 4.5 Haiku Rerun - Failed Tasks"
echo "Output: $OUTPUT_DIR"
echo "Agent Config: $AGENT_CONFIG"
echo "Screen 1: ${#SCREEN1_TASKS[@]} tasks"
echo "Screen 2: ${#SCREEN2_TASKS[@]} tasks"
echo "=============================================="

run_tasks_screen() {
    local screen_name=$1
    shift
    local tasks=("$@")
    local log_file="$OUTPUT_DIR/screen_${screen_name}.log"

    echo "Starting screen $screen_name: ${#tasks[@]} tasks"

    local tasks_str="${tasks[*]}"

    screen -dmS "haiku45_rerun_s${screen_name}" bash -c '
        cd /home/ubuntu/works/agentworld
        LOG_FILE="'"$log_file"'"
        TASKS=('"$tasks_str"')

        echo "===============================================" >> "$LOG_FILE"
        echo "Screen '"$screen_name"' started at $(date)" >> "$LOG_FILE"
        echo "Tasks: ${TASKS[*]}" >> "$LOG_FILE"
        echo "===============================================" >> "$LOG_FILE"

        for i in "${TASKS[@]}"; do
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

run_tasks_screen 1 "${SCREEN1_TASKS[@]}"
sleep 5
run_tasks_screen 2 "${SCREEN2_TASKS[@]}"

echo ""
echo "=============================================="
echo "Both screens launched!"
echo "Monitor: screen -ls"
echo "Logs: $OUTPUT_DIR"
echo "Started at: $(date)"
echo "=============================================="
