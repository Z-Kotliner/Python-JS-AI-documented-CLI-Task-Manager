// javascript
// File: `task/main.js`
// This code was automatically ported from Python to JavaScript using GitHub Copilot.
// GitHub Copilot also documented the code for clarity.

// Task class: represents a single task in memory.
class Task {
  /**
   * @param {number} id - Internal session id for referencing the task.
   * @param {string} name - Task text.
   * @param {string} status - "Pending" or "Done".
   */
  constructor(id, name, status = "Pending") {
    this.id = id;
    this.name = name;
    this.status = status;
  }
}

// javascript
// TaskManager: manages tasks per day, saving/loading, and autosave behavior.
//
// Notes:
// - Persisted JSON uses a top-level mapping of capitalized day names -> [{task, status}, ...]
// - Internal numeric ids and taskId map are NOT exported to JSON.
const fs = require("fs");
const input = require("sync-input");

class TaskManager {
  constructor() {
    this.days = [
      "monday",
      "tuesday",
      "wednesday",
      "thursday",
      "friday",
      "saturday",
      "sunday",
      "general",
    ];
    // internal mapping: lowercase day -> array of Task instances
    this.dailyTasks = {};
    this.taskId = {};
    for (const d of this.days) {
      this.dailyTasks[d] = [];
      this.taskId[d] = 0;
    }
    // file used for autosave after save/load
    this.currentFile = null;
  }

  // Produce canonical JSON object (capitalized day keys) for saving.
  toDict() {
    const out = {};
    for (const d of this.days) {
      out[d.charAt(0).toUpperCase() + d.slice(1)] = this.dailyTasks[d].map((t) => ({
        task: t.name,
        status: t.status,
      }));
    }
    return out;
  }

  save(filename) {
    try {
      fs.writeFileSync(filename, JSON.stringify(this.toDict(), null, 2), "utf-8");
      this.currentFile = filename;
      console.log(`Saved to ${filename}`);
      return true;
    } catch (e) {
      console.log(`Failed to save file: ${e}`);
      return false;
    }
  }

  load(filename) {
    if (!fs.existsSync(filename)) {
      console.log(`File not found: ${filename}`);
      return false;
    }
    try {
      const raw = fs.readFileSync(filename, "utf-8");
      const data = JSON.parse(raw);
      // detect legacy wrapped format with 'daily_tasks' key
      if (data && typeof data === "object" && data.daily_tasks) {
        const daily = data.daily_tasks;
        // convert each day's tasks into Task objects, using provided ids if any
        this.dailyTasks = {};
        for (const d of this.days) {
          const list = daily[d] || [];
          this.dailyTasks[d] = list.map((t, i) => new Task(parseInt(t.id ?? i), t.name ?? "", t.status ?? "Pending"));
        }
        // rebuild taskId ignoring any stored task_id in file
        this.taskId = {};
        for (const d of this.days) {
          const maxId = this.dailyTasks[d].reduce((m, t) => Math.max(m, t.id), -1);
          this.taskId[d] = maxId + 1;
        }
      } else {
        // new canonical format: capitalized day keys -> [{task, status}, ...]
        this.dailyTasks = {};
        this.taskId = {};
        for (const d of this.days) {
          const keyCap = d.charAt(0).toUpperCase() + d.slice(1);
          const tasksList = (data && (data[keyCap] || data[d])) || [];
          this.dailyTasks[d] = [];
          let nextId = 0;
          for (const t of tasksList) {
            // support both {task, status} and legacy {name, status}
            const name = t.task ?? t.name ?? "";
            const status = t.status ?? "Pending";
            this.dailyTasks[d].push(new Task(nextId, name, status));
            nextId++;
          }
          this.taskId[d] = nextId;
        }
      }
      this.currentFile = filename;
      console.log(`Loaded from ${filename}`);
      return true;
    } catch (e) {
      console.log(`Failed to load file: ${e}`);
      return false;
    }
  }

  _autosave() {
    if (this.currentFile) {
      this.save(this.currentFile);
    }
  }

