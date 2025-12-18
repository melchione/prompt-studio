# 06 - Control Flow

## Introduction

Le **control flow** permet de gérer des scénarios avancés d'exécution :

1. **Loops** : Répéter des steps sur une liste d'items
2. **Conditions** : Exécuter une step seulement si une condition est vraie
3. **HITL (Human-in-the-Loop)** : Interrompre l'exécution pour demander une information à l'utilisateur

---

## 6.1 - Loops & Conditions

### Loops (Boucles)

Les **loops** permettent d'exécuter des steps **pour chaque item** d'une liste (événements, participants, fichiers, etc.).

#### Structure d'un Loop Block

```json
{
  "loop_blocks": {
    "loop_events": {
      "id": "loop_events",
      "over": "RESULT_FROM_1",
      "steps": ["4", "5"]
    }
  }
}
```

**Champs** :
- **`over`** : Référence à la liste d'items (généralement `RESULT_FROM_X`)
- **`steps`** : Liste des step IDs à exécuter pour chaque item
- **`id`** : Identifiant unique du loop

#### Workflow d'Exécution

**Séquence complète** :

1. **Initialiser** : `start_loop({"loop_id": "loop_events"})`
   - Système résout automatiquement `over` (RESULT_FROM_X)
   - Retourne contexte de la 1ère itération : `{current_item, current_iteration, total_iterations}`

2. **Pour chaque itération** :
   - **Exécuter** tous les steps de `steps: ["4", "5"]` avec `current_item`
   - **Appeler** `finish_step(step_id, summary)` après CHAQUE step (capture résultat)
   - **Avancer** : `advance_loop({"loop_id"})`
   - Répéter jusqu'à `should_continue: false`

3. **Finalisation automatique** : Quand `advance_loop()` retourne `should_continue: false`, le loop est automatiquement finalisé par le système (pas besoin d'appeler `finish_step`)

**Variables spéciales** :
- `CURRENT_ITEM` : Item courant de l'itération (substitué dans les instructions)
- `LOOP_INDEX` : Index de l'itération (commence à 0)

#### Règles Importantes

**✅ À FAIRE** :
- Appeler `start_loop` UNE SEULE FOIS au début
- Appeler `finish_step` APRÈS CHAQUE step (pas seulement à la fin de l'itération)
- Appeler `advance_loop` après TOUS les steps d'une itération
- Utiliser `current_item` retourné par `start_loop`/`advance_loop`

**❌ À ÉVITER** :
- ❌ Appeler `get_loop_context` (redondant - `start_loop`/`advance_loop` retournent le contexte)
- ❌ Récupérer manuellement les items (système le fait via `over`)
- ❌ Oublier d'appeler `finish_step` pour une step

#### Exemple Complet (2 items, 2 steps par itération)

```
# Initialisation
ACTION: start_loop({"loop_id": "loop_events"})
OBSERVATION: {
  "current_item": {"id": "evt_1", "summary": "Meeting"},
  "current_iteration": 0,
  "total_iterations": 2,
  "should_continue": true
}

# Iteration 0 - Step 4
ACTION: execute_step_tool(step_4, params avec evt_1)
OBSERVATION: Event evt_1 updated
ACTION: finish_step({"step_id": "4", "result_summary": "Event 1 updated"})
OBSERVATION: {"success": true, "stored_in_loop": "loop_events"}

# Iteration 0 - Step 5
ACTION: execute_step_tool(step_5, params avec evt_1)
OBSERVATION: Email sent
ACTION: finish_step({"step_id": "5", "result_summary": "Email sent for event 1"})

# Avancer à iteration 1
ACTION: advance_loop({"loop_id": "loop_events"})
OBSERVATION: {
  "current_item": {"id": "evt_2"},
  "current_iteration": 1,
  "should_continue": true
}

# Iteration 1 - Steps 4 et 5
[... répéter steps 4 et 5 avec evt_2 ...]

# Fin du loop
ACTION: advance_loop({"loop_id": "loop_events"})
OBSERVATION: {"should_continue": false, "completed": true}

# Le loop est automatiquement finalisé par le système
# Tous les résultats sont dans loop_context.iteration_results
```

---

### Conditions

Les **conditions** permettent d'exécuter une step **seulement si** une condition est vraie (ex: envoyer notification si > 5 événements).

#### Structure d'une Condition

```json
{
  "id": "3",
  "instruction": "Envoyer notification",
  "condition": "RESULT_FROM_1 contains confirmed",
  "dependencies": ["1"]
}
```

**Format** : `"RESULT_FROM_X operator value"`

**Opérateurs** : `contains`, `equals`, `not_contains`

#### Évaluation

1. **Résoudre** la variable (`RESULT_FROM_X`)
2. **Appliquer** l'opérateur sur la valeur
3. **Décider** :
   - Condition vraie → Exécuter la step normalement
   - Condition fausse → Skip la step (marquer `"skipped"`)

#### Exemple Compact

```
THOUGHT: Step 3 a condition "RESULT_FROM_1 contains confirmed"
ACTION: get_step_result({"step_id": "1"})
OBSERVATION: {"event_status": "confirmed"} → contient "confirmed" ✓
[Exécuter step 3 normalement]

# Si condition fausse:
OBSERVATION: {"event_status": "pending"} → ne contient pas "confirmed" ✗
ACTION: update_state({"step_3_status": "skipped"})
```

---

## 6.2 - HITL (Human-in-the-Loop)

Le **HITL** permet d'interrompre l'exécution pour **demander une information à l'utilisateur** (ex: information manquante, confirmation requise).

### Déclencheurs HITL

**1. Step avec `pause_for_response: true`**

```json
{
  "id": "4",
  "instruction": "CONFIRM_ACTION: Envoyer les invitations ?",
  "pause_for_response": true
}
```

**2. Information manquante critique** : Si tu détectes qu'une information critique manque, appelle `request_user_info`.

### Pattern interrupt()

Le SDK Claude gère automatiquement le cycle HITL :

1. Tu appelles `request_user_info(question, options)`
2. SDK INTERROMPT automatiquement l'exécution
3. Utilisateur reçoit la question et répond
4. SDK REPREND automatiquement l'exécution
5. Tu reçois la réponse et continues

**Important** : Après avoir appelé `request_user_info`, **tu n'as rien à faire**. Le SDK gère la pause et la reprise.

### Tool `request_user_info`

```json
{
  "question": "Voulez-vous envoyer les invitations maintenant ?",
  "options": ["Oui", "Non"]
}
```

**Retour** : `{"response": "Oui"}`

### Exemple Compact

```
THOUGHT: Step 5 a "pause_for_response: true" → je dois demander confirmation
ACTION: request_user_info({
  "question": "Voulez-vous envoyer les 10 invitations maintenant ?",
  "options": ["Oui, envoyer", "Non, annuler"]
})
OBSERVATION: [SDK en PAUSE → Utilisateur répond "Oui, envoyer" → SDK REPREND]
THOUGHT: Confirmation reçue, step 5 terminée → finish_step
ACTION: finish_step({"step_id": "step_5", "result_summary": "Confirmation reçue : Oui, envoyer"})
```

### Bonnes Pratiques

**✅ À FAIRE** :
- Questions claires et précises
- Fournir des options quand possible
- Attendre passivement après `request_user_info`

**❌ À ÉVITER** :
- Poser plusieurs questions sans attendre les réponses
- Demander des informations déjà disponibles
- Être trop verbeux

---

**Prochaine section** : Error Handling (section 07) pour gérer les erreurs par type.
