#!/usr/bin/env python3
"""
Prompt Studio - AI Translation using Claude API

Translates prompt sections while preserving protected tokens (XML tags, variables, code blocks).

Usage:
    python tools/translate.py --project cowai --agent executive --section 01-context.md --from fr --to en
    python tools/translate.py --source projects/cowai/agents/executive/fr/01-context.md --to en

Auteur: Adapted from Cowai prompt_building scripts
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Protected tokens that should NEVER be translated
PROTECTED_PATTERNS = [
    r'<[^>]+>',  # XML tags
    r'\$[a-zA-Z_][a-zA-Z0-9_]*\$',  # Variables like $current_date_and_time$
    r'`[^`]+`',  # Inline code
    r'```[\s\S]*?```',  # Code blocks
    r'RESULT_FROM_\d+',  # Result references
    r'CURRENT_ITEM',  # Loop variables
    r'LOOP_INDEX',  # Loop variables
    r'\{%\s*include\s*[\'"][^\'"]+[\'"]\s*%\}',  # Include directives
    r'\{\{[^}]+\}\}',  # Jinja2 variables
    r'\{%[^%]+%\}',  # Jinja2 blocks
    r'mcp__\w+',  # MCP tool names
]


def extract_protected_tokens(text: str) -> Tuple[Dict[str, str], str]:
    """
    Extract protected tokens and replace them with placeholders.

    Args:
        text: Original text with protected tokens

    Returns:
        Tuple (tokens_dict, safe_text)
        - tokens_dict: {placeholder: original_token}
        - safe_text: Text with placeholders
    """
    tokens = {}
    modified_text = text
    token_count = 0

    for pattern in PROTECTED_PATTERNS:
        matches = list(re.finditer(pattern, modified_text))
        for match in reversed(matches):  # Reverse to maintain positions
            token = match.group(0)
            # Check if already replaced (avoid double replacement)
            if token.startswith("__PROTECTED_"):
                continue
            placeholder = f"__PROTECTED_{token_count}__"
            tokens[placeholder] = token
            modified_text = (
                modified_text[:match.start()] +
                placeholder +
                modified_text[match.end():]
            )
            token_count += 1

    return tokens, modified_text


def restore_protected_tokens(text: str, tokens: Dict[str, str]) -> str:
    """
    Restore protected tokens from placeholders.

    Args:
        text: Text with placeholders
        tokens: {placeholder: original_token}

    Returns:
        Text with restored tokens
    """
    restored_text = text
    for placeholder, token in tokens.items():
        restored_text = restored_text.replace(placeholder, token)
    return restored_text


def translate_with_claude(text: str, source_lang: str = "French", target_lang: str = "English") -> str:
    """
    Translate text using Claude API while preserving protected tokens.

    Args:
        text: Text to translate
        source_lang: Source language name
        target_lang: Target language name

    Returns:
        Translated text with protected tokens restored

    Raises:
        ValueError: If ANTHROPIC_API_KEY is not set
        ImportError: If anthropic package is not installed
    """
    try:
        from anthropic import Anthropic
    except ImportError:
        raise ImportError(
            "anthropic package not installed. Install with: pip install anthropic"
        )

    # Extract protected tokens
    protected_tokens, safe_text = extract_protected_tokens(text)

    # Initialize Anthropic client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable not set.\n"
            "Set it with: export ANTHROPIC_API_KEY=your_key"
        )

    client = Anthropic(api_key=api_key)

    # Translation prompt
    translation_prompt = f"""You are a professional technical translator specialized in AI/ML documentation.

Translate the following text from {source_lang} to {target_lang}.

CRITICAL RULES:
1. DO NOT translate placeholders like __PROTECTED_X__ - keep them EXACTLY as they appear
2. Preserve all markdown formatting (headers, lists, code blocks, etc.)
3. Keep the same tone and style (professional, clear, direct)
4. Maintain technical accuracy
5. Do NOT add explanations or comments - ONLY output the translated text
6. Preserve line breaks and spacing exactly
7. If you see XML-like tags, keep them unchanged

Text to translate:

