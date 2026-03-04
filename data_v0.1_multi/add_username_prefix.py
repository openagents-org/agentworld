#!/usr/bin/env python3
"""
Add task ID prefix (tNN_) to agent usernames in benchmark YAML files.

Targets: task_46 through task_60, and task_62.
Updates ALL references to each username throughout the file.
"""

import re
import glob
import os

BENCHMARK_DIR = "/home/ubuntu/works/agentworld/data_v0.1_multi/v1.3_benchmark"

# Tasks that need fixing
TASK_NUMBERS = list(range(46, 61)) + [62]  # 46-60 and 62


def extract_usernames(content):
    """Extract all usernames from username: fields in the YAML content."""
    # Match both quoted and unquoted usernames
    pattern_quoted = r'username:\s*"([^"]+)"'
    quoted = re.findall(pattern_quoted, content)

    # Pattern for unquoted (handles inline YAML like {username: Foo, ...})
    pattern_unquoted = r'username:\s+([^\s"#\{][^\s#,\}]*)'
    unquoted = re.findall(pattern_unquoted, content)

    # Combine and deduplicate while preserving order
    seen = set()
    usernames = []
    for u in quoted + unquoted:
        u = u.strip()
        if u not in seen:
            seen.add(u)
            usernames.append(u)

    return usernames


def add_prefix_to_file(filepath, task_num):
    """Add tNN_ prefix to all usernames in the given file."""
    prefix = f"t{task_num:02d}_"

    with open(filepath, 'r') as f:
        content = f.read()

    usernames = extract_usernames(content)

    if not usernames:
        print(f"  WARNING: No usernames found in {os.path.basename(filepath)}")
        return False

    # Check if already prefixed
    already_prefixed = all(u.startswith(prefix) for u in usernames)
    if already_prefixed:
        print(f"  SKIP: {os.path.basename(filepath)} - already prefixed")
        return False

    print(f"  Found usernames: {usernames}")

    # Sort usernames by length (longest first) to avoid partial replacements
    usernames_sorted = sorted(usernames, key=len, reverse=True)

    modified = content
    for username in usernames_sorted:
        new_username = prefix + username

        # Count occurrences before replacement
        count = modified.count(username)

        if count == 0:
            print(f"  WARNING: Username '{username}' not found in content")
            continue

        # Use regex with word boundaries to replace exact username references
        # \b works for word boundaries - matches between \w and \W
        # This prevents replacing substrings of longer words
        # BUT: usernames like "Weaponsmith" in "Weaponsmith Consortium" (task name)
        # would still match. We handle task name specially below.
        
        # For most usernames with underscores or numbers, simple replace is fine
        # since they won't appear as substrings of other words
        if '_' in username or any(c.isdigit() for c in username):
            # Safe to do simple replace - underscore/digit names won't be common words
            modified = modified.replace(username, new_username)
            print(f"  {username} -> {new_username} ({count} occurrences)")
        else:
            # For simple word usernames (like "Smelter", "Weaponsmith"),
            # use word-boundary regex but protect task name/description lines
            
            # First, protect the task name and description from replacement
            # by using a placeholder
            lines = modified.split('\n')
            protected_indices = set()
            for i, line in enumerate(lines):
                stripped = line.strip()
                # Protect task name and description lines
                if stripped.startswith('name:') or stripped.startswith('description:'):
                    protected_indices.add(i)
            
            new_lines = []
            replaced_count = 0
            for i, line in enumerate(lines):
                if i in protected_indices:
                    new_lines.append(line)
                else:
                    # Replace using word boundaries
                    new_line = re.sub(r'\b' + re.escape(username) + r'\b', new_username, line)
                    if new_line != line:
                        replaced_count += line.count(username)
                    new_lines.append(new_line)
            
            modified = '\n'.join(new_lines)
            print(f"  {username} -> {new_username} ({replaced_count} occurrences, protected name/desc)")

    # Verify no double-prefixing happened
    for username in usernames_sorted:
        double_prefix = prefix + prefix + username
        if double_prefix in modified:
            print(f"  ERROR: Double prefix detected for {username}!")
            return False

    with open(filepath, 'w') as f:
        f.write(modified)

    return True


def main():
    total_modified = 0
    for task_num in TASK_NUMBERS:
        # Find the file for this task number
        pattern = os.path.join(BENCHMARK_DIR, f"task_{task_num:02d}_*.yaml")
        # Exclude backup files and temp files
        files = [f for f in glob.glob(pattern)
                 if not f.endswith('.backup') and '.tmp.' not in f]

        if not files:
            print(f"WARNING: No file found for task_{task_num:02d}")
            continue

        if len(files) > 1:
            print(f"WARNING: Multiple files found for task_{task_num:02d}: {files}")
            continue

        filepath = files[0]
        print(f"\nProcessing: {os.path.basename(filepath)} (task {task_num})")
        if add_prefix_to_file(filepath, task_num):
            total_modified += 1

    print(f"\n{'='*60}")
    print(f"Modified {total_modified} files")


if __name__ == "__main__":
    main()
