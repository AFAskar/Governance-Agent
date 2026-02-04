"use client";

import { Link } from "@tanstack/react-router";
import { useAuth } from "@workos/authkit-tanstack-react-start";

export function Header() {
    const { user } = useAuth();

    return (
        <header className="sticky top-0 z-50 w-full border-b bg-white shadow-sm">
            <div className="container mx-auto flex h-16 items-center justify-between px-4">
                {/* Logo */}
                <Link to="/" className="flex items-center gap-3">
                    <img
                        src="/ndmo-logo.png"
                        alt="NDMO"
                        className="h-10 w-auto"
                    />
                </Link>

                {/* Navigation */}
                <nav className="flex items-center gap-6">
                    {user ? (
                        <>
                            <span className="text-sm text-ndmo-gray-medium">
                                {user.email}
                            </span>
                            {user.role === "admin" && (
                                <Link
                                    to="/admin"
                                    className="text-sm font-medium text-ndmo-blue-medium hover:text-ndmo-blue-dark"
                                >
                                    Admin Dashboard
                                </Link>
                            )}
                            <form action="/api/auth/signout" method="post">
                                <button
                                    type="submit"
                                    className="rounded-lg bg-ndmo-blue-medium px-4 py-2 text-sm font-medium text-white hover:bg-ndmo-blue-dark transition-colors"
                                >
                                    Sign Out
                                </button>
                            </form>
                        </>
                    ) : (
                        <Link
                            to="/api/auth/signin"
                            className="rounded-lg bg-ndmo-blue-medium px-4 py-2 text-sm font-medium text-white hover:bg-ndmo-blue-dark transition-colors"
                        >
                            Sign In
                        </Link>
                    )}
                </nav>
            </div>
        </header>
    );
}
