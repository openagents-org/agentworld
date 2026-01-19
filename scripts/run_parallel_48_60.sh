#!/bin/bash

# Run tasks 48-60 in parallel using 4 screen sessions
# Each screen session runs 3-4 tasks sequentially

PROJECT_ROOT="/nlp/data/yyuan86/workspace/agentworld"
TASK_DIR="$PROJECT_ROOT/data_v0.1_multi/v1.3_benchmark"
AGENT_CONFIG="$PROJECT_ROOT/agents/configs/openai_agent.yaml"
OUTPUT_BASE="$PROJECT_ROOT/logs/rerun_48_60_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$OUTPUT_BASE"

echo "======================================"
echo "AgentWorld Task Runner (48-60)"
echo "======================================"
echo "Output directory: $OUTPUT_BASE"
echo ""

# Function to create a runner script for a range of tasks
create_runner() {
    local start=$1
    local end=$2
    local screen_name=$3
    local runner_script="$OUTPUT_BASE/runner_${start}_${end}.sh"
    
    cat > "$runner_script" << INNEREOF
#!/bin/bash
source /nlp/data/yyuan86/miniconda3/etc/profile.d/conda.sh
conda activate agentWorld
cd $PROJECT_ROOT

echo "Starting tasks $start to $end at \$(date)"
echo "Output: $OUTPUT_BASE"

for i in \$(seq $start $end); do
    TASK_NUM=\$(printf "%02d" \$i)
    TASK_FILE=\$(ls "$TASK_DIR"/task_\${TASK_NUM}_*.yaml 2>/dev/null | head -1)
    
    if [ -z "\$TASK_FILE" ]; then
        echo "⚠️ Task \$TASK_NUM: No matching file found, skipping..."
        continue
    fi
    
    TASK_NAME=\$(basename "\$TASK_FILE" .yaml)
    TASK_OUTPUT="$OUTPUT_BASE/\$TASK_NAME"
    mkdir -p "\$TASK_OUTPUT"
    
    echo ""
    echo "========================================"
    echo "🎯 Running Task \$TASK_NUM: \$TASK_NAME"
    echo "========================================"
    
    START_TIME=\$(date +%s)
    
    python3 -u agents/run.py \\
        --task "\$TASK_FILE" \\
        --agent "$AGENT_CONFIG" \\
        --output "\$TASK_OUTPUT" \\
        2>&1 | tee "\$TASK_OUTPUT/console.log"
    
    EXIT_CODE=\$?
    END_TIME=\$(date +%s)
    DURATION=\$((END_TIME - START_TIME))
    
    if [ \$EXIT_CODE -eq 0 ]; then
        echo "✅ Task \$TASK_NUM completed in \${DURATION}s"
    else
        echo "❌ Task \$TASK_NUM failed after \${DURATION}s (exit code: \$EXIT_CODE)"
    fi
done

echo ""
echo "========================================"
echo "Screen $screen_name completed at \$(date)"
echo "========================================"
INNEREOF
    
    chmod +x "$runner_script"
    echo "$runner_script"
}

# Create runner scripts for 4 screen sessions
echo "Creating runner scripts..."
RUNNER1=$(create_runner 48 50 "agent_48_50")
RUNNER2=$(create_runner 51 53 "agent_51_53")
RUNNER3=$(create_runner 54 56 "agent_54_56")
RUNNER4=$(create_runner 57 60 "agent_57_60")

echo "✅ Created: $RUNNER1"
echo "✅ Created: $RUNNER2"
echo "✅ Created: $RUNNER3"
echo "✅ Created: $RUNNER4"

# Start screen sessions
echo ""
echo "Starting screen sessions..."

screen -dmS agent_48_50 bash -c "source /nlp/data/yyuan86/miniconda3/etc/profile.d/conda.sh && conda activate agentWorld && $RUNNER1; exec bash"
echo "✅ Started screen 'agent_48_50' (tasks 48-50)"

screen -dmS agent_51_53 bash -c "source /nlp/data/yyuan86/miniconda3/etc/profile.d/conda.sh && conda activate agentWorld && $RUNNER2; exec bash"
echo "✅ Started screen 'agent_51_53' (tasks 51-53)"

screen -dmS agent_54_56 bash -c "source /nlp/data/yyuan86/miniconda3/etc/profile.d/conda.sh && conda activate agentWorld && $RUNNER3; exec bash"
echo "✅ Started screen 'agent_54_56' (tasks 54-56)"

screen -dmS agent_57_60 bash -c "source /nlp/data/yyuan86/miniconda3/etc/profile.d/conda.sh && conda activate agentWorld && $RUNNER4; exec bash"
echo "✅ Started screen 'agent_57_60' (tasks 57-60)"

echo ""
echo "======================================"
echo "All screen sessions started!"
echo "======================================"
echo ""
echo "Monitor commands:"
echo "  screen -ls                    # List all screens"
echo "  screen -r agent_48_50         # Attach to screen"
echo "  Ctrl+A, D                     # Detach from screen"
echo ""
echo "Output directory: $OUTPUT_BASE"
