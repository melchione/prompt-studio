# 06 - Control Flow

## Introduction

**Control flow** allows managing advanced execution scenarios:

1. **Loops**: Repeat steps over a list of items
2. **Conditions**: Execute a step only if a condition is true
3. **HITL (Human-in-the-Loop)**: Interrupt execution to request information from the user

---

## 6.1 - Loops & Conditions

### Loops

**Loops** allow executing steps **for each item** in a list (events, attendees, files, etc.).

#### Loop Block Structure

```json
{
  "loop_blocks": {
    "loop_events": {
      "id": "loop_events",
      "over": "RESULT_FROM_1",
      "steps": ["4", "5"]
    }
  }
}
```

**Fields**:
- **`over`**: Reference to the list of items (usually `RESULT_FROM_X`)
- **`steps`**: List of step IDs to execute for each item
- **`id`**: Unique identifier of the loop

#### Execution Workflow

**Complete sequence**:

1. **Initialize**: `start_loop({"loop_id": "loop_events"})`
   - System automatically resolves `over` (RESULT_FROM_X)
   - Returns context of 1st iteration: `{current_item, current_iteration, total_iterations}`

2. **For each iteration**:
   - **Execute** all steps in `steps: ["4", "5"]` with `current_item`
   - **Call** `finish_step(step_id, summary)` after EACH step (capture result)
   - **Advance**: `advance_loop({"loop_id"})`
   - Repeat until `should_continue: false`

3. **Automatic finalization**: When `advance_loop()` returns `should_continue: false`, the loop is automatically finalized by the system (no need to call `finish_step`)

**Special variables**:
- `CURRENT_ITEM`: Current item of the iteration (substituted in instructions)
- `LOOP_INDEX`: Index of the iteration (starts at 0)

#### Important Rules

**✅ TO DO**:
- Call `start_loop` ONCE at the beginning
- Call `finish_step` AFTER EACH step (not only at the end of iteration)
- Call `advance_loop` after ALL steps of an iteration
- Use `current_item` returned by `start_loop`/`advance_loop`

**❌ TO AVOID**:
- ❌ Call `get_loop_context` (redundant - `start_loop`/`advance_loop` return the context)
- ❌ Manually retrieve items (system does it via `over`)
- ❌ Forget to call `finish_step` for a step

#### Complete Example (2 items, 2 steps per iteration)

```
# Initialization
ACTION: start_loop({"loop_id": "loop_events"})
OBSERVATION: {
  "current_item": {"id": "evt_1", "summary": "Meeting"},
  "current_iteration": 0,
  "total_iterations": 2,
  "should_continue": true
}

# Iteration 0 - Step 4
ACTION: execute_step_tool(step_4, params with evt_1)
OBSERVATION: Event evt_1 updated
ACTION: finish_step({"step_id": "4", "result_summary": "Event 1 updated"})
OBSERVATION: {"success": true, "stored_in_loop": "loop_events"}

# Iteration 0 - Step 5
ACTION: execute_step_tool(step_5, params with evt_1)
OBSERVATION: Email sent
ACTION: finish_step({"step_id": "5", "result_summary": "Email sent for event 1"})

# Advance to iteration 1
ACTION: advance_loop({"loop_id": "loop_events"})
OBSERVATION: {
  "current_item": {"id": "evt_2"},
  "current_iteration": 1,
  "should_continue": true
}

# Iteration 1 - Steps 4 and 5
[... repeat steps 4 and 5 with evt_2 ...]

# End of loop
ACTION: advance_loop({"loop_id": "loop_events"})
OBSERVATION: {"should_continue": false, "completed": true}

# Loop is automatically finalized by the system
# All results are in loop_context.iteration_results
```

---

### Conditions

**Conditions** allow executing a step **only if** a condition is true (e.g., send notification if > 5 events).

#### Condition Structure

```json
{
  "id": "3",
  "instruction": "Send notification",
  "condition": "RESULT_FROM_1 contains confirmed",
  "dependencies": ["1"]
}
```

**Format**: `"RESULT_FROM_X operator value"`

**Operators**: `contains`, `equals`, `not_contains`

#### Evaluation

1. **Resolve** the variable (`RESULT_FROM_X`)
2. **Apply** the operator on the value
3. **Decide**:
   - Condition true → Execute the step normally
   - Condition false → Skip the step (mark `"skipped"`)

#### Compact Example

```
THOUGHT: Step 3 has condition "RESULT_FROM_1 contains confirmed"
ACTION: get_step_result({"step_id": "1"})
OBSERVATION: {"event_status": "confirmed"} → contains "confirmed" ✓
[Execute step 3 normally]

# If condition false:
OBSERVATION: {"event_status": "pending"} → does not contain "confirmed" ✗
ACTION: update_state({"step_3_status": "skipped"})
```

---

## 6.2 - HITL (Human-in-the-Loop)

**HITL** allows interrupting execution to **request information from the user** (e.g., missing information, confirmation required).

### HITL Triggers

**1. Step with `pause_for_response: true`**

```json
{
  "id": "4",
  "instruction": "CONFIRM_ACTION: Send invitations?",
  "pause_for_response": true
}
```

**2. Critical missing information**: If you detect that critical information is missing, call `request_user_info`.

### interrupt() Pattern

The Claude SDK automatically manages the HITL cycle:

1. You call `request_user_info(question, options)`
2. SDK automatically INTERRUPTS execution
3. User receives the question and responds
4. SDK automatically RESUMES execution
5. You receive the response and continue

**Important**: After calling `request_user_info`, **you don't need to do anything**. The SDK handles the pause and resume.

### `request_user_info` Tool

```json
{
  "question": "Do you want to send the invitations now?",
  "options": ["Yes", "No"]
}
```

**Return**: `{"response": "Yes"}`

### Compact Example

```
THOUGHT: Step 5 has "pause_for_response: true" → I need to request confirmation
ACTION: request_user_info({
  "question": "Do you want to send the 10 invitations now?",
  "options": ["Yes, send", "No, cancel"]
})
OBSERVATION: [SDK in PAUSE → User responds "Yes, send" → SDK RESUMES]
THOUGHT: Confirmation received, step 5 completed → finish_step
ACTION: finish_step({"step_id": "step_5", "result_summary": "Confirmation received: Yes, send"})
```

### Best Practices

**✅ TO DO**:
- Clear and precise questions
- Provide options when possible
- Wait passively after `request_user_info`

**❌ TO AVOID**:
- Ask multiple questions without waiting for responses
- Request information already available
- Be too verbose

---

**Next section**: Error Handling (section 07) to manage errors by type.
