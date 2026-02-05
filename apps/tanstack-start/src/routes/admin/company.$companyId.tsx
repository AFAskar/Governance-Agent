import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { createFileRoute, Link, redirect } from "@tanstack/react-router";
import { getAuth } from "@workos/authkit-tanstack-react-start";
import { toast } from "@governance/ui/toast";

import { NDI_DOMAINS } from "~/lib/ndi-domains";
import { useTRPC } from "~/lib/trpc";
import { hasPermission, SUBMISSION_PERMISSIONS } from "~/lib/permissions";

export const Route = createFileRoute("/admin/company/$companyId")({
  beforeLoad: async () => {
    const auth = await getAuth();
    
    // Check if user is authenticated
    if (!auth.user) {
      throw redirect({ to: "/" });
    }
    
    // Check if user has read permission
    if (!hasPermission(auth.permissions, SUBMISSION_PERMISSIONS.READ)) {
      throw redirect({ 
        to: "/",
        search: { error: "insufficient_permissions" }
      });
    }
  },
  component: RouteComponent,
});

// --- Types for parsed evaluation data ---
interface ControlDecision {
  control_id: string;
  decision: string;
  rationale: string;
}

interface FileEvaluation {
  file_index: number;
  field_id: string;
  control_decisions: ControlDecision[];
  summary: string;
}

interface ReportData {
  evaluation_id?: string;
  mimic_json?: Record<string, unknown>;
  file_evaluations?: FileEvaluation[];
}

// --- Score helpers ---
const SCORE_MAP: Record<string, number> = {
  leader: 6,
  excellent: 5,
  good: 4,
  fair: 3,
  low: 2,
  unacceptable: 1,
  compliant: 6,
  "not compliant": 1,
};

function getScore(decision: string): number {
  return SCORE_MAP[decision.toLowerCase()] ?? 0;
}

function getDecisionColor(decision: string): string {
  const d = decision.toLowerCase();
  if (["leader", "excellent", "good", "compliant"].includes(d))
    return "bg-ndmo-green text-white";
  if (d === "fair") return "bg-ndmo-yellow text-white";
  return "bg-ndmo-red text-white";
}

function getDecisionIcon(decision: string): string {
  const d = decision.toLowerCase();
  if (["leader", "excellent", "good", "compliant"].includes(d)) return "pass";
  if (d === "fair") return "warn";
  return "fail";
}

