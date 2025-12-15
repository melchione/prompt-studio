#!/usr/bin/env python3
"""
Prompt Studio - Script de build
Compile les prompts en résolvant les includes et génère les fichiers finaux.

Usage:
    python tools/build.py --project cowai --agent executive
    python tools/build.py --project cowai --all
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class BuildError(Exception):
    """Erreur lors du build."""
    pass


class PromptBuilder:
    """Constructeur de prompts avec résolution des includes."""

    INCLUDE_PATTERN = re.compile(r"\{%\s*include\s*['\"]([^'\"]+)['\"]\s*%\}")
    MAX_INCLUDE_DEPTH = 10

    def __init__(self, studio_root: Path):
        self.studio_root = studio_root
        self.projects_dir = studio_root / "projects"
        self.stats = {
            "sections_processed": 0,
            "includes_resolved": 0,
            "total_words": 0,
            "errors": []
        }

    def get_project_path(self, project_name: str) -> Path:
        """Retourne le chemin d'un projet."""
        return self.projects_dir / project_name

    def get_agent_path(self, project_name: str, agent_name: str) -> Path:
        """Retourne le chemin d'un agent."""
        return self.get_project_path(project_name) / "agents" / agent_name

    def resolve_includes(
        self,
        content: str,
        project_path: Path,
        lang: str,
        source_file: str,
        depth: int = 0
    ) -> str:
        """Résout récursivement les includes dans le contenu."""
        if depth > self.MAX_INCLUDE_DEPTH:
            raise BuildError(
                f"Profondeur d'include maximale atteinte ({self.MAX_INCLUDE_DEPTH}). "
                f"Vérifiez les includes circulaires dans {source_file}"
            )

        def replace_include(match: re.Match) -> str:
            include_ref = match.group(1)  # ex: "common/fr/01-context.md"

            # Parser le chemin de l'include
            parts = include_ref.split("/")
            if len(parts) < 3:
                # Format simple: "section.md" -> même agent
                include_path = project_path / "agents" / source_file.split("/")[0] / lang / include_ref
            else:
                # Format complet: "agent/lang/section.md"
                agent_name = parts[0]
                include_lang = parts[1] if len(parts) > 2 else lang
                section = "/".join(parts[2:]) if len(parts) > 2 else parts[1]
                include_path = project_path / "agents" / agent_name / include_lang / section

            # Vérifier que le fichier existe
            if not include_path.exists():
                error_msg = f"Include introuvable: {include_ref} dans {source_file}"
                self.stats["errors"].append(error_msg)
                return f"<!-- ERROR: {error_msg} -->"

            # Lire et résoudre récursivement
            try:
                included_content = include_path.read_text(encoding="utf-8")
                resolved = self.resolve_includes(
                    included_content,
                    project_path,
                    lang,
                    str(include_path.relative_to(project_path)),
                    depth + 1
                )
                self.stats["includes_resolved"] += 1

                # Ajouter des marqueurs de traçabilité
                return (
                    f"<!-- @include-start: {include_ref} -->\n"
                    f"{resolved.strip()}\n"
                    f"<!-- @include-end: {include_ref} -->"
                )
            except Exception as e:
                error_msg = f"Erreur lecture include {include_ref}: {e}"
                self.stats["errors"].append(error_msg)
                return f"<!-- ERROR: {error_msg} -->"

        return self.INCLUDE_PATTERN.sub(replace_include, content)

    def build_agent(
        self,
        project_name: str,
        agent_name: str,
        languages: list[str] = None
    ) -> dict:
        """Build un agent pour toutes les langues."""
        project_path = self.get_project_path(project_name)
        agent_path = self.get_agent_path(project_name, agent_name)

        if not agent_path.exists():
            raise BuildError(f"Agent introuvable: {agent_name}")

        if languages is None:
            languages = ["fr", "en"]

        results = {}

        for lang in languages:
            lang_path = agent_path / lang
            if not lang_path.exists():
                print(f"  ⚠️ Langue {lang} non trouvée pour {agent_name}")
                continue

            # Lister et trier les sections
            sections = sorted([
                f for f in lang_path.iterdir()
                if f.is_file() and f.suffix == ".md"
            ], key=lambda x: x.name)

            if not sections:
                print(f"  ⚠️ Aucune section trouvée pour {agent_name}/{lang}")
                continue

            # Compiler les sections
            compiled_parts = []
            header = self._generate_header(project_name, agent_name, lang)
            compiled_parts.append(header)

            for section_file in sections:
                print(f"   ├── {section_file.name}", end="")

                content = section_file.read_text(encoding="utf-8")
                resolved = self.resolve_includes(
                    content,
                    project_path,
                    lang,
                    f"{agent_name}/{lang}/{section_file.name}"
                )

                word_count = len(resolved.split())
                self.stats["sections_processed"] += 1
                self.stats["total_words"] += word_count

                # Ajouter un marqueur de section
                section_marker = f"\n<!-- @section: {section_file.name} -->\n"
                compiled_parts.append(section_marker + resolved.strip())

                print(f"  ✅ ({word_count} mots)")

            # Assembler le fichier final
            final_content = "\n\n".join(compiled_parts)

            # Écrire dans dist/
            dist_dir = project_path / "dist" / lang
            dist_dir.mkdir(parents=True, exist_ok=True)
            output_file = dist_dir / f"{agent_name}.md"
            output_file.write_text(final_content, encoding="utf-8")

            results[lang] = {
                "output": str(output_file),
                "sections": len(sections),
                "words": len(final_content.split())
            }

            print(f"   📄 Généré: dist/{lang}/{agent_name}.md")

        return results

    def _generate_header(
        self,
        project_name: str,
        agent_name: str,
        lang: str
    ) -> str:
        """Génère l'en-tête du fichier compilé."""
        # Lire la version du projet
        project_config_path = self.get_project_path(project_name) / ".project.json"
        version = "0.0.0"
        if project_config_path.exists():
            with open(project_config_path, encoding="utf-8") as f:
                config = json.load(f)
                version = config.get("version", "0.0.0")

        timestamp = datetime.now(timezone.utc).isoformat()

        return f"""<!--
  Prompt Studio Build
  Project: {project_name}
  Agent: {agent_name}
  Version: {version}
  Built: {timestamp}
  Language: {lang}
-->"""

    def build_project(self, project_name: str) -> dict:
        """Build tous les agents d'un projet."""
        project_path = self.get_project_path(project_name)

        if not project_path.exists():
            raise BuildError(f"Projet introuvable: {project_name}")

        agents_dir = project_path / "agents"
        if not agents_dir.exists():
            raise BuildError(f"Aucun agent dans le projet: {project_name}")

        agents = [
            d.name for d in agents_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

        if not agents:
            raise BuildError(f"Aucun agent trouvé dans {project_name}")

        results = {}
        for agent_name in sorted(agents):
            print(f"\n🔄 Build: {agent_name}")
            results[agent_name] = self.build_agent(project_name, agent_name)

        return results


def update_state(studio_root: Path, last_build: str):
    """Met à jour le timestamp du dernier build."""
    state_path = studio_root / ".state.json"
    if state_path.exists():
        with open(state_path, encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {}

    state["last_build"] = last_build

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Compile les prompts du Prompt Studio"
    )
    parser.add_argument(
        "--project", "-p",
        required=True,
        help="Nom du projet"
    )
    parser.add_argument(
        "--agent", "-a",
        help="Nom de l'agent (optionnel, sinon tous)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Compiler tous les agents du projet"
    )

    args = parser.parse_args()

    studio_root = Path(__file__).parent.parent
    builder = PromptBuilder(studio_root)

    print()
    print("🔨 PROMPT STUDIO BUILD")
    print("=" * 50)
    print(f"📁 Projet: {args.project}")

    try:
        if args.all or not args.agent:
            results = builder.build_project(args.project)
        else:
            print(f"🤖 Agent: {args.agent}")
            results = {args.agent: builder.build_agent(args.project, args.agent)}

        # Mise à jour de l'état
        timestamp = datetime.now(timezone.utc).isoformat()
        update_state(studio_root, timestamp)

        # Résumé
        print()
        print("=" * 50)
        if builder.stats["errors"]:
            print("⚠️ Build terminé avec erreurs:")
            for error in builder.stats["errors"]:
                print(f"   ❌ {error}")
        else:
            print("✅ Build réussi !")

        print()
        print("📊 Statistiques:")
        print(f"   - Sections traitées : {builder.stats['sections_processed']}")
        print(f"   - Includes résolus  : {builder.stats['includes_resolved']}")
        print(f"   - Mots totaux       : {builder.stats['total_words']}")

        if builder.stats["errors"]:
            return 1
        return 0

    except BuildError as e:
        print(f"\n❌ Erreur: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        raise


if __name__ == "__main__":
    sys.exit(main())
