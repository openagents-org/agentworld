#!/bin/bash

# Missing Tasks Runner v2 (with fixed username prefixes)
# Claude Haiku: tasks 46-60 (15 tasks) - 3 screens
# DeepSeek: tasks 46-60, 99-100 (17 tasks) - 3 screens
# Connects to game server 2 (port 7041)

CLAUDE_OUTPUT_DIR="agents/logs/claude_haiku_tasks46_60"
DEEPSEEK_OUTPUT_DIR="agents/logs/deepseek_tasks46_60_99_100"
CLAUDE_CONFIG="agents/configs/claude_agent.yaml"
DEEPSEEK_CONFIG="agents/configs/deepseek_agent.yaml"
TASK_DIR="data_v0.1_multi/v1.3_benchmark"

# Create output directories
mkdir -p "$CLAUDE_OUTPUT_DIR"
mkdir -p "$DEEPSEEK_OUTPUT_DIR"

echo "=============================================="
echo "Missing Tasks Runner v2 (prefixed usernames)"
echo "Claude Haiku: tasks 46-60 (3 screens)"
echo "DeepSeek: tasks 46-60, 99-100 (3 screens)"
echo "Game Server: http://localhost:7041"
echo "=============================================="

# Function to run tasks in a screen
run_screen() {
    local screen_prefix=$1
    local screen_num=$2
    local agent_config=$3
    local output_dir=$4
    local task_list=$5
    local log_file="$output_dir/screen_${screen_num}.log"

    echo "Starting ${screen_prefix}_s${screen_num}: tasks [$task_list]"

    screen -dmS "${screen_prefix}_s${screen_num}" bash -c '
        cd /home/ubuntu/works/agentworld
        LOG_FILE="'"$log_file"'"
        AGENT_CONFIG="'"$agent_config"'"
        OUTPUT_DIR="'"$output_dir"'"
        TASK_DIR="'"$TASK_DIR"'"

        echo "===============================================" >> "$LOG_FILE"
        echo "Screen '"$screen_num"' started at $(date)" >> "$LOG_FILE"
        echo "Tasks: '"$task_list"'" >> "$LOG_FILE"
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

# Claude Haiku - 3 screens for tasks 46-60
# Screen 1: tasks 46-50 (5 tasks)
# Screen 2: tasks 51-55 (5 tasks)
# Screen 3: tasks 56-60 (5 tasks)
run_screen "haiku46" 1 "$CLAUDE_CONFIG" "$CLAUDE_OUTPUT_DIR" "46 47 48 49 50"
sleep 3
run_screen "haiku46" 2 "$CLAUDE_CONFIG" "$CLAUDE_OUTPUT_DIR" "51 52 53 54 55"
sleep 3
run_screen "haiku46" 3 "$CLAUDE_CONFIG" "$CLAUDE_OUTPUT_DIR" "56 57 58 59 60"
sleep 3

# DeepSeek - 3 screens for tasks 46-60, 99-100
# Screen 1: tasks 46-51 (6 tasks)
# Screen 2: tasks 52-57 (6 tasks)
# Screen 3: tasks 58-60, 99-100 (5 tasks)
run_screen "deepseek46" 1 "$DEEPSEEK_CONFIG" "$DEEPSEEK_OUTPUT_DIR" "46 47 48 49 50 51"
sleep 3
run_screen "deepseek46" 2 "$DEEPSEEK_CONFIG" "$DEEPSEEK_OUTPUT_DIR" "52 53 54 55 56 57"
sleep 3
run_screen "deepseek46" 3 "$DEEPSEEK_CONFIG" "$DEEPSEEK_OUTPUT_DIR" "58 59 60 99 100"

echo ""
echo "=============================================="
echo "All 6 screens launched!"
echo "  Claude Haiku: haiku46_s1, haiku46_s2, haiku46_s3"
echo "  DeepSeek:     deepseek46_s1, deepseek46_s2, deepseek46_s3"
echo "Monitor: screen -ls | grep -E 'haiku46|deepseek46'"
echo "Claude logs:   $CLAUDE_OUTPUT_DIR"
echo "DeepSeek logs: $DEEPSEEK_OUTPUT_DIR"
echo "Started at: $(date)"
echo "=============================================="
