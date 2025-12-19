# /ps:project - Gérer les projets

Créer ou activer un projet.

## Usage

```
/ps:project [nom]
```

## Instructions

### Si un nom est fourni :

1. Vérifier si le projet existe dans `projects/{nom}/`

2. **Si le projet existe** :
   - L'activer en mettant à jour `.state.json` avec `active_project: "{nom}"`
   - Afficher ses informations (agents, dernière modification, version)

3. **Si le projet n'existe pas** :
   - Créer la structure :
     ```
     projects/{nom}/
     ├── .project.json
     └── agents/
     ```
   - Créer `.project.json` avec :
     ```json
     {
       "name": "{nom}",
       "created_at": "{timestamp ISO}",
       "version": "0.0.0",
       "default_language": "fr",
       "export_path": null,
       "agents": []
     }
     ```
   - L'activer dans `.state.json`
   - Afficher un message de confirmation

### Si aucun nom n'est fourni :

Lister tous les projets disponibles avec leurs informations :
- Nombre d'agents
- Version actuelle
- Dernière modification

## Sortie attendue

```
✅ Projet "{nom}" activé

📋 Informations :
   Version : 0.1.0
   Agents  : 3 (executive, planner, executor)
   Langues : fr, en
   Export  : /path/to/export
```

## Résumé et Prochaines Étapes

À la fin de l'activation/création de projet, afficher :

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PROJET {CRÉÉ|ACTIVÉ}

📋 Ce qui a été fait :
   • Projet "{nom}" {créé|activé}
   • .state.json mis à jour
   {Si nouveau} • Structure de base créée
   {Si nouveau} • .project.json initialisé

📁 Structure :
   projects/{nom}/
   ├── .project.json
   └── agents/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 PROCHAINES COMMANDES DISPONIBLES

{Si nouveau projet}
▶️  /ps:agent [nom]      Créer un premier agent (RECOMMANDÉ)
    /ps:status           Voir l'état du projet

{Si projet existant sans agent actif}
▶️  /ps:agent [nom]      Activer ou créer un agent (RECOMMANDÉ)
    /ps:status           Voir les agents disponibles

{Si projet existant avec agents}
▶️  /ps:agent [nom]      Choisir un agent (RECOMMANDÉ)
    /ps:build --all      Compiler tous les agents
    /ps:status           Voir l'état complet
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
