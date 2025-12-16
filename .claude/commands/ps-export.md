# /ps:export - Exporter les prompts

Exporte les prompts compilés vers un projet externe.

## Usage

```
/ps:export [chemin] [--version X.X.X]
```

- `chemin` : Dossier de destination (ou utilise `export_path` du projet)
- `--version` : Version spécifique à exporter (défaut: dernière)

## Prérequis

- Un projet doit être actif
- Un build ou une version doit exister

## Instructions

### 1. Vérifier la destination

```
📤 EXPORT - Projet "{projet}"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Source  : {dist/ ou versions/vX.X.X/}
Version : {version}

Destination : {chemin}
```

Si le chemin n'est pas fourni et `export_path` n'est pas configuré :

```
⚠️ Aucun chemin d'export configuré.

Entrez le chemin de destination :
(Ex: /Users/melkione/Projets/Cowai/fast-api/features/prompt_building/prompts)

💡 Ce chemin sera sauvegardé dans .project.json pour les prochains exports.
```

### 2. Vérifier les permissions

Le chemin doit être dans `allowedDirectories` de `.claude/settings.json` :

```
🔐 Vérification des permissions...

✅ Chemin autorisé : /Users/melkione/Projets/Cowai/...
```

Si non autorisé :
```
❌ Chemin non autorisé.

Ajoutez ce chemin à .claude/settings.json :
{
  "allowedDirectories": [
    "/Users/melkione/Projets/Cowai"
  ]
}
```

### 3. Prévisualisation

```
📋 FICHIERS À EXPORTER :

dist/
├── fr/
│   ├── executive.md      → {dest}/executive/fr/prompt.md
│   ├── planner.md        → {dest}/planner/fr/prompt.md
│   └── executor.md       → {dest}/executor/fr/prompt.md
└── en/
    ├── executive.md      → {dest}/executive/en/prompt.md
    ├── planner.md        → {dest}/planner/en/prompt.md
    └── executor.md       → {dest}/executor/en/prompt.md

Total : 6 fichiers

⚠️ Les fichiers existants seront écrasés.

Confirmer l'export ? [O/N]
```

### 4. Exécuter l'export

```
🔄 Export en cours...

├── executive/fr/prompt.md  ✅ Créé
├── executive/en/prompt.md  ✅ Créé
├── planner/fr/prompt.md    ✅ Créé
├── planner/en/prompt.md    ✅ Créé
├── executor/fr/prompt.md   ✅ Créé
└── executor/en/prompt.md   ✅ Créé
```

### 5. Générer le manifest

Créer un fichier `_manifest.json` dans la destination :

```json
{
  "exported_from": "prompt-studio",
  "project": "{projet}",
  "version": "{version}",
  "exported_at": "{timestamp}",
  "agents": [
    {
      "name": "executive",
      "languages": ["fr", "en"],
      "path": "executive/"
    },
    ...
  ]
}
```

### 6. Confirmation

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Export réussi !

📤 Destination : {chemin}
📦 Version     : {version}
📄 Fichiers    : 6

Manifest créé : {chemin}/_manifest.json

💡 Les prompts sont prêts à être utilisés dans le projet cible.
```

### 7. Mise à jour du projet

Sauvegarder le chemin d'export dans `.project.json` :
```json
{
  "export_path": "{chemin}",
  "last_export": "{timestamp}",
  "last_export_version": "{version}"
}
```

## Résumé et Prochaines Étapes

À la fin de l'export, afficher :

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ EXPORT TERMINÉ

📋 Ce qui a été fait :
   • Prompts copiés vers {destination}
   • Structure agent/lang/ créée
   • Manifest _manifest.json généré
   • Chemin d'export sauvegardé

📁 Fichiers créés :
   {destination}/
   ├── {agent}/fr/prompt.md
   ├── {agent}/en/prompt.md
   └── _manifest.json

📊 Statistiques :
   • Fichiers exportés : {N}
   • Version : {X.Y.Z}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 PROCHAINES COMMANDES DISPONIBLES

    /ps:status           Voir l'état du projet
    /ps:version          Créer une nouvelle version
    /ps:build            Recompiler les prompts
    /ps:export           Re-exporter avec les mêmes paramètres

💡 Les prompts sont maintenant disponibles dans le projet cible.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
