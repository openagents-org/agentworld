#!/bin/bash
# Batch verification script for AgentWorld tasks
# Usage: ./batch_verify.sh [logs_dir] [output_file]
#
# Example:
#   ./batch_verify.sh logs/qwenplus-logs-00-to-100 results.csv

LOGS_DIR="${1:-logs/qwenplus-logs-00-to-100}"
OUTPUT_FILE="${2:-verify_results.csv}"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Initialize counters
total=0
passed=0
failed=0
skipped=0

# Create CSV header
echo "task_id,score,details" > "$OUTPUT_FILE"

echo "=============================================="
echo "AgentWorld Batch Task Verification"
echo "=============================================="
echo "Logs directory: $LOGS_DIR"
echo "Output file: $OUTPUT_FILE"
echo "=============================================="
echo ""

# Get all task directories and sort numerically
task_dirs=$(ls -d "$LOGS_DIR"/task_* 2>/dev/null | sort -t'_' -k2 -n)

for task_dir in $task_dirs; do
    if [ -d "$task_dir" ]; then
        task_name=$(basename "$task_dir")
        # Extract task_id (e.g., task_00 from task_00_combined_workshop)
        task_id=$(echo "$task_name" | sed 's/\(task_[0-9]*\).*/\1/')

        # Find trajectory file
        traj_file="$task_dir/${task_id}_trajectory.json"

        if [ -f "$traj_file" ]; then
            ((total++))

            # Run verifier and capture output
            output=$(python3 task_verifier.py --traj_path "$traj_file" 2>&1)
            score=$(echo "$output" | grep "^Score:" | awk '{print $2}')
            details=$(echo "$output" | grep "^Details:" | cut -d' ' -f2-)

            # Handle empty score
            if [ -z "$score" ]; then
                score=0
                details="Error running verifier"
            fi

            # Write to CSV (escape commas in details)
            details_escaped=$(echo "$details" | sed 's/,/;/g')
            echo "$task_id,$score,$details_escaped" >> "$OUTPUT_FILE"

            # Print result with color
            if [ "$score" -eq 1 ]; then
                ((passed++))
                printf "${GREEN}[PASS]${NC} %-15s %s\n" "$task_id" "$details"
            else
                ((failed++))
                printf "${RED}[FAIL]${NC} %-15s %s\n" "$task_id" "$details"
            fi
        else
            ((skipped++))
            printf "${YELLOW}[SKIP]${NC} %-15s No trajectory file found\n" "$task_id"
        fi
    fi
done

# Print summary
echo ""
echo "=============================================="
echo "Summary"
echo "=============================================="
echo "Total tasks:  $total"
printf "${GREEN}Passed:       $passed${NC}\n"
printf "${RED}Failed:       $failed${NC}\n"
printf "${YELLOW}Skipped:      $skipped${NC}\n"
echo ""
if [ "$total" -gt 0 ]; then
    pass_rate=$(awk "BEGIN {printf \"%.1f\", $passed * 100 / $total}")
    echo "Pass rate:    ${pass_rate}%"
fi
echo ""
echo "Results saved to: $OUTPUT_FILE"
