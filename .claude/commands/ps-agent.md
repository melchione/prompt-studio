# /ps:agent - Gérer les agents

Créer ou activer un agent dans le projet actif.

## Usage

```
/ps:agent [nom]
```

## Prérequis

Un projet doit être actif. Sinon, afficher :
```
⚠️ Aucun projet actif. Utilisez /ps:project [nom] d'abord.
```

## Instructions

### Si un nom est fourni :

1. Vérifier si l'agent existe dans `projects/{projet}/agents/{nom}/`

2. **Si l'agent existe** :
   - L'activer en mettant à jour `.state.json` avec `active_agent: "{nom}"`
   - Afficher ses sections et leur état

3. **Si l'agent n'existe pas** :
   - Créer la structure :
     ```
     projects/{projet}/agents/{nom}/
     ├── fr/
     └── en/
     ```
   - L'activer dans `.state.json`
   - Passer automatiquement à la phase "conceive"
   - Afficher un message de bienvenue et lancer `/ps:conceive`

### Si aucun nom n'est fourni :

Lister tous les agents du projet actif avec :
- Nombre de sections
- Langues disponibles
- Dernier build

## Sortie attendue

```
✅ Agent "{nom}" activé dans projet "{projet}"

📄 Sections :
   fr/
   ├── 01-context.md      ✅ (245 mots)
   ├── 02-instructions.md ✅ (512 mots)
   └── 03-examples.md     ⏳ (en cours)
   en/
   ├── 01-context.md      ✅ (230 mots)
   ├── 02-instructions.md ❌ (manquant)
   └── 03-examples.md     ❌ (manquant)

💡 Prochaine étape : /ps:write 02-instructions.md pour continuer
```
