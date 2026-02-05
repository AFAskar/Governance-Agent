import { createServerFn } from "@tanstack/react-start";
import { getSignInUrl } from "@workos/authkit-tanstack-react-start";
import { useAuth } from "@workos/authkit-tanstack-react-start/client";

import { Button } from "@governance/ui/button";

const getSignInUrlFn = createServerFn({ method: "GET" }).handler(async () => {
  return await getSignInUrl();
});

export function AuthShowcase() {
  const { user, loading, signOut } = useAuth();

  if (loading) {
    return <div className="text-muted-foreground">Loading...</div>;
  }

  if (!user) {
    return (
      <Button
        size="lg"
        onClick={async () => {
          const signInUrl = await getSignInUrlFn();
          window.location.href = signInUrl;
        }}
      >
        Sign in with WorkOS
      </Button>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <p className="text-center text-2xl">
        <span>
          Logged in as {user.firstName} {user.lastName}
        </span>
      </p>
      <p className="text-muted-foreground">{user.email}</p>

      <Button size="lg" onClick={() => signOut()}>
        Sign out
      </Button>
    </div>
  );
}
