# 04 - Execution Workflow

## Fundamental Principles

**7-step cycle** repeated until plan completion:
1. **Autonomy**: You determine the next step (no external instructions)
2. **ReAct Pattern**: THOUGHT → ACTION → OBSERVATION (mandatory for every action)
3. **State management**: Read/write state via MCP tools
4. **Methodical**: Respect the order of steps

---

## ReAct Pattern (MANDATORY)

Format to use for **each action**:

```
THOUGHT: [Reasoning and analysis]
ACTION: [Tool call or decision]
OBSERVATION: [Result and interpretation]
```

Ensures: traceability, debugging, transparency, quality of reasoning.

---

## 7-Step Cycle

### 1. Analyze the Context
- **Tool**: `get_state("progress")`
- **Purpose**: Know where you are (completed steps, current step, HITL pause, start/resume)
- **States**: `not_started`, `in_progress`, `hitl_paused`, `completed`

### 2. Identify the Next Step
- **Tools**: `get_state("results")` + `get_state("steps")`
- **Logic**:
  1. Retrieve results (step_id → status)
  2. For each step: verify not completed + dependencies satisfied + condition OK
  3. Choose first eligible step
- **Special cases**: Multiple dependencies (all required), conditions (evaluate RESULT_FROM_X), loops (section 06)

### 3. Read step.tools
- **Field**: `step["tools"]` (list of tool names)
- **Action**:
  - 1 tool (85%) → simple execution, continue to step 4
  - 2+ tools (15%) → see section 05 (multi-tool)

### 4. Execute with execute_step_tool
- **Workflow**:
  1. Identify the `step_id` of the current step
  2. Consult tool definition in `tool_definitions`
  3. Identify `parameters.required`
  4. Build `parameters`: extract from `step["instruction"]`, resolve variables (RESULT_FROM_X, CURRENT_ITEM)
  5. Call `execute_step_tool(step_id, tool_name, parameters)`
- **Important**: The `step_id` is mandatory and automatically updates `progress.current_step` for progress tracking
- **Fallback**: If `step["tools"]` is empty → `find_tool(service, instruction)`

### 5. Process the Result
- Parse JSON (`success`, `data`, `error`)
- Verify success
- Extract useful data (automatically stored in `state.last_tool_useful_data`)
- If error → section 07

### 6. Save the State
- **Tool**: `finish_step` (standard case - 95%)
- **Input**:
  - `step_id`: ID of the completed step
  - `result_summary`: Summary for the user
- **Automatic action**:
  - Marks `step.status = SUCCESS`
  - Saves `state.last_tool_useful_data` in `step_result.data`
  - Updates counters `completed_steps`, `current_step_id`

**Alternative**: `update_state` for advanced cases (failures, multi-field, nested fields)

### 7. Check if Completed
- **Tool**: `get_state("progress")`
- **Logic**: `completed_steps == total_steps`?
  - **Yes** → End, send final summary
  - **No** → Return to step 1 (new cycle)

---

## Complete Example: Executing Step 2

**Context**: Plan with 2 steps (create event, add attendee). Step 1 completed, executing step 2.

```
THOUGHT: New cycle. I need to understand where I am → get_state("progress")
ACTION: get_state({"key": "progress"})
OBSERVATION: completed_steps: 1/2, current: "2" → Step 2 ready

THOUGHT: Identify step to execute → retrieve results and steps
ACTION: get_state("steps")
OBSERVATION: Step 2 depends on ["1"], step 1 completed → Step 2 eligible

THOUGHT: Step 2 tools = ["GOOGLECALENDAR_ADD_ATTENDEE"] → 1 tool, simple case
ACTION: Consult definition → required params: event_id, email
OBSERVATION: Instruction: "Add jean@example.com to RESULT_FROM_1"
  → email = "jean@example.com", event_id = RESULT_FROM_1 (to resolve)

ACTION: get_step_result({"step_id": "1"})
OBSERVATION: data.event_id = "evt_abc123" → RESULT_FROM_1 resolved

ACTION: execute_step_tool({"step_id": "step_2", "tool_name": "GOOGLECALENDAR_ADD_ATTENDEE", "parameters": {"event_id": "evt_abc123", "email": "jean@example.com"}})
OBSERVATION: success: true, attendee_added: true → Success
  → progress.current_step automatically updated with "step_2"

THOUGHT: Step 2 completed successfully → finish_step
ACTION: finish_step({"step_id": "step_2", "result_summary": "Attendee jean@example.com added to event"})
OBSERVATION: Step 2 saved as SUCCESS

ACTION: get_state("progress")
OBSERVATION: 2/2 steps → Plan completed successfully
```
