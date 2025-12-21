#!/usr/bin/env python3
"""
Prompt Studio - Expand/Collapse Includes for Editing

Ce script permet d'éditer les fichiers avec includes de manière transparente :
- expand : Remplace les {% include %} par leur contenu avec marqueurs
- collapse : Parse les marqueurs et sauvegarde dans les fichiers sources

Les marqueurs utilisés :
    <!-- @include-start: agent/section.md -->
    ... contenu ...
    <!-- @include-end: agent/section.md -->

Usage:
    python tools/expand.py expand --project cowai --agent executive --lang fr --section 02-instructions.md
    python tools/expand.py expand --project cowai --agent executive --lang fr --section 02-instructions.md --html > preview.html
    python tools/expand.py collapse --project cowai --agent executive --lang fr --section 02-instructions.md --input expanded.md
    python tools/expand.py list --project cowai --agent executive --lang fr --section 02-instructions.md

Auteur: Adapted from Cowai prompt_building scripts
"""

import argparse
import html as html_module
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Configuration
STUDIO_ROOT = Path(__file__).parent.parent
PROJECTS_DIR = STUDIO_ROOT / "projects"

# Markers
INCLUDE_START = "<!-- @include-start: {path} -->"
INCLUDE_END = "<!-- @include-end: {path} -->"
LOCAL_START = "<!-- @local-start -->"
LOCAL_END = "<!-- @local-end -->"

# Patterns
INCLUDE_PATTERN = r"\{%\s*include\s*['\"]([^'\"]+)['\"]\s*%\}"
MARKER_START_PATTERN = r"<!-- @include-start: ([^>]+) -->"
MARKER_END_PATTERN = r"<!-- @include-end: ([^>]+) -->"


def get_project_agents_dir(project: str) -> Path:
    """Get the agents directory for a project."""
    return PROJECTS_DIR / project / "agents"


def get_include_path(include_ref: str, project: str, lang: str) -> Path:
    """
    Resolve an include path.

    Args:
        include_ref: Reference like 'common/01-context.md' or 'executive/fr/02-instructions.md'
        project: Project name
        lang: Language code (fr, en)

    Returns:
        Path to the include file
    """
    agents_dir = get_project_agents_dir(project)
    parts = include_ref.split('/')

    # Format: agent/section.md (language inferred) or agent/lang/section.md (explicit)
    if len(parts) == 2:
        # agent/section.md - use current language
        agent, filename = parts
        return agents_dir / agent / lang / filename
    elif len(parts) == 3:
        # agent/lang/section.md - explicit language
        agent, inc_lang, filename = parts
        return agents_dir / agent / inc_lang / filename
    else:
        raise ValueError(f"Invalid include format: {include_ref}. Expected: agent/section.md or agent/lang/section.md")


def expand_includes(
    content: str,
    project: str,
    lang: str,
    highlight_local: bool = False,
    depth: int = 0,
    max_depth: int = 10
) -> str:
    """
    Replace {% include %} with content and markers.

    Args:
        content: Content with include directives
        project: Project name
        lang: Language code
        highlight_local: If True, add markers for local content
        depth: Current recursion depth
        max_depth: Maximum include depth

    Returns:
        Expanded content with markers
    """
    if depth > max_depth:
        raise RecursionError(f"Maximum include depth ({max_depth}) exceeded")

    # Find all includes
    include_matches = list(re.finditer(INCLUDE_PATTERN, content))

    if not include_matches:
        if highlight_local:
            return f"{LOCAL_START}\n{content}\n{LOCAL_END}"
        return content

    result_parts = []
    last_end = 0

    for match in include_matches:
        # Local content before this include
        local_content = content[last_end:match.start()]
        if local_content.strip():
            if highlight_local:
                result_parts.append(f"{LOCAL_START}\n{local_content.rstrip()}\n{LOCAL_END}")
            else:
                result_parts.append(local_content.rstrip())

        # Resolve the include
        include_ref = match.group(1)
        try:
            include_path = get_include_path(include_ref, project, lang)

            if not include_path.exists():
                # Include not found - keep original directive with error comment
                error_msg = f"<!-- ⚠️ INCLUDE NOT FOUND: {include_ref} -->"
                result_parts.append(f"\n{error_msg}\n{match.group(0)}")
                last_end = match.end()
                continue

            included_content = include_path.read_text(encoding="utf-8").rstrip()

            # Recursively expand nested includes
            included_content = expand_includes(
                included_content, project, lang,
                highlight_local=False,  # Don't highlight nested includes
                depth=depth + 1,
                max_depth=max_depth
            )

            # Add markers
            start_marker = INCLUDE_START.format(path=include_ref)
            end_marker = INCLUDE_END.format(path=include_ref)

            result_parts.append(f"\n{start_marker}\n{included_content}\n{end_marker}")
        except Exception as e:
            # On error, keep original directive with error comment
            error_msg = f"<!-- ⚠️ INCLUDE ERROR ({include_ref}): {str(e)} -->"
            result_parts.append(f"\n{error_msg}\n{match.group(0)}")

        last_end = match.end()

    # Local content after last include
    remaining = content[last_end:]
    if remaining.strip():
        if highlight_local:
            result_parts.append(f"\n{LOCAL_START}\n{remaining.strip()}\n{LOCAL_END}")
        else:
            result_parts.append(remaining)

    return ''.join(result_parts)


