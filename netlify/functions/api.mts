import type { Config } from "@netlify/functions";
import { asc, desc, eq, or, sql } from "drizzle-orm";
import { db } from "../../db/index.js";
import { adaptiveLearningPaths, quizResponses, subjects, users } from "../../db/schema.js";
import { generateMultilingualClasses, tutorReply } from "../../lib/content.js";
import { evaluateAndGenerateRecommendations } from "../../lib/recommender.js";
import { hashPassword, verifyPassword } from "../../lib/auth.js";

const PASS_MARK = 7.5;
const DEFAULT_STUDENT_PASSWORD = "123456";

class HttpError extends Error {
  constructor(public status: number, public detail: string) {
    super(detail);
  }
}

const str = (v: unknown) => (typeof v === "string" ? v : v == null ? "" : String(v));

async function readJson(req: Request): Promise<Record<string, unknown>> {
  try {
    return await req.json();
  } catch {
    throw new HttpError(400, "Invalid JSON body!");
  }
}

function findUserByIdentifier(identifier: string) {
  return db
    .select()
    .from(users)
    .where(or(eq(users.email, identifier.toLowerCase()), eq(users.customId, identifier)))
    .limit(1)
    .then((rows) => rows[0]);
}

async function findOrCreateStudent(customId: string) {
  const [existing] = await db.select().from(users).where(eq(users.customId, customId)).limit(1);
  if (existing) return existing;
  const [created] = await db
    .insert(users)
    .values({
      customId,
      fullName: `Student (${customId})`,
      email: `student_${customId}@edtech.com`,
      passwordHash: hashPassword(DEFAULT_STUDENT_PASSWORD),
      role: "student",
    })
    .returning();
  return created;
}

// Replaces the student's latest quiz record and refreshes their AI recommendations.
async function recordQuizScore(customId: string, subjectName: string, topic: string, score: number) {
  const student = await findOrCreateStudent(customId);
  await db.delete(quizResponses).where(eq(quizResponses.studentId, student.id));
  await db.delete(adaptiveLearningPaths).where(eq(adaptiveLearningPaths.studentId, student.id));
  await db.insert(quizResponses).values({
    studentId: student.id,
    subjectName,
    topicTag: topic,
    obtainedScore: score,
    isCorrect: score >= PASS_MARK,
  });
  await evaluateAndGenerateRecommendations(student.id);
}

function parseCsv(text: string): Record<string, string>[] {
  const lines = text.replace(/^﻿/, "").split(/\r?\n/).filter((l) => l.trim() !== "");
  if (lines.length === 0) return [];
  const splitLine = (line: string) => {
    const cells: string[] = [];
    let cur = "";
    let quoted = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (quoted) {
        if (ch === '"' && line[i + 1] === '"') { cur += '"'; i++; }
        else if (ch === '"') quoted = false;
        else cur += ch;
      } else if (ch === '"') quoted = true;
      else if (ch === ",") { cells.push(cur); cur = ""; }
      else cur += ch;
    }
    cells.push(cur);
    return cells.map((c) => c.trim());
  };
  const headers = splitLine(lines[0]);
  return lines.slice(1).map((line) => {
    const cells = splitLine(line);
    return Object.fromEntries(headers.map((h, i) => [h, cells[i] ?? ""]));
  });
}

// --- Route handlers ---

async function chatbot(req: Request) {
  const { message } = await readJson(req);
  return { reply: tutorReply(str(message)) };
}

async function createSubject(req: Request) {
  const name = str((await readJson(req)).subject_name).trim();
  if (!name) throw new HttpError(400, "Subject name is required!");
  const [existing] = await db.select().from(subjects).where(sql`lower(${subjects.name}) = lower(${name})`).limit(1);
  if (existing) throw new HttpError(400, "Subject already exists!");
  await db.insert(subjects).values({ name });
  return { message: `Subject '${name}' successfully created!` };
}

async function listSubjects() {
  const rows = await db.select().from(subjects).orderBy(asc(subjects.name));
  return rows.map((s) => ({ id: s.id, name: s.name }));
}

