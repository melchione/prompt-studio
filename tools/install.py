#!/usr/bin/env python3
"""
Prompt Studio - Script d'installation interactive
Usage: python tools/install.py
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone


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


def print_header():
    """Affiche l'en-tête du script."""
    print()
    print(colored("=" * 50, "cyan"))
    print(colored("   PROMPT STUDIO - Installation", "bold"))
    print(colored("=" * 50, "cyan"))
    print()


def input_with_default(prompt: str, default: str = None) -> str:
    """Demande une entrée avec une valeur par défaut."""
    if default:
        user_input = input(f"{prompt} [{colored(default, 'yellow')}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()


def input_yes_no(prompt: str, default: bool = True) -> bool:
    """Demande une confirmation oui/non."""
    default_str = "O/n" if default else "o/N"
    user_input = input(f"{prompt} [{default_str}]: ").strip().lower()
    if not user_input:
        return default
    return user_input in ["o", "oui", "y", "yes"]


def get_studio_root() -> Path:
    """Retourne le chemin racine du Prompt Studio."""
    return Path(__file__).parent.parent


def create_project(name: str, config: dict) -> Path:
    """Crée un nouveau projet."""
    studio_root = get_studio_root()
    project_path = studio_root / "projects" / name

    # Créer la structure
    (project_path / "agents").mkdir(parents=True, exist_ok=True)
    (project_path / "dist" / "fr").mkdir(parents=True, exist_ok=True)
    (project_path / "dist" / "en").mkdir(parents=True, exist_ok=True)

    # Créer .project.json
    project_config = {
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "version": "0.0.0",
        "default_language": config.get("default_language", "fr"),
        "export_path": config.get("export_path"),
        "agents": []
    }

    with open(project_path / ".project.json", "w", encoding="utf-8") as f:
        json.dump(project_config, f, indent=2, ensure_ascii=False)

    return project_path


def create_agent(project_path: Path, agent_name: str, default_lang: str = "fr") -> Path:
    """Crée un nouvel agent avec un template de base."""
    agent_path = project_path / "agents" / agent_name

    # Créer la structure pour les deux langues
    (agent_path / "fr").mkdir(parents=True, exist_ok=True)
    (agent_path / "en").mkdir(parents=True, exist_ok=True)

    # Template de base pour le premier fichier
    template_fr = f"""# {agent_name.replace('_', ' ').title()}

## Contexte

Tu es un assistant spécialisé.

## Instructions

Décris ici les instructions pour cet agent.

## Format de réponse

Décris le format attendu des réponses.
"""

    template_en = f"""# {agent_name.replace('_', ' ').title()}

## Context

You are a specialized assistant.

## Instructions

Describe here the instructions for this agent.

## Response Format

Describe the expected response format.
"""

    # Créer les fichiers de base
    (agent_path / "fr" / "01-context.md").write_text(template_fr, encoding="utf-8")
    (agent_path / "en" / "01-context.md").write_text(template_en, encoding="utf-8")

    return agent_path


def update_state(studio_root: Path, active_project: str = None):
    """Met à jour le fichier .state.json."""
    state_path = studio_root / ".state.json"

    state = {
        "active_project": active_project,
        "active_agent": None,
        "phase": None,
        "current_section": None,
        "last_build": None,
        "projects": []
    }

    # Lister les projets existants
    projects_dir = studio_root / "projects"
    if projects_dir.exists():
        state["projects"] = [
            p.name for p in projects_dir.iterdir()
            if p.is_dir() and (p / ".project.json").exists()
        ]

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def update_settings(studio_root: Path, allowed_dirs: list):
    """Met à jour les settings Claude Code."""
    settings_path = studio_root / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    settings = {
        "allowedDirectories": allowed_dirs,
        "permissions": {
            "allow": [
                "Bash(python:*)",
                "Bash(python3:*)",
                "Read(**/*)",
                "Write(projects/**/*)",
                "Write(versions/**/*)",
                "Write(.state.json)"
            ]
        }
    }

    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def interactive_setup():
    """Configuration interactive du Prompt Studio."""
    print_header()

    studio_root = get_studio_root()
    config = {}

    # 1. Langue par défaut
    print(colored("1. Configuration de base", "bold"))
    print("-" * 30)
    config["default_language"] = input_with_default(
        "🌍 Langue par défaut (fr/en)",
        "fr"
    )
    print()

    # 2. Dossiers autorisés pour l'export
    print(colored("2. Permissions d'export", "bold"))
    print("-" * 30)
    print("Le Prompt Studio peut exporter vers des projets externes.")
    print("Quels dossiers voulez-vous autoriser ?")
    print()

    allowed_dirs = [str(studio_root)]

    # Proposer le dossier parent (Cowai)
    parent_dir = studio_root.parent
    if input_yes_no(f"   Autoriser {colored(str(parent_dir), 'cyan')} ?", True):
        allowed_dirs.append(str(parent_dir))

    # Permettre d'ajouter d'autres dossiers
    while input_yes_no("   Ajouter un autre dossier ?", False):
        extra_dir = input("   Chemin du dossier : ").strip()
        if extra_dir and Path(extra_dir).exists():
            allowed_dirs.append(extra_dir)
            print(colored(f"   ✅ Ajouté : {extra_dir}", "green"))
        else:
            print(colored(f"   ⚠️ Dossier invalide ou inexistant", "yellow"))
    print()

    # 3. Créer un premier projet
    print(colored("3. Premier projet", "bold"))
    print("-" * 30)

    project_name = input_with_default("📁 Nom du projet", "main")
    agent_name = None

    # Chemin d'export (obligatoire)
    print()
    print("   Où exporter les prompts compilés ?")
    print("   (Chemin absolu vers le dossier de destination)")
    print()

    while True:
        export_path = input("   📤 Chemin d'export : ").strip()
        if export_path:
            export_path_obj = Path(export_path)
            # Créer le dossier s'il n'existe pas
            if not export_path_obj.exists():
                if input_yes_no(f"   Le dossier n'existe pas. Le créer ?", True):
                    try:
                        export_path_obj.mkdir(parents=True, exist_ok=True)
                        print(colored(f"   ✅ Dossier créé : {export_path}", "green"))
                        break
                    except Exception as e:
                        print(colored(f"   ❌ Impossible de créer le dossier : {e}", "red"))
                else:
                    print("   Veuillez entrer un autre chemin.")
            else:
                break
        else:
            print(colored("   ⚠️ Le chemin d'export est obligatoire.", "yellow"))

    config["export_path"] = export_path

    # Ajouter aux dossiers autorisés si nécessaire
    export_parent = str(Path(export_path).parent)
    if export_parent not in allowed_dirs:
        allowed_dirs.append(export_parent)

    # Créer le projet
    project_path = create_project(project_name, config)
    print()
    print(colored(f"   ✅ Projet '{project_name}' créé !", "green"))

    # 4. Créer un premier agent
    print()
    print(colored("4. Premier agent", "bold"))
    print("-" * 30)

    if input_yes_no("Créer un premier agent maintenant ?", True):
        agent_name = input_with_default("🤖 Nom de l'agent", "assistant")

        # Valider le nom (snake_case ou kebab-case)
        agent_name = agent_name.lower().replace(" ", "_").replace("-", "_")

        # Créer l'agent
        agent_path = create_agent(project_path, agent_name, config.get("default_language", "fr"))
        print()
        print(colored(f"   ✅ Agent '{agent_name}' créé avec template de base !", "green"))
        print(f"   📄 Fichiers créés :")
        print(f"      - {agent_name}/fr/01-context.md")
        print(f"      - {agent_name}/en/01-context.md")

    # Activer le projet
    update_state(studio_root, project_name)

    # 5. Sauvegarder les settings
    update_settings(studio_root, allowed_dirs)

    # 6. Résumé
    print()
    print(colored("=" * 50, "cyan"))
    print(colored("   Installation terminée !", "bold"))
    print(colored("=" * 50, "cyan"))
    print()
    print(f"📁 Prompt Studio : {colored(str(studio_root), 'cyan')}")
    print(f"🌍 Langue par défaut : {colored(config['default_language'], 'cyan')}")
    print(f"📤 Export vers : {colored(export_path, 'cyan')}")
    print(f"🔐 Dossiers autorisés :")
    for d in allowed_dirs:
        print(f"   - {d}")

    print()
    print(f"🚀 Projet actif : {colored(project_name, 'green')}")
    if agent_name:
        print(f"🤖 Agent créé : {colored(agent_name, 'green')}")

    print()
    print(colored("Prochaines étapes :", "bold"))
    print("  1. Lancer l'éditeur web :")
    print(f"     {colored('python tools/server.py', 'yellow')}")
    print(f"     Puis ouvrir {colored('http://localhost:8236', 'cyan')}")
    print()
    print("  2. Ou utiliser Claude Code :")
    print(f"     {colored('cd ' + str(studio_root), 'yellow')}")
    print(f"     {colored('claude', 'yellow')}")
    print(f"     {colored('/ps:status', 'cyan')} - Voir l'état actuel")
    print()


def main():
    """Point d'entrée principal."""
    try:
        interactive_setup()
    except KeyboardInterrupt:
        print()
        print(colored("\n⚠️ Installation annulée.", "yellow"))
        return 1
    except Exception as e:
        print(colored(f"\n❌ Erreur : {e}", "red"))
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
