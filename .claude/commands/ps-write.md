# /ps:write - Rédiger une section

Rédige ou modifie une section de l'agent actif.

## Usage

```
/ps:write [section]
```

## Prérequis

- Un projet ET un agent doivent être actifs
- La structure doit être définie (dossiers fr/ et en/ existent)

## Instructions

Mettre à jour `.state.json` avec `phase: "write"` et `current_section: "{section}"`.

### 1. Si une section est spécifiée

Ouvrir la section pour édition :

```
📝 RÉDACTION : {section}
Agent : {agent} | Projet : {projet}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 Contexte (depuis conception.md) :
{résumé pertinent de la conception}

📄 Contenu actuel ({lang}) :
{contenu actuel ou "Section vide"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Instructions :
- Décrivez le contenu souhaité
- Ou fournissez directement le texte à écrire
- Utilisez {% include 'agent/lang/section.md' %} pour les réutilisations
```

### 2. Rédaction guidée

Selon le type de section, proposer un template adapté :

**Pour 01-context.md :**
```markdown
# Contexte

Tu es {rôle de l'agent}.

## Ton rôle

{description du rôle}

## Ton environnement

{contexte système}

## Tes capacités

{liste des capacités}
```

**Pour 02-instructions.md :**
```markdown
# Instructions

## Objectif principal

{objectif}

## Étapes à suivre

1. {étape 1}
2. {étape 2}
3. {étape 3}

## Règles à respecter

- {règle 1}
- {règle 2}
```

**Pour XX-examples.md :**
```markdown
# Exemples

## Exemple 1 : {titre}

**Entrée :**
```
{entrée}
```

**Sortie attendue :**
```
{sortie}
```

## Exemple 2 : {titre}
...
```

### 3. Après la rédaction

Une fois le contenu fourni :

1. Écrire le fichier dans `projects/{projet}/agents/{agent}/fr/{section}`
2. Proposer la traduction :

```
✅ Section {section} sauvegardée (fr)

🌍 Voulez-vous créer la version anglaise ?
- [O] Oui, traduire automatiquement
- [M] Je vais la rédiger manuellement
- [P] Plus tard
```

### 4. Si aucune section spécifiée

Afficher la liste des sections avec leur état :

```
📄 SECTIONS - Agent "{agent}"

fr/
├── 01-context.md        ✅ Complète (234 mots)
├── 02-instructions.md   ⏳ En cours (156 mots)
├── 03-tools.md          ❌ Vide
├── 04-examples.md       ❌ Vide
└── 05-constraints.md    ❌ Vide

💡 Utilisez /ps:write {section} pour éditer
💡 Section suggérée : 03-tools.md (prochaine vide)
```
