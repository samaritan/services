FROM python:3.7-slim-buster

WORKDIR /samaritan/services/metrics/complexity

# Install Dependencies
RUN apt-get update && apt-get install -qq --no-install-recommends \
      netcat=1.10-* && \
    rm -rf /var/lib/apt/lists/*

# Setup Application Environment
COPY requirements.txt .
RUN pip install --no-cache-dir --quiet --trusted-host pypi.python.org \
      -r requirements.txt

# Copy and Run Service
COPY config.yml .
COPY complexity complexity/
COPY run.sh .
ENTRYPOINT ["/samaritan/services/metrics/complexity/run.sh"]
