import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useTRPC } from "~/lib/trpc";
import { NDI_DOMAINS } from "~/lib/ndi-domains";

export const Route = createFileRoute("/admin/company/$companyId")({
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

function getMaxScore(decision: string): number {
  const d = decision.toLowerCase();
  if (d === "compliant" || d === "not compliant") return 6;
  return 6; // scale max is Leader = 6
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
  const { data, isLoading, error } = useQuery(
    trpc.submission.getById.queryOptions({ id: companyId }),
  );

  if (isLoading) {
    return (
      <main className="container mx-auto px-4 py-12">
        <div className="text-center py-16 text-ndmo-gray-medium">
          Loading report...
        </div>
      </main>
    );
  }

  if (error || !data) {
    return (
      <main className="container mx-auto px-4 py-12">
        <div className="text-center py-16">
          <p className="text-ndmo-red mb-4">Failed to load submission</p>
          <p className="text-sm text-ndmo-gray-medium mb-4">
            {error?.message}
          </p>
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
  const allDecisions = Object.values(evalsByDomain).flatMap(
    (e) => e.decisions,
  );
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
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link
            to="/admin/ndi"
            className="text-ndmo-blue-medium hover:text-ndmo-blue-dark mb-4 inline-flex items-center gap-2"
          >
            <svg
              className="w-4 h-4"
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
              <h1 className="text-4xl font-bold text-ndmo-blue-dark mb-2">
                {submission.companyName}
              </h1>
              <p className="text-ndmo-gray-medium">NDI Assessment Report</p>
            </div>
            {report?.reportPath && (
              <button className="bg-ndmo-blue-medium hover:bg-ndmo-blue-dark text-white px-6 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2">
                <svg
                  className="w-5 h-5"
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
        <div className="bg-gradient-to-br from-ndmo-blue-medium to-ndmo-blue-dark rounded-2xl p-8 mb-8 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">Submission Details</h2>
              <p className="text-ndmo-blue-pale">
                Submitted:{" "}
                {new Date(submission.createdAt).toLocaleDateString()}
              </p>
              <p className="text-ndmo-blue-pale">
                Files uploaded: {files.length}
              </p>
              <p className="text-ndmo-blue-pale">
                Domains covered: {domainsWithFiles.length} /{" "}
                {NDI_DOMAINS.length}
              </p>
            </div>
            <div className="text-center space-y-2">
              <span
                className={`px-4 py-2 rounded-full text-sm font-bold uppercase tracking-wide text-white ${statusColors[submission.status] ?? statusColors.pending}`}
              >
                {submission.status}
              </span>
              {hasEvaluations && (
                <div className="mt-3">
                  <div className="text-4xl font-bold">
                    {Math.round(overallScore * 100)}%
                  </div>
                  <div className="text-sm text-ndmo-blue-pale">
                    Overall Score
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Notice when evaluation failed or pending */}
        {!hasEvaluations && (
          <div className={`rounded-xl p-6 mb-6 border ${submission.status === "failed" ? "bg-red-50 border-red-200" : "bg-yellow-50 border-yellow-200"}`}>
            <div className="flex items-start gap-3">
              <svg className={`w-6 h-6 flex-shrink-0 mt-0.5 ${submission.status === "failed" ? "text-ndmo-red" : "text-ndmo-yellow"}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 className={`font-semibold ${submission.status === "failed" ? "text-red-800" : "text-yellow-800"}`}>
                  {submission.status === "failed"
                    ? "AI Evaluation Failed"
                    : submission.status === "processing"
                      ? "Evaluation In Progress"
                      : "Evaluation Pending"}
                </h3>
                <p className={`text-sm mt-1 ${submission.status === "failed" ? "text-red-700" : "text-yellow-700"}`}>
                  {submission.status === "failed"
                    ? "The AI service could not evaluate this submission. Your uploaded files have been saved. Please try submitting again when the AI service is available."
                    : submission.status === "processing"
                      ? "The AI service is currently evaluating this submission. Please check back shortly."
                      : "This submission is waiting to be evaluated."}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Domain Evaluations */}
        <div className="bg-white rounded-xl p-6 shadow-sm border mb-6">
          <h2 className="text-2xl font-bold text-ndmo-blue-dark mb-6">
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
            <div className="mt-6 pt-6 border-t">
              <h3 className="font-semibold text-ndmo-gray-dark mb-3">
                Domains Not Submitted
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {domainsWithoutFiles.map((domain) => (
                  <div
                    key={domain.id}
                    className="text-sm text-ndmo-gray-medium bg-ndmo-gray-light/50 rounded px-3 py-2"
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
    <div className="border rounded-lg overflow-hidden">
      {/* Domain Header */}
      <div className="p-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-ndmo-blue-medium text-white flex items-center justify-center font-bold text-sm">
              {domain.order}
            </div>
            <div>
              <h3 className="font-semibold text-ndmo-blue-dark">
                {domain.name}
              </h3>
              <span className="text-xs text-ndmo-gray-medium">
                {files.length} file{files.length !== 1 ? "s" : ""}
                {hasEval && ` · ${decisions.length} controls evaluated`}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {hasEval && (
              <>
                {/* Score */}
                <div className="text-right mr-2">
                  <div className="text-lg font-bold text-ndmo-blue-dark">
                    {Math.round(domainScore * 100)}%
                  </div>
                  <div className="flex gap-1 text-xs">
                    {passCount > 0 && (
                      <span className="text-ndmo-green">{passCount} pass</span>
                    )}
                    {warnCount > 0 && (
                      <span className="text-ndmo-yellow">
                        {warnCount} fair
                      </span>
                    )}
                    {failCount > 0 && (
                      <span className="text-ndmo-red">{failCount} fail</span>
                    )}
                  </div>
                </div>

                {/* More Details Button */}
                <button
                  onClick={() => setExpanded(!expanded)}
                  className="px-4 py-2 text-sm font-medium rounded-lg border border-ndmo-blue-medium text-ndmo-blue-medium hover:bg-ndmo-blue-pale transition-colors"
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
        <div className="border-t bg-ndmo-gray-light/30 p-5">
          {/* AI Summary */}
          {summaries.length > 0 && (
            <div className="mb-5">
              <h4 className="text-sm font-semibold text-ndmo-blue-dark mb-2">
                AI Assessment Summary
              </h4>
              {summaries.map((summary, i) => (
                <p
                  key={i}
                  className="text-sm text-ndmo-gray-dark leading-relaxed mb-2"
                >
                  {summary}
                </p>
              ))}
            </div>
          )}

          {/* Control Decisions Checklist */}
          <h4 className="text-sm font-semibold text-ndmo-blue-dark mb-3">
            Control Evaluations
          </h4>
          <div className="space-y-2">
            {decisions.map((decision, i) => {
              const icon = getDecisionIcon(decision.decision);
              return (
                <div
                  key={i}
                  className="bg-white rounded-lg p-4 border"
                >
                  <div className="flex items-start gap-3">
                    {/* Status Icon */}
                    <div className="flex-shrink-0 mt-0.5">
                      {icon === "pass" && (
                        <svg
                          className="w-5 h-5 text-ndmo-green"
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
                          className="w-5 h-5 text-ndmo-yellow"
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
                          className="w-5 h-5 text-ndmo-red"
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
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-sm font-semibold text-ndmo-blue-dark">
                          {decision.control_id}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded text-xs font-semibold ${getDecisionColor(decision.decision)}`}
                        >
                          {decision.decision}
                        </span>
                      </div>
                      <p className="text-sm text-ndmo-gray-dark leading-relaxed">
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
