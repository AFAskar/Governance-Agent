import { createFileRoute, Link, redirect } from "@tanstack/react-router";
import { getAuth } from "@workos/authkit-tanstack-react-start";

import { IndexCard } from "~/component/index/IndexCard";
import { hasPermission, SUBMISSION_PERMISSIONS } from "~/lib/permissions";

export const Route = createFileRoute("/admin/")({
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
  return (
    <main className="container mx-auto px-4 py-16">
      <div className="mx-auto max-w-6xl">
        {/* Header Section */}
        <div className="mb-16 text-center">
          <h1 className="text-ndmo-blue-dark mb-4 text-5xl font-bold">
            Admin Dashboard
          </h1>
          <p className="text-ndmo-gray-medium mx-auto max-w-2xl text-lg">
            Select an index to view submissions
          </p>
        </div>

        {/* Index Cards */}
        <div className="mx-auto grid max-w-4xl gap-8 md:grid-cols-2">
          <IndexCard
            title="NDI"
            subtitle="NATIONALITY DATA INDEX"
            isActive={true}
            href="/admin/ndi"
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
