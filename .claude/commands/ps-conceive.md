# /ps:conceive - Phase de conception

Démarre ou continue la phase de conception pour l'agent actif.

## Prérequis

Un projet ET un agent doivent être actifs.

## Références de Conception

**IMPORTANT** : Avant de commencer la conception, consulter les guides de référence :

📚 **Guides disponibles** (`refs/system-prompting/`) :
- `01-routing-decision-strategies.md` - Stratégies de routing
- `02-chain-of-thought-prompting.md` - Raisonnement étape par étape
- `03-least-to-most-prompting.md` - Décomposition en sous-problèmes
- `06-prompt-chaining.md` - Chaînage séquentiel et workflows
- `07-react-framework.md` - Synergie raisonnement et action
- `08-cognitive-flexibility.md` - Adaptation dynamique
- `09-implementation-guide.md` - Guide d'implémentation

Ces guides aident à choisir les meilleures techniques de prompting selon le type d'agent à concevoir.

## Instructions

Mettre à jour `.state.json` avec `phase: "conceive"`.

Guider l'utilisateur à travers une série de questions pour comprendre l'agent :

### 1. Objectif Principal
```
🎯 OBJECTIF DE L'AGENT

Quel est le but principal de cet agent ?
(Ex: "Gérer le calendrier de l'utilisateur", "Orchestrer les sous-agents")

👉 Décrivez en 1-2 phrases :
```

Attendre la réponse, puis :

### 2. Contexte d'Utilisation
```
🌍 CONTEXTE

Dans quel système s'intègre cet agent ?
- Fait-il partie d'un système multi-agents ?
- Avec quels autres agents interagit-il ?
- Qui sont les utilisateurs finaux ?

👉 Décrivez le contexte :
```

### 3. Entrées et Sorties
```
📥 ENTRÉES / 📤 SORTIES

Quelles données reçoit l'agent ?
(Ex: messages utilisateur, contexte de session, données d'outils)

Quelles données produit-il ?
(Ex: réponses textuelles, appels d'outils, décisions de routage)

👉 Listez les entrées et sorties :
```

### 4. Contraintes
```
⚠️ CONTRAINTES

Y a-t-il des contraintes à respecter ?
- Format de sortie spécifique (JSON, XML, Markdown)
- Limite de tokens
- Temps de réponse
- Règles métier

👉 Listez les contraintes :
```

### 5. Exemples d'Usage
```
💡 EXEMPLES

Donnez 2-3 exemples concrets d'utilisation :

Exemple 1 :
- Entrée : "..."
- Sortie attendue : "..."

👉 Décrivez vos exemples :
```

### Résumé

Après avoir collecté toutes les réponses, générer un résumé :

```
📋 RÉSUMÉ DE CONCEPTION - Agent "{nom}"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Objectif :
{objectif}

🌍 Contexte :
{contexte}

📥 Entrées :
{entrées}

📤 Sorties :
{sorties}

⚠️ Contraintes :
{contraintes}

💡 Exemples :
{exemples}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Conception validée !
```

Sauvegarder ce résumé dans `projects/{projet}/agents/{agent}/conception.md`

## Résumé et Prochaines Étapes

À la fin de la commande, afficher :

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ CONCEPTION TERMINÉE

📋 Ce qui a été fait :
   • Objectif de l'agent défini
   • Contexte d'utilisation documenté
   • Entrées/sorties identifiées
   • Contraintes listées
   • Exemples d'usage créés
   • Fichier conception.md sauvegardé

📁 Fichier créé :
   projects/{projet}/agents/{agent}/conception.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 PROCHAINES COMMANDES DISPONIBLES

▶️  /ps:structure      Définir les sections du prompt (RECOMMANDÉ)
    /ps:status         Voir l'état du projet
    /ps:agent          Changer d'agent
    /ps:project        Changer de projet

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