async function signup(req: Request) {
  const body = await readJson(req);
  const customId = str(body.custom_id).trim();
  const email = str(body.email).trim().toLowerCase();
  const password = str(body.password);
  const fullName = str(body.full_name).trim();
  const role = str(body.role).toLowerCase() === "teacher" ? "teacher" : "student";
  if (!customId || !email || !password || !fullName) throw new HttpError(400, "All fields are required!");

  const [byEmail] = await db.select().from(users).where(eq(users.email, email)).limit(1);
  if (byEmail) throw new HttpError(400, "Email already registered!");
  const [byId] = await db.select().from(users).where(eq(users.customId, customId)).limit(1);
  if (byId) throw new HttpError(400, "ID already registered!");

  await db.insert(users).values({ fullName, customId, email, passwordHash: hashPassword(password), role });
  return { message: `Account created for ID: ${customId}!` };
}

async function signin(req: Request) {
  const body = await readJson(req);
  const user = await findUserByIdentifier(str(body.email_or_id).trim());
  if (!user || !verifyPassword(str(body.password), user.passwordHash)) {
    throw new HttpError(401, "Invalid Credentials!");
  }
  return {
    message: "Login successful!",
    user: { id: user.id, custom_id: user.customId, full_name: user.fullName, email: user.email, role: user.role },
  };
}

async function resetPassword(req: Request) {
  const body = await readJson(req);
  const identifier = str(body.email_or_id).trim();
  const newPass = str(body.new_password).trim();
  if (!identifier || !newPass) throw new HttpError(400, "দয়া করে আইডি/ইমেইল এবং নতুন পাসওয়ার্ড প্রদান করুন!");

  const user = await findUserByIdentifier(identifier);
  if (!user) throw new HttpError(404, "এই আইডি বা ইমেইল দিয়ে কোনো অ্যাকাউন্ট পাওয়া যায়নি!");

  await db.update(users).set({ passwordHash: hashPassword(newPass) }).where(eq(users.id, user.id));
  return { message: "পাসওয়ার্ড সফলভাবে পরিবর্তন করা হয়েছে! নতুন পাসওয়ার্ড দিয়ে লগইন করুন।" };
}

async function submitQuiz(req: Request) {
  const body = await readJson(req);
  const customId = str(body.student_custom_id).trim();
  const topic = str(body.topic_tag).trim().toLowerCase();
  const subject = str(body.subject_name).trim() || "General Subject";
  const score = Number(body.obtained_score);
  if (!customId || !topic) throw new HttpError(400, "Student ID and topic are required!");
  if (!Number.isFinite(score) || score < 0 || score > 15) throw new HttpError(422, "Score must be between 0 and 15!");

  await recordQuizScore(customId, subject, topic, score);
  return { message: `Score ${score}/15 for '${topic.toUpperCase()}' saved & AI updated!` };
}

async function uploadBulkQuiz(req: Request) {
  const form = await req.formData().catch(() => null);
  const file = form?.get("file");
  if (!file || typeof file === "string") throw new HttpError(400, "Please upload a CSV file!");
  if (!file.name.toLowerCase().endsWith(".csv")) throw new HttpError(400, "Only .csv files are supported!");

  const rows = parseCsv(await file.text());
  const headers = rows.length ? Object.keys(rows[0]) : [];
  for (const col of ["student_id", "subject", "topic", "score"]) {
    if (!headers.includes(col)) throw new HttpError(400, `CSV file must contain column: '${col}'`);
  }

  let successCount = 0;
  for (const row of rows) {
    const customId = row.student_id.trim();
    const score = Number(row.score);
    if (!customId || !Number.isFinite(score)) continue;
    await recordQuizScore(customId, row.subject.trim(), row.topic.trim().toLowerCase(), score);
    successCount++;
  }
  return { message: `Successfully processed ${successCount} student scores from CSV and updated AI recommendations!` };
}

