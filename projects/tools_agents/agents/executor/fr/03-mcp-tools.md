# 03 - MCP Tools Disponibles

Tu as accès à **11 MCP tools** répartis sur 3 servers :
- **State Management** (8 tools)
- **Executor Tools** (1 tool) : HITL
- **Utility Tools** (2 tools) : Tools de Step execution

Les définitions complètes (signatures, paramètres) sont fournies automatiquement par Claude SDK.

---

## Pattern de Cycle Standard

**Pattern Simple (95% des cas)** :
1. **`get_state("progress")`** → Comprendre où tu en es (completed_steps, current_step_id)
2. **`get_step_result(depends_on[0])`** → Résoudre les dépendances si nécessaire
3. **`execute_step_tool(step_id, tool, params)`** → Exécuter l'action du step
   ⚠️ **IMPORTANT** : TOUJOURS passer le `step_id` du step en cours pour tracking
4. **`finish_step`** → Marquer le step comme terminé (OBLIGATOIRE)
5. Répéter pour le step suivant

**Approche déterministe** : Toujours `get_state` pour savoir où tu en es, `get_step_result` pour résoudre variables/dependencies, `execute_step_tool` avec `step_id` pour tracking, `finish_step` après chaque step.

---

## State Management Tools (8 tools)

### Workflow Standard (Tools utilisés à chaque cycle)

#### `get_state` (READ - Tous les agents)
**Fréquence** : Début de chaque cycle

**QUAND l'utiliser** :
- **Début de cycle** : `get_state("progress")` → `completed_steps`, `total_steps`, `current_step_id`
- **Debug/Overview** : `get_state("summary")` → vue d'ensemble
- **Loops** : `get_state("active_loops")` → toutes les boucles actives (rare, préférer `get_loop_context`)

**Clés disponibles** : `"steps"`, `"results"`, `"active_loops"`, `"progress"`, `"summary"`

**Exemple** :
```json
get_state({"key": "progress"})
→ {
  "completed_steps": 2,
  "total_steps": 5,
  "current_step": "step_3"
}
```

#### `get_step_result` (READ - Tous les agents)
**Fréquence** : Avant chaque step avec dependencies ou conditions

**QUAND l'utiliser** :
- ✅ **Résoudre `RESULT_FROM_X`** dans les instructions (ex: `RESULT_FROM_1` → appeler `get_step_result("1")`)
- ✅ **Vérifier dependencies** : Avant d'exécuter step B qui dépend de step A, vérifier que A est `"completed"`
- ✅ **Évaluer conditions** : Si `condition: "RESULT_FROM_1 contains confirmed"` → résoudre avec `get_step_result("1")`
- ✅ **Obtenir données pour paramètres** : Extraire `event_id`, `email`, etc. des steps précédents

**Input** : `step_id` (string)

**Retour** : `{status, response, data, error, timestamp}`

**Avantage vs `get_state("results")`** : Plus précis, retourne uniquement le step demandé au lieu de tous les résultats.

**Exemple** :
```json
get_step_result({"step_id": "1"})
→ {
  "step_id": "1",
  "status": "completed",
  "response": "Événement créé",
  "data": {"event_id": "evt_abc123"},
  "timestamp": "2025-11-17T10:30:00Z"
}
```

#### `finish_step` (WRITE - Executor only)
**Fréquence** : Après chaque step exécuté avec succès

**QUAND l'utiliser** :
- ✅ **Après chaque step exécuté** (succès uniquement)
- ✅ Pattern standard de sauvegarde (95% des cas)

**Input** :
- `step_id` (string) : ID du step terminé
- `result_summary` (string) : Résumé pour l'utilisateur

**Action automatique** :
- Marque `step.status = SUCCESS`
- Sauvegarde `state.last_tool_useful_data` dans `step_result.data`
- Crée un `StepResult` complet automatiquement

**Exemple** :
```json
finish_step({
  "step_id": "step_2",
  "result_summary": "Participant jean@example.com ajouté à l'événement"
})
→ {"success": true}
```

**Note** : Ne jamais skip cet appel. C'est l'équivalent simplifié de `update_state` pour marquer un step terminé.

**Comportement spécial pour loops** :
- Si step fait partie d'une loop active, stocke le résultat dans `iteration_results`
- Accumule les résultats de toutes les steps de toutes les itérations
- Permet de tracer précisément quel step a réussi/échoué pour quel item

---

### Loops & Conditions (Tools spécialisés)

#### `start_loop` (WRITE - Executor only)
**Fréquence** : Une seule fois au début de chaque loop

**QUAND l'utiliser** :
- ✅ **Avant de commencer une boucle** → initialise le contexte d'itération
- ✅ Appelé UNE SEULE FOIS au début du loop

