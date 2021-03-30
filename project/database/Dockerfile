FROM flyway/flyway:7.7-alpine

WORKDIR /samaritan/services/project/

# Copy and Run
COPY migrations migrations/
COPY flyway.conf .
COPY LICENSE .
COPY VERSION .
