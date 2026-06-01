#!/bin/bash
# Run Llama-4-Maverick judge across all 8 agent configurations.
set -u
: "${DIGITALOCEAN_TOKEN:?DIGITALOCEAN_TOKEN must be set}"
cd "$(dirname "$0")/.."

for agent in gemini claude gpt5 deepseek gemini_aug claude_aug gpt5_aug deepseek_aug; do
  echo ""
  echo "════════════════════════════════════════════════════════════"
  echo "Llama-4-Maverick judge — agent: $agent — $(date)"
  echo "════════════════════════════════════════════════════════════"
  python3 scripts/compute_cce_v2_llama_judge.py --model $agent --task all 2>&1 | tee -a logs/cce_llama_judge.log
done
echo ""
echo "ALL Llama judge runs done $(date)"
