#!/usr/bin/env bash

# Launch multiple isolated AgentWorld server instances (worlds) on distinct ports
# and dispatch tasks to the matching world so agents never cross-connect.
#
# Usage:
#   bash scripts/run_multi_world_tasks.sh
# Customize WORLDS and TASK_GLOB below as needed.

set -euo pipefail

WORK_DIR="/scratch1/wmz5132/agentworld"
AGENT_CFG="$WORK_DIR/agents/configs/openai_agent.yaml"
# 日志根路径按 agent 配置文件名的前半段（去扩展名、取第一个下划线前的片段）
agent_base="$(basename "$AGENT_CFG")"
agent_base="${agent_base%.*}"
agent_prefix="${agent_base%%_*}"
LOG_ROOT="$WORK_DIR/logs/${agent_prefix}"
mkdir -p "$LOG_ROOT"

# 端口配置可通过环境变量覆盖，默认从 8000 开始，每个世界步进 20
PORT_BASE=${PORT_BASE:-8000}
PORT_STEP=${PORT_STEP:-20}
WORLD_COUNT=${WORLD_COUNT:-20}

# 坏端口名单，可通过 BAD_PORTS="8001 8081" 覆盖；默认跳过 8001 与 8081
BAD_PORTS_STR="${BAD_PORTS:-8001 8081 8003 8002}"
read -r -a BAD_PORTS <<<"$BAD_PORTS_STR"

# 生成世界端口，自动跳过坏端口与已占用端口
is_port_bad() {
  local p="$1"
  for b in "${BAD_PORTS[@]}"; do
    [[ "$p" == "$b" ]] && return 0
  done
  return 1
}

port_blocked() {
  local p="$1"
  # 坏端口视为被占用
  if is_port_bad "$p"; then
    return 0
  fi
  # 被监听视为占用
  if command -v lsof >/dev/null 2>&1; then
    if lsof -iTCP:"$p" -sTCP:LISTEN >/dev/null 2>&1; then
      return 0
    fi
  fi
  # 正常可用
  return 1
}

WORLDS=()
for i in $(seq 1 "$WORLD_COUNT"); do
  port=$((PORT_BASE + (i - 1) * PORT_STEP))
  api=$((port + 1))
  attempts=0
  while port_blocked "$port" || port_blocked "$api"; do
    port=$((port + 2))
    api=$((port + 1))
    attempts=$((attempts + 1))
    if [ "$attempts" -gt 50 ]; then
      echo "Failed to find free ports for world$i. Adjust PORT_BASE/PORT_STEP or BAD_PORTS."
      exit 1
    fi
  done
  sid=$i
  WORLDS+=("world${i}:${port}:${api}:${sid}")
done

# Tasks to run：支持命令行传入区间，默认全量 benchmark。
# 用法示例：
#   bash scripts/run_multi_world_tasks.sh 1 20
#   bash scripts/run_multi_world_tasks.sh 21 40
# 若不传参数，则使用 data_v0.1_multi/benchmark/task_*.yaml 全量。
TASK_START="${1:-}"
TASK_END="${2:-}"

if [[ -n "$TASK_START" && -n "$TASK_END" ]]; then
  # 限制单次最多 20 个任务
  count=$((TASK_END - TASK_START + 1))
  if (( count < 1 )); then
    echo "Invalid range: START=$TASK_START END=$TASK_END"
    exit 1
  fi
  if (( count > 20 )); then
    echo "Range too large (max 20). Given $count."
    exit 1
  fi
  # 左侧补零（两位），如 1 -> 01
  start_pad=$(printf "%02d" "$TASK_START")
  end_pad=$(printf "%02d" "$TASK_END")
  TASK_GLOB="data_v0.1_multi/benchmark/task_{${start_pad}..${end_pad}}_*.yaml"
else
  TASK_GLOB="data_v0.1_multi/benchmark/task_*.yaml"
fi

# Optional: limit how many task processes per world run at once (0 = unlimited).
# Default 1 => 一世界同时只跑一个任务；20 世界即可并行 20 任务。
MAX_PARALLEL_PER_WORLD=1

cd "$WORK_DIR"

declare -a WORLD_PIDS WORLD_NAMES WORLD_API_PORTS WORLD_AGENT_CFGS WORLD_TASK_COUNTS
declare -a WORLD_ENV_FILES
declare -a TASK_PIDS
declare -a BUSY_PORTS=()

cleanup() {
  echo "Cleaning up..."
  for pid in "${TASK_PIDS[@]:-}"; do
    if kill -0 "$pid" 2>/dev/null; then kill "$pid" 2>/dev/null || true; fi
  done
  for pid in "${WORLD_PIDS[@]:-}"; do
    if kill -0 "$pid" 2>/dev/null; then kill "$pid" 2>/dev/null || true; fi
  done
  for envf in "${WORLD_ENV_FILES[@]:-}"; do
    [ -f "$envf" ] && rm -f "$envf"
  done
  for cfg in "${WORLD_AGENT_CFGS[@]:-}"; do
    [ -f "$cfg" ] && rm -f "$cfg"
  done
}
trap cleanup EXIT INT TERM

check_port_free() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1 && return 1
  fi
  return 0
}

write_env_file() {
  local name="$1" port="$2" api="$3" sid="$4"
  local envf="$WORK_DIR/.env.${name}"
  cat >"$envf" <<EOF
HOST=localhost
PORT=$port
API_ENABLED=true
API_PORT=$api
SERVER_ID=$sid
CLIENT_REMOTE_HOST=localhost
CLIENT_REMOTE_PORT=$port
SSL=false
SKIP_DATABASE=true
EOF
  WORLD_ENV_FILES+=("$envf")
}

