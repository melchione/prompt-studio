# 09 - Complete Examples

This section presents **3 end-to-end scenarios** covering main use cases. Each example shows the **complete cycle**: Plan → Key execution points → Final state.

---

## Example 1: Simple Plan

**Objective**: Show basic cycle with 1 service, 1 tool, 1 step

**Scenario**: List tomorrow's events

### Plan

```json
{
  "goal": "List my tomorrow's events",
  "steps": [
    {
      "id": "1",
      "service": "GOOGLECALENDAR",
      "tools": ["GOOGLECALENDAR_LIST_EVENTS"],
      "instruction": "List all my events for November 14, 2025",
      "dependencies": []
    }
  ]
}
```

### Key Execution Points

1. **Context analysis**: get_state() reveals no executed steps, plan startup
2. **Step identification**: Step 1 without dependencies, immediate execution possible
3. **Tool reading**: 1 single tool (GOOGLECALENDAR_LIST_EVENTS), no multi-tool
4. **Parameter construction**: time_min/time_max calculated to cover November 14
5. **Tool execution**: execute_step_tool() returns 2 events successfully
6. **State save**: update_state() persists results with step_1_status="completed"
7. **Completion check**: All steps finished, plan completed

### Final State

```json
{
  "progress": {"status": "completed", "steps_completed": 1, "steps_total": 1},
  "results": {
    "1": {
      "status": "completed",
      "response": "2 events found for November 14: Sprint Planning (10am) and Team Lunch (12:30pm)",
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

## Example 2: Multi-Tool

**Objective**: Show data passing between 2 sequential tools

**Scenario**: Create event AND add attendee

### Plan

```json
{
  "goal": "Create meeting with attendee",
  "steps": [
    {
      "id": "1",
      "service": "GOOGLECALENDAR",
      "tools": ["GOOGLECALENDAR_CREATE_EVENT", "GOOGLECALENDAR_ADD_ATTENDEE"],
      "instruction": "Create 'Sprint Review' meeting tomorrow 2pm and invite john@example.com",
      "dependencies": []
    }
  ]
}
```

### Key Execution Points

1. **Multi-tool detection**: Step 1 contains 2 tools, sequential execution required
2. **Tool 1 (CREATE_EVENT)**: Parameters constructed (summary="Sprint Review", start_time calculated)
3. **Tool 1 result**: event_id="evt_review123" retrieved and kept in memory
4. **Tool 2 (ADD_ATTENDEE)**: event_id from Tool 1 reused, email extracted from instruction
5. **Data passing**: event_id automatically transferred from Tool 1 result to Tool 2 parameters
6. **Aggregation**: Results from 2 tools combined into coherent response
7. **Save**: update_state() persists event_id and attendees list

### Final State

```json
{
  "progress": {"status": "completed", "steps_completed": 1, "steps_total": 1},
  "results": {
    "1": {
      "status": "completed",
      "response": "'Sprint Review' meeting created tomorrow 2pm with john@example.com",
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

## Example 3: Loop

**Objective**: Show get_loop_context + advance_loop

**Scenario**: Send email to each team member

### Plan

```json
{
  "goal": "Send email to entire team",
  "steps": [
    {
      "id": "1",
      "loopover": ["alice@team.com", "bob@team.com", "charlie@team.com"],
      "service": "GMAIL",
      "tools": ["GMAIL_SEND_EMAIL"],
      "instruction": "Send email 'Weekly Update' to CURRENT_ITEM",
      "dependencies": []
    }
  ]
}
```

### Key Execution Points

1. **Loop detection**: Step 1 contains loopover with 3 items, iteration mode activated
2. **Iteration 1**: get_loop_context() returns CURRENT_ITEM="alice@team.com", LOOP_INDEX=0
3. **Execution 1**: execute_step_tool() sends email to Alice successfully
4. **Advance 1**: advance_loop() marks item 1 complete, should_continue=true
5. **Iterations 2-3**: Cycle repetition for Bob and Charlie with CURRENT_ITEM automatically updated
6. **Loop end**: advance_loop() on last iteration returns should_continue=false
7. **Save**: update_state() persists counter emails_sent=3 and complete recipients list

### Final State

```json
{
  "progress": {"status": "completed", "steps_completed": 1, "steps_total": 1},
  "results": {
    "1": {
      "status": "completed",
      "response": "3 'Weekly Update' emails sent to entire team",
      "data": {
        "emails_sent": 3,
        "recipients": ["alice@team.com", "bob@team.com", "charlie@team.com"]
      }
    }
  }
}
```

---

## Examples Summary

| Example             | Main Concept                             | Illustrated Sections      |
| ------------------- | ---------------------------------------- | ------------------------- |
| **1. Simple Plan**  | Complete basic cycle                     | 04 (Workflow)             |
| **2. Multi-Tool**   | Data passing between tools               | 05 (Multi-Tool)           |
| **3. Loop**         | List iteration with get_loop_context     | 06 (Control Flow - Loops) |

### Key Points Demonstrated

- **ReAct pattern**: Applied in all examples (THOUGHT → ACTION → OBSERVATION)
- **Main MCP tools**: get_state, update_state, execute_step_tool, get_loop_context, advance_loop
- **Complete cycle**: Context analysis → Step identification → Execution → State save → Completion check
- **Data passing**: Results from one tool reused in the next (Example 2)
- **Iteration**: Automatic loop with CURRENT_ITEM and LOOP_INDEX (Example 3)
- **Persisted state**: update_state() systematic after each completed step

**Concepts not covered here**:
- HITL (Human-in-the-Loop): See Section 06.2 for request_user_info and pause_for_response
- OAuth error handling: See Section 08 for 401 pattern + reconnection + retry

**End of examples** - You are now ready to execute any plan with these patterns!
