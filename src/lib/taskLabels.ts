import type { Task } from "$lib/types";

export function hasCombinedQuestionAnswerTips(task: Task) {
  return task.source === "kool" && task.year === 2007;
}

export function taskDisplayTitle(task: Task) {
  if (!hasCombinedQuestionAnswerTips(task)) return task.title;
  if (task.title.includes("(question + answer and tips)")) return task.title;
  return `${task.title} (question + answer and tips)`;
}
