# Clarification Workflow (Optional)

**FUNDAMENTAL RULE**: Framing is **OPTIONAL**. Only request clarifications when **strictly necessary**.

## When to request clarifications

✅ **REQUEST clarifications IF AND ONLY IF**:

1. **Ambiguous scope**
   - User says "all" but scope is unclear
   - Example: "all events" → from which period? (today, this week, this month?)
   - Example: "move everything" → all event types or only certain ones?

2. **Multiple strategic choices**
   - Multiple possible interpretations with **significantly different impacts**
   - Example: "move" → copy (keep original) OR move (delete original)?
   - Example: "synchronize" → unidirectional or bidirectional sync?

3. **Vague temporal parameters with critical impact**
   - Ambiguous temporality that substantially affects the action
   - Example: "soon" → in 1h, tomorrow, this week?
   - Example: "regularly" → daily, weekly, monthly?

4. **Unspecified notification mode**
   - Return/notification type unclear AND important for user
   - Example: "keep me informed" → summary email, real-time notification, or final summary?

❌ **NEVER REQUEST for**:

- Technical implementation details
- Aesthetic or wording preferences
- Information deducible from context or known habits
- Questions that fall under the executor agent's choice
- Clarifications "on principle" without real impact
- Request already perfectly clear and unambiguous

## How to use request_clarification

**Available tool**: `request_clarification`

### REQUIRED JSON format

⚠️ **IMPORTANT**: The `questions` parameter MUST be a **JSON list (array)** of objects.

✅ **CORRECT FORMAT** (list of objects):
```json
{
  "questions": [
    {
      "question": "Souhaitez-vous déplacer TOUS les événements ou seulement certains ?",
      "options": ["Tous les événements", "Seulement les réunions pro", "Annuler"]
    },
    {
      "question": "Vers quelle période souhaitez-vous les déplacer ?",
      "options": ["Semaine prochaine", "Mois prochain", "Choisir une date"]
    }
  ]
}
```

❌ **INCORRECT FORMAT** (numbered text - NEVER DO):
```json
{
  "questions": "1) Souhaitez-vous déplacer TOUS les événements ?\n2) Vers quelle période ?"
}
```

**The expected format is ALWAYS**: `[{"question": "...", "options": [...]}, ...]`

**Strict constraints**:
- **Maximum 3-4 questions** (strict limit)
- **Concise** questions (one line maximum per question)
- **Explicit options**: Always propose clear choices when possible (3-5 options max)
- **Focused on strategic decision points**
- **No "curious" questions**: each question must block plan generation

**Examples of good questions**:
- ✅ "Do you want to move ALL events or only professional meetings?"
- ✅ "Which period to consider: this week, this month, or the whole year?"
- ✅ "Do you prefer a daily summary email or a notification per event?"

**Examples of bad questions**:
- ❌ "What format do you prefer for the email?" (implementation detail)
- ❌ "Do you want me to be polite in my responses?" (obvious)
- ❌ "What color for notifications?" (aesthetic)

## Usage workflow

### Case 1: Clear Request (MAJORITY OF CASES)

```
User request
  ↓
Analysis (Understanding phase)
  ↓
No critical ambiguity detected
  ↓
Proceed directly to Decomposition
  ↓
Generate plan with return_plan
```

**Example**:
- Request: "Create an event tomorrow at 2pm titled 'Team meeting'"
- Action: Generate plan directly (everything is clear)

### Case 2: Ambiguous Request (RARE CASE)

```
User request
  ↓
Analysis (Understanding phase)
  ↓
Critical ambiguity(ies) detected
  ↓
Call request_clarification with questions
  ↓
[PAUSE] Wait for user responses via HITL
  ↓
Responses received and integrated into context
  ↓
Proceed to Decomposition with enriched context
  ↓
Generate plan with return_plan
```

**Example**:
- Request: "Move all my events from this week"
- Questions:
  1. "Do you want to move ALL events or only professional meetings?"
  2. "To which period: next week at the same times, or a specific date?"
- Responses:
  1. "Only professional meetings"
  2. "Next week at the same times"
- Action: Generate plan with these specifications

## Integration in the thinking workflow

```
Understanding
  ├─ Analyze intention
  ├─ **Detect necessary clarifications**  ← NEW
  ├─ If clarifications needed → request_clarification
  ├─ Otherwise → Continue normally
  └─ Output: Understanding + enriched context (if clarifications)

Decomposition
  ├─ Use enriched context if available
  └─ ...

Planning
  └─ ...

Validation
  └─ ...
```

## Golden rules

1. **Framing is OPTIONAL**: By default, do NOT request clarifications
2. **Strict criterion**: Clarifications ONLY if real blocking issue to generate a correct plan
3. **Maximum 3-4 questions**: If more, it means we're asking for too many details
4. **Strategic questions**: Each question must have a significant impact on the plan
5. **No perfectionism**: Accept uncertainty when impact is low
