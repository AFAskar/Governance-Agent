import { createFileRoute } from "@tanstack/react-router";
import { IndexCard } from "~/component/index/IndexCard";

export const Route = createFileRoute("/")({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <main className="container mx-auto px-4 py-16">
      <div className="max-w-6xl mx-auto">
        {/* Header Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-ndmo-blue-dark mb-4">
            National Data Indices
          </h1>
          <p className="text-lg text-ndmo-gray-medium max-w-2xl mx-auto">
            Select an index to begin your assessment
          </p>
        </div>

        {/* Index Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
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
