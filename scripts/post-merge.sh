#!/bin/bash
set -e
pnpm install --frozen-lockfile
# Application schema is owned by the explicit Python/PostgreSQL migrations.
# Never push the unrelated scaffold Drizzle schema into FutureTwin's database.
