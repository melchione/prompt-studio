# Creation Process

When the user wants to create a new process, follow these steps:

## Step 1: Identification
- Ask for the process **name**
- Ask for the **category** (business domain: management, sales, hr, project, etc.)
- Propose a short **description**

## Step 2: Structure
- Propose 3-5 **phases** adapted to the domain
- Explain the objective of each phase
- Adjust based on user feedback

## Step 3: Initial Questions
- Define the **setup_questions** to collect information needed at startup
- Each question has: text, key (snake_case), type (text/select/number/date/boolean)

## Step 4: Prompts
- Write the **prompt_projet** (overall process context)
- Write the **prompt_phase** for each phase (specific instructions)

## Step 5: Publication
- Verify the process has at least 1 phase
- Publish the process to make it available
