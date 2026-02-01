# Base
FROM node:20-alpine AS base
WORKDIR /app

# Dependencies
FROM base AS deps
COPY package.json package-lock.json /app/
RUN npm ci

# Builder
FROM base AS builder
COPY --from=deps /app/node_modules /app/node_modules
COPY package.json package-lock.json /app/
COPY next.config.mjs tsconfig.json postcss.config.js tailwind.config.ts /app/
COPY app /app/app
COPY components /app/components
COPY lib /app/lib
COPY public /app/public
RUN npm run build

# Production
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/.next /app/.next
COPY --from=builder /app/public /app/public
COPY --from=builder /app/node_modules /app/node_modules
COPY package.json /app/package.json

EXPOSE 3000
CMD ["npm", "start"]
