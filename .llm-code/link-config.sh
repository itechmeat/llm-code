#!/usr/bin/env bash
#
# link-config.sh
#
# Configuration for link-assets.sh
# Edit this file to add new tools or asset type mappings.
#
# Compatible with bash 3.2+ (macOS default)
#

# --- Mappings ---
# Each entry: "parent_dir:target_name:asset_dir"
#
# - parent_dir: Tool's config directory (e.g., .claude, .github)
# - target_name: Symlink name to create (e.g., skills, skill)
# - asset_dir: Directory name in .llm-code to link to (e.g., skills)
#
# Add new tools by adding new entries to this array.
#
MAPPINGS=(
    # Claude Code
    ".claude:skills:skills"
    # ".claude:agents:agents"
    # ".claude:commands:commands"

    # GitHub Copilot
    ".github:skills:skills"
    # ".github:agents:agents"
    # ".github:instructions:instructions"

    # OpenCode (uses "skill" instead of "skills")
    ".opencode:skill:skills"

    # OpenAI Codex
    ".codex:skills:skills"

    # OpenAI Codex
    ".codex:skills:skills"

    # Gemini
    ".gemini:skills:skills"

    # Cursor
    ".cursor:skills:skills"

    # Qwen
    ".qwen:skills:skills"

    # Droid
    ".factory:skills:skills"

    # Aider
    ".aider:skills:skills"

    # Continue.dev
    ".continue:skills:skills"
)
