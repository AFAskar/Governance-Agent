import { createFileRoute, Link } from "@tanstack/react-router";
import { NDI_DOMAINS } from "~/lib/ndi-domains";

export const Route = createFileRoute("/admin/company/$companyId")({
    component: RouteComponent,
});

// Mock report data - will be replaced with real API data
const MOCK_REPORT = {
    companyName: "Example Corporation",
    submittedAt: "2024-02-01T10:00:00Z",
    evaluatedAt: "2024-02-01T11:30:00Z",
    status: "completed",
    overallScore: 78.5,
    domainResults: [
        {
            domainId: "1_Data_Governance",
            domainName: "Data Governance",
            score: 85,
            filesCount: 3,
            controlsEvaluated: 12,
            compliantControls: 10,
        },
        {
            domainId: "2_Data_Catalog",
            domainName: "Data Catalog",
            score: 72,
            filesCount: 2,
            controlsEvaluated: 8,
            compliantControls: 6,
        },
        {
            domainId: "3_Data_Quality",
            domainName: "Data Quality",
            score: 90,
            filesCount: 4,
            controlsEvaluated: 10,
            compliantControls: 9,
        },
    ],
};

function RouteComponent() {
    const { companyId } = Route.useParams();

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
                                {MOCK_REPORT.companyName}
                            </h1>
                            <p className="text-ndmo-gray-medium">
                                NDI Assessment Report
                            </p>
                        </div>

                        <button
                            className="bg-ndmo-blue-medium hover:bg-ndmo-blue-dark text-white px-6 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            Download PDF
                        </button>
                    </div>
                </div>

                {/* Overall Score Card */}
                <div className="bg-gradient-to-br from-ndmo-blue-medium to-ndmo-blue-dark rounded-2xl p-8 mb-8 text-white shadow-lg">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-2xl font-bold mb-2">Overall Score</h2>
                            <p className="text-ndmo-blue-pale">
                                Submitted: {new Date(MOCK_REPORT.submittedAt).toLocaleDateString()}
                            </p>
                            <p className="text-ndmo-blue-pale">
                                Evaluated: {new Date(MOCK_REPORT.evaluatedAt).toLocaleDateString()}
                            </p>
                        </div>
                        <div className="text-center">
                            <div className="text-6xl font-bold mb-2">
                                {MOCK_REPORT.overallScore}%
                            </div>
                            <div className="text-ndmo-blue-pale text-sm font-semibold">
                                {MOCK_REPORT.overallScore >= 80 ? "Excellent" : MOCK_REPORT.overallScore >= 60 ? "Good" : "Needs Improvement"}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Domain Results */}
                <div className="bg-white rounded-xl p-6 shadow-sm border">
                    <h2 className="text-2xl font-bold text-ndmo-blue-dark mb-6">
                        Domain Evaluations
                    </h2>

                    <div className="space-y-4">
                        {MOCK_REPORT.domainResults.map((result) => (
                            <DomainResultCard key={result.domainId} result={result} />
                        ))}
                    </div>

                    {/* Empty Domains */}
                    {MOCK_REPORT.domainResults.length < NDI_DOMAINS.length && (
                        <div className="mt-6 pt-6 border-t">
                            <h3 className="font-semibold text-ndmo-gray-dark mb-3">
                                Domains Not Submitted
                            </h3>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                                {NDI_DOMAINS.filter(
                                    (domain) => !MOCK_REPORT.domainResults.find((r) => r.domainId === domain.id)
                                ).map((domain) => (
                                    <div key={domain.id} className="text-sm text-ndmo-gray-medium bg-ndmo-gray-light/50 rounded px-3 py-2">
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

interface DomainResultCardProps {
    result: {
        domainId: string;
        domainName: string;
        score: number;
        filesCount: number;
        controlsEvaluated: number;
        compliantControls: number;
    };
}

function DomainResultCard({ result }: DomainResultCardProps) {
    const getScoreColor = (score: number) => {
        if (score >= 80) return "text-ndmo-green";
        if (score >= 60) return "text-ndmo-yellow";
        return "text-ndmo-red";
    };

    const getProgressColor = (score: number) => {
        if (score >= 80) return "bg-ndmo-green";
        if (score >= 60) return "bg-ndmo-yellow";
        return "bg-ndmo-red";
    };

    return (
        <div className="border rounded-lg p-5 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                    <h3 className="font-semibold text-ndmo-blue-dark mb-1">
                        {result.domainName}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-ndmo-gray-medium">
                        <span>{result.filesCount} files</span>
                        <span>•</span>
                        <span>{result.controlsEvaluated} controls</span>
                        <span>•</span>
                        <span className="text-ndmo-green">
                            {result.compliantControls} compliant
                        </span>
                    </div>
                </div>
                <div className={`text-3xl font-bold ${getScoreColor(result.score)}`}>
                    {result.score}%
                </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-ndmo-gray-light rounded-full h-2">
                <div
                    className={`h-2 rounded-full ${getProgressColor(result.score)} transition-all`}
                    style={{ width: `${result.score}%` }}
                />
            </div>
        </div>
    );
}