def collapse_includes(content: str, lang: str) -> Tuple[str, Dict[str, str]]:
    """
    Parse markers and extract content for each source file.

    Args:
        content: Expanded content with markers
        lang: Language code

    Returns:
        Tuple (collapsed_content, modified_files_dict)
        - collapsed_content: Main file with {% include %} restored
        - modified_files_dict: {include_ref: new_content}
    """
    modified_files = {}

    # Pattern to capture include blocks
    block_pattern = r"<!-- @include-start: ([^>]+) -->\n(.*?)\n<!-- @include-end: \1 -->"

    def extract_and_replace(match):
        include_ref = match.group(1)
        included_content = match.group(2)

        # Store modified content
        modified_files[include_ref] = included_content

        # Restore {% include %}
        return f"{{% include '{include_ref}' %}}"

    collapsed = re.sub(block_pattern, extract_and_replace, content, flags=re.DOTALL)

    # Remove local markers if present
    collapsed = re.sub(r"<!-- @local-start -->\n?", "", collapsed)
    collapsed = re.sub(r"\n?<!-- @local-end -->", "", collapsed)

    return collapsed, modified_files


def expand_file(
    project: str,
    agent: str,
    lang: str,
    section: str,
    highlight_local: bool = False
) -> str:
    """
    Expand a file and return expanded content.

    Args:
        project: Project name
        agent: Agent name
        lang: Language code
        section: Section filename
        highlight_local: Add markers for local content

    Returns:
        Expanded content
    """
    agents_dir = get_project_agents_dir(project)
    full_path = agents_dir / agent / lang / section

    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {full_path}")

    content = full_path.read_text(encoding="utf-8")
    expanded = expand_includes(content, project, lang, highlight_local=highlight_local)

    return expanded


def render_block(lines: List[str], block_type: str, path: str = None) -> str:
    """Render an HTML block."""
    content = html_module.escape('\n'.join(lines))
    css_class = "local-block" if block_type == 'local' else "include-block"

    if block_type == 'include' and path:
        marker = f'<div class="marker">Include: <span class="include-path">{html_module.escape(path)}</span></div>'
    else:
        marker = '<div class="marker">Contenu local</div>'

    return f'<div class="{css_class}">{marker}<pre>{content}</pre></div>'


