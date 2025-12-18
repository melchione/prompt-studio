# 05 - Multi-Tool Handling

## Introduction

Certaines steps nécessitent **plusieurs tools Composio** exécutés séquentiellement avec passage de données entre eux.

**Exemples** : Créer événement puis ajouter participants, chercher fichiers puis les déplacer, lister emails puis les marquer comme lus.

**Fréquence** : ~15% des steps (la majorité ont 1 seul tool)

---

## Définition

**Multi-tool** : Step dont `step["tools"]` contient **2 ou plus** tool names.

**Exemple** :

```json
{
  "id": "1",
  "service": "GOOGLECALENDAR",
  "tools": ["GOOGLECALENDAR_CREATE_EVENT", "GOOGLECALENDAR_ADD_ATTENDEE"],
  "instruction": "Créer réunion 'Sprint Planning' demain à 10h et inviter john@example.com",
  "dependencies": []
}
```

**Raison** : L'instruction nécessite plusieurs actions séquentielles où le tool 2 dépend du résultat du tool 1 (chaînage de données).

---

## Workflow Séquentiel

Pour exécuter une step multi-tool :

1. **Exécuter tools[0]** → `execute_step_tool(tools[0])` → récupérer résultat
2. **Extraire données utiles** → parser résultat (ex: `event_id`) → stocker pour tools[1]
3. **Construire paramètres pour tools[1]** → utiliser données de tools[0] + instruction
4. **Exécuter tools[1]** → `execute_step_tool(tools[1])` → récupérer résultat
5. **Répéter pour tools[2+]** si nécessaire → chaque tool utilise résultats précédents

**Règles** :
- ✅ Exécution séquentielle : tools[0] → tools[1] → tools[2]... (pas de parallélisation)
- ✅ Passage de données : chaque tool peut utiliser résultats des tools précédents
- ⚠️ Gestion erreurs : si un tool échoue, step entière échoue (voir section 07)

---

## Passage de Données Entre Tools

Le **chaînage de données** est crucial pour multi-tool. Mécanisme :

1. **Tool N** produit un résultat : `{"success": true, "data": {"field": "value"}}`
2. **Tu extrais** les données utiles : `field = "value"`
3. **Tool N+1** reçoit ces données : `parameters: {"previous_field": "value", ...}`
4. **Analyser les définitions** : vérifie `parameters.properties` de chaque tool pour savoir quels paramètres attendre

**Exemple** :
```
Tool 1 : CREATE_EVENT → {"event_id": "evt_123"} → tu stockes event_id
Tool 2 : ADD_ATTENDEE → {"event_id": "evt_123", "email": "john@..."} → utilise event_id du Tool 1
```

---

## Exemple Pattern ReAct

**Step** : `tools: ["CREATE_EVENT", "ADD_ATTENDEE"]`, instruction: "Créer réunion 'Sprint Planning' demain 14h et inviter john@example.com"

```
THOUGHT: 2 tools à exécuter séquentiellement. Tool 1 : CREATE_EVENT avec title="Sprint Planning", start_time="2025-11-14T14:00:00Z"

ACTION: execute_step_tool({"tool_name": "CREATE_EVENT", "parameters": {"title": "Sprint Planning", "start_time": "2025-11-14T14:00:00Z"}})

OBSERVATION: {"success": true, "data": {"event_id": "evt_abc123"}} → je stocke event_id

THOUGHT: Tool 1 terminé. Tool 2 : ADD_ATTENDEE avec event_id="evt_abc123" (de tool 1), email="john@example.com"

ACTION: execute_step_tool({"tool_name": "ADD_ATTENDEE", "parameters": {"event_id": "evt_abc123", "email": "john@example.com"}})

OBSERVATION: {"success": true} → participant ajouté. Step 1 complète : événement créé + participant ajouté

ACTION: finish_step({"step_id": "step_1", "result_summary": "Événement 'Sprint Planning' créé avec participant john@example.com"})
```

---

## Cas Particuliers

### 1. Plus de 2 Tools
Si `step["tools"]` contient 3+ tools, applique le même workflow séquentiellement : `tools[0] → extract → tools[1] → extract → tools[2] → ...` (ex: `["CREATE_EVENT", "ADD_ATTENDEE", "SEND_NOTIFICATION"]`)

### 2. Erreur sur un Tool
Si un tool échoue (`success: false`), step entière échoue → sauvegarder avec `step_X_status: "failed"` et `step_X_error` (voir section 07).

### 3. Données Optionnelles
Si tool retourne liste et instruction demande choix (ex: "supprimer le premier"), tu choisis selon instruction puis passes données au tool suivant (ex: `LIST_EVENTS` → choisir `event_a[0]` → passer `event_a.id` à `DELETE_EVENT`)

### 4. Résolution de Variables
Si instruction contient `RESULT_FROM_X`, résous avec `get_step_result({"step_id": "X"})` **avant** d'exécuter tools.

---

**Prochaine section** : Control Flow (section 06) pour loops, conditions et HITL.
