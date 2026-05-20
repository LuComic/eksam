import { loadMaterials } from "$lib/data";
import { shuffle } from "$lib/random";
import { taskDisplayTitle } from "$lib/taskLabels";
import type { Exam, Mode, Task } from "$lib/types";

class AppState {
  mode = $state<Mode | "">("");
  showAnswer = $state(false);
  loading = $state(true);
  tasks = $state<Task[]>([]);
  exams = $state<Exam[]>([]);
  shuffledTasks = $state<Task[]>([]);
  currentIndex = $state(0);
  answerTasks = $state<Task[]>([]);
  searchInput = $state("");
  searchTerm = $state("");
  selectedExamYear = $state<number | "">("");
  expandedExamYears = $state<number[]>([]);

  hasTasks = $derived(this.tasks.length > 0);
  currentTask = $derived(this.shuffledTasks[this.currentIndex] ?? null);
  examYears = $derived(Array.from({ length: 19 }, (_, index) => 2025 - index));

  tasksByYear = $derived.by(() => {
    const groups = new Map<number, Task[]>();
    for (const task of this.tasks) {
      const group = groups.get(task.year) ?? [];
      group.push(task);
      groups.set(task.year, group);
    }
    for (const group of groups.values()) {
      group.sort((a, b) => a.part - b.part || a.taskNumber - b.taskNumber);
    }
    return groups;
  });

  searchResults = $derived.by(() => {
    const term = this.searchTerm.trim().toLowerCase();
    if (!term) return [];

    return this.tasks
      .filter((task) => {
        const searchable = [
          task.id,
          taskDisplayTitle(task),
          String(task.year),
          `part ${task.part}`,
          `task ${task.taskNumber}`,
          `${task.year} ${task.part} ${task.taskNumber}`,
        ]
          .join(" ")
          .toLowerCase();

        return searchable.includes(term);
      })
      .sort(
        (a, b) =>
          a.part - b.part || a.year - b.year || a.taskNumber - b.taskNumber,
      );
  });

  async load() {
    this.loading = true;
    const materials = await loadMaterials();
    this.tasks = materials.tasks;
    this.exams = materials.exams;
    this.loading = false;
  }

  resetSingleTask() {
    this.shuffledTasks = shuffle(this.tasks);
    this.currentIndex = 0;
    this.answerTasks = this.shuffledTasks[0] ? [this.shuffledTasks[0]] : [];
  }

  previousTask() {
    if (this.shuffledTasks.length === 0) return;
    this.currentIndex =
      (this.currentIndex - 1 + this.shuffledTasks.length) %
      this.shuffledTasks.length;
    this.answerTasks = this.currentTask ? [this.currentTask] : [];
  }

  nextTask() {
    if (this.shuffledTasks.length === 0) return;
    this.currentIndex = (this.currentIndex + 1) % this.shuffledTasks.length;
    this.answerTasks = this.currentTask ? [this.currentTask] : [];
  }

  search() {
    this.searchTerm = this.searchInput.trim();
  }

  goToExam(task: Task) {
    this.selectExamYear(task.year);
  }

  selectExamYear(year: number) {
    this.selectedExamYear = year;
    this.searchInput = "";
    this.searchTerm = "";
    this.mode = "exam";
  }

  toggleExamYear(year: number) {
    this.expandedExamYears = this.expandedExamYears.includes(year)
      ? this.expandedExamYears.filter((item) => item !== year)
      : [...this.expandedExamYears, year];
  }

  selectTask(task: Task) {
    this.shuffledTasks = [
      task,
      ...shuffle(this.tasks.filter((item) => item.id !== task.id)),
    ];
    this.currentIndex = 0;
    this.answerTasks = [task];
    this.selectedExamYear = "";
    this.searchInput = "";
    this.searchTerm = "";
    this.mode = "single-task";
  }

  changeMode(nextMode: Mode | "") {
    this.mode = nextMode;
    this.searchInput = "";
    this.searchTerm = "";
    if (nextMode !== "exam") {
      this.selectedExamYear = "";
    }
  }
}

export const appState = new AppState();
