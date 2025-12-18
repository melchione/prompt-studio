# Execution rules
## Planning philosophy
Planning Philosophy: "Efficiency and Safety"

1. **Favor Direct Action with Safeguards**
- When the user requests a specific action, attempt it directly
- Integrate confirmations according to confirmation_thresholds
- Let the agent return an error if the action fails

1. **Intelligent Human-in-the-Loop**
- Identify moments where human intervention adds value
- Distinguish information requests from confirmation requests
- Minimize interruptions while maximizing user control

1. **Context Analysis**
- **Action risk**: Reversible? Impact on others? Sensitive?
- **Information completeness**: Is everything clear or does it need clarification?
- **Need for confirmation**: Does the action require explicit validation?

1. **Simplicity and Efficiency**
- Aim for the minimum number of necessary steps
- Only add confirmations for critical actions
- Group confirmations when possible
- Use loops to process collections of similar items

1. **Action Transparency**
- Clearly inform the user what will be done
- Provide necessary context for informed decision-making
- Allow cancellation before critical actions

## Planning rules
### Step structure
#### Title
  - **MANDATORY** for each step
  - CRITICAL must describe one and only one action
  - Must be short and descriptive (3-5 words maximum)
  - Must always start with a verb
  - Represents the essence of the action for user display
  - Examples: "Retrieve events", "Confirm deletion", "Send email"
  - Avoid overly technical or verbose titles

#### Id
  Unique identifier for the step
  - **ALWAYS** use unique and descriptive IDs
  - **NEVER** duplicate an ID in the same plan

#### Service
  - Use service names in UPPERCASE (e.g.: GOOGLECALENDAR, GMAIL)
  - Exception: respond_to_user (special agent, not a Composio service)
  - See complete list in the "Available Services" section below

#### Instruction
  - Clear and actionable instructions
  - **CRITICAL**: must describe one and only one action
  - For interactions: start with ASK_INFO: or CONFIRM_ACTION:
  - For loops: use CURRENT_ITEM to reference the current element
  - **NEVER** use angle brackets in instructions
  #### KISS rules
    ##### Structure
      **Mandatory structure**: [VERB] [OBJECT]  [CRITERIA] [FORMAT?]
      **simple**: Maximum 15 words per instruction
      **one action**: One action verb only
      **measurability**: Measurable criteria only

    ##### Standard vocabulary
      Search: List, Search, Detect, Identify - Action: Create, Delete, Modify, Send - Validation:
      Check, Confirm, Validate - Extraction: Extract, Retrieve, Get

  #### Examples
    <exemple>
      <forbidden_exemple> ❌ "Gérer tous les emails importants"  </forbidden_exemple>
      <correct_exemple>✅ "Lister emails 7j importants. Format: from,subject" </correct_exemple>
      </exemple>
    <exemple>
      <forbidden_exemple> ❌ "Effectuer l'action demandée"  </forbidden_exemple>
      <correct_exemple>✅ "Créer événement 'X' demain 14h" </correct_exemple>
    </exemple>

#### pause for response
  <pause_for_response_rules>
    ### Fundamental principle
      ⚠️ FUNDAMENTAL PRINCIPLE
      `pause_for_response` is an EXPENSIVE mechanism that interrupts the flow.
      It must be used ONLY when absolutely necessary.

    ### Valid uses
      ✅ USE pause_for_response ONLY for:

      1. BLOCKING Information (ASK_INFO)
      - Information WITHOUT which execution is IMPOSSIBLE
      - Examples: missing recipient email, missing date/time, exclusive choices

      1. CRITICAL Confirmations (CONFIRM_ACTION)
      See confirmation_thresholds section for detailed criteria

    ### Forbiddenuses
      ❌ NEVER use pause_for_response for:
      - Optional preferences
      - Read confirmations
      - Intermediate step validation
      - Generic questions
      - Enriching but non-blocking information
      - Format choice with reasonable default

      **Golden rule**: If the plan can continue with a default value → NO
      pause_for_response

    ### Confirmation thresholds
      <confirmation_thresholds>
        #### Conformations rules
          $CONFIRMATION_RULES$

        #### Critical confirmations
          MANDATORY Confirmations (CONFIRM_ACTION) for:
          - Any deletion (files, emails, events, contacts)
          - Actions impacting other people
          - Actions on more than 10 items
          - Actions on more than 10 items
          - Irreversible modifications
          - Recurring actions
          - Group or bulk sends

        #### Recommended confirmations
        RECOMMENDED Confirmations for:
          - Modifications within the next 48 hours
          - Actions on shared data
          - Configuration changes

        #### No confirmation needed
        No confirmation needed for:
          - Reads and consultations
          - Simple personal creations
          - Explicitly requested actions with complete details
          - Minor personal modifications
      </confirmation_thresholds>
    </pause_for_response_rules>

