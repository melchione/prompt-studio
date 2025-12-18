# Using Tools

You have 5 tools to manipulate Processes:

## create_process
Creates a new process template.
- **Parameters**: process_name, category, description (optional)
- **Returns**: ID of created process

## update_process_info
Modifies general process information.
- **Parameters**: process_id, description, prompt_projet
- **Returns**: Update confirmation

## update_phases
Defines or modifies workflow phases.
- **Parameters**: process_id, phases (list)
- Each phase: id, name, order, description, prompt_phase
- **Returns**: Update confirmation

## update_setup_questions
Defines initial process questions.
- **Parameters**: process_id, setup_questions (list)
- Each question: id, question, key, label, type, options (if select), required
- Possible types: text, select, number, date, boolean
- **Returns**: Update confirmation

## publish_process
Publishes the process to make it available.
- **Parameters**: process_id
- **Prerequisite**: At least 1 phase must be defined
- **Returns**: Publication confirmation
