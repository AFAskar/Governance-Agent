"use client";

import { Link } from "@tanstack/react-router";
import { createServerFn } from "@tanstack/react-start";
import { getSignInUrl } from "@workos/authkit-tanstack-react-start";
import { useAuth } from "@workos/authkit-tanstack-react-start/client";

import { hasPermission, SUBMISSION_PERMISSIONS } from "~/lib/permissions";

export function Header() {
  const { user, permissions, signOut } = useAuth();
  const canViewAdmin = hasPermission(permissions, SUBMISSION_PERMISSIONS.READ);

  return (
    <header className="bg-background sticky top-0 z-50 w-full border-b shadow-sm">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3">
          <img src="/ndmo-logo.png" alt="NDMO" className="h-25 w-auto" />
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-6">
          {user ? (
            <>
              <span className="text-ndmo-gray-medium text-sm">
                {user.email}
              </span>
              {canViewAdmin && (
                <Link
                  to="/admin"
                  className="text-ndmo-blue-medium hover:text-ndmo-blue-dark text-sm font-medium"
                >
                  Admin Dashboard
                </Link>
              )}
              <button
                onClick={() => signOut()}
                className="bg-ndmo-blue-medium text-primary hover:bg-ndmo-blue-dark rounded-lg px-4 py-2 text-sm font-medium transition-colors"
              >
                Sign Out
              </button>
            </>
          ) : (
            <button
              onClick={async () => {
                const url = await getSignInUrlFn();
                window.location.href = url;
              }}
              className="bg-ndmo-blue-medium text-primary hover:bg-ndmo-blue-dark rounded-lg px-4 py-2 text-sm font-medium transition-colors"
            >
              Sign In
            </button>
          )}
        </nav>
      </div>
    </header>
  );
}

const getSignInUrlFn = createServerFn({ method: "GET" }).handler(async () => {
  return await getSignInUrl();
});
