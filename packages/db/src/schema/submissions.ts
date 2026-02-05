import {
  integer,
  pgTable,
  text,
  timestamp,
  uuid,
  varchar,
} from "drizzle-orm/pg-core";
import { createInsertSchema, createSelectSchema } from "drizzle-zod";
import { z } from "zod/v4";

// Submission status enum
export const submissionStatus = [
  "pending",
  "processing",
  "completed",
  "failed",
] as const;

// Main submissions table
export const Submission = pgTable("submission", (t) => ({
  id: t.uuid().notNull().primaryKey().defaultRandom(),
  companyName: t.varchar({ length: 255 }).notNull(),
  userId: t.varchar({ length: 255 }).notNull(), // WorkOS user ID
  status: t.varchar({ length: 50 }).notNull().default("pending"),
  createdAt: t.timestamp().defaultNow().notNull(),
  updatedAt: t.timestamp().defaultNow().notNull(),
}));

// Submission files table - stores uploaded files per domain
export const SubmissionFile = pgTable("submission_file", (t) => ({
  id: t.uuid().notNull().primaryKey().defaultRandom(),
  submissionId: t
    .uuid()
    .notNull()
    .references(() => Submission.id, { onDelete: "cascade" }),
  domainId: t.varchar({ length: 100 }).notNull(),
  domainName: t.varchar({ length: 255 }).notNull(),
  fileName: t.varchar({ length: 255 }).notNull(),
  filePath: t.text().notNull(),
  fileSize: t.integer().notNull(),
  uploadedAt: t.timestamp().defaultNow().notNull(),
}));

// Evaluation reports table - stores AI service evaluation results
export const EvaluationReport = pgTable("evaluation_report", (t) => ({
  id: t.uuid().notNull().primaryKey().defaultRandom(),
  submissionId: t
    .uuid()
    .notNull()
    .references(() => Submission.id, { onDelete: "cascade" }),
  aiServiceReportId: t.varchar({ length: 255 }),
  reportPath: t.text(),
  reportData: t.text(), // JSON string of evaluation results
  status: t.varchar({ length: 50 }).notNull().default("pending"),
  completedAt: t.timestamp(),
  createdAt: t.timestamp().defaultNow().notNull(),
}));

// Zod schemas for validation
export const CreateSubmissionSchema = createInsertSchema(Submission, {
  companyName: z
    .string()
    .min(2, "Company name must be at least 2 characters")
    .max(255),
}).omit({
  id: true,
  status: true,
  createdAt: true,
  updatedAt: true,
});

export const CreateSubmissionFileSchema = createInsertSchema(SubmissionFile, {
  domainId: z.string().min(2).max(100),
  domainName: z.string().min(2).max(255),
  fileName: z.string().min(1).max(255),
  fileSize: z.number().positive(),
}).omit({
  id: true,
  uploadedAt: true,
});

export const SelectSubmissionSchema = createSelectSchema(Submission);
export const SelectSubmissionFileSchema = createSelectSchema(SubmissionFile);
export const SelectEvaluationReportSchema =
  createSelectSchema(EvaluationReport);

// Type exports
export type Submission = typeof Submission.$inferSelect;
export type NewSubmission = typeof Submission.$inferInsert;
export type SubmissionFile = typeof SubmissionFile.$inferSelect;
export type NewSubmissionFile = typeof SubmissionFile.$inferInsert;
export type EvaluationReport = typeof EvaluationReport.$inferSelect;
export type NewEvaluationReport = typeof EvaluationReport.$inferInsert;
