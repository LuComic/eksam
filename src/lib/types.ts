export type Mode = 'single-task' | 'exam' | 'shuffle-exam';

export type ExamSource = 'projektid' | 'arhmus' | 'kool';

export type Exam = {
  year: number;
  source?: ExamSource;
  part1Pdf?: string;
  part2Pdf?: string;
  gradingPdf?: string;
  gradingDocx?: string;
  answerTablePdf?: string;
  formatNote?: string;
  sourcePageUrl: string;
};

export type CropBox = {
  x0: number;
  y0: number;
  x1: number;
  y1: number;
};

export type PageCrop = {
  page: number;
  crop: CropBox | null;
  image?: string;
};

export type Task = {
  id: string;
  year: number;
  source?: ExamSource;
  part: 1 | 2;
  taskNumber: number;
  title: string;
  sourcePdf: string;
  gradingPdf: string;
  taskPieces: PageCrop[];
  answerPieces: PageCrop[];
  taskImagePaths: string[];
  answerImagePaths: string[];
  points?: number;
  extractionConfidence: 'high' | 'medium' | 'low';
  needsReview: boolean;
};

export type MaterialData = {
  tasks: Task[];
  exams: Exam[];
};
