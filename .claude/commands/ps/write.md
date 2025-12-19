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

### 1. Charger le contexte de la section

**IMPORTANT** : Avant de commencer la rédaction, lire les fichiers de contexte :

1. Lire `projects/{projet}/agents/{agent}/conception.md` pour le contexte global
2. Lire `projects/{projet}/agents/{agent}/structure.md` pour :
   - Les techniques de prompting assignées à cette section
   - Les remarques spécifiques
   - Les includes configurés

3. **Si une technique est assignée à la section**, lire le fichier de référence correspondant dans `refs/system-prompting/` pour pouvoir guider la rédaction.

### 2. Si une section est spécifiée

Ouvrir la section pour édition avec le contexte enrichi :

```
📝 RÉDACTION : {section}
Agent : {agent} | Projet : {projet}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 Contexte (depuis conception.md) :
{résumé pertinent de la conception}

📄 Contenu actuel ({lang}) :
{contenu actuel ou "Section vide"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 TECHNIQUES À APPLIQUER (depuis structure.md)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{Si technique(s) assignée(s)}
📚 Technique : {nom_technique}
   Référence : refs/system-prompting/{fichier}

   💡 Conseils d'implémentation :
   {Résumé des points clés de la technique extraits du fichier de référence}

   📝 Pattern recommandé :
   {Template ou pattern spécifique à cette technique}

{Si remarques dans structure.md}
📌 Remarques :
   {remarques de structure.md pour cette section}

{Si aucune technique}
ℹ️  Aucune technique spécifique assignée à cette section.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Instructions :
- Décrivez le contenu souhaité
- Ou fournissez directement le texte à écrire
- Utilisez {% include 'agent/lang/section.md' %} pour les réutilisations
- Appliquez les techniques indiquées ci-dessus si pertinent
```

### 3. Rédaction guidée selon la technique

**Si Chain-of-Thought (CoT) est assigné :**
```markdown
## Processus de raisonnement

Pour chaque demande, tu dois :

1. **Analyser** : Identifier les éléments clés de la demande
   - Que demande l'utilisateur ?
   - Quelles informations sont disponibles ?
   - Quelles sont les contraintes ?

2. **Planifier** : Définir les étapes nécessaires
   - Quelles actions sont requises ?
   - Dans quel ordre ?
   - Quelles dépendances ?

3. **Exécuter** : Réaliser chaque étape
   - Appliquer la logique
   - Vérifier les résultats intermédiaires

4. **Vérifier** : Valider le résultat final
   - Le résultat répond-il à la demande ?
   - Y a-t-il des erreurs ?
```

**Si ReAct est assigné :**
```markdown
## Boucle d'action

Pour chaque tâche, suivre le cycle :

### Thought (Réflexion)
Avant chaque action, expliciter ta réflexion :
- Quel est l'objectif ?
- Quelle information me manque ?
- Quelle action est la plus pertinente ?

### Action
Exécuter l'action choisie :
- Appel d'outil
- Requête
- Calcul

### Observation
Analyser le résultat :
- Qu'ai-je obtenu ?
- Est-ce suffisant ?
- Que faire ensuite ?

Répéter jusqu'à résolution complète.
```

**Si Routing/Decision est assigné :**
```markdown
## Arbre de décision

Évaluer la demande selon ces critères :

```
demande
├── Type A ?
│   ├── Oui → Action A
│   └── Non ↓
├── Type B ?
│   ├── Oui → Action B
│   └── Non ↓
└── Défaut → Action par défaut
```

Critères de classification :
- {critère 1} → {résultat}
- {critère 2} → {résultat}
```

**Si Least-to-Most est assigné :**
```markdown
## Décomposition progressive

Pour les problèmes complexes :

1. **Identifier les sous-problèmes**
   - Décomposer en éléments simples
   - Ordonner par dépendance

2. **Résoudre séquentiellement**
   - Commencer par le plus simple
   - Utiliser chaque solution pour le suivant

3. **Assembler la solution finale**
   - Combiner les résultats
   - Vérifier la cohérence globale
```

### 4. Templates standards (si aucune technique spécifique)

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

### 5. Après la rédaction

Une fois le contenu fourni :

1. Écrire le fichier dans `projects/{projet}/agents/{agent}/fr/{section}`
2. Proposer la traduction :

```
✅ Section {section} sauvegardée (fr)

{Si technique appliquée}
🧠 Technique {technique} intégrée dans cette section

🌍 Voulez-vous créer la version anglaise ?
- [O] Oui, traduire automatiquement
- [M] Je vais la rédiger manuellement
- [P] Plus tard
```

### 6. Si aucune section spécifiée

Afficher la liste des sections avec leur état ET les techniques assignées :

```
📄 SECTIONS - Agent "{agent}"

fr/
├── 01-context.md        ✅ Complète (234 mots)
├── 02-instructions.md   ⏳ En cours (156 mots)     🧠 CoT
├── 03-tools.md          ❌ Vide                    🧠 ReAct
├── 04-examples.md       ❌ Vide
└── 05-constraints.md    ❌ Vide

💡 Utilisez /ps:write {section} pour éditer
💡 Section suggérée : 03-tools.md (prochaine vide, technique ReAct à appliquer)
```

## Résumé et Prochaines Étapes

À la fin de la rédaction d'une section, afficher :

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ SECTION RÉDIGÉE

📋 Ce qui a été fait :
   • Section {section} rédigée ({N} mots)
   • Fichier sauvegardé dans {lang}/
   {Si technique appliquée}
   • Technique {technique} intégrée

📁 Fichier modifié :
   projects/{projet}/agents/{agent}/{lang}/{section}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 PROCHAINES COMMANDES DISPONIBLES

▶️  /ps:write [section]   Rédiger une autre section
    /ps:translate         Traduire vers l'autre langue
    /ps:validate          Valider le prompt complet
    /ps:build             Compiler le prompt

{Si toutes les sections sont complètes}
Suggestion : /ps:validate pour vérifier avant le build

{Si des sections sont vides}
Suggestion : /ps:write {prochaine_section_vide}
{Si technique assignée à la prochaine section}
💡 La section {prochaine} utilise la technique {technique}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
