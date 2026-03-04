#!/bin/bash
# Re-run all failed tasks from v1.3 spawn fix batch
# Tasks: 78, 82, 84, 85, 86, 87, 93, 98, 100 (no trajectory saved)

cd /home/ubuntu/works/agentworld

LOG_DIR="agents/logs/v1.3_spawn_fix_rerun2"
AGENT_CONFIG="agents/configs/openai_agent.yaml"

mkdir -p "$LOG_DIR"

echo "=============================================="
echo "Re-running failed tasks: 78, 82, 84, 85, 86, 87, 93, 98, 100"
echo "Output directory: $LOG_DIR"
echo "Started at: $(date)"
echo "=============================================="

for task_num in 78 82 84 85 86 87 93 98 100; do
    echo ""
    echo ">>> Starting Task $task_num at $(date)"

    # Find the task file
    TASK_FILE=$(ls data_v0.1_multi/v1.3_benchmark/task_${task_num}_*.yaml 2>/dev/null | head -1)

    if [ -z "$TASK_FILE" ]; then
        echo "  ERROR: No task file found for task $task_num"
        continue
    fi

    echo "  Task file: $TASK_FILE"

    # Run the task
    python3 agents/run.py \
        --task "$TASK_FILE" \
        --agent "$AGENT_CONFIG" \
        --output "$LOG_DIR" \
        --no-split-screen

    EXIT_CODE=$?
    echo "  Exit code: $EXIT_CODE"
    echo "  Completed at: $(date)"

    # Check if trajectory was saved
    TRAJ_FILE="$LOG_DIR/task_${task_num}_trajectory.json"
    if [ -f "$TRAJ_FILE" ]; then
        echo "  ✅ Trajectory saved: $TRAJ_FILE"
    else
        echo "  ❌ WARNING: No trajectory file found!"
    fi

    # Small delay between tasks
    sleep 5
done

echo ""
echo "=============================================="
echo "All failed tasks re-run completed at: $(date)"
echo "=============================================="

# List all trajectory files created
echo ""
echo "Trajectory files created:"
ls -la "$LOG_DIR"/task_*_trajectory.json 2>/dev/null || echo "No trajectory files found"
