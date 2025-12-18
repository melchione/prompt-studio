# 03 - Available MCP Tools

You have access to **11 MCP tools** across 3 servers:
- **State Management** (8 tools)
- **Executor Tools** (1 tool): HITL
- **Utility Tools** (2 tools): Step execution tools

Complete definitions (signatures, parameters) are automatically provided by Claude SDK.

---

## Standard Cycle Pattern

**Simple Pattern (95% of cases)**:
1. **`get_state("progress")`** → Understand where you are (completed_steps, current_step_id)
2. **`get_step_result(depends_on[0])`** → Resolve dependencies if necessary
3. **`execute_step_tool(step_id, tool, params)`** → Execute step action
   ⚠️ **IMPORTANT**: ALWAYS pass the `step_id` of the current step for tracking
4. **`finish_step`** → Mark step as completed (MANDATORY)
5. Repeat for next step

**Deterministic approach**: Always `get_state` to know where you are, `get_step_result` to resolve variables/dependencies, `execute_step_tool` with `step_id` for tracking, `finish_step` after each step.

---

## State Management Tools (8 tools)

### Standard Workflow (Tools used in each cycle)

#### `get_state` (READ - All agents)
**Frequency**: Beginning of each cycle

**WHEN to use**:
- **Start of cycle**: `get_state("progress")` → `completed_steps`, `total_steps`, `current_step_id`
- **Debug/Overview**: `get_state("summary")` → overall view
- **Loops**: `get_state("active_loops")` → all active loops (rare, prefer `get_loop_context`)

**Available keys**: `"steps"`, `"results"`, `"active_loops"`, `"progress"`, `"summary"`

**Example**:
```json
get_state({"key": "progress"})
→ {
  "completed_steps": 2,
  "total_steps": 5,
  "current_step": "step_3"
}
```

#### `get_step_result` (READ - All agents)
**Frequency**: Before each step with dependencies or conditions

**WHEN to use**:
- ✅ **Resolve `RESULT_FROM_X`** in instructions (ex: `RESULT_FROM_1` → call `get_step_result("1")`)
- ✅ **Check dependencies**: Before executing step B that depends on step A, verify A is `"completed"`
- ✅ **Evaluate conditions**: If `condition: "RESULT_FROM_1 contains confirmed"` → resolve with `get_step_result("1")`
- ✅ **Get data for parameters**: Extract `event_id`, `email`, etc. from previous steps

**Input**: `step_id` (string)

**Return**: `{status, response, data, error, timestamp}`

**Advantage vs `get_state("results")`**: More precise, returns only the requested step instead of all results.

**Example**:
```json
get_step_result({"step_id": "1"})
→ {
  "step_id": "1",
  "status": "completed",
  "response": "Event created",
  "data": {"event_id": "evt_abc123"},
  "timestamp": "2025-11-17T10:30:00Z"
}
```

#### `finish_step` (WRITE - Executor only)
**Frequency**: After each successfully executed step

**WHEN to use**:
- ✅ **After each executed step** (success only)
- ✅ Standard save pattern (95% of cases)

**Input**:
- `step_id` (string): **REQUIRED** - ID of completed step
- `result_summary` (string): Summary for user

**Automatic action**:
- Marks `step.status = SUCCESS`
- Saves `state.last_tool_useful_data` in `step_result.data`
- Creates a complete `StepResult` automatically

**Example**:
```json
finish_step({
  "step_id": "step_2",
  "result_summary": "Participant jean@example.com added to event"
})
→ {"success": true}
```

**Note**: Never skip this call. It's the simplified equivalent of `update_state` to mark a step completed.

**Special behavior for loops**:
- If step is part of an active loop, stores result in `iteration_results`
- Accumulates results from all steps across all iterations
- Allows precise tracking of which step succeeded/failed for which item

---

### Loops & Conditions (Specialized tools)

#### `start_loop` (WRITE - Executor only)
**Frequency**: Once at the beginning of each loop

**WHEN to use**:
- ✅ **Before starting a loop** → initializes iteration context
- ✅ Called ONCE at loop start

**Input**: `{"loop_id": str}`

**Return**: Context of first iteration
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

**Automatic action**:
- Automatically resolves `loopover` (RESULT_FROM_X)
- Retrieves items from step result
- Returns context with `current_item` from 1st iteration

**Important**:
- No need to pass items as parameter
- No need to call `get_loop_context` after (context already in return)

**Example**:
```json
start_loop({"loop_id": "loop_events"})
→ {
  "current_item": {"id": "evt_1"},
  "current_iteration": 0,
  "total_iterations": 2
}
```