  // Add a task to a day (defaults to 'general' when day falsy)
  add(day, name, status = "Pending") {
    const dayKey = (day || "").toLowerCase() || "general";
    if (!this.dailyTasks[dayKey]) {
      this.dailyTasks[dayKey] = [];
      this.taskId[dayKey] = this.taskId[dayKey] || 0;
    }
    const id = this.taskId[dayKey];
    const task = new Task(id, name, status);
    this.dailyTasks[dayKey].push(task);
    this.taskId[dayKey] += 1;
    this._autosave();
    return task;
  }

  viewTasksPerDay(day) {
    const list = this.dailyTasks[day.toLowerCase()] || [];
    for (const t of list) {
      console.log(`${t.id}: ${t.name} - ${t.status}`);
    }
  }

  viewAllTask() {
    for (const d of this.days) {
      console.log(`${d.charAt(0).toUpperCase() + d.slice(1)}:`);
      for (const t of this.dailyTasks[d]) {
        console.log(`  ${t.id}: ${t.name} - ${t.status}`);
      }
    }
  }

  editTaskStatus(day, index, status) {
    const list = this.dailyTasks[day.toLowerCase()] || [];
    for (const t of list) {
      if (t.id === index) {
        t.status = status;
        this._autosave();
        return true;
      }
    }
    return false;
  }

  editTaskName(day, index, name) {
    const list = this.dailyTasks[day.toLowerCase()] || [];
    for (const t of list) {
      if (t.id === index) {
        t.name = name;
        this._autosave();
        break;
      }
    }
  }
}

