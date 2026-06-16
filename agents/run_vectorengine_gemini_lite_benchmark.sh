#!/bin/bash
# Multi-agent benchmark — Gemini 3.1 Flash-Lite via vectorengine.cn
# 100 v1.3 tasks across 4 tmux windows (25 tasks each).

set -u

if [ -z "${YINLI_API_KEY:-}" ]; then
    echo "ERROR: YINLI_API_KEY is not set." >&2
    echo "  export YINLI_API_KEY='sk-KS2F9vUkJX2lSEz6AfU6uwbVjGPxnMV9Xs7v59D4IVtG8MKF'" >&2
    exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="agents/logs/vectorengine_gemini_lite_v1.3"
AGENT_CONFIG="agents/configs/gemini_flash_lite_vectorengine_agent.yaml"
TASK_DIR="data_v0.1_multi/v1.3_benchmark"
SESSION="bench-ve-gemini-lite"

mkdir -p "${PROJECT_ROOT}/${OUTPUT_DIR}"

echo "=============================================="
echo "Vectorengine Gemini 3.1 Flash-Lite Benchmark"
echo "Output:  $OUTPUT_DIR"
echo "Session: $SESSION (4 windows w0..w3)"
echo "=============================================="

tmux kill-session -t "$SESSION" 2>/dev/null

run_window() {
    local idx=$1
    local start_task=$2
    local end_task=$3
    local log_file="${PROJECT_ROOT}/${OUTPUT_DIR}/window_${idx}.log"

    local cmd="cd '${PROJECT_ROOT}'; \
export YINLI_API_KEY='${YINLI_API_KEY}'; \
{ echo '== window ${idx} started '\$(date)'; tasks ${start_task}..${end_task} =='; \
for i in \$(seq ${start_task} ${end_task}); do \
  T=\$(printf '%02d' \$i); \
  F=\$(ls ${TASK_DIR}/task_\${T}_*.yaml 2>/dev/null | head -1); \
  if [ -n \"\$F\" ]; then \
    echo; echo \">>> Task \$T starting \$(date)\"; echo \">>> File: \$F\"; \
    python3 agents/run.py --task \"\$F\" --agent ${AGENT_CONFIG} --output ${OUTPUT_DIR} --no-split-screen; \
    echo \">>> Task \$T exit=\$? at \$(date)\"; \
  else \
    echo \">>> Skip Task \$T (file not found)\"; \
  fi; \
done; \
echo '== window ${idx} done '\$(date)' =='; } 2>&1 | tee -a '${log_file}'"

    if [ "$idx" = "0" ]; then
        tmux new-session -d -s "$SESSION" -n "w0" bash -c "$cmd"
    else
        tmux new-window -a -t "${SESSION}:" -n "w${idx}" bash -c "$cmd"
    fi
    echo "  window $idx -> tasks $start_task..$end_task"
}

run_window 0  1  25
run_window 1 26  50
run_window 2 51  75
run_window 3 76 100

echo ""
echo "Attach: tmux attach -t $SESSION"
echo "Logs:   ${PROJECT_ROOT}/${OUTPUT_DIR}/window_*.log"
