# /ps:validate - Valider le prompt

Valide le prompt de l'agent actif avant le build.

## Prérequis

- Un projet ET un agent doivent être actifs
- Au moins une section doit exister

## Instructions

Mettre à jour `.state.json` avec `phase: "validate"`.

### 1. Vérifications automatiques

Effectuer les vérifications suivantes :

```
🔍 VALIDATION - Agent "{agent}"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 Sections (fr) :
```

Pour chaque section, vérifier :

| Vérification | Statut |
|--------------|--------|
| Fichier existe | ✅/❌ |
| Contenu non vide | ✅/❌ |
| Pas de TODO restants | ✅/⚠️ |
| Syntaxe Markdown valide | ✅/❌ |
| Includes valides | ✅/❌ |

### 2. Vérification des includes

Pour chaque `{% include '...' %}` trouvé :

```
🔗 INCLUDES :
├── {% include 'common/fr/01-context.md' %}  ✅ Fichier trouvé
├── {% include 'shared/fr/tools.md' %}       ❌ Fichier introuvable
└── {% include 'planner/fr/02-steps.md' %}   ✅ Fichier trouvé
```

### 3. Vérification des traductions

```
🌍 TRADUCTIONS :

| Section            | FR  | EN  |
|--------------------|-----|-----|
| 01-context.md      | ✅  | ✅  |
| 02-instructions.md | ✅  | ⚠️  |
| 03-tools.md        | ✅  | ❌  |
| 04-examples.md     | ✅  | ❌  |

⚠️ = Existe mais plus court que FR (peut-être incomplet)
❌ = Manquant
```

### 4. Analyse de cohérence

Vérifier la cohérence du prompt :

```
🧠 ANALYSE DE COHÉRENCE :

✅ Les sections se complètent logiquement
✅ Le contexte est cohérent avec les instructions
⚠️ L'exemple 2 ne correspond pas aux instructions décrites
✅ Les contraintes sont applicables
```

### 5. Résumé

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 RÉSUMÉ DE VALIDATION

✅ Validations réussies : 12
⚠️ Avertissements      : 3
❌ Erreurs             : 1

ERREURS À CORRIGER :
1. ❌ Include introuvable : shared/fr/tools.md

AVERTISSEMENTS :
1. ⚠️ TODO restant dans 03-tools.md ligne 15
2. ⚠️ Section en/02-instructions.md semble incomplète
3. ⚠️ Incohérence détectée dans exemple 2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{Si erreurs}
❌ Validation échouée. Corrigez les erreurs avant de build.

{Si seulement avertissements}
⚠️ Validation réussie avec avertissements.
💡 Prochaine étape : /ps:build pour compiler

{Si tout OK}
✅ Validation réussie !
```

## Résumé et Prochaines Étapes

À la fin de la validation, afficher :

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ VALIDATION TERMINÉE

📋 Ce qui a été vérifié :
   • Existence des sections
   • Contenu non vide
   • Syntaxe Markdown
   • Résolution des includes
   • Complétude des traductions
   • Cohérence globale

📊 Résultat :
   ✅ {N} validations réussies
   ⚠️ {N} avertissements
   ❌ {N} erreurs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 PROCHAINES COMMANDES DISPONIBLES

{Si succès}
▶️  /ps:build            Compiler le prompt (RECOMMANDÉ)
    /ps:translate        Compléter les traductions
    /ps:write [section]  Modifier une section

{Si erreurs}
▶️  /ps:write [section]  Corriger les erreurs (RECOMMANDÉ)
    /ps:translate        Ajouter les traductions manquantes
    /ps:status           Voir l'état détaillé
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
