# python
# File: `task/main.py`
# CLI Task Manager with per-day tasks, status, and JSON persistence.
# GitHub Copilot assisted in writing and documentation this code.

# Standard library imports
import json
import os
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict

# Valid commands accepted by the CLI
commands = ["add", "edit", "done", "view", "save", "load", "quit"]

# python
# Enum representing task status values.
class TaskStatus(str, Enum):
    # Pending when task is not completed.
    PENDING = "Pending"
    # Done when task has been completed.
    DONE = "Done"

# python
# Data model for a single task stored in memory.
# id: internal numeric identifier used in-session for edit/done operations.
# name: the user-visible task text.
# status: string representation using TaskStatus values.
@dataclass
class Task:
    id: int
    name: str
    status: str = TaskStatus.PENDING.value

# python
# TaskManager: holds tasks per day and provides persistence and CLI actions.
class TaskManager:
    def __init__(self):
        # internal keys are lowercase day names plus 'general'
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
            "general",
        ]
        # mapping day -> list[Task]
        self.daily_tasks: Dict[str, List[Task]] = {day: [] for day in days}
        # next id to assign per day (internal only; not saved)
        self.task_id: Dict[str, int] = {day: 0 for day in days}
        # file path used for autosave (set after save/load)
        self.current_file: str | None = None

    def to_dict(self) -> Dict:
        """
        Produce the canonical JSON structure for saving:
        top-level mapping of capitalized day names -> list of { 'task', 'status' }.
        Note: internal ids and task_id map are intentionally NOT exported.
        """
        return {
            day.capitalize(): [
                {"task": t.name, "status": t.status} for t in tasks
            ]
            for day, tasks in self.daily_tasks.items()
        }

    def save(self, filename: str) -> bool:
        """Write the canonical JSON to filename and set current_file for autosave."""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2)
            self.current_file = filename
            print(f"Saved to {filename}")
            return True
        except Exception as e:
            print(f"Failed to save file: {e}")
            return False

    def load(self, filename: str) -> bool:
        """
        Load tasks from filename.
        Supports two formats:
        - New canonical format: top-level mapping of capitalized day names -> [{task,status}, ...]
        - Legacy wrapper: { 'daily_tasks': { day: [ {id,name,status}, ... ] }, 'task_id': {...} }
          The loader converts legacy format into internal Task objects and rebuilds internal ids.
        """
        if not os.path.exists(filename):
            print(f"File not found: {filename}")
            return False
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Detect legacy wrapped format
            if isinstance(data, dict) and "daily_tasks" in data:
                # convert older structure into internal Task objects
                daily = data.get("daily_tasks", {})
                self.daily_tasks = {
                    day: [Task(int(t.get("id", i)), t.get("name", ""), t.get("status", TaskStatus.PENDING.value))
                          for i, t in enumerate(tasks)]
                    for day, tasks in daily.items()
                }
                # ensure all expected days exist
                for d in [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                    "general",
                ]:
                    self.daily_tasks.setdefault(d, [])
                # rebuild task_id mapping from actual task ids (ignore stored 'task_id')
                self.task_id = {}
                for d in self.daily_tasks:
                    max_id = max((t.id for t in self.daily_tasks[d]), default=-1)
                    self.task_id[d] = max_id + 1
            else:
                # New format: top-level capitalized day keys -> list of {task, status}
                self.daily_tasks = {}
                days = [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                    "general",
                ]
                for d in days:
                    key_cap = d.capitalize()
                    # accept either capitalized keys or lowercase keys for compatibility
                    tasks_list = data.get(key_cap, data.get(d, [])) if isinstance(data, dict) else []
                    self.daily_tasks[d] = []
                    next_id = 0
                    for t in tasks_list or []:
                        # t is expected to be dict with 'task' and 'status'
                        name = t.get("task") if isinstance(t, dict) else None
                        status = t.get("status") if isinstance(t, dict) else TaskStatus.PENDING.value
                        if name is None:
                            # fallback for older key name 'name'
                            name = t.get("name") if isinstance(t, dict) else ""
                        # assign sequential ids starting at 0 per day
                        self.daily_tasks[d].append(Task(next_id, name, status))
                        next_id += 1
                    # next id after loading
                    self.task_id[d] = next_id
            self.current_file = filename
            print(f"Loaded from {filename}")
            return True
        except Exception as e:
            print(f"Failed to load file: {e}")
            return False

    def _autosave(self):
        """Autosave to current_file if set (called after mutating actions)."""
        if self.current_file:
            self.save(self.current_file)

    def add(self, day: str, name: str, status: TaskStatus = TaskStatus.PENDING) -> Task:
        """Add a new task to the given day (default 'general') and autosave."""
        day_key = (day or "").lower() or "general"

        if day_key not in self.daily_tasks:
            # create day if unknown and initialise id counter
            self.daily_tasks[day_key] = []
            self.task_id.setdefault(day_key, 0)

        next_id = self.task_id[day_key]
        task = Task(next_id, name, status.value)
        self.daily_tasks[day_key].append(task)
        self.task_id[day_key] += 1

        self._autosave()
        return task

    def view_tasks_per_day(self, day: str):
        """Print tasks for a single day (ids shown are internal session ids)."""
        for task in self.daily_tasks.get(day.lower(), []):
            print(f"{task.id}: {task.name} - {task.status}")

    def view_all_task(self):
        """Print tasks for all days, grouped by day."""
        for day in self.daily_tasks:
            print(f"{day.capitalize()}:")
            for task in self.daily_tasks[day]:
                print(f"  {task.id}: {task.name} - {task.status}")

    def edit_task_status(self, day: str, index: int, status: TaskStatus) -> bool:
        """Mark a task (by internal id) as Done or Pending and autosave. Returns True if found."""
        task_list = self.daily_tasks.get(day.lower(), [])
        for task in task_list:
            if task.id == index:
                task.status = status.value
                self._autosave()
                return True
        return False

    def edit_task_name(self, day: str, task_id: int, name: str):
        """Rename a task identified by its internal id and autosave."""
        task_list = self.daily_tasks.get(day.lower(), [])
        for task in task_list:
            if task.id == task_id:
                task.name = name
                self._autosave()
                break

