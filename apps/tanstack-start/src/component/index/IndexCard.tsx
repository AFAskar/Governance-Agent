import { Link } from "@tanstack/react-router";

import { cn } from "@governance/ui";

interface IndexCardProps {
  title: string;
  subtitle: string;
  isActive: boolean;
  href?: string;
}

export function IndexCard({ title, subtitle, isActive, href }: IndexCardProps) {
  const CardContent = (
    <div
      className={cn(
        "group relative overflow-hidden rounded-2xl border-2 p-8 transition-all duration-300",
        isActive
          ? "border-ndmo-blue-medium to-ndmo-blue-pale cursor-pointer bg-gradient-to-br from-white hover:scale-105 hover:shadow-2xl"
          : "border-ndmo-gray-light bg-ndmo-gray-light/30 cursor-not-allowed opacity-60",
      )}
    >
      {/* Active Indicator */}
      {isActive && (
        <div className="absolute top-6 right-6">
          <div className="relative">
            <div className="bg-ndmo-green pulse-indicator h-4 w-4 rounded-full" />
            <div className="bg-ndmo-green/30 absolute inset-0 h-4 w-4 animate-ping rounded-full" />
          </div>
        </div>
      )}

      {/* Content */}
      <div className="space-y-3">
        <h2 className="text-ndmo-blue-dark text-3xl font-bold">{title}</h2>
        <p className="text-ndmo-gray-medium text-sm font-medium">{subtitle}</p>
      </div>

      {/* Active Label */}
      {isActive && (
        <div className="mt-6 flex items-center gap-2">
          <div className="bg-ndmo-green h-2 w-2 rounded-full" />
          <span className="text-ndmo-green text-xs font-semibold tracking-wide uppercase">
            Active
          </span>
        </div>
      )}

      {/* Hover Effect */}
      {isActive && (
        <div className="from-ndmo-blue-medium/5 absolute inset-0 bg-gradient-to-br to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
      )}
    </div>
  );

  if (isActive && href) {
    return <Link to={href}>{CardContent}</Link>;
  }

  return CardContent;
}
