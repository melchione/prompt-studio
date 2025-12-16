#!/usr/bin/env python3
"""
Prompt Studio - Build System

Compiles prompts by resolving includes and wrapping protected tokens.
Protected tokens are wrapped in {% raw %}...{% endraw %} to prevent Jinja2 interpretation.

Usage:
    python tools/build.py --project cowai --agent executive
    python tools/build.py --project cowai --all
    python tools/build.py --project cowai --all --dry-run
    python tools/build.py --project cowai --stats

Options:
    --project NAME    Project to build
    --agent NAME      Agent to build (optional, builds all if omitted)
    --all             Build all agents
    --dry-run         Preview without writing files
    --stats           Show statistics only
    --verbose         Show wrapped tokens details

Auteur: Adapted from Cowai prompt_building scripts
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

# Configuration
STUDIO_ROOT = Path(__file__).parent.parent
PROJECTS_DIR = STUDIO_ROOT / "projects"
SUPPORTED_LANGS = ["fr", "en"]

# Default protected tokens if no file exists
DEFAULT_PROTECTED_TOKENS = [
    # Variables Jinja2
    "$current_date_and_time$",
    "$user_name$",
    "$session_id$",
    # XML tags
    "<instructions>",
    "</instructions>",
    "<context>",
    "</context>",
    "<examples>",
    "</examples>",
    "<output>",
    "</output>",
    # Tool markers
    "execute_step_tool",
    "find_tool",
    "update_state",
    # MCP prefixes
    "mcp__",
]


def load_protected_tokens(project_path: Path) -> List[str]:
    """
    Load protected tokens from project's protected_tokens.txt.

    Args:
        project_path: Path to the project

    Returns:
        List of tokens to protect
    """
    tokens_file = project_path / "protected_tokens.txt"

    if not tokens_file.exists():
        # Use defaults
        return DEFAULT_PROTECTED_TOKENS

    tokens = []
    for line in tokens_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        # Ignore comments and empty lines
        if line and not line.startswith("#"):
            tokens.append(line)

    return tokens


def create_wrapping_pattern(token: str) -> Tuple[str, str]:
    """
    Generate regex pattern and replacement for a token.

    Adapts pattern based on token type:
    - $VAR$ : exact match
    - {var} : exact match
    - mcp__ : word boundary
    - XML tags : exact match
    - ReAct patterns (THOUGHT:) : exact match

    Args:
        token: Token to wrap

    Returns:
        Tuple (regex_pattern, replacement_string)
    """
    escaped = re.escape(token)

    # Pattern $VAR$ - exact match
    if token.startswith("$") and token.endswith("$"):
        return (escaped, f"{{% raw %}}{token}{{% endraw %}}")

    # Pattern {var} - exact match
    if token.startswith("{") and token.endswith("}"):
        return (escaped, f"{{% raw %}}{token}{{% endraw %}}")

    # Pattern mcp__ - word boundary
    if token.startswith("mcp__"):
        return (rf"\b{escaped}\b", f"{{% raw %}}{token}{{% endraw %}}")

    # XML tags - exact match
    if token.startswith("<") or token.startswith("</"):
        return (escaped, f"{{% raw %}}{token}{{% endraw %}}")

    # ReAct patterns (THOUGHT:, ACTION:, OBSERVATION:) - exact match
    if token.endswith(":") and token.isupper():
        return (escaped, f"{{% raw %}}{token}{{% endraw %}}")

    # COMPOSIO services (all caps) - word boundary
    if token.isupper() and "_" not in token:
        return (rf"\b{escaped}\b", f"{{% raw %}}{token}{{% endraw %}}")

    # Names with underscore - word boundary
    if "_" in token:
        return (rf"\b{escaped}\b", f"{{% raw %}}{token}{{% endraw %}}")

    # Default - word boundary
    return (rf"\b{escaped}\b", f"{{% raw %}}{token}{{% endraw %}}")


def wrap_protected_tokens(content: str, tokens: List[str], verbose: bool = False) -> Tuple[str, int]:
    """
    Wrap protected tokens in {% raw %}...{% endraw %}.

    Args:
        content: Raw content
        tokens: List of tokens to protect
        verbose: Print found tokens

    Returns:
        Tuple (wrapped_content, count_of_wrapped_tokens)
    """
    wrapped_count = 0

    for token in tokens:
        pattern, replacement = create_wrapping_pattern(token)

        # Count occurrences before wrapping
        matches = re.findall(pattern, content)
        if matches:
            wrapped_count += len(matches)
            if verbose:
                print(f"    ✓ {token} ({len(matches)}x)")

        # Apply wrapping
        content = re.sub(pattern, replacement, content)

    return content, wrapped_count


def resolve_includes(content: str, project_path: Path, lang: str, visited: set = None) -> str:
    """
    Resolve {% include 'agent/filename.md' %} directives.

    Args:
        content: Content with include directives
        project_path: Path to the project
        lang: Language code (fr, en)
        visited: Set of already visited paths (circular detection)

    Returns:
        Content with includes resolved

    Raises:
        ValueError: Circular include detected
        FileNotFoundError: Include file not found
    """
    if visited is None:
        visited = set()

    # Pattern: {% include 'agent/filename.md' %} or {% include "agent/lang/filename.md" %}
    pattern = r"\{%\s*include\s*['\"]([^'\"]+)['\"]\s*%\}"

    def replace_include(match):
        path = match.group(1)

        # Circular detection
        if path in visited:
            raise ValueError(f"Circular include detected: {path}")

        visited_copy = visited.copy()
        visited_copy.add(path)

        # Parse path: 'agent/filename.md' or 'agent/lang/filename.md'
        parts = path.split('/')

        if len(parts) == 2:
            # Format: agent/filename.md -> use current lang
            agent, filename = parts
            include_path = project_path / "agents" / agent / lang / filename
        elif len(parts) == 3:
            # Format: agent/lang/filename.md -> explicit lang
            agent, include_lang, filename = parts
            include_path = project_path / "agents" / agent / include_lang / filename
        else:
            raise ValueError(f"Invalid include path format: {path}. Expected 'agent/filename.md' or 'agent/lang/filename.md'")

        if not include_path.exists():
            raise FileNotFoundError(f"Include not found: {include_path}")

        # Read and recursively resolve
        included_content = include_path.read_text(encoding="utf-8")
        return resolve_includes(included_content, project_path, lang, visited_copy)

    return re.sub(pattern, replace_include, content)


def get_sections(agent_path: Path, lang: str) -> List[str]:
    """
    Get list of sections for an agent/language.

    Args:
        agent_path: Path to agent directory
        lang: Language code

    Returns:
        List of section filenames sorted by number
    """
    sections_dir = agent_path / lang

    if not sections_dir.exists():
        return []

    sections = []
    for f in sorted(sections_dir.glob("*.md")):
        # Include files starting with a number
        if re.match(r"^\d{2}-", f.name):
            sections.append(f.name)

    return sections


def count_tokens_estimate(content: str) -> int:
    """
    Approximate LLM token count.

    Rule: ~4 characters = 1 token (average for Claude/GPT)

    Args:
        content: Content to count

    Returns:
        Estimated token count
    """
    return len(content) // 4


def generate_header(project_name: str, agent_name: str, lang: str, version: str) -> str:
    """Generate header comment for compiled prompt."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""{{#
