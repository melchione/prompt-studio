#!/usr/bin/env python3
"""
Prompt Studio - Serveur API pour l'éditeur web

Features:
- Project/Agent/Section CRUD
- Real AI translation via Claude API
- Expand/Collapse includes for editing
- Build system integration
- HTML preview with color-coded sections

Usage: python tools/server.py [--port 8080]
"""

import argparse
import json
import mimetypes
import os
import sys
from datetime import datetime, timezone
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


class PromptStudioAPI(SimpleHTTPRequestHandler):
    """Handler HTTP pour l'API du Prompt Studio."""

    studio_root = Path(__file__).parent.parent

    def __init__(self, *args, **kwargs):
        self.projects_dir = self.studio_root / "projects"
        super().__init__(*args, directory=str(self.studio_root / "editor"), **kwargs)

    def do_GET(self):
        """Gère les requêtes GET."""
        parsed = urlparse(self.path)
        path = parsed.path

        # API endpoints
        if path.startswith("/api/"):
            self._handle_api_get(path, parse_qs(parsed.query))
        else:
            # Serve static files from editor/
            super().do_GET()

    def do_POST(self):
        """Gère les requêtes POST."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body) if body else {}
            self._handle_api_post(path, data)
        else:
            self._send_json({"error": "Not found"}, 404)

    def _handle_api_get(self, path: str, query: dict):
        """Route les requêtes GET de l'API."""
        try:
            if path == "/api/state":
                self._get_state()
            elif path == "/api/projects":
                self._list_projects()
            elif path == "/api/protected-tokens":
                self._get_protected_tokens()
            elif path == "/api/includes":
                project = query.get("project", [None])[0]
                self._list_available_includes(project)
            elif path.startswith("/api/projects/"):
                parts = path.split("/")
                project = parts[3]
                if len(parts) == 4:
                    self._get_project(project)
                elif len(parts) >= 5 and parts[4] == "agents":
                    if len(parts) == 5:
                        self._list_agents(project)
                    elif len(parts) >= 6:
                        agent = parts[5]
                        if len(parts) == 6:
                            self._get_agent(project, agent)
                        elif len(parts) == 8 and parts[6] in ["fr", "en"] and parts[7] == "all":
                            # /api/projects/{project}/agents/{agent}/{lang}/all
                            lang = parts[6]
                            self._get_all_sections(project, agent, lang)
                        elif len(parts) >= 8 and parts[6] in ["fr", "en"]:
                            lang = parts[6]
                            section = "/".join(parts[7:])
                            self._get_section(project, agent, lang, section)
                        elif path.endswith("/expand"):
                            lang = query.get("lang", ["fr"])[0]
                            section = query.get("section", [None])[0]
                            highlight = query.get("highlight", ["false"])[0] == "true"
                            html_preview = query.get("html", ["false"])[0] == "true"
                            self._expand_section(project, agent, lang, section, highlight, html_preview)
                        else:
                            self._send_json({"error": "Invalid path"}, 400)
                    else:
                        self._send_json({"error": "Invalid path"}, 400)
                else:
                    self._send_json({"error": "Invalid path"}, 400)
            else:
                self._send_json({"error": "Unknown endpoint"}, 404)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_api_post(self, path: str, data: dict):
        """Route les requêtes POST de l'API."""
        try:
            if path == "/api/state":
                self._update_state(data)
            elif path == "/api/projects":
                self._create_project(data)
            elif path == "/api/build":
                self._build(data)
            elif path == "/api/expand":
                # POST /api/expand - Expand includes in content
                self._expand_content(data)
            elif path == "/api/collapse-content":
                # POST /api/collapse-content - Collapse expanded content back to includes
                self._collapse_content(data)
            elif path.endswith("/save-all"):
                # /api/projects/{project}/agents/{agent}/{lang}/save-all
                # MUST be checked BEFORE generic section handler
                parts = path.split("/")
                project = parts[3]
                agent = parts[5]
                lang = parts[6]
                self._save_all_sections(project, agent, lang, data)
            elif path.startswith("/api/projects/") and "/agents" in path:
                parts = path.split("/")
                project = parts[3]
                if len(parts) == 5:  # /api/projects/{project}/agents
                    self._create_agent(project, data)
                elif len(parts) >= 8:  # /api/projects/{project}/agents/{agent}/{lang}/{section}
                    agent = parts[5]
                    lang = parts[6]
                    section = "/".join(parts[7:])
                    self._save_section(project, agent, lang, section, data)
                else:
                    self._send_json({"error": "Invalid path"}, 400)
            elif path.endswith("/translate"):
                # /api/projects/{project}/agents/{agent}/translate
                parts = path.split("/")
                project = parts[3]
                agent = parts[5]
                self._translate_section(project, agent, data)
            elif path.endswith("/translate-ai"):
                # /api/projects/{project}/agents/{agent}/translate-ai
                # Real AI translation using Claude API
                parts = path.split("/")
                project = parts[3]
                agent = parts[5]
                self._translate_section_ai(project, agent, data)
            elif path.endswith("/collapse"):
                # /api/projects/{project}/agents/{agent}/collapse
                parts = path.split("/")
                project = parts[3]
                agent = parts[5]
                self._collapse_section(project, agent, data)
            elif path.endswith("/reorder"):
                # /api/projects/{project}/agents/{agent}/reorder
                parts = path.split("/")
                project = parts[3]
                agent = parts[5]
                self._reorder_sections(project, agent, data)
            elif path.endswith("/delete-section"):
                # /api/projects/{project}/agents/{agent}/delete-section
                parts = path.split("/")
                project = parts[3]
                agent = parts[5]
                self._delete_section(project, agent, data)
            else:
                self._send_json({"error": "Unknown endpoint"}, 404)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _send_json(self, data: dict, status: int = 200):
        """Envoie une réponse JSON."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _get_state(self):
        """Retourne l'état global."""
        state_path = self.studio_root / ".state.json"
        if state_path.exists():
            with open(state_path, encoding="utf-8") as f:
                state = json.load(f)
        else:
            state = {
                "active_project": None,
                "active_agent": None,
                "phase": None,
                "current_section": None,
                "last_build": None,
                "projects": []
            }
        self._send_json(state)

    def _update_state(self, data: dict):
        """Met à jour l'état global."""
        state_path = self.studio_root / ".state.json"
        if state_path.exists():
            with open(state_path, encoding="utf-8") as f:
                state = json.load(f)
        else:
            state = {}

        state.update(data)

        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        self._send_json({"success": True, "state": state})

    def _list_projects(self):
        """Liste tous les projets."""
        projects = []
        if self.projects_dir.exists():
            for p in self.projects_dir.iterdir():
                if p.is_dir():
                    config_path = p / ".project.json"
                    if config_path.exists():
                        with open(config_path, encoding="utf-8") as f:
                            config = json.load(f)
                            projects.append({
                                "name": p.name,
                                "version": config.get("version", "0.0.0"),
                                "agents_count": len(list((p / "agents").iterdir())) if (p / "agents").exists() else 0
                            })
        self._send_json({"projects": projects})

    def _get_project(self, project_name: str):
        """Retourne les détails d'un projet."""
        project_path = self.projects_dir / project_name
        config_path = project_path / ".project.json"

        if not config_path.exists():
            self._send_json({"error": "Project not found"}, 404)
            return

        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)

        self._send_json(config)

    def _create_project(self, data: dict):
        """Crée un nouveau projet."""
        name = data.get("name")
        if not name:
            self._send_json({"error": "Project name required"}, 400)
            return

        project_path = self.projects_dir / name
        if project_path.exists():
            self._send_json({"error": "Project already exists"}, 400)
            return

        # Créer la structure
        (project_path / "agents").mkdir(parents=True)
        (project_path / "dist" / "fr").mkdir(parents=True)
        (project_path / "dist" / "en").mkdir(parents=True)

        config = {
            "name": name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "version": "0.0.0",
            "default_language": data.get("default_language", "fr"),
            "export_path": data.get("export_path"),
            "agents": []
        }

        with open(project_path / ".project.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        self._send_json({"success": True, "project": config})

    def _list_agents(self, project_name: str):
        """Liste les agents d'un projet."""
        agents_path = self.projects_dir / project_name / "agents"
        agents = []

        if agents_path.exists():
            for a in agents_path.iterdir():
                if a.is_dir() and not a.name.startswith("."):
                    agent_info = {
                        "name": a.name,
                        "languages": [],
                        "sections": {}
                    }
                    for lang in ["fr", "en"]:
                        lang_path = a / lang
                        if lang_path.exists():
                            agent_info["languages"].append(lang)
                            agent_info["sections"][lang] = sorted([
                                f.name for f in lang_path.iterdir()
                                if f.is_file() and f.suffix == ".md"
                            ])
                    agents.append(agent_info)

        self._send_json({"agents": agents})

    def _get_agent(self, project_name: str, agent_name: str):
        """Retourne les détails d'un agent."""
        agent_path = self.projects_dir / project_name / "agents" / agent_name

        if not agent_path.exists():
            self._send_json({"error": "Agent not found"}, 404)
            return

        agent_info = {
            "name": agent_name,
            "project": project_name,
            "languages": [],
            "sections": {}
        }

        for lang in ["fr", "en"]:
            lang_path = agent_path / lang
            if lang_path.exists():
                agent_info["languages"].append(lang)
                agent_info["sections"][lang] = []
                for f in sorted(lang_path.iterdir()):
                    if f.is_file() and f.suffix == ".md":
                        content = f.read_text(encoding="utf-8")
                        agent_info["sections"][lang].append({
                            "name": f.name,
                            "words": len(content.split()),
                            "size": len(content)
                        })

        self._send_json(agent_info)

    def _create_agent(self, project_name: str, data: dict):
        """Crée un nouvel agent."""
        name = data.get("name")
        if not name:
            self._send_json({"error": "Agent name required"}, 400)
            return

        agent_path = self.projects_dir / project_name / "agents" / name
        if agent_path.exists():
            self._send_json({"error": "Agent already exists"}, 400)
            return

        # Créer la structure
        (agent_path / "fr").mkdir(parents=True)
        (agent_path / "en").mkdir(parents=True)

        self._send_json({"success": True, "agent": {"name": name}})

    def _get_section(self, project: str, agent: str, lang: str, section: str):
        """Retourne le contenu d'une section."""
        section_path = self.projects_dir / project / "agents" / agent / lang / section

        if not section_path.exists():
            self._send_json({"error": "Section not found"}, 404)
            return

        content = section_path.read_text(encoding="utf-8")
        self._send_json({
            "project": project,
            "agent": agent,
            "language": lang,
            "section": section,
            "content": content,
            "words": len(content.split())
        })

    def _save_section(self, project: str, agent: str, lang: str, section: str, data: dict):
        """Sauvegarde une section."""
        content = data.get("content", "")
        section_path = self.projects_dir / project / "agents" / agent / lang / section

        # Créer le dossier si nécessaire
        section_path.parent.mkdir(parents=True, exist_ok=True)

        section_path.write_text(content, encoding="utf-8")
        self._send_json({
            "success": True,
            "section": section,
            "words": len(content.split())
        })

    def _list_available_includes(self, project: str = None):
        """Liste les sections disponibles pour les includes."""
        includes = []

        if project:
            project_paths = [self.projects_dir / project]
        else:
            project_paths = [p for p in self.projects_dir.iterdir() if p.is_dir()]

        for project_path in project_paths:
            agents_path = project_path / "agents"
            if not agents_path.exists():
                continue

            for agent_path in agents_path.iterdir():
                if not agent_path.is_dir() or agent_path.name.startswith("."):
                    continue

                for lang in ["fr", "en"]:
                    lang_path = agent_path / lang
                    if not lang_path.exists():
                        continue

                    for section in sorted(lang_path.iterdir()):
                        if section.is_file() and section.suffix == ".md":
                            includes.append({
                                "project": project_path.name,
                                "agent": agent_path.name,
                                "language": lang,
                                "section": section.name,
                                "ref": f"{agent_path.name}/{lang}/{section.name}"
                            })

        self._send_json({"includes": includes})

    def _translate_section(self, project: str, agent: str, data: dict):
        """Copie une section vers une autre langue."""
        section = data.get("section")
        from_lang = data.get("from_lang")
        to_lang = data.get("to_lang")

        if not all([section, from_lang, to_lang]):
            self._send_json({"error": "section, from_lang, to_lang required"}, 400)
            return

        source_path = self.projects_dir / project / "agents" / agent / from_lang / section
        target_path = self.projects_dir / project / "agents" / agent / to_lang / section

        if not source_path.exists():
            self._send_json({"error": f"Source section not found: {from_lang}/{section}"}, 404)
            return

        # Créer le dossier cible si nécessaire
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Copier le contenu avec un marqueur de traduction
        content = source_path.read_text(encoding="utf-8")

        # Si le fichier cible n'existe pas, ajouter un header
        if not target_path.exists():
            header = f"<!-- TODO: Traduire depuis {from_lang} -->\n\n"
            content = header + content

        target_path.write_text(content, encoding="utf-8")

        self._send_json({
            "success": True,
            "message": f"Section copiée vers {to_lang}/{section}",
            "from": f"{from_lang}/{section}",
            "to": f"{to_lang}/{section}"
        })

    def _reorder_sections(self, project: str, agent: str, data: dict):
        """Réordonne les sections en les renommant."""
        lang = data.get("lang", "fr")
        order = data.get("order", [])  # Liste des noms de fichiers dans le nouvel ordre

        if not order:
            self._send_json({"error": "order list required"}, 400)
            return

        lang_path = self.projects_dir / project / "agents" / agent / lang

        if not lang_path.exists():
            self._send_json({"error": "Language folder not found"}, 404)
            return

        # Phase 1: Renommer vers des fichiers temporaires
        temp_files = {}
        for i, filename in enumerate(order):
            old_path = lang_path / filename
            if old_path.exists():
                # Nouveau nom avec le bon numéro
                base_name = filename.split("-", 1)[1] if "-" in filename else filename
                new_name = f"{(i + 1):02d}-{base_name}"
                temp_name = f"_temp_{i}_{filename}"
                temp_path = lang_path / temp_name

                # Stocker le contenu et supprimer l'ancien
                content = old_path.read_text(encoding="utf-8")
                temp_files[temp_name] = (new_name, content)
                old_path.unlink()

        # Phase 2: Créer les nouveaux fichiers
        renamed = []
        for temp_name, (new_name, content) in temp_files.items():
            new_path = lang_path / new_name
            new_path.write_text(content, encoding="utf-8")
            renamed.append({"old": temp_name.replace("_temp_", "").split("_", 1)[1], "new": new_name})

        self._send_json({
            "success": True,
            "renamed": renamed
        })

    def _delete_section(self, project: str, agent: str, data: dict):
        """Supprime une section."""
        section = data.get("section")
        lang = data.get("lang")

        if not section or not lang:
            self._send_json({"error": "section and lang required"}, 400)
            return

        section_path = self.projects_dir / project / "agents" / agent / lang / section

        if not section_path.exists():
            self._send_json({"error": "Section not found"}, 404)
            return

        section_path.unlink()
        self._send_json({
            "success": True,
            "deleted": f"{lang}/{section}"
        })

    def _build(self, data: dict):
        """Lance un build via le script build.py avec export automatique."""
        import subprocess

        project = data.get("project")
        agent = data.get("agent")
        auto_export = data.get("export", True)  # Export par défaut

        if not project:
            self._send_json({"error": "Project required"}, 400)
            return

        cmd = [sys.executable, "tools/build.py", "--project", project]
        if agent:
            cmd.extend(["--agent", agent])
        else:
            cmd.append("--all")

        # Auto-export activé par défaut
        if auto_export:
            cmd.append("--export")

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.studio_root),
                capture_output=True,
                text=True
            )
            self._send_json({
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "exported": auto_export
            })
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _translate_section_ai(self, project: str, agent: str, data: dict):
        """Real AI translation using Claude API."""
        from translate import translate_with_claude, get_language_name

        section = data.get("section")
        from_lang = data.get("from_lang")
        to_lang = data.get("to_lang")

        if not all([section, from_lang, to_lang]):
            self._send_json({"error": "section, from_lang, to_lang required"}, 400)
            return

        source_path = self.projects_dir / project / "agents" / agent / from_lang / section
        target_path = self.projects_dir / project / "agents" / agent / to_lang / section

        if not source_path.exists():
            self._send_json({"error": f"Source section not found: {from_lang}/{section}"}, 404)
            return

        # Read source content
        source_text = source_path.read_text(encoding="utf-8")

        try:
            # Translate using Claude API
            source_name = get_language_name(from_lang)
            target_name = get_language_name(to_lang)
            translated_text = translate_with_claude(source_text, source_name, target_name)

            # Create target directory if needed
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Save translated content
            target_path.write_text(translated_text, encoding="utf-8")

            self._send_json({
                "success": True,
                "message": f"Section traduite vers {to_lang}/{section}",
                "from": f"{from_lang}/{section}",
                "to": f"{to_lang}/{section}",
                "source_chars": len(source_text),
                "target_chars": len(translated_text),
                "source_words": len(source_text.split()),
                "target_words": len(translated_text.split())
            })

        except ValueError as e:
            # API key not set
            self._send_json({"error": str(e)}, 400)
        except ImportError as e:
            # anthropic package not installed
            self._send_json({"error": str(e)}, 500)
        except Exception as e:
            self._send_json({"error": f"Translation failed: {str(e)}"}, 500)

    def _expand_section(self, project: str, agent: str, lang: str, section: str, highlight: bool, html_preview: bool):
        """Expand includes in a section with markers."""
        from expand import expand_file, generate_html_preview

        if not section:
            self._send_json({"error": "section query param required"}, 400)
            return

        section_path = self.projects_dir / project / "agents" / agent / lang / section
        if not section_path.exists():
            self._send_json({"error": f"Section not found: {lang}/{section}"}, 404)
            return

        try:
            expanded = expand_file(project, agent, lang, section, highlight_local=highlight)

            if html_preview:
                html_content = generate_html_preview(
                    expanded,
                    title=f"{project}/{agent}/{lang}/{section}"
                )
                self._send_json({
                    "success": True,
                    "expanded": expanded,
                    "html": html_content,
                    "format": "html"
                })
            else:
                self._send_json({
                    "success": True,
                    "expanded": expanded,
                    "format": "markdown"
                })

        except FileNotFoundError as e:
            self._send_json({"error": str(e)}, 404)
        except RecursionError as e:
            self._send_json({"error": str(e)}, 400)
        except Exception as e:
            self._send_json({"error": f"Expand failed: {str(e)}"}, 500)

    def _collapse_section(self, project: str, agent: str, data: dict):
        """Collapse expanded content back to includes and save."""
        from expand import collapse_and_save

        section = data.get("section")
        lang = data.get("lang", "fr")
        expanded_content = data.get("content")
        dry_run = data.get("dry_run", False)

        if not section or not expanded_content:
            self._send_json({"error": "section and content required"}, 400)
            return

        try:
            modified_files = collapse_and_save(
                project, agent, lang, section,
                expanded_content,
                dry_run=dry_run
            )

            self._send_json({
                "success": True,
                "section": f"{lang}/{section}",
                "modified_includes": list(modified_files.keys()),
                "dry_run": dry_run
            })

        except Exception as e:
            self._send_json({"error": f"Collapse failed: {str(e)}"}, 500)

    def _get_protected_tokens(self):
        """Retourne la liste des tokens protégés pour la traduction."""
        tokens = [
            "{% include", "{%", "%}", "{{", "}}",
            "$state", "$derived", "$effect", "$props",
            "<script>", "</script>", "<style>", "</style>"
        ]
        self._send_json({"tokens": tokens})

    def _get_all_sections(self, project: str, agent: str, lang: str):
        """Retourne toutes les sections concaténées avec délimiteurs."""
        agent_path = self.projects_dir / project / "agents" / agent / lang

        if not agent_path.exists():
            self._send_json({"error": f"Agent not found: {agent}/{lang}"}, 404)
            return

        sections = {}
        order = []

        # Get all markdown files sorted
        for f in sorted(agent_path.iterdir()):
            if f.is_file() and f.suffix == ".md":
                order.append(f.name)
                with open(f, encoding="utf-8") as fp:
                    sections[f.name] = fp.read()

        self._send_json({
            "agent": agent,
            "lang": lang,
            "order": order,
            "sections": sections
        })

    def _expand_content(self, data: dict):
        """Expand includes dans un contenu fourni."""
        from expand import expand_includes

        content = data.get("content", "")
        lang = data.get("lang", "fr")
        project = data.get("project")

        if not content:
            self._send_json({"expanded": "", "has_includes": False})
            return

        if not project:
            self._send_json({"error": "Project is required"}, 400)
            return

        try:
            # Check if content has includes
            has_includes = "{% include" in content

            if has_includes:
                expanded = expand_includes(content, project, lang)
            else:
                expanded = content

            self._send_json({
                "expanded": expanded,
                "has_includes": has_includes,
                "original": content
            })
        except Exception as e:
            self._send_json({"error": f"Expand failed: {str(e)}"}, 500)

    def _collapse_content(self, data: dict):
        """Collapse expanded content back to {% include %} directives."""
        from expand import collapse_includes

        content = data.get("content", "")
        lang = data.get("lang", "fr")

        if not content:
            self._send_json({"collapsed": "", "modified_files": {}})
            return

        try:
            collapsed, modified_files = collapse_includes(content, lang)

            self._send_json({
                "collapsed": collapsed,
                "modified_files": modified_files,
                "original": content
            })
        except Exception as e:
            self._send_json({"error": f"Collapse failed: {str(e)}"}, 500)

    def _save_all_sections(self, project: str, agent: str, lang: str, data: dict):
        """Sauvegarde les sections à partir d'un dictionnaire."""
        print(f"[DEBUG _save_all_sections] project={project}, agent={agent}, lang={lang}")
        print(f"[DEBUG _save_all_sections] data keys: {list(data.keys()) if data else 'None'}")
        print(f"[DEBUG _save_all_sections] data type: {type(data)}")

        agent_path = self.projects_dir / project / "agents" / agent / lang
        print(f"[DEBUG _save_all_sections] agent_path: {agent_path}")

        if not agent_path.exists():
            agent_path.mkdir(parents=True, exist_ok=True)

        try:
            saved = []
            for section_name, content in data.items():
                section_path = agent_path / section_name
                print(f"[DEBUG _save_all_sections] Saving {section_name} to {section_path}, content length: {len(content)}")
                with open(section_path, "w", encoding="utf-8") as f:
                    f.write(content)
                saved.append(section_name)
                print(f"[DEBUG _save_all_sections] Saved {section_name}")

            self._send_json({
                "success": True,
                "saved": saved,
                "count": len(saved)
            })
        except Exception as e:
            self._send_json({"error": f"Save failed: {str(e)}"}, 500)

    def do_OPTIONS(self):
        """Gère les requêtes CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        """Override pour un logging plus propre."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(description="Prompt Studio API Server")
    parser.add_argument("--port", "-p", type=int, default=8080, help="Port (default: 8080)")
    parser.add_argument("--host", type=str, default="localhost", help="Host (default: localhost)")
    args = parser.parse_args()

    print()
    print("=" * 50)
    print("   PROMPT STUDIO - API Server")
    print("=" * 50)
    print()
    print(f"🌐 Server: http://{args.host}:{args.port}")
    print(f"📁 Editor: http://{args.host}:{args.port}/")
    print(f"📡 API:    http://{args.host}:{args.port}/api/")
    print()
    print("Press Ctrl+C to stop")
    print()

    server = HTTPServer((args.host, args.port), PromptStudioAPI)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        server.shutdown()


if __name__ == "__main__":
    main()
