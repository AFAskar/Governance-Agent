import { useQuery } from "@tanstack/react-query";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useTRPC } from "~/lib/trpc";

export const Route = createFileRoute("/admin/ndi")({
    component: RouteComponent,
});



function RouteComponent() {
    const trpc = useTRPC();
    const { data: submissions, isLoading } = useQuery(trpc.submission.getAll.queryOptions());

    return (
        <main className="container mx-auto px-4 py-12">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <Link
                        to="/admin"
                        className="text-ndmo-blue-medium hover:text-ndmo-blue-dark mb-4 inline-flex items-center gap-2"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                        Back to Dashboard
                    </Link>
                    <h1 className="text-4xl font-bold text-ndmo-blue-dark mb-2">
                        NDI Submissions
                    </h1>
                    <p className="text-ndmo-gray-medium">
                        View and manage all company submissions
                    </p>
                </div>

                {isLoading ? (
                    <div className="text-center py-12">Loading submissions...</div>
                ) : (
                    <>
                        {/* Submissions Grid */}
                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {submissions?.map((submission) => (
                                <CompanyCard key={submission.id} submission={submission} />
                            ))}
                        </div>

                        {/* Empty State */}
                        {submissions?.length === 0 && (
                            <div className="text-center py-16">
                                <div className="text-6xl mb-4">📊</div>
                                <h3 className="text-xl font-semibold text-ndmo-gray-dark mb-2">
                                    No Submissions Yet
                                </h3>
                                <p className="text-ndmo-gray-medium">
                                    Company submissions will appear here
                                </p>
                            </div>
                        )}
                    </>
                )}
            </div>
        </main>
    );
}

interface CompanyCardProps {
    submission: {
        id: string;
        companyName: string;
        createdAt: string;
        status: string;
    };
}

function CompanyCard({ submission }: CompanyCardProps) {
    const statusColors = {
        completed: "bg-ndmo-green text-primary",
        processing: "bg-ndmo-yellow text-primary",
        pending: "bg-ndmo-gray-medium text-primary",
        failed: "bg-ndmo-red text-primary",
    };

    const statusColor = statusColors[submission.status as keyof typeof statusColors] || statusColors.pending;

    return (
        <Link
            to="/admin/company/$companyId"
            params={{ companyId: submission.id }}
            className="group"
        >
            <div className="bg-white rounded-xl p-6 shadow-sm border-2 border-transparent hover:border-ndmo-blue-medium hover:shadow-lg transition-all duration-300">
                {/* Company Name */}
                <h3 className="text-xl font-bold text-ndmo-blue-dark mb-3 group-hover:text-ndmo-blue-medium transition-colors">
                    {submission.companyName}
                </h3>

                {/* Metadata */}
                <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2 text-sm text-ndmo-gray-medium">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        {new Date(submission.createdAt).toLocaleDateString()}
                    </div>
                </div>

                {/* Status Badge */}
                <div className="flex items-center justify-between">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${statusColor} uppercase tracking-wide`}>
                        {submission.status}
                    </span>
                    <svg
                        className="w-5 h-5 text-ndmo-blue-medium opacity-0 group-hover:opacity-100 transition-opacity"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                </div>
            </div>
        </Link>
    );
}