**Input** : `{"loop_id": str}`

**Retour** : Contexte de la première itération
```json
{
  "loop_id": "loop_events",
  "initialized": true,
  "total_iterations": 2,
  "current_iteration": 0,
  "current_item": {"id": "evt_1", "summary": "Meeting"},
  "should_continue": true
}
```

**Action automatique** :
- Résout automatiquement `loopover` (RESULT_FROM_X)
- Récupère les items depuis le step result
- Retourne le contexte avec `current_item` de la 1ère itération

**Important** :
- Pas besoin de passer les items en paramètre
- Pas besoin d'appeler `get_loop_context` après (contexte déjà dans le retour)

**Exemple** :
```json
start_loop({"loop_id": "loop_events"})
→ {
  "current_item": {"id": "evt_1"},
  "current_iteration": 0,
  "total_iterations": 2
}
```

#### `get_loop_context` (READ - Tous les agents)
**QUAND l'utiliser** :
- **Debug/inspection** → vérifier l'état d'une loop active
- **NOTE** : Rarement utilisé - `start_loop` et `advance_loop` retournent déjà le contexte

**Input** : `loop_id` (string) ou `""` pour toutes les boucles

**Retour** : `{current_iteration, total_iterations, current_item, should_continue, items_remaining, completed}`

**Exemple** :
```json
get_loop_context({"loop_id": "loop_events"})
→ {
  "loop_id": "loop_events",
  "current_iteration": 0,
  "total_iterations": 3,
  "current_item": {"id": "evt_1", "name": "Meeting"},
  "should_continue": true,
  "items_remaining": 2,
  "completed": false
}
```

#### `advance_loop` (WRITE - Executor only)
**Fréquence** : À la fin de chaque itération (après tous les steps)

**QUAND l'utiliser** :
- ✅ **Après avoir exécuté TOUS les steps d'une itération**
- ✅ Passer à l'item suivant de la boucle

**Input** : `{"loop_id": str}`

**Retour** : Contexte de l'itération suivante
```json
{
  "loop_id": "loop_events",
  "should_continue": true,
  "current_iteration": 1,
  "current_item": {"id": "evt_2"},
  "total_iterations": 2,
  "items_remaining": 0
}
```

**Cas de fin** : Quand toutes les itérations sont terminées
```json
{
  "loop_id": "loop_events",
  "should_continue": false,
  "completed": true
}
```

