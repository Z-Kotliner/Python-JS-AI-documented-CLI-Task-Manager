import json

from hstest import StageTest, CheckResult, dynamic_test, TestedProgram


class Feedback:
    task_msg = "Your output should contain the task added: "
    command_msg = "Your program should display the command option: "
    input_msg = "Your program should wait for user input."


class Test(StageTest):
    # Helper function to check if the program is waiting for input
    def check_waiting_input(self, program):
        if not program.is_waiting_input():
            return Feedback.input_msg

    def check_task(self, output, task, status):
        if "0" not in output:
            return "The task index should be 0."
        if task not in output:
            return Feedback.task_msg + "Task 1"
        if status == "done" and output.count("done") != 2:
            return "The task status should be: " + status
        if status not in output:
            return "The task status should be: " + status

    def check_file(self, filename, tasks):
        try:
            with open(filename, "r") as file:
                data = json.load(file)
                if data != tasks:
                    return (f"Tasks in {filename} are not saved correctly."
                            f"Expected: {tasks}, but got: {data}")
        except FileNotFoundError:
            return f"File not found: {filename}"
        except json.JSONDecodeError:
            return f"Error decoding JSON from file: {filename}"

    @dynamic_test
    def test1(self):
        main = TestedProgram(self.source_name)
        commands = ["add", "edit", "done", "view", "quit"]
        output = main.start()

        # check commands
        for command in commands:
            if command not in output:
                return CheckResult.wrong(Feedback.command_msg + command)

        # Execute commands and check for input waiting
        commands = ["add", "Monday", "Task 1", "view"]
        for command in commands:
            result = self.check_waiting_input(main)
            if result:
                return CheckResult.wrong(result)
            main.execute(command)

        # Check if the task was added correctly
        output = main.execute("Monday").strip().lower()
        result = self.check_task(output, "task 1", "pending")
        if result:
            return CheckResult.wrong(result)

        # Check if the task was marked as done
        commands = ["done", "Monday", "0", "view"]
        for command in commands:
            result = self.check_waiting_input(main)
            if result:
                return CheckResult.wrong(result)
            main.execute(command)

        output = main.execute("Monday").strip().lower()
        result = self.check_task(output, "task 1", "done")
        if result:
            return CheckResult.wrong(result)

        # Check if the task was edited correctly
        commands = ["edit", "Monday", "0", "First Task", "view"]
        for command in commands:
            result = self.check_waiting_input(main)
            if result:
                return CheckResult.wrong(result)
            main.execute(command)

        output = main.execute("Monday").strip().lower()
        result = self.check_task(output, "first task", "done")
        if result:
            return CheckResult.wrong(result)

        # Add new task and check if it was added correctly
        commands = ["add", "Friday", "Task 2", "view"]
        for command in commands:
            result = self.check_waiting_input(main)
            if result:
                return CheckResult.wrong(result)
            main.execute(command)

        # Check if the view all tasks command works
        output = main.execute("").strip().lower()
        if "first task" not in output:
            return CheckResult.wrong(Feedback.task_msg + "First Task")
        if "task 2" not in output:
            return CheckResult.wrong(Feedback.task_msg + "Task 2")

        # Check if the program saves the tasks correctly
        commands = ["save", "tasks.json"]
        for command in commands:
            result = self.check_waiting_input(main)
            if result:
                return CheckResult.wrong(result)
            main.execute(command)

        tasks = {
            "Monday": [{"task": "First Task", "status": "Done"}],
            "Tuesday": [],
            "Wednesday": [],
            "Thursday": [],
            "Friday": [{"task": "Task 2", "status": "Pending"}],
            "Saturday": [],
            "Sunday": [],
            "General": []
        }

        result = self.check_file("tasks.json", tasks)
        if result:
            return CheckResult.wrong(result)

        # Check if the program quits correctly
        result = self.check_waiting_input(main)
        if result:
            return CheckResult.wrong(result)
        main.execute("quit")

        if not main.is_finished():
            return CheckResult.wrong("Your program should exit after the quit command.")

        return CheckResult.correct()

    @dynamic_test
    def test2(self):
        main = TestedProgram(self.source_name)
        main.start()

        # Check if the tasks are loaded correctly
        commands = ["load", "tasks.json", "view"]
        for command in commands:
            result = self.check_waiting_input(main)
            if result:
                return CheckResult.wrong(result)
            main.execute(command)

        output = main.execute("").strip().lower()
        if "first task" not in output:
            return CheckResult.wrong(Feedback.task_msg + "First Task")
        if "task 2" not in output:
            return CheckResult.wrong(Feedback.task_msg + "Task 2")

        return CheckResult.correct()



if __name__ == '__main__':
    Test().run_tests()