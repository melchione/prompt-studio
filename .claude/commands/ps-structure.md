# /ps:structure - Définir la structure

Définit la structure des sections pour l'agent actif.

## Prérequis

- Un projet ET un agent doivent être actifs
- La phase de conception devrait être complétée (fichier `conception.md` existe)

## Instructions

Mettre à jour `.state.json` avec `phase: "structure"`.

### 1. Analyser les techniques de prompting avancées (SUB-AGENT)

**IMPORTANT** : Avant de proposer une structure, lancer un sub-agent pour analyser les techniques disponibles.

```
Utiliser l'outil Task avec subagent_type="Explore" pour :

1. Lire TOUS les fichiers dans refs/system-prompting/ :
   - 01-routing-decision-strategies.md
   - 02-chain-of-thought-prompting.md
   - 03-least-to-most-prompting.md
   - 04-automatic-prompt-engineering.md
   - 05-evolinstruct-complexity.md
   - 06-prompt-chaining.md
   - 07-react-framework.md
   - 08-cognitive-flexibility.md
   - 09-implementation-guide.md

2. Lire le fichier conception.md de l'agent actif

3. Analyser et retourner :
   - Les techniques recommandées pour cet agent (avec justification)
   - Les techniques NON recommandées (avec raison)
   - Des suggestions de sections spécifiques à ajouter selon les techniques choisies
```

Afficher le résultat de l'analyse :

```
🧠 ANALYSE DES TECHNIQUES DE PROMPTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Basé sur la conception de l'agent "{agent}", voici l'analyse :

✅ TECHNIQUES RECOMMANDÉES :

1. {technique_1} ({fichier})
   → Justification : {raison}
   → Impact sur la structure : {suggestion de section}

2. {technique_2} ({fichier})
   → Justification : {raison}
   → Impact sur la structure : {suggestion de section}

❌ TECHNIQUES NON PERTINENTES :

- {technique_x} : {raison}
- {technique_y} : {raison}

💡 SECTIONS SUGGÉRÉES PAR LES TECHNIQUES :

- XX-reasoning.md (si CoT recommandé)
- XX-decision-flow.md (si Routing recommandé)
- XX-decomposition.md (si Least-to-Most recommandé)
- XX-react-loop.md (si ReAct recommandé)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 2. Proposer la structure basée sur l'analyse

Lire `projects/{projet}/agents/{agent}/conception.md` et proposer une structure intégrant les recommandations :

```
📐 STRUCTURE PROPOSÉE

Basé sur la conception ET les techniques recommandées :

📁 {agent}/
├── fr/
│   ├── 01-context.md        # Contexte et rôle de l'agent
│   ├── 02-instructions.md   # Instructions principales
│   ├── 03-tools.md          # Outils disponibles (si applicable)
│   ├── 04-examples.md       # Exemples d'utilisation
│   ├── 05-constraints.md    # Contraintes et règles
│   └── XX-{technique}.md    # Section(s) ajoutée(s) selon techniques
└── en/
    └── (même structure)

Cette structure vous convient-elle ?
- [O] Oui, créer cette structure
- [M] Modifier (ajouter/supprimer des sections)
- [P] Proposer ma propre structure
```

### 3. Si modification demandée

Permettre d'ajouter, renommer ou supprimer des sections :

```
📝 MODIFICATION DE STRUCTURE

Sections actuelles :
1. 01-context.md
2. 02-instructions.md
3. 03-tools.md
4. 04-examples.md
5. 05-constraints.md

Actions :
- [A] Ajouter une section
- [R] Renommer une section
- [S] Supprimer une section
- [I] Ajouter un include
- [V] Valider la structure
```

### 4. Identifier les includes

Analyser si certaines sections peuvent réutiliser du contenu d'autres agents :

```
🔗 INCLUDES POTENTIELS

J'ai détecté des opportunités de réutilisation :

- 01-context.md pourrait inclure :
  {% include 'common/fr/01-base-context.md' %}

