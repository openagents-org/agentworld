#!/usr/bin/env python3
"""
Trajectory Visualizer - Generate HTML visualization from agent trajectory JSON files.

Usage:
    python visualize_trajectory.py <trajectory_file.json> [--output output.html]
    python visualize_trajectory.py <logs_directory> [--output output.html]  # Uses latest trajectory

Example:
    python visualize_trajectory.py agents/logs/v1.3_experiment1/task_01_trajectory.json
    python visualize_trajectory.py agents/logs/v1.3_experiment1/
"""

import argparse
import json
import os
import re
import html
import sys
import inspect
from pathlib import Path
from datetime import datetime

# Add parent directory to path for task_verifier import
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from task_verifier import verify_task, get_verifier_map, VERIFIERS, VERIFIERS_V1, VERIFIERS_V2
    VERIFIER_AVAILABLE = True
except ImportError:
    VERIFIER_AVAILABLE = False


def get_verifier_info(task_id: str, version: int = 0) -> tuple:
    """Get verifier function source code and run verification.

    Returns: (score, message, source_code) or (None, None, None) if not available
    """
    if not VERIFIER_AVAILABLE:
        return None, None, None

    # Get the verifier function
    verifier_map = get_verifier_map(version)
    if task_id not in verifier_map:
        return None, None, f"No verifier found for {task_id}"

    verifier_func = verifier_map[task_id]

    # Extract source code
    try:
        source_code = inspect.getsource(verifier_func)
    except Exception:
        source_code = "# Source code not available"

    return verifier_func, source_code


def run_verification(trajectory_data: dict, task_id: str = None, version: int = 0) -> tuple:
    """Run verification on trajectory data.

    Returns: (score, message, source_code)
    """
    if not VERIFIER_AVAILABLE:
        return 0, "Verifier not available", ""

    if task_id is None:
        task_id = trajectory_data.get('task_id', '')

    # Determine version from task filename if available
    # e.g., task_08_v1 -> version 1
    if '_v1' in task_id:
        version = 1
        task_id = task_id.replace('_v1', '').replace('_v2', '')
    elif '_v2' in task_id:
        version = 2
        task_id = task_id.replace('_v2', '')

    # Get verifier info
    verifier_func, source_code = get_verifier_info(task_id, version)

    if verifier_func is None:
        return 0, f"No verifier found for {task_id}", source_code or ""

    # Run verification
    try:
        score, message = verifier_func(trajectory_data)
    except Exception as e:
        score, message = 0, f"Verification error: {str(e)}"

    return score, message, source_code


def find_latest_trajectory(directory: str) -> str:
    """Find the most recent trajectory file in a directory."""
    dir_path = Path(directory)
    trajectory_files = list(dir_path.glob("task_*_trajectory.json"))
    if not trajectory_files:
        raise FileNotFoundError(f"No trajectory files found in {directory}")
    # Sort by modification time, get latest
    latest = max(trajectory_files, key=lambda p: p.stat().st_mtime)
    return str(latest)


def extract_chat_messages_from_log(trajectory_path: str, timestamp: str) -> dict:
    """Extract full chat messages from task_runner log file.

    Returns a dict mapping agent_name -> list of full messages in order.
    """
    dir_path = Path(trajectory_path).parent

    # Find matching task_runner log by timestamp
    # Trajectory timestamp format: 2026-01-09T00:37:50.800414
    # Log filename format: task_runner_20260109_003750.log
    try:
        dt = datetime.fromisoformat(timestamp)
        log_suffix = dt.strftime("%Y%m%d_%H%M%S")
        log_file = dir_path / f"task_runner_{log_suffix}.log"

        if not log_file.exists():
            # Try to find a close match
            log_files = list(dir_path.glob("task_runner_*.log"))
            if log_files:
                # Find the one closest to our timestamp
                log_file = min(log_files, key=lambda f: abs(
                    datetime.strptime(f.stem.replace("task_runner_", ""), "%Y%m%d_%H%M%S").timestamp() - dt.timestamp()
                ))
    except Exception:
        return {}

    if not log_file.exists():
        return {}

    # Parse chat messages from log
    # Format: 2026-01-09 00:38:30,698 - TaskRunner - INFO - 💬 agent_1: <message>
    chat_messages = {"agent_1": [], "agent_2": [], "agent_3": []}
    chat_pattern = re.compile(r'💬 (agent_\d+): (.+)$')

    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                match = chat_pattern.search(line)
                if match:
                    agent = match.group(1)
                    message = match.group(2).strip()
                    if agent in chat_messages:
                        chat_messages[agent].append(message)
    except Exception:
        pass

    return chat_messages


