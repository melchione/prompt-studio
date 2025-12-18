# 02 - Enriched Plan Format

## Global Structure

```json
{
  "goal": "Description of user objective",
  "steps": [
    { /* step 1 */ },
    { /* step 2 */ }
  ]
}
```

- **`goal`** (string): Final objective to achieve
- **`steps`** (list): Ordered list of steps to execute

---

## Step Format

```json
{
  // REQUIRED
  "id": "1",
  "service": "GOOGLECALENDAR",
  "tools": ["GOOGLECALENDAR_CREATE_EVENT"],
  "instruction": "Create an event 'Team Meeting' tomorrow at 2pm",
  "dependencies": [],

  // OPTIONAL
  "condition": "RESULT_FROM_0 contains confirmed",
  "loopover": "RESULT_FROM_1",
  "start_step": "2",
  "display_result": true,
  "pause_for_response": false,
  "title": "Create meeting",
  "expected_result": "Event created with ID"
}
```

### Required Fields

- **`id`** (string): Unique identifier, used for dependencies and `RESULT_FROM_X`
- **`service`** (string): Concerned service in UPPERCASE (ex: `GOOGLECALENDAR`, `GMAIL`)
- **`tools`** (list): List of 1+ tools. Multi-tool (2+) = sequential execution (see section 05)
- **`instruction`** (string): Action to perform. Supported variables: `RESULT_FROM_X`, `CURRENT_ITEM`, `LOOP_INDEX`
- **`dependencies`** (list): IDs of prerequisite steps (determines execution order)

### Optional Fields

- **`condition`** (string): Execution condition (if false → skipped). Operators: `contains`, `equals`, `not_contains` → Section 06.1
- **`loopover`** (string): Loop over list (ex: `RESULT_FROM_1`) → Section 06.1
- **`start_step`** (string): ID of initial step in a loop
- **`display_result`** (boolean): Display result to user
- **`pause_for_response`** (boolean): Requires user response (tool `request_user_info`) → Section 06.2
- **`title`** (string): Short title for logging/UI
- **`expected_result`** (string): Description of expected result

---

## Tool Usage Flow

**Process**:
1. `step["tools"]` contains tool names → Extracted at startup
2. During execution → Consult Section 03 (Available Composio Tools) to build parameters according to `instruction`
3. Call `execute_step_tool(tool_name, parameters)` with built parameters
