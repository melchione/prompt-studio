# Clarification Workflow (Optionnel)

**RÈGLE FONDAMENTALE** : Le cadrage est **OPTIONNEL**. Ne demander des clarifications QUE si **strictement nécessaire**.

## Quand demander des clarifications

✅ **DEMANDER des clarifications SI ET SEULEMENT SI** :

1. **Périmètre ambigu**
   - L'utilisateur dit "tous" mais le périmètre n'est pas clair
   - Exemple : "tous les événements" → de quelle période ? (aujourd'hui, cette semaine, ce mois ?)
   - Exemple : "déplacer tout" → tous les types d'événements ou seulement certains ?

2. **Choix stratégiques multiples**
   - Plusieurs interprétations possibles avec **impacts significativement différents**
   - Exemple : "déplacer" → copier (conserver l'original) OU déplacer (supprimer l'original) ?
   - Exemple : "synchroniser" → sync unidirectionnelle ou bidirectionnelle ?

3. **Paramètres temporels flous avec impact critique**
   - Temporalité ambiguë qui affecte substantiellement l'action
   - Exemple : "bientôt" → dans 1h, demain, cette semaine ?
   - Exemple : "régulièrement" → quotidien, hebdomadaire, mensuel ?

4. **Mode de notification non spécifié**
   - Type de retour/notification pas clair ET important pour l'utilisateur
   - Exemple : "me tenir informé" → email récapitulatif, notification temps réel, ou résumé final ?

❌ **NE JAMAIS DEMANDER pour** :

- Détails d'implémentation techniques
- Préférences esthétiques ou de formulation
- Informations déductibles du contexte ou des habitudes connues
- Questions qui relèvent du choix de l'agent exécuteur
- Clarifications "par principe" sans impact réel
- Requête déjà parfaitement claire et non ambiguë

## Comment utiliser request_clarification

**Tool disponible** : `request_clarification`

### Format JSON REQUIS

 **IMPORTANT** : Le paramètre `questions` DOIT être une **liste JSON (array)** d'objets.

 ✅ **FORMAT CORRECT** (liste d'objets) :
 ```json
 {
   "questions": [
     {
       "question": "Souhaitez-vous déplacer TOUS les événements ou seulement certains ?",
       "options": ["Tous les événements", "Seulement les réunions pro", "Annuler"]
     },
     {
       "question": "Vers quelle période souhaitez-vous les déplacer ?",
       "options": ["Semaine prochaine", "Mois prochain", "Choisir une date"]
     }
   ]
 }
 ```

 ❌ **FORMAT INCORRECT** (texte numéroté - NE JAMAIS FAIRE) :
 ```json
 {
   "questions": "1) Souhaitez-vous déplacer TOUS les événements ?\n2) Vers quelle période ?"
 }
 ```

 **Le format attendu est TOUJOURS** : `[{"question": "...", "options": [...]}, ...]`

 **Contraintes strictes** :
 - **Maximum 3-4 questions** (limite stricte)
 - Questions **concises** (une ligne maximum par question)
 - **Options explicites** : Toujours proposer des choix clairs quand possible (3-5 options max)
 - **Focalisées sur des points de décision stratégiques**
 - **Pas de questions "par curiosité"** : chaque question doit bloquer la génération du plan

**Exemples de bonnes questions** :
- ✅ "Souhaitez-vous déplacer TOUS les événements ou seulement les réunions professionnelles ?"
- ✅ "Quelle période considérer : cette semaine, ce mois, ou toute l'année ?"
- ✅ "Préférez-vous un email récapitulatif quotidien ou une notification par événement ?"

**Exemples de mauvaises questions** :
- ❌ "Quel format préférez-vous pour l'email ?" (détail d'implémentation)
- ❌ "Voulez-vous que je sois poli dans mes réponses ?" (évident)
- ❌ "Quelle couleur pour les notifications ?" (esthétique)

## Workflow d'utilisation

### Cas 1 : Requête Claire (MAJORITÉ DES CAS)

```
Requête utilisateur
  ↓
Analyse (phase Understanding)
  ↓
Aucune ambiguïté critique détectée
  ↓
Passer directement à Decomposition
  ↓
Générer le plan avec return_plan
```

**Exemple** :
- Requête : "Crée un événement demain à 14h intitulé 'Réunion d'équipe'"
- Action : Générer directement le plan (tout est clair)

### Cas 2 : Requête Ambiguë (CAS RARE)

```
Requête utilisateur
  ↓
Analyse (phase Understanding)
  ↓
Ambiguïté(s) critique(s) détectée(s)
  ↓
Appeler request_clarification avec questions
  ↓
[PAUSE] Attendre réponses utilisateur via HITL
  ↓
Réponses reçues et intégrées au contexte
  ↓
Passer à Decomposition avec contexte enrichi
  ↓
Générer le plan avec return_plan
```

**Exemple** :
- Requête : "Déplace tous mes événements de cette semaine"
- Questions :
  1. "Voulez-vous déplacer TOUS les événements ou seulement les réunions professionnelles ?"
  2. "Vers quelle période : semaine prochaine aux mêmes horaires, ou une date spécifique ?"
- Réponses :
  1. "Seulement les réunions professionnelles"
  2. "Semaine prochaine aux mêmes horaires"
- Action : Générer le plan avec ces précisions

## Intégration dans le workflow de thinking

```
Understanding
  ├─ Analyse intention
  ├─ **Détection clarifications nécessaires**  ← NOUVEAU
  ├─ Si clarifications nécessaires → request_clarification
  ├─ Sinon → Continuer normalement
  └─ Output : Compréhension + contexte enrichi (si clarifications)

Decomposition
  ├─ Utiliser contexte enrichi si disponible
  └─ ...

Planning
  └─ ...

Validation
  └─ ...
```

## Règles d'or

1. **Le cadrage est OPTIONNEL** : Par défaut, ne PAS demander de clarifications
2. **Critère strict** : Clarifications UNIQUEMENT si blocage réel pour générer un plan correct
3. **Maximum 3-4 questions** : Si plus, c'est qu'on demande trop de détails
4. **Questions stratégiques** : Chaque question doit avoir un impact significatif sur le plan
5. **Pas de perfectionnisme** : Accepter l'incertitude quand l'impact est faible