{safe_text}

Translation ({target_lang}):"""

    # Call Claude API
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=8000,
        temperature=0.3,
        messages=[
            {"role": "user", "content": translation_prompt}
        ]
    )

    # Extract translated text
    translated_text = message.content[0].text.strip()

    # Restore protected tokens
    final_text = restore_protected_tokens(translated_text, protected_tokens)

    return final_text


def detect_language(file_path: Path) -> str:
    """Detect language from file path (expects /lang/ in path)."""
    path_str = str(file_path)
    if "/fr/" in path_str:
        return "fr"
    elif "/en/" in path_str:
        return "en"
    return None


def get_language_name(code: str) -> str:
    """Convert language code to full name."""
    return {"fr": "French", "en": "English"}.get(code, code)


def translate_section(
    source_path: Path,
    target_path: Path,
    source_lang: str,
    target_lang: str,
    dry_run: bool = False
) -> str:
    """
    Translate a section file.

    Args:
        source_path: Path to source file
        target_path: Path to target file
        source_lang: Source language code
        target_lang: Target language code
        dry_run: If True, don't write files

    Returns:
        Translated content
    """
    # Read source content
    print(f"📖 Reading: {source_path}")
    source_text = source_path.read_text(encoding="utf-8")

    # Translate
    source_name = get_language_name(source_lang)
    target_name = get_language_name(target_lang)
    print(f"🌐 Translating: {source_name} → {target_name}...")

    translated_text = translate_with_claude(source_text, source_name, target_name)

    # Create target directory if needed
    if not dry_run:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(translated_text, encoding="utf-8")
        print(f"💾 Written: {target_path}")
    else:
        print(f"🔍 DRY RUN: Would write to {target_path}")

    # Stats
    print(f"\n📊 Translation stats:")
    print(f"   Source: {len(source_text):,} chars | {len(source_text.split()):,} words")
    print(f"   Target: {len(translated_text):,} chars | {len(translated_text.split()):,} words")

    return translated_text


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Translate prompt sections using Claude AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Translate a specific section
  python tools/translate.py --project cowai --agent executive --section 01-context.md --from fr --to en

  # Translate using direct paths
  python tools/translate.py --source projects/cowai/agents/executive/fr/01-context.md --to en

  # Dry run (preview without writing)
  python tools/translate.py --source file.md --to en --dry-run
"""
    )

    parser.add_argument("--project", "-p", help="Project name")
    parser.add_argument("--agent", "-a", help="Agent name")
    parser.add_argument("--section", "-s", help="Section filename")
    parser.add_argument("--source", help="Direct path to source file")
    parser.add_argument("--from", dest="from_lang", help="Source language (fr/en)")
    parser.add_argument("--to", dest="to_lang", required=True, help="Target language (fr/en)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")

    args = parser.parse_args()

    studio_root = Path(__file__).parent.parent

    # Determine source path
    if args.source:
        source_path = Path(args.source)
        if not source_path.is_absolute():
            source_path = studio_root / source_path
    elif args.project and args.agent and args.section:
        source_lang = args.from_lang or "fr"
        source_path = studio_root / "projects" / args.project / "agents" / args.agent / source_lang / args.section
    else:
        parser.error("Either --source or (--project, --agent, --section) required")
        return

    if not source_path.exists():
        print(f"❌ Source file not found: {source_path}")
        sys.exit(1)

    # Detect source language if not specified
    source_lang = args.from_lang or detect_language(source_path)
    if not source_lang:
        parser.error("Could not detect source language. Use --from to specify.")
        return

    target_lang = args.to_lang

    # Determine target path
    target_path_str = str(source_path).replace(f"/{source_lang}/", f"/{target_lang}/")
    target_path = Path(target_path_str)

    print()
    print("=" * 50)
    print("   PROMPT STUDIO - AI Translation")
    print("=" * 50)
    print()

    try:
        translate_section(
            source_path=source_path,
            target_path=target_path,
            source_lang=source_lang,
            target_lang=target_lang,
            dry_run=args.dry_run
        )
        print("\n✅ Translation complete!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
