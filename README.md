# CLI Task Manager — Documentation

This project was done to demonstrate and apply the use of AI-assisted coding for code generation, code completion and code documentation.
GitHub Copilot was used for part of the code writing, especially for JSON file handling and Documentation generation.
It was also used to port the code from Python to JavaScript.
The part of this file below was also generated with the help of GitHub Copilot.

---

This document describes the Task Manager implemented in Python (`task/main.py`) and the ported JavaScript version (`task/main.js`). Both provide the same CLI behavior: add, edit, mark done, view, save to JSON, load from JSON, and quit. Saved JSON uses a top-level mapping of capitalized day names to lists of tasks (no wrapper like `daily_tasks` and no `task_id` export).

GitHub Copilot assisted in writing the JavaScript port based on the Python code.
---

## Quick Setup

Windows instructions.

Python
- Ensure Python 3.10+ is installed.
- No extra pip packages required for the Python script.
- Run:
  - Open a terminal (PowerShell or cmd)
  - `python task\main.py`

JavaScript (Node.js)
- Ensure Node.js and npm are installed.
- Install runtime dependency used by the CLI:
  - `npm install sync-input`
- Run:
  - `node task\main.js`

---

## CLI Usage

Prompt:
Enter command (add/edit/done/view/save/load/quit):

Available commands
- `add` — add a new task
  - Prompts:
    - `Enter day:` (one of monday..sunday or general; blank defaults to general)
    - `Enter task:`
- `edit` — rename a task
  - Prompts:
    - `Enter day:`
    - `Enter task index:` (numeric id)
    - `Enter task:`
- `done` — mark a task as Done
  - Prompts:
    - `Enter day:`
    - `Enter task index:`
- `view` — view tasks
  - Prompts:
    - `Enter day:` (leave blank to view all)
- `save` — write tasks to a JSON file
  - Prompt:
    - `Enter filename (default: tasks.json):`
  - Writes the canonical top-level JSON format (see below).
- `load` — load tasks from a JSON file
  - Prompt:
    - `Enter filename (default: tasks.json):`
  - Loads either the new top-level format or an older wrapped format (`daily_tasks`) — code detects and converts older format.
- `quit` — exit program

Autosave behavior
- After any mutating action (`add`, `edit`, `done`) the manager will automatically save to `current_file` if a file has been loaded or previously saved.

---

## JSON File Format (canonical / new)
Saved JSON is a top-level object mapping capitalized day names to an array of tasks. Each task is an object with keys `task` and `status`. Example:

    ```json
    {
      "Monday": [
        { "task": "First Task", "status": "Done" }
      ],
      "Tuesday": [],
      "Wednesday": [],
      "Thursday": [],
      "Friday": [
        { "task": "Task 2", "status": "Pending" }
      ],
      "Saturday": [],
      "Sunday": [],
      "General": []
    }