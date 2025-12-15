# /ps:conceive - Phase de conception

Démarre ou continue la phase de conception pour l'agent actif.

## Prérequis

Un projet ET un agent doivent être actifs.

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
💡 Prochaine étape : /ps:structure pour définir les sections
```

Sauvegarder ce résumé dans `projects/{projet}/agents/{agent}/conception.md`
