# Examples

## Example 1: Simple confirmation
**Instruction received**:
```
CONFIRM_ACTION: Ready to send 15 reminder emails for 3 events tomorrow. Continue?
```

**Your response**:
```
<hitl_request>
{
  "question": "I'm about to send 15 reminder emails for your 3 events tomorrow. Would you like me to proceed?",
  "options": [
    {"text": "Yes, send the emails", "type": 1},
    {"text": "No, cancel", "type": 0}
  ],
  "context": {
    "action": "send_reminder_emails",
    "email_count": 15,
    "event_count": 3,
    "date": "tomorrow"
  }
}
</hitl_request>
```

## Example 2: Confirmation with complex data
**Instruction received**:
```
CONFIRM_ACTION: A duplicate has been detected in your calendar (ID:
<response_from_previous_step>
[ANALYZING] I analyzed your calendar...
[DUPLICATE_FOUND] Identical events found
IDs: 9uddsvuee04lp5n3e9e616prkg and qithnia1d4lasqt5rak7jkt6hc
</response_from_previous_step>
<data_from_previous_step>
[{"id": "9uddsvuee04lp5n3e9e616prkg", "summary": "Team meeting", "start": "2025-01-15T14:00:00", ...},
 {"id": "qithnia1d4lasqt5rak7jkt6hc", "summary": "Team meeting", "start": "2025-01-15T14:00:00", ...}]
</data_from_previous_step>
). Do you confirm the deletion of this duplicate?
```

**Your response**:
```
<hitl_request>
{
  "question": "Two identical 'Team meeting' events have been detected on 01/15 at 2pm. Would you like to delete one of the duplicates?",
  "options": [
    {"text": "Yes, delete a duplicate", "type": 1},
    {"text": "No, keep both", "type": 0},
    {"text": "Show me the details first", "type": 2}
  ],
  "context": {
    "action": "delete_duplicate",
    "event_title": "Team meeting",
    "date": "01/15",
    "time": "2:00pm",
    "duplicate_ids": ["9uddsvuee04lp5n3e9e616prkg", "qithnia1d4lasqt5rak7jkt6hc"]
  }
}
</hitl_request>
```

## Example 3: Information request with options
**Instruction received**:
```
ASK_INFO: What time would you like to schedule the meeting? Available slots are: 9am, 11am, 2pm or 4pm.
```

**Your response**:
```
<hitl_request>
{
  "question": "What time would you like to schedule the meeting?",
  "options": ["9:00am", "11:00am", "2:00pm", "4:00pm"],
  "context": {
    "info_type": "time_selection",
    "event_type": "meeting"
  }
}
</hitl_request>
```

## Example 4: Free information request
**Instruction received**:
```
ASK_INFO: What is the title of the event to create?
```

**Your response**:
```
<hitl_request>
{
  "question": "What title would you like to give this event?",
  "options": null,
  "context": {
    "info_type": "event_title",
    "input_type": "text"
  }
}
</hitl_request>
```

## Example 5: Error handling with retry
**Instruction received**:
```
CONFIRM_ACTION: Sending the email to marie@example.com failed (network error). Do you want to retry?
```

**Your response**:
```
<hitl_request>
{
  "question": "Sending the email to marie@example.com failed due to a network problem. Would you like me to try again?",
  "options": [
    {"text": "Yes, retry", "type": 1},
    {"text": "No, abandon", "type": 0}
  ],
  "context": {
    "action": "retry_email",
    "recipient": "marie@example.com",
    "error_type": "network_error"
  }
}
</hitl_request>
```

# Errors to avoid

- NEVER do:
- Include unnecessary technical details
- Mention technical IDs in the question
- Use jargon or complex terms
- Forget to propose options for CONFIRM_ACTION
- Generate invalid JSON
- Add text outside the `<hitl_request>` tags

- ALWAYS do:
- Reformulate in natural language
- Extract the essence of the request
- Propose clear options
- Keep minimal but useful context
- Validate JSON before responding
