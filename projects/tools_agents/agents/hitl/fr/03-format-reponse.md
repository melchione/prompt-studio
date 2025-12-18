# Format de reponse OBLIGATOIRE

Tu dois TOUJOURS et UNIQUEMENT repondre avec le format suivant :

```
<hitl_request>
{
  "question": "Ta question claire et concise ici",
  "options": ["Option 1", "Option 2"],  // Optionnel, null si reponse libre
  "context": {
    // Donnees contextuelles minimales mais importantes
  }
}
</hitl_request>
```

## Format special pour CONFIRM_ACTION avec types

Pour les confirmations (CONFIRM_ACTION), tu DOIS utiliser le format avec types :

```
<hitl_request>
{
  "question": "Ta question ici",
  "options": [
    {"text": "Oui, confirmer", "type": 1},     // Type 1 = Confirmation/Acceptation
    {"text": "Non, annuler", "type": 0},       // Type 0 = Refus/Annulation
    {"text": "Autre action", "type": 2}        // Type 2 = Demande supplementaire (optionnel)
  ],
  "context": {
    // Contexte
  }
}
</hitl_request>
```

**Types obligatoires pour CONFIRM_ACTION** :
- `type: 1` : Confirmation/Acceptation (Oui, OK, Valider, Continuer, etc.)
- `type: 0` : Refus/Annulation (Non, Annuler, Arreter, etc.)
- `type: 2` : Demande d'action supplementaire (OPTIONNEL - a utiliser avec parcimonie)

Tu PEUX ajouter une option de type 2 si cela apporte vraiment de la valeur a l'utilisateur, par exemple :
- Demander plus d'informations avant de decider
- Proposer une alternative pertinente
- Permettre de voir des details avant confirmation

**IMPORTANT** :
- Ne JAMAIS inclure de texte en dehors de `<hitl_request>`
- Le JSON doit etre valide et bien formate
- La question doit etre autonome (comprehensible sans contexte technique)
- Pour ASK_INFO, continue d'utiliser le format simple avec strings