def parse_action(action_str: str) -> dict:
    """Parse action string into structured data."""
    if not action_str:
        return {"type": "waiting", "raw": "", "params": "No action taken this round"}

    # Match function call pattern: function_name(param=value, ...)
    match = re.match(r'(\w+)\((.*)\)', action_str, re.DOTALL)
    if match:
        func_name = match.group(1)
        params_str = match.group(2)

        # For chat actions, extract the full message
        if func_name == "chat":
            msg_match = re.search(r'message=["\']?(.*?)["\']?\s*\)', params_str + ")", re.DOTALL)
            if msg_match:
                params_str = msg_match.group(1)

        return {
            "type": func_name,
            "params": params_str,
            "raw": action_str
        }
    return {"type": "unknown", "raw": action_str, "params": ""}


def get_action_icon(action_type: str) -> str:
    """Get emoji icon for action type."""
    icons = {
        "chat": "💬",
        "move_character": "🚶",
        "harvest_resource": "⛏️",
        "craft_item": "🔨",
        "transfer_item": "📦",
        "equip_item": "🎒",
        "attack": "⚔️",
        "complete": "✅",
        "observe": "👁️",
        "use_item": "🧪",
        "waiting": "⏳",
        "unknown": "❓"
    }
    return icons.get(action_type, "🔷")


def get_agent_color(agent_idx: int) -> str:
    """Get color for agent based on index."""
    colors = [
        "#3b82f6",  # Blue
        "#10b981",  # Green
        "#f59e0b",  # Amber
        "#ef4444",  # Red
        "#8b5cf6",  # Purple
        "#ec4899",  # Pink
    ]
    return colors[agent_idx % len(colors)]


def format_observation(obs: dict | str) -> str:
    """Format observation data for display."""
    if not obs:
        return "<em>No observation</em>"
    if isinstance(obs, str):
        return html.escape(obs[:500]) + ("..." if len(obs) > 500 else "")

    # Extract key info from observation dict
    parts = []
    if "status" in obs:
        parts.append(f"<strong>Status:</strong> {obs['status']}")
    if "location" in obs:
        loc = obs["location"]
        parts.append(f"<strong>Location:</strong> ({loc.get('x')}, {loc.get('y')})")
    if "inventory" in obs:
        inv = obs["inventory"]
        # Handle both dict (with 'items' key) and list formats
        if isinstance(inv, dict):
            inv = inv.get("items", [])
        if isinstance(inv, list):
            items = [f"{item.get('name', 'Unknown')} ({item.get('count', 1)}x)"
                     for item in inv[:5]]
            if items:
                parts.append(f"<strong>Inventory:</strong> {', '.join(items)}")
    if "nearby_resources" in obs:
        resources = obs["nearby_resources"][:3]
        if resources:
            res_names = [r.get("type", "Unknown") for r in resources]
            parts.append(f"<strong>Nearby:</strong> {', '.join(res_names)}")

    if not parts:
        # Fallback: show truncated JSON
        json_str = json.dumps(obs, indent=2)
        return f"<pre>{html.escape(json_str[:500])}{'...' if len(json_str) > 500 else ''}</pre>"

    return "<br>".join(parts)


