/**
 * MathMentor AI — Mastery model (PROTOTYPE, front-end only)
 *
 * Placeholder data + in-memory store standing in for the secure per-student
 * database. Real version (after the Linux migration) will:
 *   - load the full topic/concept catalogue (~100 topics) from the backend
 *   - persist every attempt (steps attempted / steps correct / difficulty)
 *   - compute error rate = 1 - (correct steps / attempted steps)
 *   - mark topics & concepts above the global average error rate as "weak"
 *   - score mastery in [0,1] from low error rate + higher average difficulty
 *   - feed weak lists + level into the problem recommendation score
 *
 * TODO(real version): replace everything below with API calls.
 */

export type Level = "beginner" | "intermediate" | "advanced";

export const LEVELS: Level[] = ["beginner", "intermediate", "advanced"];

/** Mastery level ↔ problem difficulty used by the recommender. */
export const LEVEL_DIFFICULTY: Record<Level, 1 | 2 | 3> = {
  beginner: 1,
  intermediate: 2,
  advanced: 3,
};

export interface ConceptMastery {
  id: string;
  name: string;
  /** 0–1 float. */
  mastery: number;
  errorRate: number;
  avgDifficulty: number;
  attempts: number;
  weak: boolean;
}

export interface TopicMastery {
  id: string;
  name: string;
  level: Level;
  /** 0–1 float, rolled up from its concepts. */
  mastery: number;
  errorRate: number;
  avgDifficulty: number;
  attempts: number;
  weak: boolean;
  concepts: ConceptMastery[];
}

/** Placeholder catalogue — real topic/concept names come from the dataset. */
function placeholderTopic(n: number, conceptCount: number): TopicMastery {
  return {
    id: `topic-${n}`,
    name: `Topic ${n}`,
    level: "beginner",
    mastery: 0,
    errorRate: 0,
    avgDifficulty: 0,
    attempts: 0,
    weak: false,
    concepts: Array.from({ length: conceptCount }, (_, i) => ({
      id: `topic-${n}-concept-${i + 1}`,
      name: `Concept ${n}.${i + 1}`,
      mastery: 0,
      errorRate: 0,
      avgDifficulty: 0,
      attempts: 0,
      weak: false,
    })),
  };
}

/** In-memory store. TODO: replace with the student's secure database. */
let topics: TopicMastery[] = [
  placeholderTopic(1, 4),
  placeholderTopic(2, 3),
  placeholderTopic(3, 5),
  placeholderTopic(4, 3),
];

export function getTopics(): TopicMastery[] {
  return topics;
}

export function setTopicLevel(topicId: string, level: Level): TopicMastery[] {
  topics = topics.map((t) => (t.id === topicId ? { ...t, level } : t));
  return topics;
}

export interface MasteryDelta {
  scope: "topic" | "concept";
  name: string;
  old: number;
  next: number;
  delta: number;
}

/**
 * Record an attempt and return the old / new / delta mastery for the
 * problem's topic and concept.
 *
 * STUB: mastery = (1 - errorRate) * difficultyWeight, blended with history.
 * TODO(real version): backend computes this from the full attempt history.
 */
export function recordAttempt(params: {
  topicName: string;
  conceptName: string;
  difficulty: number;
  stepsAttempted: number;
  stepsCorrect: number;
}): MasteryDelta[] {
  const { conceptName, difficulty, stepsAttempted, stepsCorrect } = params;
  const errorRate =
    stepsAttempted > 0 ? 1 - stepsCorrect / stepsAttempted : 0;

  // Attach the attempt to the first placeholder topic/concept until the real
  // catalogue exists.
  const topic = topics[0];
  const concept = topic.concepts[0];

  const score = (1 - errorRate) * (0.6 + 0.4 * (Math.min(difficulty, 3) / 3));

  const conceptOld = concept.mastery;
  const topicOld = topic.mastery;

  const blend = (prev: number, n: number) =>
    Math.max(0, Math.min(1, n === 0 ? score : (prev * n + score) / (n + 1)));

  concept.attempts += 1;
  concept.errorRate =
    (concept.errorRate * (concept.attempts - 1) + errorRate) / concept.attempts;
  concept.avgDifficulty =
    (concept.avgDifficulty * (concept.attempts - 1) + difficulty) /
    concept.attempts;
  concept.mastery = blend(conceptOld, concept.attempts - 1);

  topic.attempts += 1;
  topic.errorRate =
    (topic.errorRate * (topic.attempts - 1) + errorRate) / topic.attempts;
  topic.avgDifficulty =
    (topic.avgDifficulty * (topic.attempts - 1) + difficulty) / topic.attempts;
  topic.mastery =
    topic.concepts.reduce((s, c) => s + c.mastery, 0) / topic.concepts.length;

  // Weak flags: above the average error rate across all attempted work.
  const attempted = topics.flatMap((t) =>
    t.concepts.filter((c) => c.attempts > 0)
  );
  const avgError =
    attempted.length > 0
      ? attempted.reduce((s, c) => s + c.errorRate, 0) / attempted.length
      : 0;
  topics.forEach((t) => {
    t.concepts.forEach((c) => {
      c.weak = c.attempts > 0 && c.errorRate > avgError;
    });
    t.weak = t.attempts > 0 && t.errorRate > avgError;
  });

  return [
    {
      scope: "topic",
      name: params.topicName || topic.name,
      old: topicOld,
      next: topic.mastery,
      delta: topic.mastery - topicOld,
    },
    {
      scope: "concept",
      name: conceptName || concept.name,
      old: conceptOld,
      next: concept.mastery,
      delta: concept.mastery - conceptOld,
    },
  ];
}
