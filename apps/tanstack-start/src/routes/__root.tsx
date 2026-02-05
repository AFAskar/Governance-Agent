/// <reference types="vite/client" />
import type { QueryClient } from "@tanstack/react-query";
import type { TRPCOptionsProxy } from "@trpc/tanstack-react-query";
import type * as React from "react";
import {
  createRootRouteWithContext,
  HeadContent,
  Outlet,
  Scripts,
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
