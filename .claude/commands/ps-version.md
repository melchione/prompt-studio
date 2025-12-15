# /ps:version - Créer une version

Crée une nouvelle version du projet avec les prompts compilés.

## Usage

```
/ps:version [patch|minor|major]
```

- `patch` : 0.0.X - Corrections mineures
- `minor` : 0.X.0 - Nouvelles fonctionnalités (défaut)
- `major` : X.0.0 - Changements majeurs

## Prérequis

- Un projet doit être actif
- Un build récent doit exister (dist/ non vide)

## Instructions

### 1. Calcul de la nouvelle version

Lire la version actuelle depuis `.project.json` et incrémenter :

```
📦 VERSIONING - Projet "{projet}"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Version actuelle : 1.2.3
Type de release  : {type}
Nouvelle version : {nouvelle_version}

Voulez-vous continuer ? [O/N]
```

### 2. Générer le changelog

Demander un résumé des changements :

```
📝 CHANGELOG

Décrivez les changements de cette version :
(Laissez vide pour générer automatiquement depuis les commits)

```

Si auto-généré, analyser les modifications des fichiers depuis la dernière version.

### 3. Créer l'archive de version

Structure :
```
versions/{projet}/v{version}/
├── CHANGELOG.md
├── dist/
│   ├── fr/
│   │   ├── executive.md
│   │   ├── planner.md
│   │   └── ...
│   └── en/
│       └── ...
└── metadata.json
```

**metadata.json :**
```json
{
  "version": "{version}",
  "created_at": "{timestamp}",
  "previous_version": "{version_precedente}",
  "agents": ["executive", "planner", "executor"],
  "languages": ["fr", "en"],
  "changelog": "{résumé}",
  "stats": {
    "total_words": 12500,
    "total_sections": 45,
    "total_includes": 12
  }
}
```

### 4. Mise à jour du projet

Mettre à jour `.project.json` :
```json
{
  "version": "{nouvelle_version}",
  "last_release": "{timestamp}"
}
```

### 5. Confirmation

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Version {version} créée !

📦 Archivée dans : versions/{projet}/v{version}/

📋 Changelog :
{changelog}

📊 Contenu :
   - Agents   : 5
   - Langues  : 2
   - Sections : 45
   - Mots     : 12,500

💡 Prochaine étape : /ps:export pour déployer cette version
```

### 6. Liste des versions

Si appelé sans argument et qu'il existe des versions :

```
📦 VERSIONS - Projet "{projet}"

| Version | Date       | Agents | Changelog              |
|---------|------------|--------|------------------------|
| v1.2.3  | 2025-01-20 | 5      | Ajout agent planner    |
| v1.2.2  | 2025-01-15 | 4      | Fix traductions EN     |
| v1.2.1  | 2025-01-10 | 4      | Corrections mineures   |
| v1.2.0  | 2025-01-05 | 4      | Nouvelle structure     |

💡 Utilisez /ps:version [patch|minor|major] pour créer une nouvelle version
```
