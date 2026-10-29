import { pgTable, text, doublePrecision, boolean, timestamp, uuid } from "drizzle-orm/pg-core";

export const users = pgTable("users", {
  id: uuid().primaryKey().defaultRandom(),
  customId: text("custom_id").notNull().unique(),
  fullName: text("full_name").notNull(),
  email: text().notNull().unique(),
  passwordHash: text("password_hash").notNull(),
  role: text().notNull(),
});

export const subjects = pgTable("subjects", {
  id: uuid().primaryKey().defaultRandom(),
  name: text().notNull().unique(),
});

export const lessons = pgTable("lessons", {
  id: uuid().primaryKey().defaultRandom(),
  title: text().notNull(),
  contentUrl: text("content_url").notNull(),
});

export const quizResponses = pgTable("quiz_responses", {
  id: uuid().primaryKey().defaultRandom(),
  studentId: uuid("student_id").notNull().references(() => users.id, { onDelete: "cascade" }),
  subjectName: text("subject_name"),
  topicTag: text("topic_tag").notNull(),
  obtainedScore: doublePrecision("obtained_score").notNull().default(0),
  isCorrect: boolean("is_correct").notNull(),
  createdAt: timestamp("created_at").defaultNow(),
});

export const adaptiveLearningPaths = pgTable("adaptive_learning_paths", {
  id: uuid().primaryKey().defaultRandom(),
  studentId: uuid("student_id").notNull().references(() => users.id, { onDelete: "cascade" }),
  recommendedLessonId: uuid("recommended_lesson_id").references(() => lessons.id),
  weakTopicTag: text("weak_topic_tag").notNull(),
  confidenceScore: doublePrecision("confidence_score").notNull(),
  status: text().default("pending"),
  generatedAt: timestamp("generated_at").defaultNow(),
});
