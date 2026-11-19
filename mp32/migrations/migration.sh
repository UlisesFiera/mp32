#!/bin/sh
set -eu

export PGHOST="${PGHOST:-postgres}"
export PGPORT="${PGPORT:-5432}"
export PGUSER="${POSTGRES_USER}"
export PGDATABASE="${POSTGRES_DB}"
export PGPASSWORD="${POSTGRES_PASSWORD}"

echo "Checking database migrations..."

psql -X -v ON_ERROR_STOP=1 <<'SQL'
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
SQL

for file in /migrations/*.sql; do
    [ -f "$file" ] || continue

    version=$(basename "$file")

    echo "Checking $version..."

    # Each migration runs in a transaction.
    # The advisory lock prevents concurrent migration runners.
    {
        printf 'BEGIN;\n'
        printf "SELECT pg_advisory_xact_lock(420032);\n"
        printf "SELECT CASE WHEN EXISTS (SELECT 1 FROM schema_migrations WHERE version = '%s') THEN 'false' ELSE 'true' END AS pending \\gset\n" "$version"
        printf '\\if :pending\n'
        cat "$file"
        printf '\n'
        printf "INSERT INTO schema_migrations (version) VALUES ('%s');\n" "$version"
        printf '\\endif\n'
        printf 'COMMIT;\n'
    } | psql -X -v ON_ERROR_STOP=1

    echo "Checked $version"
done

echo "Database migrations completed!"