// javascript
// Remaining CLI helpers and main loop for `task/main.js`.
//
// Uses sync-input to synchronously prompt user input in Node.
function promptDay() {
  while (true) {
    console.log("Enter day:");
    const day = input().trim().toLowerCase();
    if (["monday","tuesday","wednesday","thursday","friday","saturday","sunday","general",""].includes(day)) {
      return day;
    }
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

function promptFilename(defaultName = "tasks.json") {
  console.log(`Enter filename (default: ${defaultName}):`);
  const name = input("> ").trim();
  return name || defaultName;
}

// Handlers corresponding to Python implementation
function handleAdd(tm) {
  const day = promptDay();
  const name = promptTaskName();
  tm.add(day, name);
}

function handleEdit(tm) {
  const day = promptDay();
  const idx = promptIndex();
  const name = promptTaskName();
  tm.editTaskName(day, idx, name);
}

function handleDone(tm) {
  const day = promptDay();
  const idx = promptIndex();
  tm.editTaskStatus(day, idx, "Done");
}

function handleView(tm) {
  const day = promptDay();
  if (day === "") tm.viewAllTask();
  else tm.viewTasksPerDay(day);
}

function handleSave(tm) {
  const filename = promptFilename();
  tm.save(filename);
}

function handleLoad(tm) {
  const filename = promptFilename();
  tm.load(filename);
}

function acceptInput() {
  console.log("Enter command (add/edit/done/view/save/load/quit):");
  return input().toLowerCase();
}

function main() {
  const tm = new TaskManager();
  const handlers = {
    add: handleAdd,
    edit: handleEdit,
    done: handleDone,
    view: handleView,
    save: handleSave,
    load: handleLoad,
  };

  while (true) {
    const cmd = acceptInput();
    if (cmd === "quit") process.exit(0);
    const h = handlers[cmd];
    if (h) h(tm);
    else console.log("Invalid command");
  }
}

// If executed directly, start the CLI
if (require.main === module) {
  main();
}


//// Task class
//class Task {
//  constructor(id, name, status = TaskStatus.PENDING) {
//    this.id = id;
//    this.name = name;
//    this.status = status;
//  }
//}
//// TaskManager class
//class TaskManager {
//  constructor() {
//    this.days = [...DAYS];
//    this.dailyTasks = {};
//    this.taskId = {};
//    for (const d of this.days) {
//      this.dailyTasks[d] = [];
//      this.taskId[d] = 0;
//    }
//    this.currentFile = null;
//  }
//
//  toDict() {
//    // New format: top-level mapping with capitalized day names -> [{ task, status }, ...]
//    const out = {};
//    for (const day of this.days) {
//      const cap = day.charAt(0).toUpperCase() + day.slice(1);
//      out[cap] = (this.dailyTasks[day] || []).map(t => ({ task: t.name, status: t.status }));
//    }
//    return out;
//  }
//
//  save(filename) {
//    try {
//      fs.writeFileSync(filename, JSON.stringify(this.toDict(), null, 2), { encoding: 'utf8' });
//      this.currentFile = filename;
//      console.log(`Saved to ${filename}`);
//      return true;
//    } catch (e) {
//      console.log(`Failed to save file: ${e.message || e}`);
//      return false;
//    }
//  }
//
//  load(filename) {
//    if (!fs.existsSync(filename)) {
//      console.log(`File not found: ${filename}`);
//      return false;
//    }
//    try {
//      const raw = fs.readFileSync(filename, { encoding: 'utf8' });
//      const data = JSON.parse(raw || "{}");
//
//      // Detect old format with wrapper `daily_tasks`
//      if (data && typeof data === 'object' && data.daily_tasks) {
//        const daily = data.daily_tasks || {};
//        this.dailyTasks = {};
//        for (const d of this.days) {
//          const tasks = daily[d] || [];
//          this.dailyTasks[d] = (tasks || []).map(t => new Task(Number(t.id ?? 0), t.name ?? "", t.status ?? TaskStatus.PENDING));
//        }
//        // ensure all days exist
//        for (const d of this.days) {
//          if (!this.dailyTasks[d]) this.dailyTasks[d] = [];
//        }
//        // rebuild taskId map (ignore stored task_id)
//        this.taskId = {};
//        for (const d of this.days) {
//          const tasks = this.dailyTasks[d] || [];
//          const maxId = tasks.length ? Math.max(...tasks.map(t => Number(t.id))) : -1;
//          this.taskId[d] = maxId + 1;
//        }
//      } else {
//        // New format: top-level mapping of Capitalized day names -> [{task, status}, ...]
//        this.dailyTasks = {};
//        this.taskId = {};
//        for (const d of this.days) {
//          const cap = d.charAt(0).toUpperCase() + d.slice(1);
//          const tasksList = (data && (data[cap] || data[d])) || [];
//          this.dailyTasks[d] = [];
//          let nextId = 0;
//          for (const t of tasksList || []) {
//            const name = (t && typeof t === 'object') ? (t.task ?? t.name ?? "") : "";
//            const status = (t && typeof t === 'object') ? (t.status ?? TaskStatus.PENDING) : TaskStatus.PENDING;
//            this.dailyTasks[d].push(new Task(nextId, name, status));
//            nextId++;
//          }
//          this.taskId[d] = nextId;
//        }
//      }
//
//      this.currentFile = filename;
//      console.log(`Loaded from ${filename}`);
//      return true;
//    } catch (e) {
//      console.log(`Failed to load file: ${e.message || e}`);
//      return false;
//    }
//  }
//
//  _autosave() {
//    if (this.currentFile) this.save(this.currentFile);
//  }
//
//  add(day, name, status = TaskStatus.PENDING) {
//    const dayKey = (day || "").toLowerCase() || "general";
//    if (!(dayKey in this.dailyTasks)) {
//      this.dailyTasks[dayKey] = [];
//      this.taskId[dayKey] = this.taskId[dayKey] || 0;
//    }
//    const nextId = this.taskId[dayKey];
//    const task = new Task(nextId, name, status);
//    this.dailyTasks[dayKey].push(task);
//    this.taskId[dayKey] = nextId + 1;
//    this._autosave();
//    return task;
//  }
//
//  viewTasksPerDay(day) {
//    const dayKey = (day || "").toLowerCase() || "general";
//    const tasks = this.dailyTasks[dayKey] || [];
//    for (const task of tasks) {
//      console.log(`${task.id}: ${task.name} - ${task.status}`);
//    }
//  }
//
//  viewAllTask() {
//    for (const day of Object.keys(this.dailyTasks)) {
//      console.log(`${day.charAt(0).toUpperCase() + day.slice(1)}:`);
//      for (const task of this.dailyTasks[day]) {
//        console.log(`  ${task.id}: ${task.name} - ${task.status}`);
//      }
//    }
//  }
//
//  editTaskStatus(day, index, status) {
//    const dayKey = (day || "").toLowerCase() || "general";
//    const tasks = this.dailyTasks[dayKey] || [];
//    for (const task of tasks) {
//      if (task.id === index) {
//        task.status = status;
//        this._autosave();
//        return true;
//      }
//    }
//    return false;
//  }
//
//  editTaskName(day, taskId, name) {
//    const dayKey = (day || "").toLowerCase() || "general";
//    const tasks = this.dailyTasks[dayKey] || [];
//    for (const task of tasks) {
//      if (task.id === taskId) {
//        task.name = name;
//        this._autosave();
//        break;
//      }
//    }
//  }
//}
//// remaining helpers and main (place into `task/main.js`)
//const input = require('sync-input');
//const fs = require('fs');
//
//const DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "general"];
//const VALID_DAYS = new Set(DAYS);
//
//const TaskStatus = {
//  PENDING: "Pending",
//  DONE: "Done"
//};
//
//function promptDay(allowBlank = false) {
//  while (true) {
//    console.log(allowBlank ? "Enter day (or leave blank):" : "Enter day:");
//    const day = input().trim().toLowerCase();
//    if (day === "" && allowBlank) return "";
//    if (VALID_DAYS.has(day)) return day;
//  }
//}
//
//function promptIndex() {
//  while (true) {
//    console.log("Enter task index:");
//    const idx = input().trim();
//    if (/^\d+$/.test(idx)) return parseInt(idx, 10);
//    console.log("Invalid index. Please enter a number.");
//  }
//}
//
//function promptTaskName() {
//  console.log("Enter task:");
//  return input().trim();
//}
//
//function promptFilename(defaultName = "tasks.json") {
//  console.log(`Enter filename (default: ${defaultName}):`);
//  const name = input("> ").trim();
//  return name ? name : defaultName;
//}
//
//// handlers
//function handleAdd(taskManager) {
//  const day = promptDay();
//  const name = promptTaskName();
//  taskManager.add(day, name);
//}
//
//function handleEdit(taskManager) {
//  const day = promptDay();
//  const index = promptIndex();
//  const name = promptTaskName();
//  taskManager.editTaskName(day, index, name);
//}
//
//function handleDone(taskManager) {
//  const day = promptDay();
//  const index = promptIndex();
//  taskManager.editTaskStatus(day, index, TaskStatus.DONE);
//}
//
//function handleView(taskManager) {
//  const day = promptDay(true);
//  if (day === "") {
//    taskManager.viewAllTask();
//  } else {
//    taskManager.viewTasksPerDay(day);
//  }
//}
//
//function handleSave(taskManager) {
//  const filename = promptFilename();
//  taskManager.save(filename);
//}
//
//function handleLoad(taskManager) {
//  const filename = promptFilename();
//  taskManager.load(filename);
//}
//
//function acceptInput() {
//  console.log("Enter command (add/edit/done/view/save/load/quit):");
//  return input().trim().toLowerCase();
//}
//
//function main() {
//  const taskManager = new TaskManager();
//
//  const handlers = {
//    add: handleAdd,
//    edit: handleEdit,
//    done: handleDone,
//    view: handleView,
//    save: handleSave,
//    load: handleLoad
//  };
//
//  while (true) {
//    const command = acceptInput();
//    if (command === "quit") {
//      process.exit(0);
//    }
//    const handler = handlers[command];
//    if (handler) {
//      handler(taskManager);
//    } else {
//      console.log("Invalid command");
//    }
//  }
//}
//
//if (require.main === module) {
//  main();
//}
