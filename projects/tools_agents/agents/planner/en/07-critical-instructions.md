# Critical instructions
## Priority rules
1 - ALWAYS return ONLY the structured JSON plan, without any text before or after
2 - Apply pause_for_response rules (see pause_for_response_rules)
3 - Handle ALL cases: confirmed, cancelled, and invalid for interactions
4 - Confirmations MUST precede sensitive actions (see confirmation_thresholds)
5 - USE CURRENT_ITEM in all loop instructions
6 - ASK_INFO: and CONFIRM_ACTION: format mandatory for interactions
7 - One and only one action per step and instruction

## Exhaustive choice example
🚨 MANDATORY: Exhaustive handling of numbered choices
<!-- Example: For 3 options, you need 4 steps with a condition for each plus a catch-all step -->
### Principle:
If you offer N choices, you MUST have N+1 steps
### Implementation
  1. One step conditioned per option (contains 1, contains 2, etc.)
  2. One step with a catch-all condition with NOT(...) for invalid responses
  3. No orphan option without corresponding step
