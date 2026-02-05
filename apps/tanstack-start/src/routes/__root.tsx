/// <reference types="vite/client" />
import type { QueryClient } from "@tanstack/react-query";
import type { TRPCOptionsProxy } from "@trpc/tanstack-react-query";
import type * as React from "react";
import {
  createRootRouteWithContext,
  HeadContent,
  Outlet,
  Scripts,
  ErrorComponent,
  Link,
} from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import { AuthKitProvider } from "@workos/authkit-tanstack-react-start/client";

import type { AppRouter } from "@governance/api";
import {
  themeDetectorScript,
  ThemeProvider,
  ThemeToggle,
} from "@governance/ui/theme";
import { Toaster } from "@governance/ui/toast";
import { Button } from "@governance/ui/button";

import appCss from "~/styles.css?url";
import { Header } from "../component/layout/Header";
import { NotFound } from "../component/NotFound";

export const Route = createRootRouteWithContext<{
  queryClient: QueryClient;
  trpc: TRPCOptionsProxy<AppRouter>;
}>()({
  head: () => ({
    links: [{ rel: "stylesheet", href: appCss }],
  }),
  component: RootComponent,
  notFoundComponent: NotFound,
  errorComponent: ({ error }) => {
    return (
      <RootDocument>
        <div className="container mx-auto px-4 py-16">
          <div className="mx-auto max-w-2xl text-center">
            <div className="bg-ndmo-red/10 border-ndmo-red mb-6 rounded-lg border p-6">
              <h1 className="text-ndmo-red mb-4 text-4xl font-bold">Error</h1>
              <p className="text-ndmo-gray-dark mb-4 text-lg">
                {error.message || "An unexpected error occurred"}
              </p>
            </div>
            <Button asChild className="bg-ndmo-blue-medium hover:bg-ndmo-blue-dark">
              <Link to="/">Go Home</Link>
            </Button>
          </div>
        </div>
      </RootDocument>
    );
  },
});

function RootComponent() {
  return (
    <AuthKitProvider>
      <RootDocument>
        <Outlet />
      </RootDocument>
    </AuthKitProvider>
  );
}

function RootDocument({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <html lang="en" suppressHydrationWarning>
        <head>
          <HeadContent />
          <script
            dangerouslySetInnerHTML={{ __html: themeDetectorScript }}
            suppressHydrationWarning
          />
        </head>
        <body className="bg-background text-foreground min-h-screen font-sans antialiased">
          <Header />
          {children}
          <div className="absolute right-4 bottom-12">
            <ThemeToggle />
          </div>
          <Toaster />
          <TanStackRouterDevtools position="bottom-right" />
          <Scripts />
        </body>
      </html>
    </ThemeProvider>
  );
}
