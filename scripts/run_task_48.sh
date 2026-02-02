#!/bin/bash

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="logs/task_48_run_${TIMESTAMP}"
SCREEN_NAME="task_48"

echo "=========================================="
echo "Running Task 48: Cross-Region Expedition"
echo "=========================================="
echo "Output directory: ${OUTPUT_DIR}"
echo "Screen session: ${SCREEN_NAME}"
echo ""

# Kill any existing task_48 screen session before starting
screen -S "${SCREEN_NAME}" -X quit 2>/dev/null

screen -dmS "${SCREEN_NAME}" bash -c "
    cd /Users/yuanyuan/workspace/agentworld
    python agents/run.py \
        --task data_v0.1_multi/v1.3_benchmark/task_48_cross_region_expedition.yaml \
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