- 03-tools.md pourrait inclure :
  {% include 'shared/fr/composio-tools.md' %}

Voulez-vous ajouter ces includes ?
```

### 5. Créer la structure et le fichier structure.md

Une fois validée :

**A. Créer les fichiers de sections** avec un template de base :

Pour chaque section, créer :

```markdown
<!-- Section: {nom} -->
<!-- Agent: {agent} -->
<!-- Projet: {projet} -->
<!-- Langue: {lang} -->
<!-- Techniques: {techniques applicables ou "Aucune"} -->

# {Titre de la section}

<!-- TODO: Rédiger cette section -->
<!-- Utilisez /ps:write {nom} pour commencer -->

{Si technique applicable}
<!--
🧠 TECHNIQUE À APPLIQUER : {nom_technique}
   Référence : refs/system-prompting/{fichier}
   Conseil : {conseil spécifique pour cette section}
-->
```

**B. Créer le fichier `structure.md`** dans `projects/{projet}/agents/{agent}/` :

```markdown
# Structure - Agent {agent}

> Généré le : {date}
> Projet : {projet}

## Techniques de Prompting Sélectionnées

| Technique | Fichier de référence | Justification |
|-----------|---------------------|---------------|
| {technique_1} | refs/system-prompting/{fichier} | {justification} |
| {technique_2} | refs/system-prompting/{fichier} | {justification} |

## Sections

| # | Fichier | Description | Techniques | Remarques |
|---|---------|-------------|------------|-----------|
| 01 | 01-context.md | Contexte et rôle | - | {remarques} |
| 02 | 02-instructions.md | Instructions principales | CoT | Implémenter le raisonnement étape par étape |
| 03 | 03-tools.md | Outils disponibles | ReAct | Boucle Thought → Action → Observation |
| 04 | 04-examples.md | Exemples d'utilisation | - | Illustrer les techniques en action |
| 05 | 05-constraints.md | Contraintes et règles | - | {remarques} |

## Includes Configurés

| Section | Include | Source |
|---------|---------|--------|
| 01-context.md | {% include 'common/fr/01-base-context.md' %} | Agent common |

## Notes de Conception

{Notes libres sur les choix de structure}
```

### 6. Résumé

```
✅ Structure créée !

📁 {agent}/
├── structure.md             📋 Guide de structure
├── fr/
│   ├── 01-context.md        ⏳
│   ├── 02-instructions.md   ⏳ (CoT)
│   ├── 03-tools.md          ⏳ (ReAct)
│   ├── 04-examples.md       ⏳
│   └── 05-constraints.md    ⏳
└── en/
    └── (5 fichiers créés)    ⏳

🧠 Techniques appliquées : {liste}
```

Mettre à jour `.state.json` avec `current_section: "01-context.md"`

## Résumé et Prochaines Étapes

À la fin de la commande, afficher :

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ STRUCTURE CRÉÉE

📋 Ce qui a été fait :
   • Analyse des techniques de prompting effectuée
   • Structure des sections définie
   • Dossiers fr/ et en/ créés
   • {N} fichiers de section créés par langue
   • Fichier structure.md généré avec les remarques
   • Includes potentiels identifiés
   • Templates de base ajoutés avec références aux techniques

📁 Fichiers créés :
   projects/{projet}/agents/{agent}/structure.md
   projects/{projet}/agents/{agent}/fr/*.md
   projects/{projet}/agents/{agent}/en/*.md

🧠 Techniques sélectionnées :
   {liste des techniques avec leurs sections cibles}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 PROCHAINES COMMANDES DISPONIBLES

▶️  /ps:write [section]   Rédiger une section (RECOMMANDÉ)
    /ps:status            Voir l'état du projet
    /ps:validate          Valider le prompt
    /ps:conceive          Revoir la conception

Suggestion : Commencez par /ps:write 01-context.md
💡 Consultez structure.md pour voir les techniques à appliquer par section
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
