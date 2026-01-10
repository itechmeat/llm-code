#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="${SCRIPT_DIR}/link-config.sh"
ASSETS_ROOT="${SCRIPT_DIR}"
MAPPINGS=()
TOOL_FILTER=()

print_usage() {
    cat << 'EOF'
Usage: link-assets.sh [OPTIONS]

Creates symlinks in the parent directory of .llm-code.

Options:
  -h, --help         Show this help message
  -n, --dry-run      Show what would be done without making changes
  -v, --verbose      Verbose output
  -l, --list         List configured mappings
  -t, --tool TOOL    Only process mappings for TOOL (can be repeated)

Examples:
  .llm-code/link-assets.sh                   # Link all tools
  .llm-code/link-assets.sh -t claude          # Link only Claude
  .llm-code/link-assets.sh -t claude -t github # Link Claude and GitHub
  .llm-code/link-assets.sh --dry-run          # Preview changes
  .llm-code/link-assets.sh --list             # Show configuration
EOF
}

load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        source "$CONFIG_FILE"
    else
        MAPPINGS=(
            ".claude:skills:skills"
            # ".claude:agents:agents"
            # ".claude:commands:commands"
            ".github:skills:skills"
            # ".github:agents:agents"
            # ".github:instructions:instructions"
            ".opencode:skill:skills"
            ".codex:skills:skills"
            ".gemini:skills:skills"
            ".cursor:skills:skills"
            ".qwen:skills:skills"
            ".factory:skills:skills"
            ".aider:skills:skills"
            ".continue:skills:skills"
        )
    fi
}

list_config() {
    echo "Mappings:"
    printf "  %-20s %-15s %-15s %s\n" "TOOL" "SYMLINK" "ASSET" "STATUS"
    for mapping in "${MAPPINGS[@]}"; do
        IFS=':' read -r parent_dir target_name asset_dir <<< "$mapping"
        local source_path="${ASSETS_ROOT}/${asset_dir}"
        local status="missing"
        [[ -d "$source_path" ]] && status="ready"
        printf "  %-20s %-15s %-15s %s\n" "$parent_dir" "$target_name" "$asset_dir" "$status"
    done
    echo ""
    echo "Tool names for -t filter:"
    local tools=""
    for mapping in "${MAPPINGS[@]}"; do
        IFS=':' read -r parent_dir _ _ <<< "$mapping"
        local tool_name="${parent_dir#.}"
        if [[ "$tools" != *"|${tool_name}|"* ]]; then
            tools="${tools}|${tool_name}|"
            echo "  ${tool_name}"
        fi
    done
}

tool_matches_filter() {
    local parent_dir="$1"
    local tool_name="${parent_dir#.}"
    if [[ ${#TOOL_FILTER[@]} -eq 0 ]]; then return 0; fi
    for filter_tool in "${TOOL_FILTER[@]}"; do
        if [[ "$filter_tool" == "$tool_name" ]]; then return 0; fi
    done
    return 1
}

create_symlink() {
    local parent_dir="$1" target_name="$2" asset_dir="$3" dry_run="$4" verbose="$5"
    local full_parent="${PROJECT_ROOT}/${parent_dir}"
    local symlink_path="${full_parent}/${target_name}"
    local source_path="${ASSETS_ROOT}/${asset_dir}"

    [[ ! -d "$source_path" ]] && return 0

    if [[ "$dry_run" == "true" ]]; then
        if [[ -L "$symlink_path" ]]; then echo "  [DRY] Would replace symlink: ${parent_dir}/${target_name}"
        elif [[ -d "$symlink_path" ]]; then echo "  [DRY] Would replace directory: ${parent_dir}/${target_name}/"
        else echo "  [DRY] Would create: ${parent_dir}/${target_name}"
        fi
        return 0
    fi

    [[ ! -d "$full_parent" ]] && mkdir -p "$full_parent"
    [[ -L "$symlink_path" ]] && rm "$symlink_path"
    [[ -d "$symlink_path" ]] && rm -rf "$symlink_path"

    local rel_source="../.llm-code/${asset_dir}"
    ln -s "$rel_source" "$symlink_path"
    echo "  + ${parent_dir}/${target_name} -> ${rel_source}"
}

DRY_RUN="false"
VERBOSE="false"
LIST_MODE="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help) print_usage; exit 0 ;;
        -n|--dry-run) DRY_RUN="true"; shift ;;
        -v|--verbose) VERBOSE="true"; shift ;;
        -l|--list) LIST_MODE="true"; shift ;;
        -t|--tool) TOOL_FILTER+=("$2"); shift 2 ;;
        -*) echo "Unknown: $1"; exit 1 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

load_config

if [[ "$LIST_MODE" == "true" ]]; then list_config; exit 0; fi

echo "Linking LLM assets"
echo "Project: ${PROJECT_ROOT}"
echo "Source:  .llm-code/"
[[ "$DRY_RUN" == "true" ]] && echo "Mode:    DRY RUN"
[[ ${#TOOL_FILTER[@]} -gt 0 ]] && echo "Tools:   ${TOOL_FILTER[*]}"
echo ""

for mapping in "${MAPPINGS[@]}"; do
    IFS=':' read -r parent_dir target_name asset_dir <<< "$mapping"
    tool_matches_filter "$parent_dir" || continue
    create_symlink "$parent_dir" "$target_name" "$asset_dir" "$DRY_RUN" "$VERBOSE"
done

echo ""
echo "Done!"
