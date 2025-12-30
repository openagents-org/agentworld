#!/usr/bin/env bash

# Sequentially run batches of tasks with run_multi_world_tasks_deepseek_v2.sh.
# Each batch waits until previous tasks/servers are idle before starting.
#
# DeepSeek v2 Benchmark - 每批次跑 5 个任务，使用 benchmark_v2 数据集
# 任务范围: task_00 到 task_105 (共106个任务)

set -euo pipefail

WORK_DIR="/home/ubuntu/agentworld"
RUN_SCRIPT="$WORK_DIR/scripts/run_multi_world_tasks_deepseek_v2.sh"

# DeepSeek v2 批次（每批 5 个，从 1 开始跑到 100）
# 1-5, 6-10, 11-15, ..., 96-100
BATCHES=(
  "1 5" "6 10" "11 15" "16 20" "21 25"
  "26 30" "31 35" "36 40" "41 45" "46 50"
  "51 55" "56 60" "61 65" "66 70" "71 75"
  "76 80" "81 85" "86 90" "91 95" "96 100"
)

# DeepSeek API Key - 请替换为你的实际 API Key
export DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-your-deepseek-api-key-here}"

# DeepSeek v2 使用端口范围 (11000+)，避免与 v1 (10000+) 冲突
export BAD_PORTS="${BAD_PORTS:-11001 11002 11003 11081}"
export PORT_BASE="${PORT_BASE:-11000}"
export PORT_STEP="${PORT_STEP:-20}"
export WORLD_COUNT="${WORLD_COUNT:-5}"

wait_for_idle() {
  echo "[batch] 检查是否有 DeepSeek v2 任务运行中..."
  # 只检查 deepseek_v2 相关进程（通过日志路径或临时配置文件名判断）
  while pgrep -f "deepseek_v2/task_" >/dev/null 2>&1 || pgrep -f "deepseek_v2_world" >/dev/null 2>&1; do
    echo "[batch] 检测到 DeepSeek v2 任务仍在运行，60s 后重试..."
    sleep 60
  done
  echo "[batch] DeepSeek v2 环境空闲，可以启动下一批。"
}

cd "$WORK_DIR"

# 先等待当前已有的运行
wait_for_idle

for rng in "${BATCHES[@]}"; do
  read -r start end <<<"$rng"
  echo "[batch] 准备运行区间: $start-$end (DeepSeek v2)"
  wait_for_idle
  echo "[batch] 启动区间: $start-$end (DeepSeek v2)"
  "$RUN_SCRIPT" "$start" "$end"
  echo "[batch] 区间 $start-$end (DeepSeek v2) 完成。"
done

echo "[batch] 所有 DeepSeek v2 批次已完成。"
