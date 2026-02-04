import { useQuery } from "@tanstack/react-query";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useTRPC } from "~/lib/trpc";
import { NDI_DOMAINS } from "~/lib/ndi-domains";

export const Route = createFileRoute("/admin/company/$companyId")({
  component: RouteComponent,
});

function RouteComponent() {
  const { companyId } = Route.useParams();
  const trpc = useTRPC();
  const { data, isLoading, error } = useQuery(trpc.submission.getById.queryOptions({ id: companyId }));

  if (isLoading) {
    return (
      <main className="container mx-auto px-4 py-12">
        <div className="text-center py-16 text-ndmo-gray-medium">Loading report...</div>
      </main>
    );
  }

  if (error || !data) {
    return (
      <main className="container mx-auto px-4 py-12">
        <div className="text-center py-16">
          <p className="text-ndmo-red mb-4">Failed to load submission</p>
          <Link to="/admin/ndi" className="text-ndmo-blue-medium hover:underline">
            Back to Submissions
          </Link>
        </div>
      </main>
    );
  }

  const { submission, files, report } = data;
  let reportData: unknown = null;
  try {
    reportData = report?.reportData ? JSON.parse(report.reportData) : null;
  } catch {
    reportData = null;
  }

  // Group files by domain
  const filesByDomain = files.reduce<Record<string, typeof files>>((acc, f) => {
    if (!acc[f.domainId]) acc[f.domainId] = [];
    acc[f.domainId]!.push(f);
    return acc;
  }, {});

  const domainsWithFiles = NDI_DOMAINS.filter((d) => filesByDomain[d.id]);
  const domainsWithoutFiles = NDI_DOMAINS.filter((d) => !filesByDomain[d.id]);

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
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
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
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download PDF
              </button>
            )}
          </div>
        </div>

        {/* Status Card */}
        <div className="bg-gradient-to-br from-ndmo-blue-medium to-ndmo-blue-dark rounded-2xl p-8 mb-8 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">Submission Details</h2>
              <p className="text-ndmo-blue-pale">
                Submitted: {new Date(submission.createdAt).toLocaleDateString()}
              </p>
              <p className="text-ndmo-blue-pale">
                Files uploaded: {files.length}
              </p>
              <p className="text-ndmo-blue-pale">
                Domains covered: {domainsWithFiles.length} / {NDI_DOMAINS.length}
              </p>
            </div>
            <div className="text-center">
              <span className={`px-4 py-2 rounded-full text-sm font-bold uppercase tracking-wide text-white ${statusColors[submission.status] ?? statusColors.pending}`}>
                {submission.status}
              </span>
            </div>
          </div>
        </div>

        {/* Submitted Domains */}
        <div className="bg-white rounded-xl p-6 shadow-sm border mb-6">
          <h2 className="text-2xl font-bold text-ndmo-blue-dark mb-6">
            Submitted Domains
          </h2>

          <div className="space-y-4">
            {domainsWithFiles.map((domain) => {
              const domainFiles = filesByDomain[domain.id] ?? [];
              return (
                <div key={domain.id} className="border rounded-lg p-5">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-ndmo-blue-medium text-white flex items-center justify-center font-bold text-sm">
                        {domain.order}
                      </div>
                      <h3 className="font-semibold text-ndmo-blue-dark">
                        {domain.name}
                      </h3>
                    </div>
                    <span className="text-sm text-ndmo-gray-medium">
                      {domainFiles.length} file{domainFiles.length !== 1 ? "s" : ""}
                    </span>
                  </div>
                  <div className="ml-11 space-y-1">
                    {domainFiles.map((f) => (
                      <div key={f.id} className="flex items-center gap-2 text-sm text-ndmo-gray-dark">
                        <svg className="w-4 h-4 text-ndmo-blue-medium flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span className="truncate">{f.fileName}</span>
                        <span className="text-xs text-ndmo-gray-medium flex-shrink-0">
                          ({(f.fileSize / 1024).toFixed(1)} KB)
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Domains Not Submitted */}
          {domainsWithoutFiles.length > 0 && (
            <div className="mt-6 pt-6 border-t">
              <h3 className="font-semibold text-ndmo-gray-dark mb-3">
                Domains Not Submitted
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {domainsWithoutFiles.map((domain) => (
                  <div key={domain.id} className="text-sm text-ndmo-gray-medium bg-ndmo-gray-light/50 rounded px-3 py-2">
                    {domain.order}. {domain.name}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Report Data */}
        {reportData && (
          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <h2 className="text-2xl font-bold text-ndmo-blue-dark mb-4">
              AI Evaluation Results
            </h2>
            <pre className="bg-ndmo-gray-light/50 rounded-lg p-4 overflow-x-auto text-sm text-ndmo-gray-dark">
              {JSON.stringify(reportData, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </main>
  );
}