def generate_html(trajectory_data: dict, output_path: str, trajectory_path: str = None, version: int = 0) -> None:
    """Generate HTML visualization from trajectory data."""

    task_def = trajectory_data.get("task_definition", {})
    task_info = task_def.get("task", {})
    rounds = trajectory_data.get("rounds", [])
    metrics = trajectory_data.get("metrics", {})

    # Extract full chat messages from task_runner log
    chat_messages = {}
    if trajectory_path:
        timestamp = trajectory_data.get("timestamp", "")
        chat_messages = extract_chat_messages_from_log(trajectory_path, timestamp)

    # Track chat message index per agent
    chat_indices = {f"agent_{i}": 0 for i in range(1, 10)}

    # Extract agent info
    agents = []
    for key in task_def:
        if key.startswith("agent_"):
            agent_num = key.split("_")[1]
            agent_data = task_def[key]
            agents.append({
                "id": key,
                "num": agent_num,
                "username": agent_data.get("username", f"Agent {agent_num}"),
                "location": agent_data.get("location", {}),
                "skills": agent_data.get("skill_levels", {}),
                "inventory": agent_data.get("inventory_items", []),
                "equipped": agent_data.get("equipped_items", [])
            })

    # Sort agents by number
    agents.sort(key=lambda a: int(a["num"]))

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(task_info.get("name", "Agent Trajectory"))}</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f8f9fa;
            color: #1a1a1a;
            min-height: 100vh;
            padding: 24px;
            line-height: 1.5;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        /* Header */
        .header {{
            background: #fff;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 20px;
            border: 1px solid #e0e0e0;
        }}

        .header h1 {{
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 6px;
            color: #1a1a1a;
        }}

        .header .task-description {{
            color: #666;
            font-size: 15px;
            margin-bottom: 12px;
        }}

        .header .primary-objective {{
            background: #e8f4ff;
            padding: 12px 16px;
            border-radius: 6px;
            font-size: 14px;
            color: #1a1a1a;
            margin-bottom: 16px;
            border-left: 3px solid #2563eb;
        }}

        .header .task-meta {{
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
        }}

        .header .meta-item {{
            background: #f0f0f0;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 13px;
            color: #444;
        }}

        .header .meta-item strong {{
            color: #2563eb;
        }}

        /* Metrics bar */
        .metrics-bar {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }}

        .metric-card {{
            background: #fff;
            border-radius: 8px;
            padding: 16px 20px;
            border: 1px solid #e0e0e0;
            flex: 1;
            min-width: 120px;
        }}

        .metric-card .value {{
            font-size: 28px;
            font-weight: 600;
            color: #1a1a1a;
        }}

        .metric-card .label {{
            font-size: 13px;
            color: #666;
            margin-top: 2px;
        }}

        /* Agent cards */
        .agents-section {{
            margin-bottom: 20px;
        }}

        .agents-section h2 {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #1a1a1a;
        }}

        .agents-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 12px;
        }}

        .agent-card {{
            background: #fff;
            border-radius: 8px;
            padding: 16px;
            border-left: 3px solid;
            border-top: 1px solid #e0e0e0;
            border-right: 1px solid #e0e0e0;
            border-bottom: 1px solid #e0e0e0;
        }}

        .agent-card .agent-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}

        .agent-card .agent-avatar {{
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            color: #fff;
        }}

        .agent-card .agent-name {{
            font-size: 15px;
            font-weight: 600;
            color: #1a1a1a;
        }}

        .agent-card .agent-details {{
            font-size: 12px;
            color: #666;
        }}

        .agent-card .skills-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-top: 10px;
        }}

        .skill-tag {{
            background: #f0f0f0;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            color: #444;
        }}

        /* Timeline */
        .timeline-section {{
            margin-top: 24px;
        }}

        .timeline-section h2 {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #1a1a1a;
        }}

        .timeline-controls {{
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}

        .timeline-controls button {{
            padding: 8px 16px;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            background: #fff;
            color: #333;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 13px;
        }}

        .timeline-controls button:hover {{
            background: #f0f0f0;
            border-color: #bbb;
        }}

        .timeline-controls button.active {{
            background: #2563eb;
            color: #fff;
            border-color: #2563eb;
        }}

        .round-slider {{
            flex: 1;
            min-width: 200px;
        }}

        .round-slider input {{
            width: 100%;
        }}

        .round-slider .slider-label {{
            font-size: 13px;
            color: #666;
            margin-bottom: 4px;
        }}

        /* Round display */
        .round-container {{
            background: #fff;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 12px;
            border: 1px solid #e0e0e0;
        }}

        .round-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #eee;
        }}

        .round-number {{
            font-size: 18px;
            font-weight: 600;
            color: #2563eb;
        }}

        .round-timestamp {{
            font-size: 13px;
            color: #888;
        }}

        /* Agent actions in round */
        .agent-actions {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 12px;
        }}

        .agent-action-card {{
            background: #fafafa;
            border-radius: 6px;
            padding: 14px;
            border-left: 3px solid;
            border-top: 1px solid #eee;
            border-right: 1px solid #eee;
            border-bottom: 1px solid #eee;
        }}

        .agent-action-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}

        .agent-action-name {{
            font-weight: 600;
            font-size: 14px;
            color: #1a1a1a;
        }}

        .agent-status {{
            font-size: 11px;
            color: #666;
            background: #f0f0f0;
            padding: 3px 6px;
            border-radius: 3px;
        }}

        .action-content {{
            margin-bottom: 10px;
        }}

        .action-type {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background: #e8f4ff;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 13px;
            margin-bottom: 8px;
            color: #2563eb;
        }}

        .action-params {{
            font-size: 12px;
            color: #444;
            background: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            word-break: break-word;
            font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            white-space: pre-wrap;
        }}

        .observation-toggle {{
            background: #f5f5f5;
            border: 1px solid #ddd;
            color: #2563eb;
            padding: 6px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            width: 100%;
            text-align: left;
        }}

        .observation-toggle:hover {{
            background: #eee;
        }}

        .observation-content {{
            display: none;
            margin-top: 8px;
            font-size: 11px;
            color: #555;
            background: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid #eee;
        }}

        .observation-content.show {{
            display: block;
        }}

        .observation-content pre {{
            white-space: pre-wrap;
            word-break: break-word;
        }}

        /* Task Result */
        .task-result {{
            margin-top: 24px;
            background: #fff;
            border-radius: 8px;
            padding: 20px;
            border: 2px solid;
        }}

        .task-result.result-success {{
            border-color: #10b981;
            background: linear-gradient(135deg, #ecfdf5 0%, #fff 100%);
        }}

        .task-result.result-failure {{
            border-color: #ef4444;
            background: linear-gradient(135deg, #fef2f2 0%, #fff 100%);
        }}

        .result-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }}

        .result-icon {{
            font-size: 32px;
        }}

        .result-text {{
            font-size: 20px;
            font-weight: 700;
        }}

        .result-success .result-text {{
            color: #059669;
        }}

        .result-failure .result-text {{
            color: #dc2626;
        }}

        .result-details {{
            display: flex;
            gap: 24px;
            margin-bottom: 16px;
        }}

        .result-stat {{
            display: flex;
            flex-direction: column;
        }}

        .result-stat .stat-value {{
            font-size: 24px;
            font-weight: 600;
            color: #1a1a1a;
        }}

        .result-stat .stat-label {{
            font-size: 12px;
            color: #666;
        }}

        .criteria-reference {{
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #e0e0e0;
        }}

        .criteria-reference h4 {{
            font-size: 13px;
            font-weight: 600;
            color: #666;
            margin-bottom: 8px;
        }}

        .criteria-reference ul {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .criteria-reference li {{
            padding: 4px 0;
            font-size: 12px;
            color: #555;
        }}

        .criteria-reference li:before {{
            content: "• ";
            color: #999;
        }}

        /* Hide rounds by default for pagination */
        .round-container.hidden {{
            display: none;
        }}

        /* Verification code section */
        .verification-section {{
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #e0e0e0;
        }}

        .verification-section h4 {{
            font-size: 13px;
            font-weight: 600;
            color: #666;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .verification-section h4 .toggle-btn {{
            background: #f0f0f0;
            border: 1px solid #ddd;
            color: #2563eb;
            padding: 4px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            font-weight: normal;
        }}

        .verification-section h4 .toggle-btn:hover {{
            background: #e5e5e5;
        }}

        .verification-code {{
            display: none;
            background: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 12px;
            font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            font-size: 12px;
            line-height: 1.4;
            overflow-x: auto;
            white-space: pre;
            color: #333;
        }}

        .verification-code.show {{
            display: block;
        }}

        .verification-message {{
            background: #f0f0f0;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 13px;
            color: #333;
            margin-bottom: 12px;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .agent-actions {{
                grid-template-columns: 1fr;
            }}

            .agents-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🎮 {html.escape(task_info.get("name", "Unknown Task"))}</h1>
            <p class="task-description">{html.escape(task_info.get("description", ""))}</p>
            <div class="primary-objective">
                <strong>🎯 Objective:</strong> {html.escape(task_def.get("objectives", {}).get("primary", "N/A"))}
            </div>
            <div class="task-meta">
                <div class="meta-item"><strong>Task ID:</strong> {html.escape(trajectory_data.get("task_id", "N/A"))}</div>
                <div class="meta-item"><strong>Timestamp:</strong> {html.escape(trajectory_data.get("timestamp", "N/A"))}</div>
                <div class="meta-item"><strong>Max Steps:</strong> {task_def.get("max_action_steps", "N/A")}</div>
            </div>
        </div>

        <!-- Metrics -->
        <div class="metrics-bar">
            <div class="metric-card">
                <div class="value">{metrics.get("total_rounds", len(rounds))}</div>
                <div class="label">Total Rounds</div>
            </div>
            <div class="metric-card">
                <div class="value">{metrics.get("total_agents", len(agents))}</div>
                <div class="label">Agents</div>
            </div>
            <div class="metric-card">
                <div class="value">{metrics.get("total_actions", 0)}</div>
                <div class="label">Actions</div>
            </div>
            <div class="metric-card">
                <div class="value">{metrics.get("total_chats", 0)}</div>
                <div class="label">Chats</div>
            </div>
            <div class="metric-card">
                <div class="value">{int(metrics.get("total_duration_seconds", 0) // 60)}m</div>
                <div class="label">Duration</div>
            </div>
        </div>

        <!-- Agent Cards -->
        <div class="agents-section">
            <h2>👥 Team Agents</h2>
            <div class="agents-grid">
'''

    # Add agent cards
    for idx, agent in enumerate(agents):
        color = get_agent_color(idx)
        skills_html = "".join([
            f'<span class="skill-tag">{html.escape(skill)}: {level}</span>'
            for skill, level in agent["skills"].items()
        ])
        inventory_items = ", ".join([
            f"{item.get('item', 'Unknown')} ({item.get('count', 1)}x)"
            for item in agent["inventory"][:5]
        ])

        html_content += f'''
                <div class="agent-card" style="border-color: {color};">
                    <div class="agent-header">
                        <div class="agent-avatar" style="background: {color};">👤</div>
                        <div>
                            <div class="agent-name">{html.escape(agent["username"])}</div>
                            <div class="agent-details">
                                Agent {agent["num"]} · Start: ({agent["location"].get("x", "?")}, {agent["location"].get("y", "?")})
                            </div>
                        </div>
                    </div>
                    <div class="agent-details">📦 {html.escape(inventory_items) if inventory_items else "Empty inventory"}</div>
                    <div class="skills-list">{skills_html}</div>
                </div>
'''

    html_content += '''
            </div>
        </div>

        <!-- Timeline -->
        <div class="timeline-section">
            <h2>📜 Action Timeline</h2>
            <div class="timeline-controls">
                <button onclick="showAllRounds()">Show All</button>
                <button onclick="showRound('first')">First</button>
                <button onclick="showRound('prev')">← Prev</button>
                <button onclick="showRound('next')">Next →</button>
                <button onclick="showRound('last')">Last</button>
                <div class="round-slider">
                    <div class="slider-label">Jump to round: <span id="slider-value">1</span></div>
                    <input type="range" min="1" max="''' + str(len(rounds)) + '''" value="1" oninput="jumpToRound(this.value)">
                </div>
            </div>
            <div id="rounds-container">
'''

    # Add rounds
    for round_data in rounds:
        round_num = round_data.get("round", 0)
        actions = round_data.get("actions", [])

        html_content += f'''
                <div class="round-container" data-round="{round_num}">
                    <div class="round-header">
                        <span class="round-number">Round {round_num}</span>
                    </div>
                    <div class="agent-actions">
'''

        for action_data in actions:
            agent_name = action_data.get("agent_name", "unknown")
            # Find agent index for color
            agent_idx = 0
            for i, a in enumerate(agents):
                if a["id"] == agent_name:
                    agent_idx = i
                    break

            color = get_agent_color(agent_idx)
            status = action_data.get("status", "")
            action = parse_action(action_data.get("action", ""))
            action_icon = get_action_icon(action["type"])
            observation = action_data.get("observation", "")
            obs_id = f"obs_{round_num}_{agent_name}"

            # Get full chat message from log if available
            action_display = action.get("params", action.get("raw", "")[:150])
            if action["type"] == "chat" and agent_name in chat_messages:
                agent_chats = chat_messages[agent_name]
                chat_idx = chat_indices.get(agent_name, 0)
                if chat_idx < len(agent_chats):
                    action_display = agent_chats[chat_idx]
                    chat_indices[agent_name] = chat_idx + 1

            # Format observation
            obs_html = format_observation(observation)

            html_content += f'''
                        <div class="agent-action-card" style="border-left-color: {color};">
                            <div class="agent-action-header">
                                <span class="agent-action-name">{html.escape(agent_name.replace("_", " ").title())}</span>
                                <span class="agent-status">{html.escape(status)}</span>
                            </div>
                            <div class="action-content">
                                <div class="action-type">{action_icon} {html.escape(action["type"])}</div>
                                <div class="action-params">{html.escape(action_display)}</div>
                            </div>
                            <button class="observation-toggle" onclick="toggleObservation('{obs_id}')">
                                👁️ View Observation
                            </button>
                            <div class="observation-content" id="{obs_id}">
                                {obs_html}
                            </div>
                        </div>
'''

        html_content += '''
                    </div>
                </div>
'''

    # Task Result section - run actual verification
    task_id = trajectory_data.get('task_id', '')
    score, verification_msg, verifier_code = run_verification(trajectory_data, task_id, version)

    task_success = score > 0
    result_class = "result-success" if task_success else "result-failure"
    result_icon = "✅" if task_success else "❌"
    result_text = "TASK SUCCEEDED" if task_success else "TASK FAILED"

    # Also show agent stats
    successful_agents = metrics.get("successful_agents", 0)
    failed_agents = metrics.get("failed_agents", 0)
    total_agents_count = metrics.get("total_agents", len(agents))

    html_content += f'''
        <div class="task-result {result_class}">
            <div class="result-header">
                <span class="result-icon">{result_icon}</span>
                <span class="result-text">{result_text}</span>
            </div>
            <div class="verification-message">
                <strong>Verification Result:</strong> {html.escape(verification_msg)}
            </div>
            <div class="result-details">
                <div class="result-stat">
                    <span class="stat-value">{score}</span>
                    <span class="stat-label">Score</span>
                </div>
                <div class="result-stat">
                    <span class="stat-value">{successful_agents}/{total_agents_count}</span>
                    <span class="stat-label">Agents Completed</span>
                </div>
                <div class="result-stat">
                    <span class="stat-value">{len(rounds)}</span>
                    <span class="stat-label">Rounds</span>
                </div>
            </div>
    '''

    # Add verification code section
    if verifier_code:
        html_content += f'''
            <div class="verification-section">
                <h4>
                    🔍 Verification Code
                    <button class="toggle-btn" onclick="toggleVerificationCode()">Show/Hide</button>
                </h4>
                <pre class="verification-code" id="verifier-code">{html.escape(verifier_code)}</pre>
            </div>
    '''

    html_content += '''
        </div>
'''

    html_content += '''
            </div>
        </div>
    </div>

    <script>
        let currentRound = 1;
        const totalRounds = ''' + str(len(rounds)) + ''';
        let showAll = true;

        function toggleObservation(id) {
            const elem = document.getElementById(id);
            elem.classList.toggle('show');
        }

        function toggleVerificationCode() {
            const elem = document.getElementById('verifier-code');
            elem.classList.toggle('show');
        }

        function updateRoundVisibility() {
            const containers = document.querySelectorAll('.round-container');
            containers.forEach(container => {
                const roundNum = parseInt(container.dataset.round);
                if (showAll || roundNum === currentRound) {
                    container.classList.remove('hidden');
                } else {
                    container.classList.add('hidden');
                }
            });
            document.getElementById('slider-value').textContent = currentRound;
            document.querySelector('input[type="range"]').value = currentRound;
        }

        function showAllRounds() {
            showAll = true;
            updateRoundVisibility();
        }

        function showRound(direction) {
            showAll = false;
            if (direction === 'first') {
                currentRound = 1;
            } else if (direction === 'last') {
                currentRound = totalRounds;
            } else if (direction === 'prev') {
                currentRound = Math.max(1, currentRound - 1);
            } else if (direction === 'next') {
                currentRound = Math.min(totalRounds, currentRound + 1);
            }
            updateRoundVisibility();
        }

        function jumpToRound(round) {
            showAll = false;
            currentRound = parseInt(round);
            updateRoundVisibility();
        }

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                showRound('prev');
            } else if (e.key === 'ArrowRight') {
                showRound('next');
            }
        });
    </script>
</body>
</html>
'''

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Generated visualization: {output_path}")
    print(f"   Task: {task_info.get('name', 'Unknown')}")
    print(f"   Rounds: {len(rounds)}")
    print(f"   Agents: {len(agents)}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate HTML visualization from agent trajectory JSON"
    )
    parser.add_argument(
        "input",
        help="Path to trajectory JSON file or directory containing trajectory files"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output HTML file path (default: trajectory_visualization.html)"
    )

    args = parser.parse_args()

    # Determine input file
    input_path = args.input
    if os.path.isdir(input_path):
        input_path = find_latest_trajectory(input_path)
        print(f"📂 Using latest trajectory: {input_path}")

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        # Default: same directory as input, with .html extension
        base_name = Path(input_path).stem
        output_dir = Path(input_path).parent
        output_path = str(output_dir / f"{base_name}.html")

    # Load trajectory data
    with open(input_path, 'r', encoding='utf-8') as f:
        trajectory_data = json.load(f)

    # Generate HTML (pass trajectory path for chat message extraction)
    generate_html(trajectory_data, output_path, trajectory_path=input_path)


if __name__ == "__main__":
    main()
