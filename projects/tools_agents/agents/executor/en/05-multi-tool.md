# 05 - Multi-Tool Handling

## Introduction

Some steps require **multiple Composio tools** executed sequentially with data passing between them.

**Examples**: Create event then add attendees, search files then move them, list emails then mark them as read.

**Frequency**: ~15% of steps (majority have 1 single tool)

---

## Definition

**Multi-tool**: Step whose `step["tools"]` contains **2 or more** tool names.

**Example**:

```json
{
  "id": "1",
  "service": "GOOGLECALENDAR",
  "tools": ["GOOGLECALENDAR_CREATE_EVENT", "GOOGLECALENDAR_ADD_ATTENDEE"],
  "instruction": "Create meeting 'Sprint Planning' tomorrow at 10am and invite john@example.com",
  "dependencies": []
}
```

**Reason**: The instruction requires multiple sequential actions where tool 2 depends on the result of tool 1 (data chaining).

---

## Sequential Workflow

To execute a multi-tool step:

1. **Execute tools[0]** → `execute_step_tool(tools[0])` → get result
2. **Extract useful data** → parse result (e.g., `event_id`) → store for tools[1]
3. **Build parameters for tools[1]** → use data from tools[0] + instruction
4. **Execute tools[1]** → `execute_step_tool(tools[1])` → get result
5. **Repeat for tools[2+]** if needed → each tool uses previous results

**Rules**:
- ✅ Sequential execution: tools[0] → tools[1] → tools[2]... (no parallelization)
- ✅ Data passing: each tool can use results from previous tools
- ⚠️ Error handling: if one tool fails, entire step fails (see section 07)

---

## Data Passing Between Tools

**Data chaining** is crucial for multi-tool. Mechanism:

1. **Tool N** produces a result: `{"success": true, "data": {"field": "value"}}`
2. **You extract** useful data: `field = "value"`
3. **Tool N+1** receives this data: `parameters: {"previous_field": "value", ...}`
4. **Analyze definitions**: check `parameters.properties` of each tool to know what parameters to expect

**Example**:
```
Tool 1: CREATE_EVENT → {"event_id": "evt_123"} → you store event_id
Tool 2: ADD_ATTENDEE → {"event_id": "evt_123", "email": "john@..."} → uses event_id from Tool 1
```

---

## ReAct Pattern Example

**Step**: `tools: ["CREATE_EVENT", "ADD_ATTENDEE"]`, instruction: "Create meeting 'Sprint Planning' tomorrow 2pm and invite john@example.com"

```
THOUGHT: 2 tools to execute sequentially. Tool 1: CREATE_EVENT with title="Sprint Planning", start_time="2025-11-14T14:00:00Z"

ACTION: execute_step_tool({"tool_name": "CREATE_EVENT", "parameters": {"title": "Sprint Planning", "start_time": "2025-11-14T14:00:00Z"}})

OBSERVATION: {"success": true, "data": {"event_id": "evt_abc123"}} → I store event_id

THOUGHT: Tool 1 completed. Tool 2: ADD_ATTENDEE with event_id="evt_abc123" (from tool 1), email="john@example.com"

ACTION: execute_step_tool({"tool_name": "ADD_ATTENDEE", "parameters": {"event_id": "evt_abc123", "email": "john@example.com"}})

OBSERVATION: {"success": true} → attendee added. Step 1 complete: event created + attendee added

ACTION: finish_step({"step_id": "step_1", "result_summary": "Event 'Sprint Planning' created with attendee john@example.com"})
```

---

## Special Cases

### 1. More than 2 Tools
If `step["tools"]` contains 3+ tools, apply the same workflow sequentially: `tools[0] → extract → tools[1] → extract → tools[2] → ...` (e.g., `["CREATE_EVENT", "ADD_ATTENDEE", "SEND_NOTIFICATION"]`)

### 2. Tool Error
If a tool fails (`success: false`), entire step fails → save with `step_X_status: "failed"` and `step_X_error` (see section 07).

### 3. Optional Data
If tool returns list and instruction asks for choice (e.g., "delete the first one"), you choose according to instruction then pass data to next tool (e.g., `LIST_EVENTS` → choose `event_a[0]` → pass `event_a.id` to `DELETE_EVENT`)

### 4. Variable Resolution
If instruction contains `RESULT_FROM_X`, resolve with `get_step_result({"step_id": "X"})` **before** executing tools.

---

**Next section**: Control Flow (section 06) for loops, conditions and HITL.
