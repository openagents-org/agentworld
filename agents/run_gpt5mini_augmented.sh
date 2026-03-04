#!/bin/bash

# GPT-5-mini Augmented Dataset Benchmark Runner
# Runs all 200 augmented tasks across 6 parallel screens
# Connects to game server 2 (port 7041)

OUTPUT_DIR="agents/logs/gpt5mini_augmented"
AGENT_CONFIG="agents/configs/openai_agent.yaml"
TASK_DIR="data_v0.1_multi/v1.3_augmented"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "=============================================="
echo "GPT-5-mini Augmented Dataset Benchmark"
echo "Output: $OUTPUT_DIR"
echo "Agent Config: $AGENT_CONFIG"
echo "Total Tasks: 200 (100 tasks x 2 variants)"
echo "=============================================="

# Get all task files sorted
TASK_FILES=($(ls "$TASK_DIR"/*.yaml | sort -V))
TOTAL_FILES=${#TASK_FILES[@]}
FILES_PER_SCREEN=$((TOTAL_FILES / 6))

echo "Total files: $TOTAL_FILES"
echo "Files per screen: ~$FILES_PER_SCREEN"

# Function to run tasks in a screen
run_screen() {
    local screen_num=$1
    local start_idx=$2
    local end_idx=$3
    local log_file="$OUTPUT_DIR/screen_${screen_num}.log"

    echo "Starting screen $screen_num: files $start_idx to $end_idx"

    # Create a file list for this screen
    local file_list=""
    for ((i=start_idx; i<=end_idx && i<TOTAL_FILES; i++)); do
        file_list="$file_list ${TASK_FILES[$i]}"
    done

    screen -dmS "gpt5_aug_s${screen_num}" bash -c '
        cd /home/ubuntu/works/agentworld
        LOG_FILE="'"$log_file"'"

        echo "===============================================" >> "$LOG_FILE"
        echo "Screen '"$screen_num"' started at $(date)" >> "$LOG_FILE"
        echo "Files: '"$start_idx"' to '"$end_idx"'" >> "$LOG_FILE"
        echo "===============================================" >> "$LOG_FILE"

        for TASK_FILE in '"$file_list"'; do
            TASK_NAME=$(basename "$TASK_FILE" .yaml)

            echo "" >> "$LOG_FILE"
            echo ">>> Starting $TASK_NAME at $(date)" >> "$LOG_FILE"
            echo ">>> Task file: $TASK_FILE" >> "$LOG_FILE"

            python agents/run.py \
                --task "$TASK_FILE" \
                --agent '"$AGENT_CONFIG"' \
                --output '"$OUTPUT_DIR"' \
                --no-split-screen 2>&1 | tee -a "$LOG_FILE"

            echo ">>> $TASK_NAME completed with exit code $? at $(date)" >> "$LOG_FILE"
        done

        echo "===============================================" >> "$LOG_FILE"
        echo "Screen '"$screen_num"' completed all tasks at $(date)" >> "$LOG_FILE"
        echo "===============================================" >> "$LOG_FILE"
    '
}

# Launch 6 screens with ~33-34 tasks each
# Screen 1: files 0-33 (34 files)
# Screen 2: files 34-67 (34 files)
# Screen 3: files 68-100 (33 files)
# Screen 4: files 101-133 (33 files)
# Screen 5: files 134-166 (33 files)
# Screen 6: files 167-199 (33 files)

run_screen 1 0 33
sleep 3
run_screen 2 34 67
sleep 3
run_screen 3 68 100
sleep 3
run_screen 4 101 133
sleep 3
run_screen 5 134 166
sleep 3
run_screen 6 167 199

echo ""
echo "=============================================="
echo "All 6 screens launched!"
echo "Monitor progress with: screen -ls | grep gpt5_aug"
echo "View logs in: $OUTPUT_DIR"
echo "Started at: $(date)"
echo "=============================================="
