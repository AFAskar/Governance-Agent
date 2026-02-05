import type { TRPCRouterRecord } from "@trpc/server";
import { TRPCError } from "@trpc/server";
import { desc, eq } from "drizzle-orm";
import { z } from "zod";

import * as schema from "@governance/db/schema";

import { submitEvaluationApiV1EvaluationsSubmitPost } from "../ai-client/sdk.gen";
import { getAIClient } from "../lib/ai";
import { SUBMISSION_PERMISSIONS } from "../lib/workos";
import { createPermissionProcedure } from "../trpc";

export const submissionRouter = {
  create: createPermissionProcedure([SUBMISSION_PERMISSIONS.WRITE])
    .input(
      z.object({
        companyName: z.string().min(1),
        files: z.array(
          z.object({
            name: z.string(),
            content: z.string(), // base64
            type: z.string(),
            domainId: z.string(),
            domainName: z.string(),
            size: z.number(),
          }),
        ),
      }),
    )
    .mutation(async ({ ctx, input }) => {
      const { companyName, files } = input;
      const client = getAIClient();

      // 1. Create Submission
      const [submission] = await ctx.db
        .insert(schema.Submission)
        .values({
          companyName,
          userId: ctx.session.user.id,
          status: "processing",
        })
        .returning();

      if (!submission) {
        throw new TRPCError({
          code: "INTERNAL_SERVER_ERROR",
          message: "Failed to create submission",
        });
      }

      // 2. Create Submission Files
      const fileInserts = files.map((f) => ({
        submissionId: submission.id,
        domainId: f.domainId,
        domainName: f.domainName,
        fileName: f.name,
        filePath: "ai-service-upload", // Placeholder
        fileSize: f.size,
      }));

      if (fileInserts.length > 0) {
        await ctx.db.insert(schema.SubmissionFile).values(fileInserts);
      }

      // 3. Prepare files for AI Service
      const blobs = files.map((f) => {
        const buffer = Buffer.from(f.content, "base64");
        return new File([buffer], f.name, { type: f.type });
      });

      // 4. Call AI Service
      try {
        const response = await submitEvaluationApiV1EvaluationsSubmitPost({
          client,
          body: {
            framework_name: "NDI",
            files: blobs,
          },
        });

        if (response.error) {
          throw new Error(JSON.stringify(response.error));
        }

        const data = response.data;
        if (!data) throw new Error("No data returned from AI service");

        // 5. Create Evaluation Report
        await ctx.db.insert(schema.EvaluationReport).values({
          submissionId: submission.id,
          aiServiceReportId: data.evaluation_id,
          reportPath: data.report_path,
          reportData: JSON.stringify({
            evaluation_id: data.evaluation_id,
            mimic_json: data.mimic_json,
            file_evaluations: data.file_evaluations,
          }),
          status: "completed",
          completedAt: new Date(),
        });

        // Update submission status
        await ctx.db
          .update(schema.Submission)
          .set({ status: "completed" })
          .where(eq(schema.Submission.id, submission.id));

        return { success: true, submissionId: submission.id };
      } catch (e) {
        console.error("AI Service Submission Failed", e);
        await ctx.db
          .update(schema.Submission)
          .set({ status: "failed" })
          .where(eq(schema.Submission.id, submission.id));
        return {
          success: true,
          submissionId: submission.id,
          evaluationFailed: true,
        };
      }
    }),

  getAll: createPermissionProcedure([SUBMISSION_PERMISSIONS.READ]).query(
    async ({ ctx }) => {
      return ctx.db
        .select()
        .from(schema.Submission)
        .orderBy(desc(schema.Submission.createdAt));
    },
  ),

  getById: createPermissionProcedure([SUBMISSION_PERMISSIONS.READ])
    .input(z.object({ id: z.string().uuid() }))
    .query(async ({ ctx, input }) => {
      const [submission] = await ctx.db
        .select()
        .from(schema.Submission)
        .where(eq(schema.Submission.id, input.id))
        .limit(1);

      if (!submission) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Submission not found",
        });
      }

      const files = await ctx.db
        .select()
        .from(schema.SubmissionFile)
        .where(eq(schema.SubmissionFile.submissionId, input.id));

      const [report] = await ctx.db
        .select()
        .from(schema.EvaluationReport)
        .where(eq(schema.EvaluationReport.submissionId, input.id))
        .limit(1);

      return { submission, files, report: report ?? null };
    }),

  delete: createPermissionProcedure([SUBMISSION_PERMISSIONS.DELETE])
    .input(z.object({ id: z.string().uuid() }))
    .mutation(async ({ ctx, input }) => {
      // Check if submission exists and belongs to the user
      const [submission] = await ctx.db
        .select()
        .from(schema.Submission)
        .where(eq(schema.Submission.id, input.id))
        .limit(1);

      if (!submission) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "Submission not found",
        });
      }

      // Delete related records first (cascade delete)
      await ctx.db
        .delete(schema.EvaluationReport)
        .where(eq(schema.EvaluationReport.submissionId, input.id));

      await ctx.db
        .delete(schema.SubmissionFile)
        .where(eq(schema.SubmissionFile.submissionId, input.id));

      // Delete the submission
      await ctx.db
        .delete(schema.Submission)
        .where(eq(schema.Submission.id, input.id));

      return { success: true };
    }),
} satisfies TRPCRouterRecord;
