# 04 - Workflow Exécution

## Principes Fondamentaux

Cycle en **7 étapes** répété jusqu'à complétion du plan :
1. **Autonomie** : Tu détermines la prochaine step (pas d'instructions externes)
2. **Pattern ReAct** : THOUGHT → ACTION → OBSERVATION (obligatoire pour toute action)
3. **State management** : Lecture/écriture état via MCP tools
4. **Méthodique** : Respecter l'ordre des étapes

---

## Pattern ReAct (OBLIGATOIRE)

Format à utiliser pour **chaque action** :

```
THOUGHT: [Raisonnement et analyse]
ACTION: [Tool call ou décision]
OBSERVATION: [Résultat et interprétation]
```

Garantit : traçabilité, débogage, transparence, qualité du raisonnement.

---

## Cycle en 7 Étapes

### 1. Analyser le Contexte
- **Tool** : `get_state("progress")`
- **But** : Savoir où tu en es (steps complétées, step courante, pause HITL, démarrage/reprise)
- **États** : `not_started`, `in_progress`, `hitl_paused`, `completed`

### 2. Identifier la Prochaine Step
- **Tools** : `get_state("results")` + `get_state("steps")`
- **Logique** :
  1. Récupérer résultats (step_id → status)
  2. Pour chaque step : vérifier non completed + dependencies satisfied + condition OK
  3. Choisir première step éligible
- **Cas spéciaux** : Dependencies multiples (toutes required), conditions (évaluer RESULT_FROM_X), loops (section 06)

### 3. Lire step.tools
- **Champ** : `step["tools"]` (liste de tool names)
- **Action** :
  - 1 tool (85%) → exécution simple, continuer étape 4
  - 2+ tools (15%) → voir section 05 (multi-tool)

### 4. Exécuter avec execute_step_tool
- **Workflow** :
  1. Identifier le `step_id` du step en cours
  2. Consulter définition tool dans `tool_definitions`
  3. Identifier `parameters.required`
  4. Construire `parameters` : extraire de `step["instruction"]`, résoudre variables (RESULT_FROM_X, CURRENT_ITEM)
  5. Appeler `execute_step_tool(step_id, tool_name, parameters)`
- **Important** : Le `step_id` est obligatoire et met à jour automatiquement `progress.current_step` pour le suivi d'avancement
- **Fallback** : Si `step["tools"]` vide → `find_tool(service, instruction)`

### 5. Traiter le Résultat
- Parser JSON (`success`, `data`, `error`)
- Vérifier succès
- Extraire données utiles (automatiquement stockées dans `state.last_tool_useful_data`)
- Si erreur → section 07

### 6. Sauvegarder l'État
- **Tool** : `finish_step` (cas standard - 95%)
- **Input** :
  - `step_id` : ID du step terminé
  - `result_summary` : Résumé pour l'utilisateur
- **Action automatique** :
  - Marque `step.status = SUCCESS`
  - Sauvegarde `state.last_tool_useful_data` dans `step_result.data`
  - Met à jour compteurs `completed_steps`, `current_step_id`

**Alternative** : `update_state` pour cas avancés (échecs, multi-champs, champs imbriqués)

### 7. Vérifier si Terminé
- **Tool** : `get_state("progress")`
- **Logique** : `completed_steps == total_steps` ?
  - **Oui** → Fin, envoyer résumé final
  - **Non** → Retour étape 1 (nouveau cycle)

---

## Exemple Complet : Exécution Step 2

**Contexte** : Plan avec 2 steps (créer événement, ajouter participant). Step 1 completed, on exécute step 2.

```
THOUGHT: Nouveau cycle. Je dois comprendre où j'en suis → get_state("progress")
ACTION: get_state({"key": "progress"})
OBSERVATION: completed_steps: 1/2, current: "2" → Step 2 prête

THOUGHT: Identifier step à exécuter → récupérer results et steps
ACTION: get_state("steps")
OBSERVATION: Step 2 dépend de ["1"], step 1 completed → Step 2 éligible

THOUGHT: Step 2 tools = ["GOOGLECALENDAR_ADD_ATTENDEE"] → 1 tool, cas simple
ACTION: Consulter définition → params requis: event_id, email
OBSERVATION: Instruction: "Ajouter jean@example.com à RESULT_FROM_1"
  → email = "jean@example.com", event_id = RESULT_FROM_1 (à résoudre)

ACTION: get_step_result({"step_id": "1"})
OBSERVATION: data.event_id = "evt_abc123" → RESULT_FROM_1 résolu

ACTION: execute_step_tool({"step_id": "step_2", "tool_name": "GOOGLECALENDAR_ADD_ATTENDEE", "parameters": {"event_id": "evt_abc123", "email": "jean@example.com"}})
OBSERVATION: success: true, attendee_added: true → Succès
  → progress.current_step mis à jour automatiquement avec "step_2"

THOUGHT: Step 2 terminée avec succès → finish_step
ACTION: finish_step({"step_id": "step_2", "result_summary": "Participant jean@example.com ajouté à l'événement"})
OBSERVATION: Step 2 sauvegardée comme SUCCESS

ACTION: get_state("progress")
OBSERVATION: 2/2 steps → Plan terminé avec succès
```
