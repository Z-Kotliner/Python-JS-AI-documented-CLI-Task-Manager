// javascript
const input = require('sync-input');

const DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "general"];
const VALID_DAYS = new Set(DAYS);

// javascript
const TaskStatus = {
  PENDING: "Pending",
  DONE: "Done"
};


// javascript
class Task {
  constructor(id, name, status = TaskStatus.PENDING) {
    this.id = id;
    this.name = name;
    this.status = status;
  }
}


// javascript
class TaskManager {
  constructor() {
    this.days = [...DAYS];
    this.dailyTasks = {};
    this.taskId = {};
    for (const d of this.days) {
      this.dailyTasks[d] = [];
      this.taskId[d] = 0;
    }
  }

  add(day, name, status = TaskStatus.PENDING) {
    const dayKey = (day || "").toLowerCase() || "general";
    if (!(dayKey in this.dailyTasks)) {
      this.dailyTasks[dayKey] = [];
      this.taskId[dayKey] = 0;
    }
    const nextId = this.taskId[dayKey];
    const task = new Task(nextId, name, status);
    this.dailyTasks[dayKey].push(task);
    this.taskId[dayKey] = nextId + 1;
    return task;
  }

  viewTasksPerDay(day) {
    const dayKey = (day || "").toLowerCase() || "general";
    const tasks = this.dailyTasks[dayKey] || [];
    for (const task of tasks) {
      console.log(`${task.id}: ${task.name} - ${task.status}`);
    }
  }

  viewAllTask() {
    for (const day of Object.keys(this.dailyTasks)) {
      console.log(`${day.charAt(0).toUpperCase() + day.slice(1)}:`);
      for (const task of this.dailyTasks[day]) {
        console.log(`  ${task.id}: ${task.name} - ${task.status}`);
      }
    }
  }

  editTaskStatus(day, index, status) {
    const dayKey = (day || "").toLowerCase() || "general";
    const tasks = this.dailyTasks[dayKey] || [];
    for (const task of tasks) {
      if (task.id === index) {
        task.status = status;
        return true;
      }
    }
    return false;
  }

  editTaskName(day, taskId, name) {
    const dayKey = (day || "").toLowerCase() || "general";
    const tasks = this.dailyTasks[dayKey] || [];
    for (const task of tasks) {
      if (task.id === taskId) {
        task.name = name;
        break;
      }
    }
  }
}

// javascript
function promptDay(allowBlank = false) {
  while (true) {
    console.log(allowBlank ? "Enter day (or leave blank):" : "Enter day:");
    const day = input().trim().toLowerCase();
    if (day === "" && allowBlank) return "";
    if (VALID_DAYS.has(day)) return day;
    // if user types other keys, treat as unknown and re-prompt
  }
}

function promptIndex() {
  while (true) {
    console.log("Enter task index:");
    const idx = input().trim();
    if (/^\d+$/.test(idx)) return parseInt(idx, 10);
    console.log("Invalid index. Please enter a number.");
  }
}

function promptTaskName() {
  console.log("Enter task:");
  return input().trim();
}

function handleAdd(taskManager) {
  const day = promptDay();
  const name = promptTaskName();
  taskManager.add(day, name);
}

function handleEdit(taskManager) {
  const day = promptDay();
  const index = promptIndex();
  const name = promptTaskName();
  taskManager.editTaskName(day, index, name);
}

function handleDone(taskManager) {
  const day = promptDay();
  const index = promptIndex();
  taskManager.editTaskStatus(day, index, TaskStatus.DONE);
}

function handleView(taskManager) {
  const day = promptDay(true);
  if (day === "") {
    taskManager.viewAllTask();
  } else {
    taskManager.viewTasksPerDay(day);
  }
}

function acceptInput() {
  console.log("Enter command (add/edit/done/view/quit):");
  return input().trim().toLowerCase();
}

function main() {
  const taskManager = new TaskManager();

  const handlers = {
    add: handleAdd,
    edit: handleEdit,
    done: handleDone,
    view: handleView
  };

  while (true) {
    const command = acceptInput();
    if (command === "quit") {
      process.exit(0);
    }
    const handler = handlers[command];
    if (handler) {
      handler(taskManager);
    } else {
      console.log("Invalid command");
    }
  }
}

if (require.main === module) {
  main();
}



