import { authRouter } from "./router/auth";
import { postRouter } from "./router/post";
import { submissionRouter } from "./router/submission";
import { createTRPCRouter } from "./trpc";

export const appRouter = createTRPCRouter({
  auth: authRouter,
  post: postRouter,
  submission: submissionRouter,
});

// export type definition of API
export type AppRouter = typeof appRouter;
