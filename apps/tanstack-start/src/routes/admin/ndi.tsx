import { useQuery } from "@tanstack/react-query";
import { createFileRoute, Link, redirect } from "@tanstack/react-router";
import { getAuth } from "@workos/authkit-tanstack-react-start";

import { useTRPC } from "~/lib/trpc";
import { hasPermission, SUBMISSION_PERMISSIONS } from "~/lib/permissions";

export const Route = createFileRoute("/admin/ndi")({
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

function RouteComponent() {
  const trpc = useTRPC();
  const {
    data: submissions,
    isLoading,
    error,
  } = useQuery(trpc.submission.getAll.queryOptions());

  return (
    <main className="container mx-auto px-4 py-12">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <Link
            to="/admin"
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
            Back to Dashboard
          </Link>
          <h1 className="text-ndmo-blue-dark mb-2 text-4xl font-bold">
            NDI Submissions
          </h1>
          <p className="text-ndmo-gray-medium">
            View and manage all company submissions
          </p>
        </div>

        {isLoading ? (
          <div className="text-ndmo-gray-medium py-12 text-center">
            Loading submissions...
          </div>
        ) : error ? (
          <div className="py-16 text-center">
            <p className="text-ndmo-red mb-2">Failed to load submissions</p>
            <p className="text-ndmo-gray-medium text-sm">{error.message}</p>
          </div>
        ) : !submissions || submissions.length === 0 ? (
          <div className="py-16 text-center">
            <h3 className="text-ndmo-gray-dark mb-2 text-xl font-semibold">
              No Submissions Yet
            </h3>
            <p className="text-ndmo-gray-medium">
              Company submissions will appear here
            </p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {submissions.map((submission) => (
              <CompanyCard key={submission.id} submission={submission} />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}

interface CompanyCardProps {
  submission: {
    id: string;
    companyName: string;
    userId: string;
    status: string;
    createdAt: Date;
    updatedAt: Date;
  };
}

function CompanyCard({ submission }: CompanyCardProps) {
  const statusColors = {
    completed: "bg-ndmo-green text-primary",
    processing: "bg-ndmo-yellow text-primary",
    pending: "bg-ndmo-gray-medium text-primary",
    failed: "bg-ndmo-red text-primary",
  };

  const statusColor =
    statusColors[submission.status as keyof typeof statusColors] ||
    statusColors.pending;

  return (
    <Link
      to="/admin/company/$companyId"
      params={{ companyId: submission.id }}
      className="group"
    >
      <div className="hover:border-ndmo-blue-medium rounded-xl border-2 border-transparent bg-white p-6 shadow-sm transition-all duration-300 hover:shadow-lg">
        {/* Company Name */}
        <h3 className="text-ndmo-blue-dark group-hover:text-ndmo-blue-medium mb-3 text-xl font-bold transition-colors">
          {submission.companyName}
        </h3>

        {/* Metadata */}
        <div className="mb-4 space-y-2">
          <div className="text-ndmo-gray-medium flex items-center gap-2 text-sm">
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
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            {new Date(submission.createdAt).toLocaleDateString()}
          </div>
        </div>

        {/* Status Badge */}
        <div className="flex items-center justify-between">
          <span
            className={`rounded-full px-3 py-1 text-xs font-semibold ${statusColor} tracking-wide uppercase`}
          >
            {submission.status}
          </span>
          <svg
            className="text-ndmo-blue-medium h-5 w-5 opacity-0 transition-opacity group-hover:opacity-100"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </div>
      </div>
    </Link>
  );
}
