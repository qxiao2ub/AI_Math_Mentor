/**
 * MathMentor AI — Problem Bank (prototype)
 *
 * Skeleton dataset standing in for the real problem database.
 * Real columns TBD by the dataset the user provides later; for now:
 *   id               — unique problem id
 *   problemText      — the problem shown to the student
 *   concept          — the concept tested (shown in feedback)
 *   groundTruthSteps — reference solution steps used for comparison
 *   difficulty       — placeholder for mastery-based selection (1-5)
 */

export interface Problem {
  id: string;
  problemText: string;
  concept: string;
  groundTruthSteps: string[];
  difficulty: 1 | 2 | 3 | 4 | 5;
}

export const problemBank: Problem[] = [
  {
    id: "alg-quad-001",
    problemText: "Solve for x: 3x² − 12x + 9 = 0",
    concept: "Factoring quadratics",
    groundTruthSteps: [
      "3(x² − 4x + 3) = 0",
      "3(x − 1)(x − 3) = 0",
      "x = 1 or x = 3",
    ],
    difficulty: 2,
  },
  {
    id: "alg-lin-001",
    problemText: "Solve for y: 2y + 6 = 14",
    concept: "Linear equations",
    groundTruthSteps: ["2y = 14 − 6", "2y = 8", "y = 4"],
    difficulty: 1,
  },
  {
    id: "alg-sys-001",
    problemText: "Solve the system: x + y = 7 and x − y = 1",
    concept: "Systems of equations",
    groundTruthSteps: ["Add the equations: 2x = 8", "x = 4", "y = 7 − 4 = 3"],
    difficulty: 2,
  },
];

/** Pick a problem at random. Later: select based on the student's mastery. */
export function pickRandomProblem(): Problem {
  return problemBank[Math.floor(Math.random() * problemBank.length)];
}
