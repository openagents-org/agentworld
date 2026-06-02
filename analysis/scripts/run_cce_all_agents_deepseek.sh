#!/bin/bash
# Run DeepSeek V4 Pro judge across all 8 agent configurations.
set -u
: "${DIGITALOCEAN_TOKEN:?DIGITALOCEAN_TOKEN must be set}"
cd "$(dirname "$0")/.."

for agent in gemini claude gpt5 deepseek gemini_aug claude_aug gpt5_aug deepseek_aug; do
  echo ""
  echo "════════════════════════════════════════════════════════════"
  echo "DeepSeek judge — agent: $agent — $(date)"
  echo "════════════════════════════════════════════════════════════"
  python3 scripts/compute_cce_v2_deepseek_judge.py --model $agent --task all 2>&1 | tee -a logs/cce_deepseek_judge.log
done
echo ""
echo "ALL DeepSeek judge runs done $(date)"
