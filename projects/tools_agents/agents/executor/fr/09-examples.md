# 09 - Exemples Complets

Cette section présente **3 scénarios end-to-end** couvrant les cas d'usage principaux. Chaque exemple montre le **cycle complet** : Plan → Points clés d'exécution → État final.

---

## Exemple 1 : Plan Simple

**Objectif** : Montrer le cycle basique avec 1 service, 1 tool, 1 step

**Scénario** : Lister les événements de demain

### Plan

```json
{
  "goal": "Lister mes événements de demain",
  "steps": [
    {
      "id": "1",
      "service": "GOOGLECALENDAR",
      "tools": ["GOOGLECALENDAR_LIST_EVENTS"],
      "instruction": "Liste tous mes événements du 14 novembre 2025",
      "dependencies": []
    }
  ]
}
```

### Points Clés d'Exécution

1. **Analyse contexte** : get_state() révèle aucune step exécutée, démarrage du plan
2. **Identification step** : Step 1 sans dépendances, exécution immédiate possible
3. **Lecture tool** : 1 seul tool (GOOGLECALENDAR_LIST_EVENTS), pas de multi-tool
4. **Construction paramètres** : time_min/time_max calculés pour couvrir le 14 novembre
5. **Exécution tool** : execute_step_tool() retourne 2 événements avec succès
6. **Sauvegarde état** : update_state() persiste résultats avec step_1_status="completed"
7. **Vérification fin** : Toutes steps terminées, plan completed

### État Final

```json
{
  "progress": {"status": "completed", "steps_completed": 1, "steps_total": 1},
  "results": {
    "1": {
      "status": "completed",
      "response": "2 événements trouvés pour le 14 novembre : Sprint Planning (10h) et Team Lunch (12h30)",
      "data": {
        "events_count": 2,
        "events": [
          {"id": "evt_abc123", "summary": "Sprint Planning", "start": "10:00"},
          {"id": "evt_xyz789", "summary": "Team Lunch", "start": "12:30"}
        ]
      }
    }
  }
}
```

---

## Exemple 2 : Multi-Tool

**Objectif** : Montrer passage de données entre 2 tools séquentiels

**Scénario** : Créer événement ET ajouter un participant

### Plan

```json
{
  "goal": "Créer une réunion avec participant",
  "steps": [
    {
      "id": "1",
      "service": "GOOGLECALENDAR",
      "tools": ["GOOGLECALENDAR_CREATE_EVENT", "GOOGLECALENDAR_ADD_ATTENDEE"],
      "instruction": "Créer réunion 'Sprint Review' demain 14h et inviter john@example.com",
      "dependencies": []
    }
  ]
}
```

### Points Clés d'Exécution

1. **Détection multi-tool** : Step 1 contient 2 tools, exécution séquentielle requise
2. **Tool 1 (CREATE_EVENT)** : Paramètres construits (summary="Sprint Review", start_time calculé)
3. **Résultat Tool 1** : event_id="evt_review123" récupéré et conservé en mémoire
4. **Tool 2 (ADD_ATTENDEE)** : event_id du Tool 1 réutilisé, email extrait de l'instruction
5. **Passage de données** : event_id transféré automatiquement du résultat Tool 1 vers paramètres Tool 2
6. **Agrégation** : Résultats des 2 tools combinés dans une réponse cohérente
7. **Sauvegarde** : update_state() persiste l'event_id et la liste des attendees

### État Final

```json
{
  "progress": {"status": "completed", "steps_completed": 1, "steps_total": 1},
  "results": {
    "1": {
      "status": "completed",
      "response": "Réunion 'Sprint Review' créée demain 14h avec john@example.com",
      "data": {
        "event_id": "evt_review123",
        "summary": "Sprint Review",
        "attendees": ["john@example.com"]
      }
    }
  }
}
```

---

## Exemple 3 : Loop

**Objectif** : Montrer get_loop_context + advance_loop

**Scénario** : Envoyer email à chaque membre d'équipe

### Plan

```json
{
  "goal": "Envoyer email à toute l'équipe",
  "steps": [
    {
      "id": "1",
      "loopover": ["alice@team.com", "bob@team.com", "charlie@team.com"],
      "service": "GMAIL",
      "tools": ["GMAIL_SEND_EMAIL"],
      "instruction": "Envoie email 'Weekly Update' à CURRENT_ITEM",
      "dependencies": []
    }
  ]
}
```

### Points Clés d'Exécution

1. **Détection loop** : Step 1 contient loopover avec 3 items, mode itération activé
2. **Itération 1** : get_loop_context() retourne CURRENT_ITEM="alice@team.com", LOOP_INDEX=0
3. **Exécution 1** : execute_step_tool() envoie email à Alice avec succès
4. **Avancement 1** : advance_loop() marque item 1 terminé, should_continue=true
5. **Itérations 2-3** : Répétition du cycle pour Bob et Charlie avec CURRENT_ITEM automatiquement mis à jour
6. **Fin loop** : advance_loop() sur dernière itération retourne should_continue=false
7. **Sauvegarde** : update_state() persiste compteur emails_sent=3 et liste complète recipients

### État Final

```json
{
  "progress": {"status": "completed", "steps_completed": 1, "steps_total": 1},
  "results": {
    "1": {
      "status": "completed",
      "response": "3 emails 'Weekly Update' envoyés à toute l'équipe",
      "data": {
        "emails_sent": 3,
        "recipients": ["alice@team.com", "bob@team.com", "charlie@team.com"]
      }
    }
  }
}
```

---

## Résumé des Exemples

| Exemple            | Concept Principal                         | Sections Illustrées       |
| ------------------ | ----------------------------------------- | ------------------------- |
| **1. Plan Simple** | Cycle basique complet                     | 04 (Workflow)             |
| **2. Multi-Tool**  | Passage de données entre tools            | 05 (Multi-Tool)           |
| **3. Loop**        | Itération sur liste avec get_loop_context | 06 (Control Flow - Loops) |

### Points Clés Démontrés

- **Pattern ReAct** : Appliqué dans tous les exemples (THOUGHT → ACTION → OBSERVATION)
- **Tools MCP principaux** : get_state, update_state, execute_step_tool, get_loop_context, advance_loop
- **Cycle complet** : Analyse contexte → Identification step → Exécution → Sauvegarde état → Vérification fin
- **Passage de données** : Résultats d'un tool réutilisés dans le suivant (Exemple 2)
- **Itération** : Loop automatique avec CURRENT_ITEM et LOOP_INDEX (Exemple 3)
- **État persisté** : update_state() systématique après chaque step terminée

**Concepts non couverts ici** :
- HITL (Human-in-the-Loop) : Voir Section 06.2 pour request_user_info et pause_for_response
- Gestion erreurs OAuth : Voir Section 08 pour pattern 401 + reconnexion + retry

**Fin des exemples** - Tu es maintenant prêt à exécuter n'importe quel plan avec ces patterns !