def generate_html_preview(content: str, title: str = "Prompt Preview") -> str:
    """
    Generate an HTML preview with color-coded sections.

    - Green: Local content (specific to this agent)
    - Blue: Included content (shared via include)

    Args:
        content: Expanded content with markers
        title: Page title

    Returns:
        Complete HTML
    """
    css = """
    <style>
        body {
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
            font-size: 14px;
            line-height: 1.6;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background: #1e1e1e;
            color: #d4d4d4;
        }
        h1 {
            color: #569cd6;
            border-bottom: 1px solid #444;
            padding-bottom: 10px;
        }
        .legend {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            padding: 10px;
            background: #252526;
            border-radius: 4px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }
        .local-block {
            background: rgba(78, 201, 176, 0.15);
            border-left: 3px solid #4ec9b0;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 0 4px 4px 0;
        }
        .include-block {
            background: rgba(86, 156, 214, 0.15);
            border-left: 3px solid #569cd6;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 0 4px 4px 0;
        }
        .marker {
            font-size: 11px;
            color: #808080;
            font-style: italic;
            margin-bottom: 5px;
        }
        .include-path {
            color: #ce9178;
            font-weight: bold;
        }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            margin: 0;
        }
        .content {
            background: #2d2d2d;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
        }
    </style>
    """

    html_parts = [f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{html_module.escape(title)}</title>
    {css}
</head>
<body>
    <h1>{html_module.escape(title)}</h1>
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background: rgba(78, 201, 176, 0.4);"></div>
            <span>Contenu LOCAL (specifique a cet agent)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: rgba(86, 156, 214, 0.4);"></div>
            <span>Contenu INCLUS (partage via include)</span>
        </div>
    </div>
    <div class="content">
"""]

    # Parse blocks
    lines = content.split('\n')
    current_block = []
    current_type = None
    current_path = None

    for line in lines:
        local_start = line.strip() == LOCAL_START
        local_end = line.strip() == LOCAL_END
        include_start_match = re.match(MARKER_START_PATTERN, line.strip())
        include_end_match = re.match(MARKER_END_PATTERN, line.strip())

        if local_start:
            if current_block and current_type:
                html_parts.append(render_block(current_block, current_type, current_path))
            current_block = []
            current_type = 'local'
            current_path = None
        elif local_end:
            if current_block:
                html_parts.append(render_block(current_block, current_type, current_path))
            current_block = []
            current_type = None
        elif include_start_match:
            if current_block and current_type:
                html_parts.append(render_block(current_block, current_type, current_path))
            current_block = []
            current_type = 'include'
            current_path = include_start_match.group(1)
        elif include_end_match:
            if current_block:
                html_parts.append(render_block(current_block, current_type, current_path))
            current_block = []
            current_type = None
            current_path = None
        else:
            if current_type:
                current_block.append(line)
            else:
                if line.strip():
                    html_parts.append(f"<pre>{html_module.escape(line)}</pre>")

    if current_block and current_type:
        html_parts.append(render_block(current_block, current_type, current_path))

    html_parts.append("""
    </div>
</body>
</html>""")

    return ''.join(html_parts)


def collapse_and_save(
    project: str,
    agent: str,
    lang: str,
    section: str,
    expanded_content: str,
    dry_run: bool = False
) -> Dict[str, str]:
    """
    Collapse content and save to source files.

    Args:
        project: Project name
        agent: Agent name
        lang: Language code
        section: Section filename
        expanded_content: Expanded content to save
        dry_run: If True, don't write files

    Returns:
        Dict of modified files with their new content
    """
    agents_dir = get_project_agents_dir(project)
    full_path = agents_dir / agent / lang / section

    collapsed, modified_files = collapse_includes(expanded_content, lang)

    if not dry_run:
        # Save main file
        full_path.write_text(collapsed, encoding="utf-8")
        print(f"  Saved: {project}/{agent}/{lang}/{section}")

        # Save modified includes
        for include_ref, content in modified_files.items():
            include_path = get_include_path(include_ref, project, lang)
            include_path.parent.mkdir(parents=True, exist_ok=True)
            include_path.write_text(content + "\n", encoding="utf-8")
            print(f"  Saved include: {include_ref}")
    else:
        print(f"  DRY RUN: Would save {project}/{agent}/{lang}/{section}")
        for include_ref in modified_files:
            print(f"  DRY RUN: Would save include: {include_ref}")

    return modified_files


def edit_file(project: str, agent: str, lang: str, section: str, editor: str = None):
    """
    Expand file, open editor, then collapse and save.

    Args:
        project: Project name
        agent: Agent name
        lang: Language code
        section: Section filename
        editor: Editor to use (default: $EDITOR or vim)
    """
    if editor is None:
        editor = os.environ.get('EDITOR', 'vim')

    print(f"\nExpanding {project}/{agent}/{lang}/{section}...")
    expanded = expand_file(project, agent, lang, section)

    with tempfile.NamedTemporaryFile(mode='w', suffix=f"_{section}", delete=False, encoding='utf-8') as tmp:
        tmp.write(expanded)
        tmp_path = tmp.name

    print(f"  Temp file: {tmp_path}")
    print(f"\nOpening editor: {editor}")
    print("  (Save and close to apply changes, or close without saving to cancel)\n")

    try:
        result = subprocess.run([editor, tmp_path])

        if result.returncode != 0:
            print(f"Editor exited with error code {result.returncode}")
            return

        modified_content = Path(tmp_path).read_text(encoding='utf-8')

        if modified_content == expanded:
            print("\nNo changes detected, skipping save")
            return

        print(f"\nSaving changes...")
        collapse_and_save(project, agent, lang, section, modified_content)

        print("\nChanges saved successfully!")

    finally:
        Path(tmp_path).unlink(missing_ok=True)


def list_includes(project: str, agent: str, lang: str, section: str):
    """
    List includes in a file.

    Args:
        project: Project name
        agent: Agent name
        lang: Language code
        section: Section filename
    """
    agents_dir = get_project_agents_dir(project)
    full_path = agents_dir / agent / lang / section
    content = full_path.read_text(encoding="utf-8")

    includes = re.findall(INCLUDE_PATTERN, content)

    if includes:
        print(f"\nIncludes in {project}/{agent}/{lang}/{section}:")
        for inc in includes:
            print(f"  - {inc}")
    else:
        print(f"\nNo includes in {project}/{agent}/{lang}/{section}")


def main():
    parser = argparse.ArgumentParser(
        description="Prompt Studio - Expand/Collapse includes for transparent editing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List includes in a file
  python tools/expand.py list --project cowai --agent executive --lang fr --section 02-instructions.md

  # Expand a file (output to stdout)
  python tools/expand.py expand --project cowai --agent executive --lang fr --section 02-instructions.md

  # Expand content from stdin (for API usage)
  echo "content with includes" | python tools/expand.py expand-stdin --project cowai --lang fr

  # Expand with local content highlighting
  python tools/expand.py expand --project cowai --agent executive --lang fr --section 02-instructions.md --highlight

  # Generate colored HTML preview (green=local, blue=include)
  python tools/expand.py expand --project cowai --agent executive --lang fr --section 02-instructions.md --highlight --html > preview.html

  # Collapse an expanded file (dry-run)
  python tools/expand.py collapse --project cowai --agent executive --lang fr --section 02-instructions.md --input expanded.md --dry-run

  # Edit a file interactively (expand + editor + collapse)
  python tools/expand.py edit --project cowai --agent executive --lang fr --section 02-instructions.md
"""
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # expand-stdin command (for API usage - reads content from stdin)
    stdin_parser = subparsers.add_parser("expand-stdin", help="Expand includes from stdin content")
    stdin_parser.add_argument("--project", "-p", required=True, help="Project name")
    stdin_parser.add_argument("--lang", "-l", default="fr", help="Language (fr/en)")

    # list command
    list_parser = subparsers.add_parser("list", help="List includes in a file")
    list_parser.add_argument("--project", "-p", required=True, help="Project name")
    list_parser.add_argument("--agent", "-a", required=True, help="Agent name")
    list_parser.add_argument("--lang", "-l", default="fr", help="Language (fr/en)")
    list_parser.add_argument("--section", "-s", required=True, help="Section filename")

    # expand command
    expand_parser = subparsers.add_parser("expand", help="Expand includes to stdout")
    expand_parser.add_argument("--project", "-p", required=True, help="Project name")
    expand_parser.add_argument("--agent", "-a", required=True, help="Agent name")
    expand_parser.add_argument("--lang", "-l", default="fr", help="Language (fr/en)")
    expand_parser.add_argument("--section", "-s", required=True, help="Section filename")
    expand_parser.add_argument("--highlight", "-H", action="store_true", help="Add markers for local content sections")
    expand_parser.add_argument("--html", action="store_true", help="Generate HTML preview with color coding")

    # collapse command
    collapse_parser = subparsers.add_parser("collapse", help="Collapse and save from expanded content")
    collapse_parser.add_argument("--project", "-p", required=True, help="Project name")
    collapse_parser.add_argument("--agent", "-a", required=True, help="Agent name")
    collapse_parser.add_argument("--lang", "-l", default="fr", help="Language (fr/en)")
    collapse_parser.add_argument("--section", "-s", required=True, help="Section filename")
    collapse_parser.add_argument("--input", "-i", required=True, help="Expanded file to read")
    collapse_parser.add_argument("--dry-run", action="store_true", help="Don't write files")

    # edit command
    edit_parser = subparsers.add_parser("edit", help="Expand, edit, then collapse")
    edit_parser.add_argument("--project", "-p", required=True, help="Project name")
    edit_parser.add_argument("--agent", "-a", required=True, help="Agent name")
    edit_parser.add_argument("--lang", "-l", default="fr", help="Language (fr/en)")
    edit_parser.add_argument("--section", "-s", required=True, help="Section filename")
    edit_parser.add_argument("--editor", "-e", help="Editor to use (default: $EDITOR or vim)")

    args = parser.parse_args()

    try:
        if args.command == "expand-stdin":
            # Read content from stdin and expand includes
            content = sys.stdin.read()
            expanded = expand_includes(content, args.project, args.lang)
            print(expanded)

        elif args.command == "list":
            list_includes(args.project, args.agent, args.lang, args.section)

        elif args.command == "expand":
            expanded = expand_file(args.project, args.agent, args.lang, args.section, highlight_local=args.highlight)
            if args.html:
                html_output = generate_html_preview(expanded, title=f"{args.project}/{args.agent}/{args.lang}/{args.section}")
                print(html_output)
            else:
                print(expanded)

        elif args.command == "collapse":
            input_content = Path(args.input).read_text(encoding="utf-8")
            collapse_and_save(args.project, args.agent, args.lang, args.section, input_content, dry_run=args.dry_run)

        elif args.command == "edit":
            edit_file(args.project, args.agent, args.lang, args.section, editor=args.editor)

    except (FileNotFoundError, ValueError, RecursionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
