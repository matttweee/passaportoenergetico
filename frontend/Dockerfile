FROM node:20-alpine AS base

WORKDIR /app

# Dependencies
FROM base AS deps
COPY package.json package-lock.json /app/
RUN npm ci

# Builder
FROM base AS builder
COPY --from=deps /app/node_modules /app/node_modules
COPY next.config.mjs tsconfig.json postcss.config.js tailwind.config.ts /app/
COPY app /app/app
COPY components /app/components
COPY lib /app/lib
RUN npm run build

# Production
FROM base AS runner
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public /app/public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone /app/
COPY --from=builder --chown=nextjs:nodejs /app/.next/static /app/.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]

