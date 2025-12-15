# /ps:structure - Définir la structure

Définit la structure des sections pour l'agent actif.

## Prérequis

- Un projet ET un agent doivent être actifs
- La phase de conception devrait être complétée (fichier `conception.md` existe)

## Instructions

Mettre à jour `.state.json` avec `phase: "structure"`.

### 1. Analyser la conception

Lire `projects/{projet}/agents/{agent}/conception.md` et proposer une structure :

```
📐 STRUCTURE PROPOSÉE

Basé sur la conception, voici la structure recommandée :

📁 {agent}/
├── fr/
│   ├── 01-context.md        # Contexte et rôle de l'agent
│   ├── 02-instructions.md   # Instructions principales
│   ├── 03-tools.md          # Outils disponibles (si applicable)
│   ├── 04-examples.md       # Exemples d'utilisation
│   └── 05-constraints.md    # Contraintes et règles
└── en/
    └── (même structure)

Cette structure vous convient-elle ?
- [O] Oui, créer cette structure
- [M] Modifier (ajouter/supprimer des sections)
- [P] Proposer ma propre structure
```

### 2. Si modification demandée

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

### 3. Identifier les includes

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

### 4. Créer la structure

Une fois validée, créer les fichiers vides avec un template de base :

Pour chaque section, créer :

```markdown
<!-- Section: {nom} -->
<!-- Agent: {agent} -->
<!-- Projet: {projet} -->
<!-- Langue: {lang} -->

# {Titre de la section}

<!-- TODO: Rédiger cette section -->
<!-- Utilisez /ps:write {nom} pour commencer -->
```

### 5. Résumé

```
✅ Structure créée !

📁 {agent}/
├── fr/
│   ├── 01-context.md        ⏳
│   ├── 02-instructions.md   ⏳
│   ├── 03-tools.md          ⏳
│   ├── 04-examples.md       ⏳
│   └── 05-constraints.md    ⏳
└── en/
    └── (5 fichiers créés)    ⏳

💡 Prochaine étape : /ps:write 01-context.md pour commencer la rédaction
```

Mettre à jour `.state.json` avec `current_section: "01-context.md"`
