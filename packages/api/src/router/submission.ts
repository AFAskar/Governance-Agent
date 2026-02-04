
import type { TRPCRouterRecord } from "@trpc/server";
import { TRPCError } from "@trpc/server";
import { z } from "zod";
import { eq, desc } from "drizzle-orm";
import { protectedProcedure } from "../trpc";
import { submitEvaluationApiV1EvaluationsSubmitPost } from "../ai-client/sdk.gen";
import { getAIClient } from "../lib/ai";
import { Submission, SubmissionFile, EvaluationReport } from "@governance/db/schema";

export const submissionRouter = {
    create: protectedProcedure
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
                    })
                ),
            })
        )
        .mutation(async ({ ctx, input }) => {
            const { companyName, files } = input;
            const client = getAIClient();

            // 1. Create Submission
            const [submission] = await ctx.db
                .insert(Submission)
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
                await ctx.db.insert(SubmissionFile).values(fileInserts);
            }

            // 3. Prepare files for AI Service
            const blobs = files.map((f) => {
                const buffer = Buffer.from(f.content, 'base64');
                return new File([buffer], f.name, { type: f.type });
            });

            // 4. Call AI Service
            try {
                const response = await submitEvaluationApiV1EvaluationsSubmitPost({
                    client,
                    body: {
                        framework_name: "NDI",
                        files: blobs,
                    }
                });

                if (response.error) {
                    // @ts-ignore
                    throw new Error(JSON.stringify(response.error));
                }

                const data = response.data;
                if (!data) throw new Error("No data returned from AI service");

                // 5. Create Evaluation Report
                await ctx.db.insert(EvaluationReport).values({
                    submissionId: submission.id,
                    aiServiceReportId: data.evaluation_id,
                    reportPath: data.report_path,
                    reportData: JSON.stringify(data.mimic_json),
                    status: "completed",
                    completedAt: new Date(),
                });

                // Update submission status
                await ctx.db.update(Submission)
                    .set({ status: "completed" })
                    .where(eq(Submission.id, submission.id));

                return { success: true, submissionId: submission.id };

            } catch (e) {
                console.error("AI Service Submission Failed", e);
                await ctx.db.update(Submission).set({ status: "failed" }).where(eq(Submission.id, submission.id));
                throw new TRPCError({
                    code: "INTERNAL_SERVER_ERROR",
                    message: "Failed to process submission with AI service",
                    cause: e
                });
            }
        }),

    getAll: protectedProcedure.query(async ({ ctx }) => {
        return ctx.db.select().from(Submission).orderBy(desc(Submission.createdAt));
    }),
} satisfies TRPCRouterRecord;
