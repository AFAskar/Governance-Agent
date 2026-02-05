import { createFileRoute, useSearch } from "@tanstack/react-router";
import { z } from "zod";

import { IndexCard } from "~/component/index/IndexCard";

const searchSchema = z.object({
  error: z.string().optional(),
});

export const Route = createFileRoute("/")({
  validateSearch: searchSchema,
  component: RouteComponent,
});

function RouteComponent() {
  const search = useSearch({ from: "/" });
  const showPermissionError = search.error === "insufficient_permissions";

  return (
    <main className="container mx-auto px-4 py-16">
      <div className="mx-auto max-w-6xl">
        {/* Permission Error Alert */}
        {showPermissionError && (
          <div className="mb-8 rounded-lg border-2 border-red-500 bg-red-50 p-4">
            <div className="flex items-start gap-3">
              <svg
                className="h-6 w-6 flex-shrink-0 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <div>
                <h3 className="font-semibold text-red-900">
                  Insufficient Permissions
                </h3>
                <p className="mt-1 text-sm text-red-700">
                  You don't have the necessary permissions to access that page. Please contact your administrator if you believe this is an error.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Header Section */}
        <div className="mb-16 text-center">
          <h1 className="text-ndmo-blue-dark mb-4 text-5xl font-bold">
            National Data Indices
          </h1>
          <p className="text-ndmo-gray-medium mx-auto max-w-2xl text-lg">
            Select an index to begin your assessment
          </p>
        </div>

        {/* Index Cards */}
        <div className="mx-auto grid max-w-4xl gap-8 md:grid-cols-2">
          <IndexCard
            title="NDI"
            subtitle="NATIONALITY DATA INDEX"
            isActive={true}
            href="/submit"
          />
          <IndexCard
            title="NAII"
            subtitle="NATIONALITY ARTIFICIAL INTELLIGENCE INDEX"
            isActive={false}
          />
        </div>
      </div>
    </main>
  );
}
