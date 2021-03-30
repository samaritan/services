FROM flyway/flyway:7.7-alpine

WORKDIR /samaritan/services/metrics/

# Copy and Run
COPY migrations migrations/
COPY flyway.conf .
COPY LICENSE .
COPY VERSION .