Prompt Studio Build
Project: {project_name}
Agent: {agent_name}
Version: {version}
Language: {lang}
Built: {now}

GENERATED AUTOMATICALLY - DO NOT EDIT DIRECTLY
Protected tokens are wrapped in {{% raw %}}...{{% endraw %}} for Jinja2.
#}}
"""


def build_agent(
    project_name: str,
    project_path: Path,
    agent_name: str,
    tokens: List[str],
    dry_run: bool = False,
    verbose: bool = False
) -> dict:
    """
    Build an agent for all languages.

    Args:
        project_name: Name of the project
        project_path: Path to the project
        agent_name: Name of the agent
        tokens: Protected tokens list
        dry_run: Don't write files
        verbose: Show details

    Returns:
        Dict with stats per language
    """
    agent_path = project_path / "agents" / agent_name

    if not agent_path.exists():
        print(f"  ⏭️  Agent not found: {agent_name}")
        return {"status": "skipped"}

    # Get project version
    config_path = project_path / ".project.json"
    version = "0.0.0"
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
            version = config.get("version", "0.0.0")

    results = {}

    for lang in SUPPORTED_LANGS:
        sections = get_sections(agent_path, lang)

        if not sections:
            continue

        print(f"\n  📖 Building {agent_name}/{lang}...")

        # Read all sections
        sections_content = []
        total_source_lines = 0
        includes_resolved = 0

        for section_file in sections:
            section_path = agent_path / lang / section_file
            content = section_path.read_text(encoding="utf-8")
            line_count = len(content.splitlines())
            total_source_lines += line_count

            # Resolve includes BEFORE wrapping
            try:
                includes_count = content.count("{% include")
                resolved_content = resolve_includes(content, project_path, lang)
                includes_resolved += includes_count
                if includes_count > 0 and verbose:
                    print(f"     ↪ {section_file}: {includes_count} include(s) resolved")
            except (ValueError, FileNotFoundError) as e:
                print(f"     ❌ Include error in {section_file}: {e}")
                raise

            # Wrap protected tokens
            wrapped_content, _ = wrap_protected_tokens(resolved_content, tokens, verbose=verbose)
            sections_content.append(wrapped_content)

            print(f"     ✓ {section_file} ({line_count} lines)")

        # Assemble final content
        prompt_parts = []

        # Add header
        header = generate_header(project_name, agent_name, lang, version)
        prompt_parts.append(header)

        # Add sections with markers
        for i, (section_file, content) in enumerate(zip(sections, sections_content)):
            section_marker = f"\n{{# Section: {section_file} #}}\n"
            prompt_parts.append(section_marker + content.strip())

            # Add blank line between sections
            if i < len(sections) - 1:
                prompt_parts.append("")

        final_content = "\n".join(prompt_parts)

        if includes_resolved > 0:
            print(f"     📎 {includes_resolved} include(s) resolved")

        # Stats
        final_lines = len(final_content.splitlines())
        char_count = len(final_content)
        token_estimate = count_tokens_estimate(final_content)

        # Write to dist/
        output_file = project_path / "dist" / lang / f"{agent_name}.md"

        if not dry_run:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(final_content, encoding="utf-8")
            print(f"     → Written to dist/{lang}/{agent_name}.md")
        else:
            print(f"     → DRY RUN: Would write to dist/{lang}/{agent_name}.md")

        print(f"     📊 {len(sections)} sections | {total_source_lines:,} → {final_lines:,} lines | ~{token_estimate:,} tokens")

        results[lang] = {
            "output": str(output_file),
            "sections": len(sections),
            "source_lines": total_source_lines,
            "final_lines": final_lines,
            "chars": char_count,
            "tokens": token_estimate,
            "includes_resolved": includes_resolved,
            "status": "success"
        }

    return results


def build_project(
    project_name: str,
    tokens: List[str],
    dry_run: bool = False,
    verbose: bool = False
) -> dict:
    """
    Build all agents in a project.

    Args:
        project_name: Name of the project
        tokens: Protected tokens list
        dry_run: Don't write files
        verbose: Show details

    Returns:
        Dict with stats per agent
    """
    project_path = PROJECTS_DIR / project_name

    if not project_path.exists():
        raise FileNotFoundError(f"Project not found: {project_name}")

    agents_dir = project_path / "agents"
    if not agents_dir.exists():
        raise FileNotFoundError(f"No agents directory in project: {project_name}")

    agents = [
        d.name for d in agents_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ]

    if not agents:
        raise FileNotFoundError(f"No agents found in {project_name}")

    results = {}
    success_count = 0
    skip_count = 0

    for agent_name in sorted(agents):
        print(f"\n🔄 Building: {agent_name}")
        try:
            result = build_agent(
                project_name=project_name,
                project_path=project_path,
                agent_name=agent_name,
                tokens=tokens,
                dry_run=dry_run,
                verbose=verbose
            )
            results[agent_name] = result
            if result.get("status") == "skipped":
                skip_count += 1
            else:
                success_count += 1
        except Exception as e:
            results[agent_name] = {"status": "error", "error": str(e)}
            print(f"  ❌ Error: {e}")

    # Summary
    print(f"\n{'='*50}")
    print(f"✅ Built: {success_count} | ⏭️ Skipped: {skip_count}")

    if not dry_run:
        print(f"📁 Output: {project_path / 'dist'}")
    else:
        print("ℹ️  DRY RUN - No files written")

    return results


def print_stats(project_name: str, tokens: List[str]):
    """Print project statistics."""
    project_path = PROJECTS_DIR / project_name

    print(f"\n📊 Statistics for project: {project_name}\n")
    print(f"Protected tokens: {len(tokens)}")
    print(f"Supported languages: {', '.join(SUPPORTED_LANGS)}")
    print()

    # List available agents
    agents_dir = project_path / "agents"
    if agents_dir.exists():
        print("Available agents:")
        for agent_dir in sorted(agents_dir.iterdir()):
            if agent_dir.is_dir() and not agent_dir.name.startswith("."):
                for lang in SUPPORTED_LANGS:
                    sections = get_sections(agent_dir, lang)
                    if sections:
                        print(f"  ✓ {agent_dir.name}/{lang}: {len(sections)} sections")
    print()

    # List existing dist files
    dist_dir = project_path / "dist"
    if dist_dir.exists():
        print("Generated prompts (dist/):")
        for lang in SUPPORTED_LANGS:
            lang_dir = dist_dir / lang
            if lang_dir.exists():
                for f in sorted(lang_dir.glob("*.md")):
                    content = f.read_text(encoding="utf-8")
                    lines = len(content.splitlines())
                    tokens_est = count_tokens_estimate(content)
                    print(f"  ✓ {lang}/{f.name}: {lines:,} lines | ~{tokens_est:,} tokens")


def update_state(project_path: Path, last_build: str):
    """Update last build timestamp in project config."""
    config_path = project_path / ".project.json"

    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {}

    config["last_build"] = last_build

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build prompts for Prompt Studio projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/build.py --project cowai --agent executive
  python tools/build.py --project cowai --all
  python tools/build.py --project cowai --all --dry-run
  python tools/build.py --project cowai --stats
"""
    )
    parser.add_argument("--project", "-p", required=True, help="Project name")
    parser.add_argument("--agent", "-a", help="Agent name (optional, builds all if omitted)")
    parser.add_argument("--all", action="store_true", help="Build all agents")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show wrapped tokens details")

    args = parser.parse_args()

    project_path = PROJECTS_DIR / args.project

    if not project_path.exists():
        print(f"❌ Project not found: {args.project}")
        sys.exit(1)

    try:
        # Load protected tokens
        tokens = load_protected_tokens(project_path)
        print(f"\n🔒 Loaded {len(tokens)} protected tokens")

        print()
        print("=" * 50)
        print("   PROMPT STUDIO BUILD")
        print("=" * 50)
        print(f"📁 Project: {args.project}")

        if args.stats:
            print_stats(args.project, tokens)
        elif args.all or not args.agent:
            build_project(args.project, tokens, dry_run=args.dry_run, verbose=args.verbose)

            # Update state
            if not args.dry_run:
                timestamp = datetime.now(timezone.utc).isoformat()
                update_state(project_path, timestamp)
        else:
            print(f"🤖 Agent: {args.agent}")
            build_agent(
                project_name=args.project,
                project_path=project_path,
                agent_name=args.agent,
                tokens=tokens,
                dry_run=args.dry_run,
                verbose=args.verbose
            )
            print("\n✅ Build complete!")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
