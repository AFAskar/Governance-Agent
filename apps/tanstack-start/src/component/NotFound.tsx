import { Link, useLocation } from "@tanstack/react-router";

export function NotFound() {
    const location = useLocation();
    console.log("NotFound triggered for path:", location.pathname);

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground p-4">
            <h1 className="text-9xl font-extrabold tracking-widest text-primary">404</h1>
            <div className="bg-primary px-2 text-sm rounded rotate-12 absolute text-primary-foreground">
                Page Not Found
            </div>
            <div className="mt-8 text-center">
                <div className="text-xl font-medium mb-4">
                    Oops! The page you asked for doesn't exist.
                </div>
                <Link
                    to="/"
                    className="px-6 py-3 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors duration-200"
                >
                    Go Home
                </Link>
            </div>
        </div>
    );
}
