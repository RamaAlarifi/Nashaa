# syntax=docker/dockerfile:1.6
# Nashaa Next.js frontend image (Nashaa_Guide.md §25).
# Multi-stage with a `dev` target (HMR + source mount) and a `runner` target
# (standalone production server, non-root). Both targets run as non-root.

# ---- Base ----------------------------------------------------------------
FROM node:22-slim AS base
RUN groupadd --system --gid 10001 nashaa \
 && useradd  --system --uid 10001 --gid nashaa --create-home --home-dir /home/nashaa nashaa
WORKDIR /app

# ---- deps: install locked dependencies -----------------------------------
FROM base AS deps
COPY package.json package-lock.json ./
RUN npm ci

# ---- dev: full source + node_modules, runs the dev server (HMR) ----------
# Used by docker-compose.yml with a source mount and anonymous volumes for
# node_modules and .next. Runs as the non-root nashaa user.
FROM deps AS dev
COPY --chown=nashaa:nashaa . .
RUN mkdir -p /app/.next && chown nashaa:nashaa /app /app/.next
USER nashaa
ENV NEXT_TELEMETRY_DISABLED=1
EXPOSE 3000
CMD ["npm", "run", "dev"]

# ---- builder: produce the standalone production build --------------------
FROM deps AS builder
ARG BACKEND_URL=http://backend:8000
ENV BACKEND_URL=$BACKEND_URL
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ---- runner: minimal standalone runtime, non-root -----------------------
FROM node:22-slim AS runner

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN groupadd --system --gid 10001 nashaa \
 && useradd  --system --uid 10001 --gid nashaa --create-home --home-dir /home/nashaa nashaa

WORKDIR /app

# Standalone server + trimmed node_modules, then static assets and public.
COPY --from=builder --chown=nashaa:nashaa /app/.next/standalone ./
COPY --from=builder --chown=nashaa:nashaa /app/.next/static ./.next/static
COPY --from=builder --chown=nashaa:nashaa /app/public ./public

USER nashaa
EXPOSE 3000
CMD ["node", "server.js"]
