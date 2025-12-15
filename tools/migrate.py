#!/usr/bin/env python3
"""
Prompt Studio - Migration Tool
Import existing prompts from Cowai into Prompt Studio format.

Usage:
    python tools/migrate.py --source /path/to/prompts --project cowai
"""

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def colored(text: str, color: str) -> str:
    """Retourne le texte coloré pour le terminal."""
    colors = {
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "red": "\033[91m",
        "cyan": "\033[96m",
        "bold": "\033[1m",
        "reset": "\033[0m"
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


def get_studio_root() -> Path:
    """Retourne le chemin racine du Prompt Studio."""
    return Path(__file__).parent.parent


def analyze_source(source_path: Path) -> dict:
    """Analyse la structure source pour planifier la migration."""
    analysis = {
        "agents": [],
        "languages": set(),
        "total_files": 0,
        "structure": {}
    }

    if not source_path.exists():
        raise ValueError(f"Source path does not exist: {source_path}")

    # Analyser les agents (dossiers au premier niveau)
    for agent_dir in source_path.iterdir():
        if not agent_dir.is_dir() or agent_dir.name.startswith("."):
            continue

        agent_info = {
            "name": agent_dir.name,
            "languages": [],
            "sections": {}
        }

        # Vérifier les langues
        for lang in ["fr", "en"]:
            lang_path = agent_dir / lang
            if lang_path.exists():
                analysis["languages"].add(lang)
                agent_info["languages"].append(lang)

                # Lister les sections
                sections = sorted([
                    f.name for f in lang_path.iterdir()
                    if f.is_file() and f.suffix == ".md"
                ])
                agent_info["sections"][lang] = sections
                analysis["total_files"] += len(sections)

        if agent_info["languages"]:
            analysis["agents"].append(agent_info)

    analysis["languages"] = sorted(list(analysis["languages"]))
    return analysis


def migrate_prompts(source_path: Path, project_name: str, dry_run: bool = False):
    """Migre les prompts vers le format Prompt Studio."""
    studio_root = get_studio_root()
    project_path = studio_root / "projects" / project_name

    print()
    print(colored("=" * 50, "cyan"))
    print(colored("   MIGRATION - Prompt Studio", "bold"))
    print(colored("=" * 50, "cyan"))
    print()
    print(f"📂 Source  : {colored(str(source_path), 'cyan')}")
    print(f"📁 Projet  : {colored(project_name, 'cyan')}")
    print(f"🔍 Mode    : {colored('DRY RUN' if dry_run else 'RÉEL', 'yellow' if dry_run else 'green')}")
    print()

    # Analyser la source
    print(colored("1. Analyse de la source...", "bold"))
    print("-" * 30)

    analysis = analyze_source(source_path)

    print(f"   Agents trouvés : {len(analysis['agents'])}")
    print(f"   Langues        : {', '.join(analysis['languages'])}")
    print(f"   Fichiers       : {analysis['total_files']}")
    print()

    for agent in analysis["agents"]:
        print(f"   📦 {agent['name']}")
        for lang in agent["languages"]:
            print(f"      └── {lang}/ ({len(agent['sections'][lang])} sections)")

    print()

    if dry_run:
        print(colored("⚠️  Mode DRY RUN - Aucune modification ne sera effectuée", "yellow"))
        print()
        return

    # Créer le projet s'il n'existe pas
    print(colored("2. Création du projet...", "bold"))
    print("-" * 30)

    if not project_path.exists():
        (project_path / "agents").mkdir(parents=True)
        (project_path / "dist" / "fr").mkdir(parents=True)
        (project_path / "dist" / "en").mkdir(parents=True)

        project_config = {
            "name": project_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "version": "0.0.0",
            "default_language": "fr",
            "export_path": str(source_path),
            "agents": [a["name"] for a in analysis["agents"]],
            "migrated_from": str(source_path),
            "migrated_at": datetime.now(timezone.utc).isoformat()
        }

        with open(project_path / ".project.json", "w", encoding="utf-8") as f:
            json.dump(project_config, f, indent=2, ensure_ascii=False)

        print(f"   ✅ Projet créé : {project_path}")
    else:
        print(f"   ⚠️  Projet existant : {project_path}")

    print()

    # Copier les fichiers
    print(colored("3. Migration des fichiers...", "bold"))
    print("-" * 30)

    copied = 0
    errors = []

    for agent in analysis["agents"]:
        agent_name = agent["name"]
        print(f"\n   📦 {agent_name}")

        for lang in agent["languages"]:
            print(f"      {lang}/")

            # Créer le dossier de destination
            dest_lang_path = project_path / "agents" / agent_name / lang
            dest_lang_path.mkdir(parents=True, exist_ok=True)

            for section in agent["sections"][lang]:
                source_file = source_path / agent_name / lang / section
                dest_file = dest_lang_path / section

                try:
                    shutil.copy2(source_file, dest_file)
                    print(f"         ├── {section} ✅")
                    copied += 1
                except Exception as e:
                    errors.append(f"{agent_name}/{lang}/{section}: {e}")
                    print(f"         ├── {section} ❌")

    # Résumé
    print()
    print(colored("=" * 50, "cyan"))
    print(colored("   RÉSUMÉ", "bold"))
    print(colored("=" * 50, "cyan"))
    print()
    print(f"   ✅ Fichiers copiés : {colored(str(copied), 'green')}")

    if errors:
        print(f"   ❌ Erreurs         : {colored(str(len(errors)), 'red')}")
        for err in errors:
            print(f"      - {err}")

    print()
    print(f"📁 Projet disponible dans : {colored(str(project_path), 'cyan')}")
    print()
    print(colored("Prochaines étapes :", "bold"))
    print(f"   1. cd {studio_root}")
    print("   2. python tools/server.py")
    print(f"   3. Ouvrir http://localhost:8080")
    print()

    # Mettre à jour l'état
    state_path = studio_root / ".state.json"
    state = {
        "active_project": project_name,
        "active_agent": None,
        "phase": None,
        "current_section": None,
        "last_build": None,
        "projects": [project_name]
    }

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Migre des prompts existants vers Prompt Studio"
    )
    parser.add_argument(
        "--source", "-s",
        required=True,
        help="Chemin vers les prompts sources"
    )
    parser.add_argument(
        "--project", "-p",
        required=True,
        help="Nom du projet de destination"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche ce qui serait fait sans modifier"
    )

    args = parser.parse_args()

    try:
        migrate_prompts(
            Path(args.source),
            args.project,
            args.dry_run
        )
    except Exception as e:
        print(colored(f"\n❌ Erreur : {e}", "red"))
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
