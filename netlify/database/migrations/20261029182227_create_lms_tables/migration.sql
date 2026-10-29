CREATE TABLE "adaptive_learning_paths" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"student_id" uuid NOT NULL,
	"recommended_lesson_id" uuid,
	"weak_topic_tag" text NOT NULL,
	"confidence_score" double precision NOT NULL,
	"status" text DEFAULT 'pending',
	"generated_at" timestamp DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "lessons" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"title" text NOT NULL,
	"content_url" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "quiz_responses" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"student_id" uuid NOT NULL,
	"subject_name" text,
	"topic_tag" text NOT NULL,
	"obtained_score" double precision DEFAULT 0 NOT NULL,
	"is_correct" boolean NOT NULL,
	"created_at" timestamp DEFAULT now()
);
--> statement-breakpoint
CREATE TABLE "subjects" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"name" text NOT NULL UNIQUE
);
--> statement-breakpoint
CREATE TABLE "users" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	"custom_id" text NOT NULL UNIQUE,
	"full_name" text NOT NULL,
	"email" text NOT NULL UNIQUE,
	"password_hash" text NOT NULL,
	"role" text NOT NULL
);
--> statement-breakpoint
ALTER TABLE "adaptive_learning_paths" ADD CONSTRAINT "adaptive_learning_paths_student_id_users_id_fkey" FOREIGN KEY ("student_id") REFERENCES "users"("id") ON DELETE CASCADE;--> statement-breakpoint
ALTER TABLE "adaptive_learning_paths" ADD CONSTRAINT "adaptive_learning_paths_recommended_lesson_id_lessons_id_fkey" FOREIGN KEY ("recommended_lesson_id") REFERENCES "lessons"("id");--> statement-breakpoint
ALTER TABLE "quiz_responses" ADD CONSTRAINT "quiz_responses_student_id_users_id_fkey" FOREIGN KEY ("student_id") REFERENCES "users"("id") ON DELETE CASCADE;