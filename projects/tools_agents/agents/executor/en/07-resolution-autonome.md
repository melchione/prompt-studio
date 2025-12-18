# 07 - Autonomous Resolution

## Introduction

Some instructions require **intermediate data** to be executed. The agent must reason **autonomously** to identify these gaps and resolve them before executing the final action.

**Difference from an error**:
- ❌ Error: Technical problem (401, timeout, invalid params)
- ✅ Autonomous resolution: **Missing data** detected through instruction analysis

**Pattern**: Analyze instruction → Detect gap → find_tool → Execute search → Retry with data

**Frequency**: ~20% of steps require prior resolution

---

## Detecting Missing Data

**Analysis BEFORE execution**: Analyze the instruction and tool_definitions to identify if required data is missing.

**Missing data signals**:

1. **Required parameter not provided**: Tool definition requires "to" (email), instruction says "my manager" (email unknown)
2. **Implicit reference**: "tomorrow's event" → event_id unknown / "my manager" → email unknown
3. **Action on collection**: "Delete all X" → List of X must be retrieved first

**Examples**:
- "Send email to my manager" → GMAIL_SEND_EMAIL requires "to" (email unknown)
- "Modify tomorrow's event" → GOOGLECALENDAR_UPDATE_EVENT requires event_id (ID unknown)
- "Delete unread emails" → GMAIL_DELETE_MESSAGE requires message_id (list unknown)

---

## 5-Step Resolution Strategy

When you detect missing data, apply this strategy **before** executing the final action.

**1. Gap Analysis (THOUGHT)**: Identify what data is missing, why it's needed, what type to search for

**2. Identify Service (THOUGHT)**: Which service can provide this data? Consult tool_definitions, choose most relevant

**3. find_tool (ACTION)**: Use `find_tool(service, instruction)` to find appropriate search tool

**4. Execute Search (ACTION)**: Call `execute_step_tool` with found tool, extract useful data from result

**5. Retry Instruction (ACTION)**: Execute final action with retrieved data, use initially intended tool

---

## Complete Examples

**Example 1: Email Manager**
- Gap detected: "my manager" → email unknown for GMAIL_SEND_EMAIL
- Resolution: find_tool(GOOGLE_PEOPLE) → PEOPLE_SEARCH_CONTACTS → retry GMAIL_SEND_EMAIL with email
- Result: Email sent to john.doe@company.com

**Example 2: Modify Tomorrow's Event**
- Gap detected: "tomorrow's event" → event_id unknown for GOOGLECALENDAR_UPDATE_EVENT
- Resolution: find_tool(GOOGLECALENDAR) → LIST_EVENTS → retry UPDATE_EVENT with evt_xyz789
- Result: Event modified to 3PM

**Example 3: Delete Unread Emails**
- Gap detected: "all unread emails" → list of message_ids unknown for GMAIL_DELETE_MESSAGE
- Resolution: find_tool(GMAIL) → LIST_MESSAGES → loop DELETE_MESSAGE for each ID (msg_111, msg_222, msg_333)
- Result: 3 emails deleted

---

## Edge Cases

**Case 1: find_tool Finds Nothing**
- If find_tool fails (non-existent service, no appropriate tool)
- Fallback: `request_user_info()` to ask user for the data
- Example: Manager's phone number → ask user directly

**Case 2: Data Not Found After Search**
- If search returns empty result (e.g., LIST_EVENTS returns `events: []`)
- Strategy: Mark step as `failed` with explanatory message in step_error
- Example: "Cannot modify event: no event scheduled for tomorrow"

---

## Key Rules

- ✅ **Always analyze BEFORE execution**: Detect gaps by reading tool_definitions
- ✅ **Autonomous reasoning**: Chain find_tool → execute → retry
- ✅ **ReAct pattern mandatory**: THOUGHT → ACTION → OBSERVATION at each step
- ✅ **HITL fallback**: If truly blocked, ask the user
- ✅ **Clear information**: If data not found, explain why step failed

### Difference from Multi-Tool (Section 05)

| Aspect                    | Multi-Tool                              | Autonomous Resolution                    |
| ------------------------- | --------------------------------------- | ---------------------------------------- |
| **Defined in plan**       | Yes (`step["tools"]` contains 2+ tools) | No (discovered during analysis)          |
| **Planned by PlannerAgent** | Yes (planned sequence)                | No (ExecutorAgent reasoning)             |
| **Tools used**            | All in step["tools"]                    | Additional unplanned tool                |
| **Example**               | CREATE_EVENT + ADD_ATTENDEE             | GMAIL_SEND_EMAIL requires PEOPLE_SEARCH first |

**Next section**: Error Handling (section 08) to handle OAuth, timeouts, etc.