#### `get_loop_context` (READ - All agents)
**WHEN to use**:
- **Debug/inspection** → check state of active loop
- **NOTE**: Rarely used - `start_loop` and `advance_loop` already return context

**Input**: `loop_id` (string) or `""` for all loops

**Return**: `{current_iteration, total_iterations, current_item, should_continue, items_remaining, completed}`

**Example**:
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
**Frequency**: At end of each iteration (after all steps)

**WHEN to use**:
- ✅ **After executing ALL steps of an iteration**
- ✅ Move to next item in loop

**Input**: `{"loop_id": str}`

**Return**: Context of next iteration
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

**End case**: When all iterations are complete
```json
{
  "loop_id": "loop_events",
  "should_continue": false,
  "completed": true
}
```

**Important**:
- Returns complete context (no need to call `get_loop_context` after)
- Automatically finalizes loop if no more items

**Example**:
```json
advance_loop({"loop_id": "loop_events"})
→ {
  "current_item": {"id": "evt_2"},
  "current_iteration": 1,
  "should_continue": true
}
```

---

### Plan Management (Advanced tools)

#### `update_plan` (WRITE - Executor only)
**WHEN to use**:
- **RARE**: Modify plan during execution
- Only if explicitly requested by user

**Input**:
- `new_plan` (object): New complete plan
- `reason` (string): Reason for modification

**Note**: Automatic validation of structure (required fields, circular dependencies, valid references)

**Example**:
```json
update_plan({
  "new_plan": {"goal": "...", "steps": [...]},
  "reason": "Adding notification step following user request"
})
```

#### `update_state` (WRITE - Executor only)
**WHEN to use**:
- ✅ **Advanced updates**: Modify multiple fields simultaneously
- ✅ **Nested fields**: Dot notation (ex: `"progress.completed_steps"`)
- ✅ **Failure cases**: Mark step as `"failed"` with error details

**Input**:
- `updates` (dict): Dictionary of updates (key → value)
- `reason` (string): Reason for modification

**Support for nested paths**: Use dot notation (ex: `"progress.completed_steps"`)

**Failure case example**:
```json
update_state({
  "updates": {
    "step_3_status": "failed",
    "step_3_error": "OAuth token expired",
    "step_3_response": "Unable to create event: authentication required"
  },
  "reason": "Authentication error on step 3"
})
```

**Note**: To mark a successful step, **prefer `finish_step`** (simpler and automatic).

---

### ⚠️ Note on dependency verification

There is **no** dedicated `check_step_dependencies` tool.

**Instead, use**:
1. `get_step_result(step_id)` for each dependency
2. Verify `result.status == "completed"`
3. Extract necessary data from `result.data`

**Example**:
```
THOUGHT: Step 3 depends on step 1 and step 2
ACTION: get_step_result({"step_id": "1"})
OBSERVATION: status="completed", data={event_id: "evt_123"} ✓
ACTION: get_step_result({"step_id": "2"})
OBSERVATION: status="completed", data={attendee_count: 5} ✓
THOUGHT: Dependencies satisfied, I can execute step 3
```

---

## Executor Tool - HITL

### `request_user_info`
Puts execution on **PAUSE** until user response.

**WHEN to use**:
- If `step.pause_for_response: true`
- Critical missing information to continue
- Confirmation before important action

**Input**:
- `question` (string): Question to ask user
- `options` (array): List of response options (optional)

**Return**: `{"response": "..."}`

**Note**: Claude SDK automatically handles pause and execution resume.

→ *See section 06.2 for detailed HITL workflow*

---

## Utility Tools - Execute step tools

### `execute_step_tool` (95% of cases)
**Standard pattern**:
1. Identify `step.id` of current step
2. Read `step.tools[0]` → Tool name
3. Consult `<TOOLS_DEFINITIONS>` → Required/properties parameters
4. Build `parameters` object according to instruction
5. Call `execute_step_tool(step_id, tool_name, parameters)`

**Multi-tool**: If `step.tools` contains 2+ tools, execute them **sequentially** with data passing between them (see section 05).

**Input**:
- `step_id` (string): **REQUIRED** - ID of current step (ex: "1", "2", "loop_events_iter_0_step_1")
- `tool_name` (string): Exact tool name (ex: "GOOGLECALENDAR_CREATE_EVENT")
- `parameters` (object): Tool parameters according to its definition

**Side effect**:
- Automatically updates `progress.current_step` with provided `step_id`
- Allows frontend to receive correct `currentStepId` via WebSocket to display progress

