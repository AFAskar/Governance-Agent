FROM node:22-alpine AS base

RUN npm install -g pnpm@10.19.0

WORKDIR /app

# Copy workspace root config
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml turbo.json ./

# Copy all workspace package.json files for dependency resolution
COPY apps/tanstack-start/package.json ./apps/tanstack-start/
COPY packages/api/package.json ./packages/api/
COPY packages/auth/package.json ./packages/auth/
COPY packages/db/package.json ./packages/db/
COPY packages/ui/package.json ./packages/ui/
COPY packages/validators/package.json ./packages/validators/
COPY tooling/eslint/package.json ./tooling/eslint/
COPY tooling/prettier/package.json ./tooling/prettier/
COPY tooling/tailwind/package.json ./tooling/tailwind/
COPY tooling/typescript/package.json ./tooling/typescript/
COPY tooling/github/package.json ./tooling/github/

RUN pnpm install --frozen-lockfile

# Development stage
FROM base AS development
COPY . .
WORKDIR /app/apps/tanstack-start
EXPOSE 3001
CMD ["pnpm", "dev"]

# Build stage
FROM base AS builder
COPY . .
RUN pnpm turbo run build --filter=@governance/tanstack-start

# Production stage
FROM node:22-alpine AS runner
WORKDIR /app

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 appuser

COPY --from=builder --chown=appuser:nodejs /app/apps/tanstack-start/.output ./.output

USER appuser

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", ".output/server/index.mjs"]
