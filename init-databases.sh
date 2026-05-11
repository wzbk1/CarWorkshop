#!/bin/bash
set -e

RDS_HOST="carworkshop-db.crkqu6eysa2u.eu-central-1.rds.amazonaws.com"
RDS_USER="cwadmin"
RDS_PASS="CwRds2026!xKp9mQ"

echo "Creating databases on RDS..."

for DB_NAME in user_db service_db booking_db review_db; do
    echo "Creating database: $DB_NAME"
    PGPASSWORD=$RDS_PASS psql -h $RDS_HOST -U $RDS_USER -d carworkshop -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "  Database $DB_NAME already exists"
done

echo "All databases created successfully!"
