import type { Task } from './types';

export function shuffle<T>(items: T[]): T[] {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j] as T, copy[i] as T];
  }
  return copy;
}

export function buildShuffleExam(tasks: Task[]): Task[] {
  const part1 = shuffle(tasks.filter((task) => task.part === 1)).slice(0, 7);
  const part2 = shuffle(tasks.filter((task) => task.part === 2)).slice(0, 5);
  const selected = [...part1, ...part2];
  const selectedIds = new Set(selected.map((task) => task.id));

  if (selected.length < 12) {
    for (const task of shuffle(tasks)) {
      if (selected.length >= 12) break;
      if (!selectedIds.has(task.id)) {
        selected.push(task);
        selectedIds.add(task.id);
      }
    }
  }

  return selected.sort((a, b) => a.part - b.part || a.taskNumber - b.taskNumber || a.year - b.year);
}
