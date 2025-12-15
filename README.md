# Prompt Studio

Système de gestion et conception de prompts pour systèmes multi-agents, intégré à Claude Code.

## Installation

```bash
git clone https://github.com/[votre-repo]/prompt-studio.git
cd prompt-studio
bash install.sh
```

## Conception Guidée avec Claude Code

Prompt Studio propose un workflow en 5 phases pour concevoir des prompts de qualité :

### Phase 1 : Conception (`/ps:conceive`)

Claude vous guide à travers une série de questions pour comprendre :

1. **Objectif** - Quel est le but de l'agent ?
2. **Contexte** - Dans quel système s'intègre-t-il ?
3. **Entrées/Sorties** - Quelles données traite-t-il ?
4. **Contraintes** - Limites techniques, format, langue ?
5. **Exemples** - Cas d'usage concrets

Cette phase produit un document de conception qui servira de base.

### Phase 2 : Structure (`/ps:structure`)

Définition de l'architecture du prompt :

- **Sections numérotées** : `01-context.md`, `02-instructions.md`, `03-examples.md`...
- **Includes** : Identifier les sections réutilisables d'autres agents
- **Variables** : Définir les placeholders `{{ variable }}`
- **Langues** : Planifier les versions `fr/` et `en/`

### Phase 3 : Rédaction (`/ps:write`)

Écriture section par section avec Claude :

```bash
/ps:write 01-context      # Rédiger le contexte
/ps:write 02-instructions # Rédiger les instructions
/ps:write                 # Rédiger la section suivante
```

Bonnes pratiques appliquées automatiquement :
- Format XML pour la structure
- Concision sans sacrifier la clarté
- Exemples intégrés quand pertinent

### Phase 4 : Validation (`/ps:validate`)

Vérification complète :

- Cohérence entre toutes les sections
- Résolution des includes (pas de références cassées)
- Complétude des traductions FR/EN
- Test de build

### Phase 5 : Versioning (`/ps:version`)

Publication d'une version :

```bash
/ps:version patch  # 1.0.0 → 1.0.1 (corrections)
/ps:version minor  # 1.0.0 → 1.1.0 (nouvelles fonctionnalités)
/ps:version major  # 1.0.0 → 2.0.0 (changements majeurs)
```

Chaque version est archivée avec son changelog.

## Interface Web

L'éditeur web permet de visualiser et modifier les prompts avec une interface graphique.

### Lancement

```bash
# Via Claude Code
/ps:editor

# Ou directement
python3 tools/server.py
# Ouvrir http://localhost:8080
```

### Fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| **Monaco Editor** | Éditeur de code avec coloration syntaxique Markdown |
| **Navigation projet** | Sélection projet → agent → section |
| **Switch FR/EN** | Basculer entre les versions linguistiques |
| **Traduction** | Copier une section vers l'autre langue pour traduction |
| **Réorganisation** | Drag & drop pour réordonner les sections |
| **Création de section** | Modal avec numérotation automatique et création bilingue |
| **Suppression** | Supprimer une section (par langue) |
| **Synchronisation** | Copier les sections manquantes vers l'autre langue |
| **Insertion d'includes** | Modal pour parcourir et insérer des références |
| **Build intégré** | Compiler et prévisualiser le résultat |

### Gestion des traductions

L'interface affiche un indicateur visuel pour chaque section :
- ✓ (vert) : La traduction existe dans l'autre langue
- ! (rouge) : La section n'a pas encore été traduite

**Actions disponibles :**
- **Bouton "Traduire vers EN/FR"** : Copie la section actuelle vers l'autre langue
- **Bouton "🔄" (sidebar)** : Synchronise toutes les sections manquantes entre FR et EN

### Réorganisation des sections

Glissez-déposez les sections dans la sidebar pour modifier leur ordre. Les fichiers sont automatiquement renommés avec le bon numéro (01-, 02-, etc.).

### Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl+S` | Sauvegarder la section |
| `Ctrl+I` | Ouvrir le modal d'includes |
| `Escape` | Fermer les modales |

### Modal d'Includes

Le modal d'includes (`Ctrl+I`) permet de :

1. **Parcourir** tous les agents et leurs sections
2. **Prévisualiser** le contenu avant insertion
3. **Insérer** la référence au curseur