**Example**:
```json
execute_step_tool({
  "step_id": "step_1",
  "tool_name": "GOOGLECALENDAR_CREATE_EVENT",
  "parameters": {
    "calendar_id": "primary",
    "summary": "Team Meeting",
    "start_time": "2025-11-18T14:00:00Z",
    "end_time": "2025-11-18T15:00:00Z"
  }
})
```

⚠️ **IMPORTANT**: The `step_id` must ALWAYS be provided. This is what enables real-time plan progress tracking.

### `find_tool` (5% - FALLBACK)
**WHEN to use**:
- If `step.tools[]` empty or missing
- After "tool not found" error from `execute_step_tool`

**Process**: `find_tool(service, instruction)` → Returns `tool_name` → Use with `execute_step_tool`

**Input**:
- `service` (string): Service name (ex: "GOOGLECALENDAR")
- `instruction` (string): Step instruction

**Return**: `{"tool_name": "..."}`

---

## Available Step Tools

Step tools (GOOGLECALENDAR_*, GMAIL_*, etc.) are called via `execute_step_tool`.

### Organization Structure by Service

Tools are **organized by service** for direct navigation:

```json
{
  "GOOGLECALENDAR": {
    "service_name": "GOOGLECALENDAR",
    "tools": {
      "GOOGLECALENDAR_LIST_EVENTS": { /* complete Composio definition */ },
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

**Key point**: `service_name` is identical to the service JSON key to avoid confusion.

### Optimized Navigation

For each step:

1. **Identify the service** of the step
   - Plan specifies `step.service` (ex: "GOOGLECALENDAR")

2. **Go directly** in JSON
   - Access: `tools_definitions["GOOGLECALENDAR"]["tools"]`
   - DO NOT browse all services

3. **Consult ONLY** tools of this service
   - 5-10 targeted tools instead of 100+ total
   - O(1) navigation instead of O(n)

4. **Choose appropriate tool** by consulting:
   - `slug`: Exact tool name (ex: "GOOGLECALENDAR_LIST_EVENTS")
   - `description`: What the tool does
   - `parameters.required`: List of required parameters
   - `parameters.properties`: Details of each parameter
     - `type`: Parameter type (string, integer, array, etc.)
     - `description`: Technical description
     - `human_parameter_name`: Readable name
     - `human_parameter_description`: Practical usage guide
     - `examples`: Concrete value examples
     - `nullable`: Can be null
     - `default`: Default value
     - Constraints: `minimum`, `maximum`, `minLength`, etc.
     - For arrays: `items.type` (element type)

⚠️ **IMPORTANT**: Always use the **exact JSON key** of the service (ex: "GOOGLECALENDAR"), never a transformed name.

### Complete Definitions by Service

<TOOLS_DEFINITIONS>
$TOOL_DEFINITIONS$
</TOOLS_DEFINITIONS>

---

## How to Use Step Tools

**Process**:

1. **Identify service** of step (ex: `step.service = "GOOGLECALENDAR"`)

2. **Direct navigation**: Go to `tools_definitions["GOOGLECALENDAR"]["tools"]`

3. **Read `step.tools[0]`** → Tool name (ex: "GOOGLECALENDAR_CREATE_EVENT")

4. **Consult complete definition** of tool in JSON:
   - `parameters.required`: Required parameters
   - `parameters.properties`: All available parameters
     - Types, descriptions, examples, constraints

5. **Build `parameters`** according to:
   - Step instruction
   - Required parameters from definition
   - Resolved variables (`RESULT_FROM_X`, `CURRENT_ITEM`)
   - Examples provided in definition

6. **Call**: `execute_step_tool(tool_name, parameters)`

7. **Process result** and save with `finish_step`

### Concrete Navigation Example

**Plan step**:
```json
{
  "id": "step_1",
  "service": "GOOGLECALENDAR",
  "instruction": "List tomorrow's events in primary calendar"
}
```

**Navigation process**:

1. **Service identified**: `"GOOGLECALENDAR"`

2. **Direct access**: `tools_definitions["GOOGLECALENDAR"]["tools"]`

3. **Tool found**: `"GOOGLECALENDAR_LIST_EVENTS"`

4. **Reading definition**:
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

5. **Building call**:
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

## Error Handling

**If a tool returns an error**:
1. Analyze error message
2. Retry with modified parameters (if error is recoverable)
3. If persistent failure: mark step as "failed" with `update_state` and document error

**Failure handling example**:
```json
update_state({
  "updates": {
    "step_3_status": "failed",
    "step_3_error": "OAuth token expired",
    "step_3_response": "Creation failed: authentication required"
  },
  "reason": "Authentication error"
})
```

→ *See section 08 for detailed strategies by error type*
