#!/bin/bash
# Run YC-bench with automatic resume on timeout, logging progress to stdout
set -e

# ANTHROPIC_API_KEY must be set in environment before running

DB="/Users/floris.fok/Documents/AutoResearch/yc/yc-bench-main/db/custom_config_1_anthropic_claude-sonnet-4-6.db"
ATTEMPT=0

while true; do
    ATTEMPT=$((ATTEMPT + 1))
    echo "=== Attempt $ATTEMPT ($(date)) ==="

    # Log sim state before run
    python3 -c "
import sqlite3, sys
try:
    conn = sqlite3.connect('$DB')
    c = conn.cursor()
    row = c.execute('SELECT sim_time, horizon_end FROM sim_state LIMIT 1').fetchone()
    if row: print(f'  sim_time: {row[0]}, horizon_end: {row[1]}')
    funds = c.execute('SELECT funds_cents FROM companies LIMIT 1').fetchone()
    if funds: print(f'  funds: \${funds[0]/100:,.2f}')
    tasks = c.execute('SELECT status, COUNT(*) FROM tasks GROUP BY status').fetchall()
    print(f'  tasks: {dict(tasks)}')
    conn.close()
except: print('  (no DB yet)')
" 2>/dev/null

    # Run benchmark
    python3 run_bench.py > run.log 2>&1
    EXIT=$?

    # Show result
    echo "  exit=$EXIT"
    cat run.log | head -20

    # Check if we got a final result (not timeout)
    if grep -q "^outcome:" run.log 2>/dev/null; then
        OUTCOME=$(grep "^outcome:" run.log | awk '{print $NF}')
        if [ "$OUTCOME" != "timeout" ]; then
            echo ""
            echo "=== FINAL RESULT ==="
            grep "^final_funds:\|^funds_cents:\|^tasks_done:\|^tasks_failed:\|^turns:\|^api_cost:\|^elapsed:\|^outcome:" run.log
            break
        fi
    fi

    echo "  (timed out, resuming...)"
    echo ""
done