// --- Main Component ---
function RouteComponent() {
  const { companyId } = Route.useParams();
  const trpc = useTRPC();
  const { data, isLoading, error, refetch } = useQuery(
    trpc.submission.getById.queryOptions({ id: companyId }),
  );

  const rerunEvaluation = useMutation(
    trpc.submission.rerunEvaluation.mutationOptions(),
  );

  const [isRerunning, setIsRerunning] = useState(false);

  const handleRerun = async () => {
    try {
      setIsRerunning(true);
      toast.info("Starting evaluation...");
      
      await rerunEvaluation.mutateAsync({ id: companyId });
      
      toast.success("Evaluation completed successfully!");
      await refetch();
    } catch (err) {
      console.error("Rerun failed:", err);
      const errorMessage = err instanceof Error ? err.message : "Failed to rerun evaluation";
      toast.error(errorMessage);
    } finally {
      setIsRerunning(false);
    }
  };

  if (isLoading) {
    return (
      <main className="container mx-auto px-4 py-12">
        <div className="text-ndmo-gray-medium py-16 text-center">
          Loading report...
        </div>
      </main>
    );
  }

  if (error || !data) {
    return (
      <main className="container mx-auto px-4 py-12">
        <div className="py-16 text-center">
          <p className="text-ndmo-red mb-4">Failed to load submission</p>
          <p className="text-ndmo-gray-medium mb-4 text-sm">{error?.message}</p>
          <Link
            to="/admin/ndi"
            className="text-ndmo-blue-medium hover:underline"
          >
            Back to Submissions
          </Link>
        </div>
      </main>
    );
  }

  const { submission, files, report } = data;

  // Parse report data
  let reportData: ReportData | null = null;
  try {
    reportData = report?.reportData ? JSON.parse(report.reportData) : null;
  } catch {
    reportData = null;
  }

  const fileEvaluations = reportData?.file_evaluations ?? [];

  // Map evaluations to domains: match files[i] -> fileEvaluations[i] by index
  // Then group by domainId
  const evalsByDomain: Record<
    string,
    { decisions: ControlDecision[]; summaries: string[] }
  > = {};

  files.forEach((file, index) => {
    const evaluation = fileEvaluations[index];
    if (!evaluation) return;
    if (!evalsByDomain[file.domainId]) {
      evalsByDomain[file.domainId] = { decisions: [], summaries: [] };
    }
    evalsByDomain[file.domainId]!.decisions.push(
      ...evaluation.control_decisions,
    );
    if (evaluation.summary) {
      evalsByDomain[file.domainId]!.summaries.push(evaluation.summary);
    }
  });

  // Calculate overall score
  const allDecisions = Object.values(evalsByDomain).flatMap((e) => e.decisions);
  const overallScore =
    allDecisions.length > 0
      ? allDecisions.reduce((sum, d) => sum + getScore(d.decision), 0) /
        (allDecisions.length * 6)
      : 0;

  // Group files by domain
  const filesByDomain = files.reduce<Record<string, typeof files>>((acc, f) => {
    if (!acc[f.domainId]) acc[f.domainId] = [];
    acc[f.domainId]!.push(f);
    return acc;
  }, {});

  const domainsWithFiles = NDI_DOMAINS.filter((d) => filesByDomain[d.id]);
  const domainsWithoutFiles = NDI_DOMAINS.filter((d) => !filesByDomain[d.id]);
  const hasEvaluations = fileEvaluations.length > 0;

  const statusColors: Record<string, string> = {
    completed: "bg-ndmo-green",
    processing: "bg-ndmo-yellow",
    pending: "bg-ndmo-gray-medium",
    failed: "bg-ndmo-red",
  };

  return (
    <main className="container mx-auto px-4 py-12">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <Link
            to="/admin/ndi"
            className="text-ndmo-blue-medium hover:text-ndmo-blue-dark mb-4 inline-flex items-center gap-2"
          >
            <svg
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Back to Submissions
          </Link>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-ndmo-blue-dark mb-2 text-4xl font-bold">
                {submission.companyName}
              </h1>
              <p className="text-ndmo-gray-medium">NDI Assessment Report</p>
            </div>
            {report?.reportPath && (
              <button className="bg-ndmo-blue-medium hover:bg-ndmo-blue-dark flex items-center gap-2 rounded-lg px-6 py-3 font-semibold text-white transition-colors">
                <svg
                  className="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                Download PDF
              </button>
            )}
          </div>
        </div>

        {/* Summary Card */}
        <div className="from-ndmo-blue-medium to-ndmo-blue-dark mb-8 rounded-2xl bg-gradient-to-br p-8 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="mb-2 text-2xl font-bold">Submission Details</h2>
              <p className="text-ndmo-blue-pale">
                Submitted: {new Date(submission.createdAt).toLocaleDateString()}
              </p>
              <p className="text-ndmo-blue-pale">
                Files uploaded: {files.length}
              </p>
              <p className="text-ndmo-blue-pale">
                Domains covered: {domainsWithFiles.length} /{" "}
                {NDI_DOMAINS.length}
              </p>
            </div>
            <div className="space-y-2 text-center">
              <span
                className={`rounded-full px-4 py-2 text-sm font-bold tracking-wide text-white uppercase ${statusColors[submission.status] ?? statusColors.pending}`}
              >
                {submission.status}
              </span>
              {hasEvaluations && (
                <div className="mt-3">
                  <div className="text-4xl font-bold">
                    {Math.round(overallScore * 100)}%
                  </div>
                  <div className="text-ndmo-blue-pale text-sm">
                    Overall Score
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Notice when evaluation failed or pending */}
        {!hasEvaluations && (
          <div
            className={`mb-6 rounded-xl border p-6 ${submission.status === "failed" ? "border-red-200 bg-red-50" : "border-yellow-200 bg-yellow-50"}`}
          >
            <div className="flex items-start gap-3">
              <svg
                className={`mt-0.5 h-6 w-6 flex-shrink-0 ${submission.status === "failed" ? "text-ndmo-red" : "text-ndmo-yellow"}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <div className="flex-1">
                <h3
                  className={`font-semibold ${submission.status === "failed" ? "text-red-800" : "text-yellow-800"}`}
                >
                  {submission.status === "failed"
                    ? "AI Evaluation Failed"
                    : submission.status === "processing"
                      ? "Evaluation In Progress"
                      : "Evaluation Pending"}
                </h3>
                <p
                  className={`mt-1 text-sm ${submission.status === "failed" ? "text-red-700" : "text-yellow-700"}`}
                >
                  {submission.status === "failed"
                    ? "The AI service could not evaluate this submission. Your uploaded files have been saved. Please try submitting again when the AI service is available."
                    : submission.status === "processing"
                      ? "The AI service is currently evaluating this submission. Please check back shortly."
                      : "This submission is waiting to be evaluated."}
                </p>
                
                {/* Rerun Button - only show for failed submissions */}
                {submission.status === "failed" && (
                  <button
                    onClick={handleRerun}
                    disabled={isRerunning}
                    className="mt-4 bg-ndmo-blue-medium hover:bg-ndmo-blue-dark disabled:bg-ndmo-gray-medium flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-white transition-colors disabled:cursor-not-allowed"
                  >
                    {isRerunning ? (
                      <>
                        <svg
                          className="h-4 w-4 animate-spin"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                          />
                        </svg>
                        Rerunning Evaluation...
                      </>
                    ) : (
                      <>
                        <svg
                          className="h-4 w-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                          />
                        </svg>
                        Rerun Evaluation
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Domain Evaluations */}
        <div className="mb-6 rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="text-ndmo-blue-dark mb-6 text-2xl font-bold">
            {hasEvaluations ? "Domain Evaluations" : "Submitted Domains"}
          </h2>

          <div className="space-y-4">
            {domainsWithFiles.map((domain) => {
              const domainFiles = filesByDomain[domain.id] ?? [];
              const domainEval = evalsByDomain[domain.id];
              return (
                <DomainCard
                  key={domain.id}
                  domain={domain}
                  files={domainFiles}
                  evaluation={domainEval}
                />
              );
            })}
          </div>

          {domainsWithoutFiles.length > 0 && (
            <div className="mt-6 border-t pt-6">
              <h3 className="text-ndmo-gray-dark mb-3 font-semibold">
                Domains Not Submitted
              </h3>
              <div className="grid grid-cols-2 gap-2 md:grid-cols-3">
                {domainsWithoutFiles.map((domain) => (
                  <div
                    key={domain.id}
                    className="text-ndmo-gray-medium bg-ndmo-gray-light/50 rounded px-3 py-2 text-sm"
                  >
                    {domain.order}. {domain.name}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

// --- Domain Card Component ---
interface DomainCardProps {
  domain: (typeof NDI_DOMAINS)[number];
  files: {
    id: string;
    fileName: string;
    fileSize: number;
    domainId: string;
  }[];
  evaluation?: { decisions: ControlDecision[]; summaries: string[] };
}

function DomainCard({ domain, files, evaluation }: DomainCardProps) {
  const [expanded, setExpanded] = useState(false);

  const decisions = evaluation?.decisions ?? [];
  const summaries = evaluation?.summaries ?? [];
  const hasEval = decisions.length > 0;

  // Score for this domain
  const domainScore =
    decisions.length > 0
      ? decisions.reduce((sum, d) => sum + getScore(d.decision), 0) /
        (decisions.length * 6)
      : 0;

  const passCount = decisions.filter((d) => {
    const icon = getDecisionIcon(d.decision);
    return icon === "pass";
  }).length;
  const failCount = decisions.filter((d) => {
    const icon = getDecisionIcon(d.decision);
    return icon === "fail";
  }).length;
  const warnCount = decisions.length - passCount - failCount;

  return (
    <div className="overflow-hidden rounded-lg border">
      {/* Domain Header */}
      <div className="p-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-ndmo-blue-medium flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-sm font-bold text-white">
              {domain.order}
            </div>
            <div>
              <h3 className="text-ndmo-blue-dark font-semibold">
                {domain.name}
              </h3>
              <span className="text-ndmo-gray-medium text-xs">
                {files.length} file{files.length !== 1 ? "s" : ""}
                {hasEval && ` · ${decisions.length} controls evaluated`}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {hasEval && (
              <>
                {/* Score */}
                <div className="mr-2 text-right">
                  <div className="text-ndmo-blue-dark text-lg font-bold">
                    {Math.round(domainScore * 100)}%
                  </div>
                  <div className="flex gap-1 text-xs">
                    {passCount > 0 && (
                      <span className="text-ndmo-green">{passCount} pass</span>
                    )}
                    {warnCount > 0 && (
                      <span className="text-ndmo-yellow">{warnCount} fair</span>
                    )}
                    {failCount > 0 && (
                      <span className="text-ndmo-red">{failCount} fail</span>
                    )}
                  </div>
                </div>

                {/* More Details Button */}
                <button
                  onClick={() => setExpanded(!expanded)}
                  className="border-ndmo-blue-medium text-ndmo-blue-medium hover:bg-ndmo-blue-pale rounded-lg border px-4 py-2 text-sm font-medium transition-colors"
                >
                  {expanded ? "Hide Details" : "More Details"}
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Expanded Details */}
      {expanded && hasEval && (
        <div className="bg-ndmo-gray-light/30 border-t p-5">
          {/* AI Summary */}
          {summaries.length > 0 && (
            <div className="mb-5">
              <h4 className="text-ndmo-blue-dark mb-2 text-sm font-semibold">
                AI Assessment Summary
              </h4>
              {summaries.map((summary, i) => (
                <p
                  key={i}
                  className="text-ndmo-gray-dark mb-2 text-sm leading-relaxed"
                >
                  {summary}
                </p>
              ))}
            </div>
          )}

          {/* Control Decisions Checklist */}
          <h4 className="text-ndmo-blue-dark mb-3 text-sm font-semibold">
            Control Evaluations
          </h4>
          <div className="space-y-2">
            {decisions.map((decision, i) => {
              const icon = getDecisionIcon(decision.decision);
              return (
                <div key={i} className="rounded-lg border bg-white p-4">
                  <div className="flex items-start gap-3">
                    {/* Status Icon */}
                    <div className="mt-0.5 flex-shrink-0">
                      {icon === "pass" && (
                        <svg
                          className="text-ndmo-green h-5 w-5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                      )}
                      {icon === "warn" && (
                        <svg
                          className="text-ndmo-yellow h-5 w-5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
                          />
                        </svg>
                      )}
                      {icon === "fail" && (
                        <svg
                          className="text-ndmo-red h-5 w-5"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                      )}
                    </div>

                    {/* Content */}
                    <div className="min-w-0 flex-1">
                      <div className="mb-1 flex items-center gap-2">
                        <span className="text-ndmo-blue-dark font-mono text-sm font-semibold">
                          {decision.control_id}
                        </span>
                        <span
                          className={`rounded px-2 py-0.5 text-xs font-semibold ${getDecisionColor(decision.decision)}`}
                        >
                          {decision.decision}
                        </span>
                      </div>
                      <p className="text-ndmo-gray-dark text-sm leading-relaxed">
                        {decision.rationale}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
