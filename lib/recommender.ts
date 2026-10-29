import { eq, ilike } from "drizzle-orm";
import { db } from "../db/index.js";
import { adaptiveLearningPaths, lessons, quizResponses } from "../db/schema.js";

// Flags topics where the student's accuracy is below 50% and stores a lesson recommendation for each.
export async function evaluateAndGenerateRecommendations(studentId: string) {
  const responses = await db.select().from(quizResponses).where(eq(quizResponses.studentId, studentId));
  if (responses.length === 0) return;

  const topics = new Map<string, { total: number; correct: number }>();
  for (const r of responses) {
    const t = topics.get(r.topicTag) ?? { total: 0, correct: 0 };
    t.total += 1;
    if (r.isCorrect) t.correct += 1;
    topics.set(r.topicTag, t);
  }

  await db.delete(adaptiveLearningPaths).where(eq(adaptiveLearningPaths.studentId, studentId));

  for (const [topic, { total, correct }] of topics) {
    const accuracy = correct / total;
    if (accuracy >= 0.5) continue;

    const weakTag = topic.trim().toLowerCase();
    let [lesson] = await db.select().from(lessons).where(ilike(lessons.title, `%${weakTag}%`)).limit(1);
    if (!lesson) {
      [lesson] = await db
        .insert(lessons)
        .values({
          title: `Masterclass on ${weakTag.toUpperCase()}`,
          contentUrl: `https://www.youtube.com/results?search_query=${encodeURIComponent(weakTag)}+programming+tutorial`,
        })
        .returning();
    }

    await db.insert(adaptiveLearningPaths).values({
      studentId,
      recommendedLessonId: lesson.id,
      weakTopicTag: weakTag,
      confidenceScore: Math.round((1 - accuracy) * 100) / 100,
      status: "pending",
    });
  }
}
