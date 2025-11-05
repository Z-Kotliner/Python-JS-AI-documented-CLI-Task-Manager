# python
import json
import os
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict

commands = ["add", "edit", "done", "view", "save", "load", "quit"]


class TaskStatus(str, Enum):
    PENDING = "Pending"
    DONE = "Done"


@dataclass
class Task:
    id: int
    name: str
    status: str = TaskStatus.PENDING.value


class TaskManager:
    def __init__(self):
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
        self.daily_tasks: Dict[str, List[Task]] = {day: [] for day in days}
        self.task_id: Dict[str, int] = {day: 0 for day in days}
        self.current_file: str | None = None

    def to_dict(self) -> Dict:
        # Save as top-level mapping: 'Monday': [ {'task': ..., 'status': ...}, ... ]
        return {
            day.capitalize(): [
                {"task": t.name, "status": t.status} for t in tasks
            ]
            for day, tasks in self.daily_tasks.items()
        }

    def save(self, filename: str) -> bool:
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
        if not os.path.exists(filename):
            print(f"File not found: {filename}")
            return False
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Detect old format (wrapped) vs new top-level mapping
            if isinstance(data, dict) and "daily_tasks" in data:
                # old format: keep previous behavior but convert to internal Task objects
                daily = data.get("daily_tasks", {})
                self.daily_tasks = {
                    day: [Task(int(t.get("id", i)), t.get("name", ""), t.get("status", TaskStatus.PENDING.value))
                          for i, t in enumerate(tasks)]
                    for day, tasks in daily.items()
                }
                # ensure all days exist
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
                # rebuild task_id map (ignore stored task_id if present)
                self.task_id = {}
                for d in self.daily_tasks:
                    max_id = max((t.id for t in self.daily_tasks[d]), default=-1)
                    # ensure sequential ids starting after max existing id
                    # if some ids are missing, keep next id = max_id + 1
                    self.task_id[d] = max_id + 1
            else:
                # new format: top-level mapping of capitalized day names to list of {task, status}
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
                    tasks_list = data.get(key_cap, data.get(d, [])) if isinstance(data, dict) else []
                    self.daily_tasks[d] = []
                    next_id = 0
                    for t in tasks_list or []:
                        name = t.get("task") if isinstance(t, dict) else None
                        status = t.get("status") if isinstance(t, dict) else TaskStatus.PENDING.value
                        if name is None:
                            # support legacy dicts that may use other keys
                            name = t.get("name") if isinstance(t, dict) else ""
                        self.daily_tasks[d].append(Task(next_id, name, status))
                        next_id += 1
                    self.task_id[d] = next_id
            self.current_file = filename
            print(f"Loaded from {filename}")
            return True
        except Exception as e:
            print(f"Failed to load file: {e}")
            return False

    def _autosave(self):
        if self.current_file:
            self.save(self.current_file)

    def add(self, day: str, name: str, status: TaskStatus = TaskStatus.PENDING) -> Task:
        day_key = (day or "").lower() or "general"

        if day_key not in self.daily_tasks:
            self.daily_tasks[day_key] = []
            self.task_id.setdefault(day_key, 0)

        next_id = self.task_id[day_key]
        task = Task(next_id, name, status.value)
        self.daily_tasks[day_key].append(task)
        self.task_id[day_key] += 1

        self._autosave()
        return task

    def view_tasks_per_day(self, day: str):
        for task in self.daily_tasks.get(day.lower(), []):
            print(f"{task.id}: {task.name} - {task.status}")

    def view_all_task(self):
        for day in self.daily_tasks:
            print(f"{day.capitalize()}:")
            for task in self.daily_tasks[day]:
                print(f"  {task.id}: {task.name} - {task.status}")

    def edit_task_status(self, day: str, index: int, status: TaskStatus) -> bool:
        task_list = self.daily_tasks.get(day.lower(), [])
        for task in task_list:
            if task.id == index:
                task.status = status.value
                self._autosave()
                return True
        return False

    def edit_task_name(self, day: str, task_id: int, name: str):
        task_list = self.daily_tasks.get(day.lower(), [])
        for task in task_list:
            if task.id == task_id:
                task.name = name
                self._autosave()
                break


def prompt_day() -> str:
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
    while True:
        print("Enter task index:")
        idx = input().strip()
        if idx.isdigit():
            return int(idx)
        print("Invalid index. Please enter a number.")


def prompt_task_name() -> str:
    print("Enter task:")
    return input().strip()


def prompt_filename(default: str = "tasks.json") -> str:
    print(f"Enter filename (default: {default}):")
    name = input("> ").strip()
    return name if name else default


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
    print("Enter command (add/edit/done/view/save/load/quit):")
    command = input().lower()
    return command


def main():
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
