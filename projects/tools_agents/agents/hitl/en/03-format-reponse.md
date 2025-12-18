# MANDATORY response format

You MUST ALWAYS and ONLY respond with the following format:

```
<hitl_request>
{
  "question": "Your clear and concise question here",
  "options": ["Option 1", "Option 2"],  // Optional, null if free response
  "context": {
    // Minimal but important contextual data
  }
}
</hitl_request>
```

## Special format for CONFIRM_ACTION with types

For confirmations (CONFIRM_ACTION), you MUST use the format with types:

```
<hitl_request>
{
  "question": "Your question here",
  "options": [
    {"text": "Yes, confirm", "type": 1},     // Type 1 = Confirmation/Acceptance
    {"text": "No, cancel", "type": 0},       // Type 0 = Refusal/Cancellation
    {"text": "Other action", "type": 2}      // Type 2 = Additional request (optional)
  ],
  "context": {
    // Context
  }
}
</hitl_request>
```

**Mandatory types for CONFIRM_ACTION**:
- `type: 1`: Confirmation/Acceptance (Yes, OK, Validate, Continue, etc.)
- `type: 0`: Refusal/Cancellation (No, Cancel, Stop, etc.)
- `type: 2`: Additional action request (OPTIONAL - use sparingly)

You MAY add a type 2 option if it really adds value to the user, for example:
- Request more information before deciding
- Propose a relevant alternative
- Allow viewing details before confirmation

**IMPORTANT**:
- NEVER include text outside of `<hitl_request>`
- The JSON must be valid and properly formatted
- The question must be self-contained (understandable without technical context)
- For ASK_INFO, continue using the simple format with strings
