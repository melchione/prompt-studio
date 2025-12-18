# Resources
## Available Services
Available Composio services for orchestration.
Each service corresponds to an external integration (Google Calendar, Gmail, etc.).

**IMPORTANT**: Use UPPERCASE service names (GOOGLECALENDAR, GMAIL, etc.)
in the `service` field of each step, EXCEPT for respond_to_user.

$SERVICES_TAXONOMY$

### respond_to_user_agent
  - **Name**: respond_to_user
  - **Function**: Direct interaction with the user
  - **Used for**: information, confirmations, clarifications, ASK_INFO, CONFIRM_ACTION
  - **Special capability**: Can pause the workflow with `pause_for_response`
  - **When to use**: critical confirmations, missing information, final results

## Services Reference
All available services are listed in the "$SERVICES_TAXONOMY$" section above.
ALWAYS use UPPERCASE names (GOOGLECALENDAR, GMAIL, etc.)

## Decision guides
Decision Guide

### When to use loops
  When to Use Loops
  - Identical processing on multiple items
  - More than 3 similar actions to perform
  - Search result returns a collection

### When to use pause_for_response
  When to Ask for Confirmation
    See confirmation_thresholds section for detailed rules

### When to use display_result
  - The user asks to SEE ("Show me", "What are", "List me")
  - Details are necessary for a decision (duplicates, priorities)
  - The result IS the main objective of the request
  - There are specific elements to examine

### When to create a conditionnal step
  #### Rule:
    When an agent is going to return its response, you can define several next steps each dependent on its result.
    <exemple>
      Step with id "3" in the plan returns a list of events
      We must then have:
      One step with depencies = ["3"] and condition: "RESULT_FROM3 contains at least 1 event"
      and another step with depencies = ["3"] and condition: "RESULT_FROM3 events are empty"
    </exemples>

## Reusable patterns
### Action simple pattern
  <!-- Simple action without confirmation -->
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
  <!-- Sensitive action with confirmation -->
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
  <!-- Bulk processing with confirmation -->
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
