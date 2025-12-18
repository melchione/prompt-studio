# Resources
## Available Services
Services Composio disponibles pour l'orchestration.
Chaque service correspond à une intégration externe (Google Calendar, Gmail, etc.).

**IMPORTANT**: Utiliser les noms de services en UPPERCASE (GOOGLECALENDAR, GMAIL, etc.)
dans le champ `service` de chaque step, SAUF pour respond_to_user.

$SERVICES_TAXONOMY$

### respond_to_user_agent
  - **Nom** : respond_to_user
  - **Fonction** : Interaction directe avec l'utilisateur
  - **Utilisé pour** : informations, confirmations, clarifications, ASK_INFO, CONFIRM_ACTION
  - **Capacité spéciale** : Peut mettre le workflow en pause avec `pause_for_response`
  - **Quand l'utiliser** : confirmations critiques, informations manquantes, résultats finaux

## Services Reference
Tous les services disponibles sont listés dans la section "$SERVICES_TAXONOMY$" ci-dessus.
Utiliser TOUJOURS les noms en UPPERCASE (GOOGLECALENDAR, GMAIL, etc.)

## Decision guides
Guide de Décision

### When to use loops
  Quand Utiliser des Boucles
  - Traitement identique sur plusieurs éléments
  - Plus de 3 actions similaires à effectuer
  - Résultat d'une recherche retourne une collection

### When to use pause_for_response
  Quand Demander Confirmation
    Voir section confirmation_thresholds pour les règles détaillées

### When to use display_result
  - L'utilisateur demande à VOIR ("Montre-moi", "Quels sont", "Liste-moi")
  - Les détails sont nécessaires pour une décision (doublons, priorités)
  - Le résultat EST l'objectif principal de la demande
  - Il y a des éléments spécifiques à examiner

### When to create a conditionnal step
  #### Rule:
    Quand un agent va retourner sa réponse, tu peux définir plkusieurs etapes suivantes chacune dépendante du résultat de celle-ci.
    <exemple>
      L'étape avec l'id "3" du plan retourne une liste d évenement
      On doit alors avoir :
      Une etape avec depencies = ["3"] et condition: "RESULT_FROM3 contains at least 1 event"
      et une autre étape avec depencies = ["3"] et condition: "RESULT_FROM3 events are empty"
    </exemples>

## Reusable patterns
### Action simple pattern
  <!-- Action simple sans confirmation -->
  ```json
  [
    {
      "id": "execute_action",
      "service": "GOOGLECALENDAR",
      "instruction": "Exécuter action",
      "expected_result": "Action complétée"
    },
    {
      "id": "inform_result",
      "service": "respond_to_user",
      "instruction": "Résultat: RESULT_FROM_execute_action",
      "dependencies": ["execute_action"]
    }
  ]
  ```

### Action with confirmation pattern
  <!-- Action sensible avec confirmation -->
  ```json
  [
    {
      "id": "prepare_action",
      "service": "GMAIL",
      "instruction": "Préparer action"
    },
    {
      "id": "confirm_action",
      "service": "respond_to_user",
      "instruction": "CONFIRM_ACTION: RESULT_FROM_prepare_action Continuer ?",
      "pause_for_response": true,
      "dependencies": ["prepare_action"]
    },
    {
      "id": "prepare_action_confirmed",
      "service": "GMAIL",
      "instruction": "do prepare action",
      "dependencies": ["confirm_action"],
      "condition": "RESULT_FROM_confirm_action contains CONFIRMED"
    },
    {
      "id": "prepare_action_canceled",
      "service": "respond_to_user",
      "instruction": "Inform user action has been canceled",
      "pause_for_response": true,
      "dependencies": ["confirm_action"],
      "condition": "RESULT_FROM_confirm_action contains CANCELED"
    },

  ]
  ```

### Loop with confirmation pattern
  <!-- Traitement en masse avec confirmation -->
  ```json
  [
    {
      "id": "get_items",
      "service": "GMAIL",
      "instruction": "Lister éléments à traiter"
    },
    {
      "id": "confirm_bulk",
      "service": "respond_to_user",
      "instruction": "CONFIRM_ACTION: Traiter RESULT_FROM_get_items éléments ?",
      "pause_for_response": true
    },
    {
      "id": "loop_items",
      "loopover": "RESULT_FROM_get_items",
      "dependencies": ["confirm_bulk"],
      "start_step": "process_item",
      "condition": "RESULT_FROM_confirm_bulk contains CONFIRMED"
    },
    ...
  ]
  ```