# python
# Remaining CLI helpers and main loop with brief comments.
def prompt_day() -> str:
    """Prompt the user for a day; accept blank for 'general'."""
    while True:
        print("Enter day:")
        day = input().strip().lower()
        if day in [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
            "general",
            "",
        ]:
            return day


def prompt_index() -> int:
    """Prompt until a numeric task index is entered."""
    while True:
        print("Enter task index:")
        idx = input().strip()
        if idx.isdigit():
            return int(idx)
        print("Invalid index. Please enter a number.")


def prompt_task_name() -> str:
    """Prompt for the task text."""
    print("Enter task:")
    return input().strip()


def prompt_filename(default: str = "tasks.json") -> str:
    """Prompt for a filename, returning a default when input is blank."""
    print(f"Enter filename (default: {default}):")
    name = input("> ").strip()
    return name if name else default


# Handlers delegate to TaskManager methods; kept simple for CLI flow.
def handle_add(task_manager: TaskManager):
    day = prompt_day()
    name = prompt_task_name()
    task_manager.add(day, name)


def handle_edit(task_manager: TaskManager):
    day = prompt_day()
    index = prompt_index()
    name = prompt_task_name()
    task_manager.edit_task_name(day, index, name)


def handle_done(task_manager: TaskManager):
    day = prompt_day()
    index = prompt_index()
    task_manager.edit_task_status(day, index, TaskStatus.DONE)


def handle_view(task_manager: TaskManager):
    day = prompt_day()
    if day == "":
        task_manager.view_all_task()
    else:
        task_manager.view_tasks_per_day(day)


def handle_save(task_manager: TaskManager):
    filename = prompt_filename()
    task_manager.save(filename)


def handle_load(task_manager: TaskManager):
    filename = prompt_filename()
    task_manager.load(filename)


def accept_input() -> str:
    """Prompt the user for a command and return it lowercased."""
    print("Enter command (add/edit/done/view/save/load/quit):")
    command = input().lower()
    return command


def main():
    """Main REPL loop creating TaskManager and dispatching commands."""
    task_manager = TaskManager()

    handlers = {
        "add": handle_add,
        "edit": handle_edit,
        "done": handle_done,
        "view": handle_view,
        "save": handle_save,
        "load": handle_load,
    }

    while True:
        command = accept_input()
        if command == "quit":
            exit(0)
        handler = handlers.get(command)
        if handler:
            handler(task_manager)
        else:
            print("Invalid command")


if __name__ == "__main__":
    main()
