#!/bin/bash

# Run Task 49 in a screen session

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="logs/task_49_run_${TIMESTAMP}"
SCREEN_NAME="task_49"

echo "=========================================="
echo "Running Task 49: Jewelry Workshop"
echo "=========================================="
echo "Output directory: ${OUTPUT_DIR}"
echo "Screen session: ${SCREEN_NAME}"
echo ""

# Kill any existing task_49 screen session
screen -S "${SCREEN_NAME}" -X quit 2>/dev/null

# Create the screen session and run the task
screen -dmS "${SCREEN_NAME}" bash -c "
    cd /Users/yuanyuan/workspace/agentworld
    python agents/run.py \
        --task data_v0.1_multi/benchmark_rewritten/task_49_jewelry_workshop.yaml \
        --agent agents/configs/openai_agent.yaml \
        --output ${OUTPUT_DIR}
    echo ''
    echo 'Task completed. Press Enter to close this screen session.'
    read
"

echo "Screen session '${SCREEN_NAME}' started."
echo ""
echo "Commands:"
echo "  Attach:  screen -r ${SCREEN_NAME}"
echo "  List:    screen -ls"
echo "  Kill:    screen -S ${SCREEN_NAME} -X quit"
echo ""
