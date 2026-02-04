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
                    ? "border-ndmo-blue-medium bg-gradient-to-br from-white to-ndmo-blue-pale hover:shadow-2xl hover:scale-105 cursor-pointer"
                    : "border-ndmo-gray-light bg-ndmo-gray-light/30 cursor-not-allowed opacity-60"
            )}
        >
            {/* Active Indicator */}
            {isActive && (
                <div className="absolute top-6 right-6">
                    <div className="relative">
                        <div className="h-4 w-4 rounded-full bg-ndmo-green pulse-indicator" />
                        <div className="absolute inset-0 h-4 w-4 rounded-full bg-ndmo-green/30 animate-ping" />
                    </div>
                </div>
            )}

            {/* Content */}
            <div className="space-y-3">
                <h2 className="text-3xl font-bold text-ndmo-blue-dark">
                    {title}
                </h2>
                <p className="text-sm font-medium text-ndmo-gray-medium">
                    {subtitle}
                </p>
            </div>

            {/* Active Label */}
            {isActive && (
                <div className="mt-6 flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-ndmo-green" />
                    <span className="text-xs font-semibold text-ndmo-green uppercase tracking-wide">
                        Active
                    </span>
                </div>
            )}

            {/* Hover Effect */}
            {isActive && (
                <div className="absolute inset-0 bg-gradient-to-br from-ndmo-blue-medium/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            )}
        </div>
    );

    if (isActive && href) {
        return <Link to={href}>{CardContent}</Link>;
    }

    return CardContent;
}
