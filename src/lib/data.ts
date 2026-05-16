import type { Exam, MaterialData, Task } from './types';

async function loadJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(path, { cache: 'no-store' });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

function isTaskArray(value: unknown): value is Task[] {
  return Array.isArray(value);
}

function isExamArray(value: unknown): value is Exam[] {
  return Array.isArray(value);
}

export async function loadMaterials(): Promise<MaterialData> {
  const [tasksJson, examsJson] = await Promise.all([
    loadJson<unknown>('/data/tasks.json'),
    loadJson<unknown>('/data/exams.json')
  ]);

  return {
    tasks: isTaskArray(tasksJson) ? tasksJson : [],
    exams: isExamArray(examsJson) ? examsJson : []
  };
}
