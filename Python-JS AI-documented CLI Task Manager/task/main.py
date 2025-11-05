from dataclasses import dataclass
from enum import Enum
from typing import List, Dict

commands = ["add", "edit", "done", "view", "quit"]


class TaskStatus(str, Enum):
    PENDING = "Pending"
    DONE = "Done"


@dataclass
class Task():
    id: int
    name: str
    status: str = TaskStatus.PENDING


class TaskManager:
    def __init__(self):
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "general"]
        self.daily_tasks: Dict[str, List[Task]] = {day: [] for day in days}
        self.task_id: Dict[str, int] = {day: 0 for day in days}

    def add(self, day: str, name: str, status: TaskStatus = TaskStatus.PENDING) -> Task:
        day_key = day.lower()

        if day_key not in self.daily_tasks:
            self.daily_tasks[day_key] = []
            self.task_id.setdefault(day_key, 0)

        next_id = self.task_id[day_key]
        task = Task(next_id, name, status.value)
        self.daily_tasks[day_key].append(task)
        self.task_id[day_key] += 1

        return task

    def view_tasks_per_day(self, day: str):
        for task in self.daily_tasks[day.lower()]:
            print(f"{task.id}: {task.name} - {task.status}")

    def view_all_task(self):
        for day in self.daily_tasks:
            print(f"{day.capitalize()}:")
            for task in self.daily_tasks[day]:
                print(f"  {task.id}: {task.name} - {task.status}")

    def edit_task_status(self, day: str, index: int, status: TaskStatus) -> bool:
        task_list = self.daily_tasks[day.lower()]
        for task in task_list:
            if task.id == index:
                task.status = status.value
                return True
        return False

    def edit_task_name(self, day: str, task_id: int, name: str):
        task_list = self.daily_tasks[day.lower()]
        for task in task_list:
            if task.id == task_id:
                task.name = name
                break


def prompt_day() -> str:
    while True:
        print("Enter day:")
        day = input().strip().lower()
        if day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "general", ""]:
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


def accept_input() -> str:
    print("Enter command (add/edit/done/view/quit):")
    command = input().lower()
    return command


def main():
    task_manager = TaskManager()

    handlers = {
        "add": handle_add,
        "edit": handle_edit,
        "done": handle_done,
        "view": handle_view,
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
