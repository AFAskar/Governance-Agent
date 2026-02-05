import { createFileRoute } from "@tanstack/react-router";

import { IndexCard } from "~/component/index/IndexCard";

export const Route = createFileRoute("/")({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <main className="container mx-auto px-4 py-16">
      <div className="mx-auto max-w-6xl">
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