Format inséré :
```markdown
{% include 'agent-name/fr/01-section.md' %}
```

### API REST

L'éditeur communique via une API :

| Endpoint | Description |
|----------|-------------|
| `GET /api/state` | État actuel (projet, agent, phase) |
| `GET /api/projects` | Liste des projets |
| `GET /api/projects/{name}/agents` | Agents d'un projet |
| `GET /api/projects/{p}/agents/{a}/{lang}/{section}` | Contenu d'une section |
| `POST /api/projects/{p}/agents/{a}/{lang}/{section}` | Sauvegarder une section |
| `POST /api/projects/{p}/agents/{a}/translate` | Copier section vers autre langue |
| `POST /api/projects/{p}/agents/{a}/reorder` | Réordonner les sections |
| `POST /api/projects/{p}/agents/{a}/delete-section` | Supprimer une section |
| `GET /api/includes` | Sections disponibles pour includes |
| `POST /api/build` | Compiler un prompt |

## Commandes Claude Code

| Commande | Description |
|----------|-------------|
| `/ps:status` | État actuel du projet |
| `/ps:project [name]` | Créer ou activer un projet |
| `/ps:agent [name]` | Créer ou éditer un agent |
| `/ps:conceive` | Démarrer la conception guidée |
| `/ps:structure` | Définir les sections |
| `/ps:write [section]` | Rédiger une section |
| `/ps:validate` | Valider le prompt |
| `/ps:build` | Compiler (résoudre includes) |
| `/ps:version [type]` | Créer une version |
| `/ps:export [path]` | Exporter vers un autre projet |
| `/ps:editor` | Lancer l'interface web |

## Structure des fichiers

```
prompt-studio/
├── CLAUDE.md              # System prompt pour Claude Code
├── .state.json            # État global (projet actif, phase)
├── projects/
│   └── {project}/
│       ├── .project.json  # Configuration du projet
│       ├── agents/
│       │   └── {agent}/
│       │       ├── fr/
│       │       │   ├── 01-context.md
│       │       │   ├── 02-instructions.md
│       │       │   └── ...
│       │       └── en/
│       │           └── ...
│       └── dist/          # Prompts compilés
│           ├── fr/
│           └── en/
├── versions/
│   └── {project}/
│       └── v1.0.0/        # Archives versionnées
├── tools/
│   ├── install.py         # Installation interactive
│   ├── build.py           # Compilation des prompts
│   ├── server.py          # API pour l'éditeur web
│   └── migrate.py         # Import de prompts existants
└── editor/
    └── index.html         # Interface web
```

## Système d'Includes

Réutilisez des sections entre agents pour éviter la duplication :

```markdown
{% include 'common/fr/01-context.md' %}
{% include 'executive/fr/03-tools.md' %}
```

### Résolution

Lors du build, les includes sont remplacés par le contenu réel :

```markdown
<!-- @include-start: common/fr/01-context.md -->
[Contenu de la section]
<!-- @include-end: common/fr/01-context.md -->
```

### Règles

- **Profondeur max** : 10 niveaux d'includes imbriqués
- **Références relatives** : Par rapport au dossier `agents/` du projet
- **Marqueurs** : Tracabilité conservée dans le build

## Migration de prompts existants

Pour importer des prompts depuis un autre projet :

```bash
python3 tools/migrate.py --source /chemin/vers/prompts --project mon-projet
```

Le script détecte automatiquement la structure et crée les fichiers appropriés.

## Exemple de workflow complet

```bash
# 1. Démarrer Claude Code
cd prompt-studio
claude

# 2. Créer un projet
/ps:project mon-saas

# 3. Créer un agent
/ps:agent support-client

# 4. Conception guidée
/ps:conceive
# → Claude pose des questions sur l'objectif, contexte, etc.

# 5. Définir la structure
/ps:structure
# → Claude propose une architecture de sections

# 6. Rédiger
/ps:write 01-context
/ps:write 02-instructions
/ps:write 03-examples

# 7. Valider
/ps:validate

# 8. Compiler
/ps:build

# 9. Versionner
/ps:version minor

# 10. Exporter vers votre projet
/ps:export /chemin/vers/mon-projet/prompts
```

## License

MIT