start_world() {
  local name="$1" port="$2" api="$3" sid="$4"
  local log_file="$WORK_DIR/logs/${name}_server.log"
  write_env_file "$name" "$port" "$api" "$sid"
  echo "Starting $name (PORT=$port, API_PORT=$api, SERVER_ID=$sid)..."
  NODE_ENV="$name" \
  PORT="$port" API_PORT="$api" SERVER_ID="$sid" CLIENT_REMOTE_PORT="$port" CLIENT_REMOTE_HOST="localhost" \
    yarn workspace @kaetram/server dev >"$log_file" 2>&1 &
  WORLD_PIDS+=("$!")
  WORLD_NAMES+=("$name")
  WORLD_API_PORTS+=("$api")
  WORLD_TASK_COUNTS+=("0")
}

make_agent_cfg() {
  local api="$1" name="$2"
  local tmp_cfg
  tmp_cfg="$(mktemp "/tmp/${name}_agent_cfg_XXXX.yaml")"
  # Rewrite host to this world's API port
  perl -pe "s|http://localhost:\\d+|http://localhost:${api}|g" "$AGENT_CFG" >"$tmp_cfg"
  WORLD_AGENT_CFGS+=("$tmp_cfg")
}

launch_task() {
  local task="$1" world_idx="$2"
  local api="${WORLD_API_PORTS[$world_idx]}"
  local name="${WORLD_NAMES[$world_idx]}"
  local agent_cfg="${WORLD_AGENT_CFGS[$world_idx]}"
  local task_base
  task_base="$(basename "${task%.yaml}")"
  local log_dir="$LOG_ROOT/$task_base"
  mkdir -p "$log_dir"
  local log_file="$log_dir/${task_base}.log"
  mkdir -p "$log_dir"
  echo "  [$name] -> $task"
  (
    cd "$WORK_DIR"
    AGENTWORLD_BASE_URL="http://localhost:${api}" \
      python agents/run.py \
      --task "$task" \
      --agent "$agent_cfg" \
      --output "$log_dir" \
      --no-split-screen \
      >"$log_file" 2>&1
  ) &
  TASK_PIDS+=("$!")
  WORLD_TASK_COUNTS[$world_idx]=$(( WORLD_TASK_COUNTS[$world_idx] + 1 ))
}

# 1) Start all worlds（先检查端口占用）
for world in "${WORLDS[@]}"; do
  IFS=":" read -r name port api sid <<<"$world"
  if ! check_port_free "$port"; then
    BUSY_PORTS+=("$port")
  fi
  if ! check_port_free "$api"; then
    BUSY_PORTS+=("$api")
  fi
done

if [ ${#BUSY_PORTS[@]} -ne 0 ]; then
  echo "以下端口已被占用，调整 PORT_BASE/PORT_STEP 或先清理进程:"
  printf "  %s\n" "${BUSY_PORTS[@]}"
  exit 1
fi

for world in "${WORLDS[@]}"; do
  IFS=":" read -r name port api sid <<<"$world"
  start_world "$name" "$port" "$api" "$sid"
  make_agent_cfg "$api" "$name"
done

echo "Waiting 15s for servers to warm up..."
sleep 15

# 2) Collect tasks（仅取无版本后缀的原始文件，过滤掉 *_v1.yaml / *_v2.yaml）
TASKS=()
if [[ -n "$TASK_START" && -n "$TASK_END" ]]; then
  for num in $(seq -w "$TASK_START" "$TASK_END"); do
    for f in data_v0.1_multi/benchmark/task_${num}_*.yaml; do
      [[ -f "$f" ]] || continue
      [[ "$f" =~ _v[12]\.yaml$ ]] && continue
      TASKS+=("$f")
    done
  done
else
  for f in data_v0.1_multi/benchmark/task_*.yaml; do
    [[ -f "$f" ]] || continue
    [[ "$f" =~ _v[12]\.yaml$ ]] && continue
    TASKS+=("$f")
  done
fi

if [ ${#TASKS[@]} -eq 0 ]; then
  echo "No tasks matched (after filtering v1/v2) in range: $TASK_START..$TASK_END"
  exit 1
fi

# 排序稳定
IFS=$'\n' TASKS=($(printf "%s\n" "${TASKS[@]}" | sort))

# 3) Dispatch tasks round-robin to worlds (respect per-world cap if set)
for idx in "${!TASKS[@]}"; do
  task="${TASKS[$idx]}"
  world_idx=$(( idx % ${#WORLDS[@]} ))

  if [ "$MAX_PARALLEL_PER_WORLD" -gt 0 ]; then
    # Throttle per world if needed
    while :; do
      running=0
      for pid in "${TASK_PIDS[@]:-}"; do
        if kill -0 "$pid" 2>/dev/null; then running=$((running+1)); fi
      done
      # Approximate: only count global running tasks; simple guard
      if [ "$running" -lt $(( MAX_PARALLEL_PER_WORLD * ${#WORLDS[@]} )) ]; then
        break
      fi
      sleep 1
    done
  fi

  launch_task "$task" "$world_idx"
done

# 4) Wait for tasks to finish (servers stay alive until cleanup trap fires)
wait "${TASK_PIDS[@]}"

echo "All tasks finished. Summary:"
for i in "${!WORLD_NAMES[@]}"; do
  echo "  ${WORLD_NAMES[$i]} (API:${WORLD_API_PORTS[$i]}): ${WORLD_TASK_COUNTS[$i]} tasks"
done

echo "Stopping servers..."
# cleanup trap will handle termination and temp removal

