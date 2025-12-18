# 08 - Error Handling

## Introduction

Technical errors require a specific recovery strategy.

**Difference**:
- ❌ **Error**: Technical problem (401, timeout, invalid params)
- ✅ **Autonomous resolution**: Missing data detected through analysis

**Error types**:
1. OAuth (401/403): Expired token or disconnected app
2. Tool not found (404): Incorrect tool name
3. Invalid parameters (400): Incorrect format/type
4. Timeout (504): API too slow
5. Business error: Tool executed but logic fails

**General pattern**: THOUGHT (analyze type + cause) → ACTION (strategy) → OBSERVATION (result)

---

## OAuth Error (401/403) ⭐

**Causes**: Expired token, revoked, disconnected app, insufficient permissions

**Detection**: 401/403 codes or messages "unauthorized", "token expired"

**Strategy (max 1 retry)**:
1. THOUGHT: Analyze cause (expired token vs disconnected app)
2. ACTION: `request_user_info` to request reconnection
3. OBSERVATION: SDK pauses → user connects → connection established
4. ACTION: Retry execute_step_tool with same parameters
5. If fails after reconnection → FAIL step

**OAuth Error Example**:
```
ACTION: execute_step_tool("GOOGLECALENDAR_LIST_EVENTS")
OBSERVATION: {"success": false, "error": "401 Unauthorized: Token has expired"}

THOUGHT: Token expired → request reconnection
ACTION: request_user_info("Reconnect to Google Calendar")
OBSERVATION: Connection established → retry successful ✓
```

---

## Tool Not Found (404)

**Causes**: Typo in tool name, missing tool after enrichment, misidentified service

**Detection**: Message "Tool {tool_name} not found in tool_definitions"

**Strategy (max 1 retry)**:
1. THOUGHT: Tool not found → probably typo or incorrect service
2. ACTION: `find_tool(service, instruction)` to find correct tool
3. OBSERVATION: Tool found or error
4. If found → ACTION: execute_step_tool with new tool
5. If not found → FAIL step

**Tool 404 Example**:
```
ACTION: execute_step_tool("GOOGLECALENDAR_CREAT_EVENT")  ← Typo
OBSERVATION: Tool not found

THOUGHT: Typo detected (missing E in CREATE)
ACTION: find_tool("GOOGLECALENDAR", "Create event") → GOOGLECALENDAR_CREATE_EVENT
OBSERVATION: Retry with corrected tool → success ✓
```

---

## Invalid Parameters (400)

**Causes**: Wrong type, incorrect format (date, email), missing required field, value out of range

**Detection**: Code 400 + message "Invalid parameter 'X': expected format Y"

**Strategy (max 2 retries)**:
1. THOUGHT: Analyze message → identify faulty parameter
2. ACTION: Re-read tool_definitions for expected format
3. THOUGHT: Correct parameter with proper format/type
4. ACTION: execute_step_tool with corrected params

**Invalid Params Example**:
```
ACTION: execute_step_tool("CREATE_EVENT", {start_time: "2025-11-14 10:00"})
OBSERVATION: {"error": "400: expected ISO8601 format"}

THOUGHT: Invalid format → must be ISO8601 with T and Z
ACTION: Re-read definitions → retry with "2025-11-14T10:00:00Z"
OBSERVATION: Success after correction ✓
```

---

## Timeout (504)

**Causes**: Slow external API, high server load, unstable network, complex operation

**Detection**: Code 504 + message "Request timeout after X seconds"

**Strategy (0 retry)**:
1. THOUGHT: Timeout detected → action may have partially succeeded
2. ACTION: Log error with full context
3. THOUGHT: Blocking or optional step?
4. If blocking → FAIL step with clear message
5. If optional → SKIP and continue

**❌ No retry**: Risk of duplicate if action partially succeeded

**Timeout Example**:
```
ACTION: execute_step_tool("GMAIL_SEND_EMAIL", {...})
OBSERVATION: {"error": "504 Gateway Timeout"}

THOUGHT: Timeout → email may have been partially sent, no retry
ACTION: update_state(step_failed) → inform user to retry manually
OBSERVATION: State saved, user notified
```

---

## Business Error

**Definition**: Tool executes technically but fails for logical/business reason

**Examples**: "Event not found", "Quota exceeded", "Calendar is read-only", "Email address invalid"

**Detection**: `{"success": false, "error": "Business error message"}` (no HTTP code)

**Strategy (case by case)**:
1. THOUGHT: Analyze business error message
2. THOUGHT: Can we adapt instruction or workaround?
3. If adaptable → correct and retry
4. If not adaptable → FAIL with clear message

**Business Error Example 1** (objective achieved):
```
ACTION: execute_step_tool("DELETE_EVENT", {event_id: "evt_123"})
OBSERVATION: {"error": "Event not found (already deleted)"}

THOUGHT: Event already deleted → objective achieved
ACTION: update_state(step_completed, note="already_deleted")
```

**Business Error Example 2** (not recoverable):
```
ACTION: execute_step_tool("SEND_EMAIL", {...})
OBSERVATION: {"error": "Quota exceeded (max 500/day)"}

THOUGHT: Gmail quota exceeded → cannot workaround
ACTION: update_state(step_failed, response="Try again tomorrow")
```

---

## Summary Table

| Error Type           | Code    | Strategy                        | Retry?       | Max | Fallback              |
| -------------------- | ------- | ------------------------------- | ------------ | --- | --------------------- |
| **OAuth**            | 401/403 | request_user_info → reconnect   | ✅ Yes       | 1x  | Fail if refused       |
| **Tool not found**   | 404     | find_tool → retry with correct  | ✅ Yes       | 1x  | Fail if not found     |
| **Invalid params**   | 400     | Re-read definitions → correct   | ✅ Yes       | 2x  | Fail after 2          |
| **Timeout**          | 504     | Log → Inform user               | ❌ No        | 0x  | Fail (risk duplicate) |
| **Business error**   | 200/500 | Analyze → Adapt if possible     | ⚠️ Case by case | 1x | Fail with message  |

---

## General Rules

**Pattern**: Always THOUGHT → ACTION → OBSERVATION for each error

**Retry limits**: Maximum 2 retries per step (OAuth: 1x, Tool 404: 1x, Params: 2x, Timeout: 0x)

**Logging**: Log with error type, code, original message, parameters, recovery attempt

**Messages**: Clear and actionable, explain why, avoid technical jargon

**State**: Always update_state after handling (status: "failed"/"completed", error: technical, response: user)

**Next section**: Examples (section 09) with 5 complete end-to-end scenarios.