async function studentDashboard(customId: string) {
  const [student] = await db.select().from(users).where(eq(users.customId, customId)).limit(1);
  if (!student) return { student_name: `Student (${customId})`, quiz_info: null, recommendations: [] };

  const [quiz] = await db
    .select()
    .from(quizResponses)
    .where(eq(quizResponses.studentId, student.id))
    .orderBy(desc(quizResponses.createdAt))
    .limit(1);
  const [rec] = await db
    .select()
    .from(adaptiveLearningPaths)
    .where(eq(adaptiveLearningPaths.studentId, student.id))
    .orderBy(desc(adaptiveLearningPaths.generatedAt))
    .limit(1);

  const quizInfo = quiz
    ? {
        subject_name: quiz.subjectName,
        topic_tag: quiz.topicTag.toUpperCase(),
        obtained_score: quiz.obtainedScore,
        status: quiz.isCorrect ? "PASS" : "NEEDS REVISION (WEAK)",
      }
    : null;

  const recommendations = rec
    ? [
        {
          id: rec.id,
          weak_topic: rec.weakTopicTag,
          confidence_score: rec.confidenceScore,
          recommended_videos: generateMultilingualClasses(rec.weakTopicTag.toLowerCase().trim(), quiz?.subjectName ?? ""),
          status: rec.status,
        },
      ]
    : [];

  return { student_name: student.fullName, student_id: student.customId, quiz_info: quizInfo, recommendations };
}

async function teacherSummary() {
  const all = await db.select().from(quizResponses);
  if (all.length === 0) {
    return { total_students: 0, avg_score: 0, pass_count: 0, fail_count: 0, subject_weakness: {} };
  }
  const totalStudents = new Set(all.map((q) => q.studentId)).size;
  const avgScore = Math.round((all.reduce((s, q) => s + q.obtainedScore, 0) / all.length) * 100) / 100;
  const passCount = all.filter((q) => q.obtainedScore >= PASS_MARK).length;
  const subjectWeakness: Record<string, number> = {};
  for (const q of all) {
    if (q.obtainedScore < PASS_MARK) {
      const subj = q.subjectName ?? "General Subject";
      subjectWeakness[subj] = (subjectWeakness[subj] ?? 0) + 1;
    }
  }
  return {
    total_students: totalStudents,
    avg_score: avgScore,
    pass_count: passCount,
    fail_count: all.length - passCount,
    subject_weakness: subjectWeakness,
  };
}

async function studentHistory(customId: string) {
  const [student] = await db.select().from(users).where(eq(users.customId, customId)).limit(1);
  if (!student) return { history: [] };
  const quizzes = await db
    .select()
    .from(quizResponses)
    .where(eq(quizResponses.studentId, student.id))
    .orderBy(asc(quizResponses.createdAt));
  return {
    history: quizzes.map((q) => ({
      topic: q.topicTag.toUpperCase(),
      subject: q.subjectName,
      score: q.obtainedScore,
      date: q.createdAt ? q.createdAt.toLocaleDateString("en-US", { month: "short", day: "2-digit" }) : "Quiz",
    })),
  };
}

// --- Router ---

async function route(req: Request): Promise<unknown> {
  const path = new URL(req.url).pathname.replace(/^\/api/, "").replace(/\/+$/, "");
  const method = req.method;

  if (method === "POST" && path === "/ai/chatbot") return chatbot(req);
  if (path === "/subjects") {
    if (method === "GET") return listSubjects();
    if (method === "POST") return createSubject(req);
  }
  if (method === "POST" && path === "/auth/signup") return signup(req);
  if (method === "POST" && path === "/auth/signin") return signin(req);
  if (method === "POST" && path === "/auth/reset-password") return resetPassword(req);
  if (method === "POST" && path === "/teacher/submit-quiz") return submitQuiz(req);
  if (method === "POST" && path === "/teacher/upload-bulk-quiz") return uploadBulkQuiz(req);
  if (method === "GET" && path === "/analytics/teacher-summary") return teacherSummary();

  const dashboard = path.match(/^\/dashboard\/custom\/([^/]+)$/);
  if (method === "GET" && dashboard) return studentDashboard(decodeURIComponent(dashboard[1]).trim());
  const history = path.match(/^\/analytics\/student-history\/([^/]+)$/);
  if (method === "GET" && history) return studentHistory(decodeURIComponent(history[1]).trim());

  throw new HttpError(404, "Not Found");
}

export default async (req: Request) => {
  try {
    return Response.json(await route(req));
  } catch (err) {
    if (err instanceof HttpError) return Response.json({ detail: err.detail }, { status: err.status });
    console.error(err);
    return Response.json({ detail: "Internal server error" }, { status: 500 });
  }
};

export const config: Config = {
  path: "/api/*",
};
