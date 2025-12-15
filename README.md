# Prompt Studio

Système de gestion et conception de prompts pour systèmes multi-agents, intégré à Claude Code.

## Installation

```bash
git clone https://github.com/[votre-repo]/prompt-studio.git
cd prompt-studio
bash install.sh
```

## Utilisation

### Avec Claude Code (recommandé)

```bash
cd prompt-studio
claude
```

Commandes disponibles :
- `/ps:status` - État actuel
- `/ps:project [name]` - Créer/activer un projet
- `/ps:agent [name]` - Créer/éditer un agent
- `/ps:conceive` - Phase de conception guidée
- `/ps:structure` - Définir les sections
- `/ps:write [section]` - Rédiger une section
- `/ps:validate` - Valider le prompt
- `/ps:build` - Compiler (résoudre includes)
- `/ps:version [type]` - Créer une version
- `/ps:export [path]` - Exporter
- `/ps:editor` - Lancer l'interface web

### Interface Web

```bash
python3 tools/server.py
# Ouvrir http://localhost:8080
```

## Structure

```
prompt-studio/
├── CLAUDE.md              # System prompt
├── projects/              # Vos projets
│   └── {project}/
│       ├── agents/
│       │   └── {agent}/
│       │       ├── fr/
│       │       └── en/
│       └── dist/          # Prompts compilés
├── tools/
│   ├── install.py         # Installation
│   ├── build.py           # Compilation
│   ├── server.py          # API web
│   └── migrate.py         # Import existant
└── editor/                # Interface web
```

## Includes

Réutiliser des sections entre agents :

```markdown
{% include 'common/fr/01-context.md' %}
```

## License

MIT