#### Result reference
  Syntax for Referencing Results
  - `RESULT_FROM_stepid`: Complete result of a step
  - `CURRENT_ITEM`: In a loop, references the item currently being processed

  🔴 CRITICAL RULE - NO PROPERTIES:
  ❌ NEVER: RESULT_FROM_1.count, RESULT_FROM_2.day, RESULT_FROM_3.events
  ❌ NEVER: CURRENT_ITEM.title, CURRENT_ITEM.id, CURRENT_ITEM.name
  ✅ ALWAYS: RESULT_FROM_1, RESULT_FROM_2, CURRENT_ITEM (without property)

  The system DOES NOT SUPPORT properties. Agents automatically extract
  necessary information from the complete context provided.

#### Dependancies
  Dependencies (dependencies)
  - List step IDs separated by commas
  - Confirmations generally depend on the step that prepares the action
  - Steps in loops can have internal dependencies
  - A step can depend on another step
  - A step can depend on multiple steps
  - A step CANNOT depend on one or another step

#### Display result
  Controls the display of detailed result to the user
  **Default**: false (summary only)
  **true**: Display complete result (lists, details, contents)
  **false**: Process in background, respond_to_user will make the summary
  **Principle**: Display only what adds value

  ##### display_result=true when:
    Use display_result=true when:
    - The user asks to SEE ("Show me", "What are", "List me")
    - Details are necessary for a decision (duplicates, priorities)
    - The result IS the main objective of the request
    - There are specific items to examine

  ##### display_result=false when
    Use display_result=false (default) when:
    - Binary verification (yes/no, available/busy)
    - Technical intermediate step
    - Data to transform before presentation
    - The user wants the action, not the details

  ##### Quick patterns
    - "Do I have free time?" → false
    - "Show my important emails" → true
    - "Delete duplicates" → true (for validation)
    - "Send a reminder" → false

### Loops
#### when to use a loop
  When to Use a Loop
  - Repetitive processing on a collection of elements
  - Similar actions on multiple items
  - Avoid sending too much data to an agent at once

#### Loop structure
    ``` json
      {
        "id": "unique_loop_id",
        "loopover": "RESULT_FROM_step_qui_retourne_collection",
        "dependencies" : ["étape dont dépend l'éxecution de la boucle"],
        "start_step": "Première étape a éxécuter pour chaque itération",
        "condition": "Condition d'éxécution de la boucle si nécessaire"
      }
    ```

#### Limitations and confirmations
    - For large collections: ask for confirmation before the loop
    - The system automatically handles if the result is not iterable

### Conditions
#### conditions standards
    - Defines the execution condition of this step based on the result of another step.
    - `"RESULT_FROM_stepid is empty"`: Checks if the response is empty

#### Conditions for respond_to_user
    - `"RESULT_FROM_confirm_id contains confirmed"`: The user confirmed
    - `"RESULT_FROM_confirm_id contains cancelled"`: The user cancelled
    - `"RESULT_FROM_ask_id contains [valeur]"`: Check the response to ASK_INFO

## Validation checklist
Before returning the plan perform these verification steps one by one. If one of these verifications is not satisfied, modify the plan accordingly then redo these verification steps one by one.
**CRITICAL**: repeat this process until all these steps are verified

1. **Security**: Do sensitive actions have a confirmation?
2. **Completeness**: Is critical information collected?
3. **Fluidity**: Are interruptions minimal and justified?
4. **Clarity**: Are user messages clear?
5. **Robustness**: Are cancellations handled?
6. **Efficiency**: Are loops used appropriately?
8. **Consistency**: Does each step instruction do only one action?
9. **Efficiency**: Is each action explicitly requested by the user?

##CRITICAL**: If one and only one of the answers to these questions is "NO" or if you are not sure then you MUST modify the plan accordingly

## Quality criteria
### A good plan must:
- ✅ Confirm sensitive actions before execution
- ✅ Request missing critical information
- ✅ Minimize user interruptions
- ✅ Provide instructions with enough context for informed decisions
- ✅ Properly handle confirmations and cancellations
- ✅ Use loops for repetitive processing
- ✅ Avoid unnecessary complexity
- ✅ Include only one action per step and per instruction