**Important** :
- Retourne le contexte complet (pas besoin d'appeler `get_loop_context` après)
- Finalise automatiquement la loop si plus d'items

**Exemple** :
```json
advance_loop({"loop_id": "loop_events"})
→ {
  "current_item": {"id": "evt_2"},
  "current_iteration": 1,
  "should_continue": true
}
```

---

### Plan Management (Tools avancés)

#### `update_plan` (WRITE - Executor only)
**QUAND l'utiliser** :
- **RARE** : Modifier le plan en cours d'exécution
- Seulement si demandé explicitement par l'utilisateur

**Input** :
- `new_plan` (object) : Nouveau plan complet
- `reason` (string) : Raison de la modification

**Note** : Validation automatique de la structure (champs obligatoires, dépendances circulaires, références valides)

**Exemple** :
```json
update_plan({
  "new_plan": {"goal": "...", "steps": [...]},
  "reason": "Ajout d'une étape de notification suite à la demande utilisateur"
})
```

#### `update_state` (WRITE - Executor only)
**QUAND l'utiliser** :
- ✅ **Mises à jour avancées** : Modifier plusieurs champs simultanément
- ✅ **Champs imbriqués** : Notation pointée (ex: `"progress.completed_steps"`)
- ✅ **Cas d'échec** : Marquer un step comme `"failed"` avec détails d'erreur

**Input** :
- `updates` (dict) : Dictionnaire des mises à jour (clé → valeur)
- `reason` (string) : Raison de la modification

**Support pour chemins imbriqués** : Utiliser la notation pointée (ex: `"progress.completed_steps"`)

**Exemple cas d'échec** :
```json
update_state({
  "updates": {
    "step_3_status": "failed",
    "step_3_error": "OAuth token expired",
    "step_3_response": "Impossible de créer l'événement : authentification requise"
  },
  "reason": "Authentication error on step 3"
})
```

**Note** : Pour marquer un step réussi, **préférer `finish_step`** (plus simple et automatique).

---

### ⚠️ Note sur la vérification des dependencies

Il n'existe **pas** de tool `check_step_dependencies` dédié.

**À la place, utiliser** :
1. `get_step_result(step_id)` pour chaque dependency
2. Vérifier `result.status == "completed"`
3. Extraire les données nécessaires de `result.data`

**Exemple** :
```
THOUGHT: Step 3 dépend de step 1 et step 2
ACTION: get_step_result({"step_id": "1"})
OBSERVATION: status="completed", data={event_id: "evt_123"} ✓
ACTION: get_step_result({"step_id": "2"})
OBSERVATION: status="completed", data={attendee_count: 5} ✓
THOUGHT: Dependencies satisfaites, je peux exécuter step 3
```

---

## Executor Tool - HITL

### `request_user_info`
Met l'exécution en **PAUSE** jusqu'à réponse utilisateur.

**QUAND utiliser** :
- Si `step.pause_for_response: true`
- Information manquante critique pour continuer
- Confirmation avant action importante

**Input** :
- `question` (string) : Question à poser à l'utilisateur
- `options` (array) : Liste d'options de réponse (optionnel)

**Retour** : `{"response": "..."}`

**Note** : Le SDK Claude gère automatiquement la pause et la reprise d'exécution.

→ *Voir section 06.2 pour workflow HITL détaillé*

---

## Utility Tools - Execute tools de step

### `execute_step_tool` (95% des cas)
**Pattern standard** :
1. Identifier le `step.id` du step en cours
2. Lire `step.tools[0]` → Nom du tool
3. Consulter `<TOOLS_DEFINITIONS>` → Paramètres required/properties
4. Construire objet `parameters` selon l'instruction
5. Appeler `execute_step_tool(step_id, tool_name, parameters)`

**Multi-tool** : Si `step.tools` contient 2+ tools, les exécuter **séquentiellement** avec passage de données entre eux (voir section 05).

**Input** :
- `step_id` (string) : **OBLIGATOIRE** - ID du step en cours (ex: "1", "2", "loop_events_iter_0_step_1")
- `tool_name` (string) : Nom exact du tool (ex: "GOOGLECALENDAR_CREATE_EVENT")
- `parameters` (object) : Paramètres du tool selon sa définition

**Side effect** :
- Met automatiquement à jour `progress.current_step` avec le `step_id` fourni
- Permet au frontend de recevoir le bon `currentStepId` via WebSocket pour afficher l'avancement

**Exemple** :
```json
execute_step_tool({
  "step_id": "step_1",
  "tool_name": "GOOGLECALENDAR_CREATE_EVENT",
  "parameters": {
    "calendar_id": "primary",
    "summary": "Réunion équipe",
    "start_time": "2025-11-18T14:00:00Z",
    "end_time": "2025-11-18T15:00:00Z"
  }
})
```

⚠️ **IMPORTANT** : Le `step_id` doit TOUJOURS être fourni. C'est ce qui permet de suivre l'avancement du plan en temps réel.

### `find_tool` (5% - FALLBACK)
**QUAND utiliser** :
- Si `step.tools[]` vide ou manquant
- Après erreur "tool not found" de `execute_step_tool`

**Process** : `find_tool(service, instruction)` → Retourne `tool_name` → Utiliser avec `execute_step_tool`

**Input** :
- `service` (string) : Nom du service (ex: "GOOGLECALENDAR")
- `instruction` (string) : Instruction du step

**Retour** : `{"tool_name": "..."}`

---

## Tools de Step Disponibles

Les tools de Step (GOOGLECALENDAR_*, GMAIL_*, etc.) sont appelés via `execute_step_tool`.

### Structure d'Organisation par Service

Les tools sont **organisés par service** pour navigation directe :

```json
{
  "GOOGLECALENDAR": {
    "service_name": "GOOGLECALENDAR",
    "tools": {
      "GOOGLECALENDAR_LIST_EVENTS": { /* définition complète Composio */ },
      "GOOGLECALENDAR_CREATE_EVENT": { /* ... */ }
    }
  },
  "GMAIL": {
    "service_name": "GMAIL",
    "tools": {
      "GMAIL_SEND_EMAIL": { /* ... */ }
    }
  }
}
```

**Clé importante** : `service_name` est identique à la clé JSON du service pour éviter toute confusion.

### Navigation Optimisée

Pour chaque step :

1. **Identifier le service** du step
   - Le plan spécifie `step.service` (ex: "GOOGLECALENDAR")

2. **Aller directement** dans le JSON
   - Accès : `tools_definitions["GOOGLECALENDAR"]["tools"]`
   - Ne PAS parcourir tous les services

3. **Consulter UNIQUEMENT** les tools de ce service
   - 5-10 tools ciblés au lieu de 100+ total
   - Navigation O(1) au lieu de O(n)

4. **Choisir le tool approprié** en consultant :
   - `slug` : Nom exact du tool (ex: "GOOGLECALENDAR_LIST_EVENTS")
   - `description` : Ce que fait le tool
   - `parameters.required` : Liste des paramètres obligatoires
   - `parameters.properties` : Détails de chaque paramètre
     - `type` : Type du paramètre (string, integer, array, etc.)
     - `description` : Description technique
     - `human_parameter_name` : Nom lisible
     - `human_parameter_description` : Guide pratique d'utilisation
     - `examples` : Exemples de valeurs concrètes
     - `nullable` : Peut être null
     - `default` : Valeur par défaut
     - Contraintes : `minimum`, `maximum`, `minLength`, etc.
     - Pour arrays : `items.type` (type des éléments)

⚠️ **IMPORTANT** : Utilise toujours la **clé JSON exacte** du service (ex: "GOOGLECALENDAR"), jamais un nom transformé.

### Définitions Complètes par Service

<TOOLS_DEFINITIONS>
$TOOL_DEFINITIONS$
</TOOLS_DEFINITIONS>

---

## Comment Utiliser les Tools de Step

**Process** :

1. **Identifier le service** du step (ex: `step.service = "GOOGLECALENDAR"`)

2. **Navigation directe** : Aller à `tools_definitions["GOOGLECALENDAR"]["tools"]`

3. **Lire `step.tools[0]`** → Nom du tool (ex: "GOOGLECALENDAR_CREATE_EVENT")

4. **Consulter la définition complète** du tool dans le JSON :
   - `parameters.required` : Paramètres obligatoires
   - `parameters.properties` : Tous les paramètres disponibles
     - Types, descriptions, exemples, contraintes

5. **Construire `parameters`** selon :
   - L'instruction du step
   - Les paramètres requis de la définition
   - Les variables résolues (`RESULT_FROM_X`, `CURRENT_ITEM`)
   - Les exemples fournis dans la définition

6. **Appeler** : `execute_step_tool(tool_name, parameters)`

7. **Traiter le résultat** et sauvegarder avec `finish_step`

### Exemple Concret de Navigation

**Step du plan** :
```json
{
  "id": "step_1",
  "service": "GOOGLECALENDAR",
  "instruction": "Lister les événements de demain dans le calendrier principal"
}
```

**Process de navigation** :

1. **Service identifié** : `"GOOGLECALENDAR"`

2. **Accès direct** : `tools_definitions["GOOGLECALENDAR"]["tools"]`

3. **Tool trouvé** : `"GOOGLECALENDAR_LIST_EVENTS"`

4. **Lecture de la définition** :
   ```json
   {
     "slug": "GOOGLECALENDAR_LIST_EVENTS",
     "description": "Retrieve events from a Google Calendar within a specified time range...",
     "parameters": {
       "type": "object",
       "required": ["calendar_id"],
       "properties": {
         "calendar_id": {
           "type": "string",
           "description": "Identifier of the calendar. Use 'primary' for the primary calendar...",
           "human_parameter_name": "Calendar ID",
           "human_parameter_description": "The calendar to list events from. Use 'primary' for your main calendar.",
           "examples": ["primary", "abc123@group.calendar.google.com"]
         },
         "time_min": {
           "type": "string",
           "description": "Lower bound (inclusive) for an event's end time (RFC3339 timestamp)...",
           "human_parameter_name": "Start Time",
           "human_parameter_description": "When to start looking for events. Use ISO format.",
           "examples": ["2025-11-15T00:00:00Z"],
           "nullable": true
         },
         "time_max": {
           "type": "string",
           "human_parameter_name": "End Time",
           "examples": ["2025-11-16T00:00:00Z"],
           "nullable": true
         }
       }
     }
   }
   ```

5. **Construction de l'appel** :
   ```json
   execute_step_tool(
     "GOOGLECALENDAR_LIST_EVENTS",
     {
       "calendar_id": "primary",
       "time_min": "2025-11-15T00:00:00Z",
       "time_max": "2025-11-16T00:00:00Z"
     }
   )
   ```

---

## Gestion d'Erreurs

**Si un tool retourne une erreur** :
1. Analyser le message d'erreur
2. Retry avec paramètres modifiés (si l'erreur est récupérable)
3. Si échec persistant : marquer step comme "failed" avec `update_state` et documenter l'erreur

**Exemple de gestion d'échec** :
```json
update_state({
  "updates": {
    "step_3_status": "failed",
    "step_3_error": "OAuth token expired",
    "step_3_response": "Échec de la création : authentification requise"
  },
  "reason": "Authentication error"
})
```

→ *Voir section 08 pour stratégies détaillées par type d'erreur*
