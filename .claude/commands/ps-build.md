# /ps:build - Compiler les prompts

Compile les prompts en résolvant les includes et génère les fichiers finaux.

## Usage

```
/ps:build [--all]
```

- Sans argument : build l'agent actif
- `--all` : build tous les agents du projet

## Prérequis

- Un projet doit être actif
- Un agent doit être actif (sauf si --all)

## Instructions

### 1. Exécuter le script de build

```bash
python tools/build.py --project {projet} --agent {agent}
```

Le script effectue :

1. **Lecture des sections** : Charge tous les fichiers .md de l'agent
2. **Résolution des includes** : Remplace les `{% include '...' %}` par le contenu réel
3. **Concaténation** : Assemble les sections dans l'ordre numérique
4. **Génération** : Écrit le fichier final dans `dist/`

### 2. Affichage du processus

```
🔨 BUILD - Agent "{agent}"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 Source : projects/{projet}/agents/{agent}/
📂 Output : projects/{projet}/dist/{lang}/

🔄 Traitement FR :
   ├── 01-context.md        ✅ (234 mots)
   │   └── include: common/fr/01-base.md  ✅
   ├── 02-instructions.md   ✅ (512 mots)
   ├── 03-tools.md          ✅ (189 mots)
   │   └── include: shared/fr/composio.md ✅
   ├── 04-examples.md       ✅ (345 mots)
   └── 05-constraints.md    ✅ (98 mots)

   📄 Généré : dist/fr/{agent}.md (1378 mots)

🔄 Traitement EN :
   ├── 01-context.md        ✅ (220 mots)
   ...

   📄 Généré : dist/en/{agent}.md (1290 mots)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Build réussi !

📊 Statistiques :
   - Sections traitées : 10
   - Includes résolus  : 4
   - Fichiers générés  : 2
   - Taille totale     : 2668 mots

💡 Prochaine étape : /ps:version pour créer une release
```

### 3. Structure du fichier généré

Le fichier compilé contient des marqueurs pour traçabilité :

```markdown
<!--
  Prompt Studio Build
  Project: {projet}
  Agent: {agent}
  Version: {version}
  Built: {timestamp}
  Language: {lang}
-->

<!-- @section: 01-context.md -->
{contenu de 01-context.md}

<!-- @section: 02-instructions.md -->
{contenu de 02-instructions.md}

<!-- @include-start: common/fr/01-base.md -->
{contenu inclus}
<!-- @include-end: common/fr/01-base.md -->

...
```

### 4. Mise à jour de l'état

Mettre à jour `.state.json` :
```json
{
  "last_build": "{timestamp ISO}",
  "phase": "build"
}
```

### 5. En cas d'erreur

```
❌ BUILD ÉCHOUÉ

Erreur : Include introuvable
   Fichier : shared/fr/tools.md
   Dans    : 03-tools.md ligne 15

💡 Vérifiez que le fichier existe ou corrigez le chemin de l'include.
💡 Utilisez /ps:validate pour vérifier tous les includes.
```

## Résumé et Prochaines Étapes

À la fin du build, afficher :

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ BUILD TERMINÉ

📋 Ce qui a été fait :
   • Sections chargées et validées
   • Includes résolus récursivement
   • Fichiers compilés générés
   • Marqueurs de traçabilité ajoutés

📁 Fichiers créés :
   projects/{projet}/dist/fr/{agent}.md
   projects/{projet}/dist/en/{agent}.md

📊 Statistiques :
   • Sections : {N}
   • Includes : {N}
   • Mots (FR) : {N}
   • Mots (EN) : {N}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 PROCHAINES COMMANDES DISPONIBLES

▶️  /ps:version [type]   Créer une release (RECOMMANDÉ)
    /ps:export [chemin]  Exporter vers un projet externe
    /ps:validate         Revalider le prompt
    /ps:editor           Ouvrir l'éditeur web

{Si erreurs de build}
▶️  /ps:validate         Diagnostiquer les erreurs (RECOMMANDÉ)
    /ps:write [section]  Corriger les sections
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
