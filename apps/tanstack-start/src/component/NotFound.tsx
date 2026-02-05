import { Link, useLocation } from "@tanstack/react-router";

export function NotFound() {
  const location = useLocation();
  console.log("NotFound triggered for path:", location.pathname);

  return (
    <div className="bg-background text-foreground flex min-h-screen flex-col items-center justify-center p-4">
      <h1 className="text-primary text-9xl font-extrabold tracking-widest">
        404
      </h1>
      <div className="bg-primary text-primary-foreground absolute rotate-12 rounded px-2 text-sm">
        Page Not Found
      </div>
      <div className="mt-8 text-center">
        <div className="mb-4 text-xl font-medium">
          Oops! The page you asked for doesn't exist.
        </div>
        <Link
          to="/"
          className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-md px-6 py-3 transition-colors duration-200"
        >
          Go Home
        </Link>
      </div>
    </div>
  );
}
