FROM python:3.7-slim-buster

WORKDIR /samaritan/services/metrics/collaboration

# Install Dependencies
RUN apt-get update && apt-get install -qq --no-install-recommends \
      gnupg=2.2.* \
      netcat=1.10-* && \
    apt-key adv --batch --keyserver keys.gnupg.net \
      --recv-key 612DEFB798507F25 && \
    echo "deb http://downloads.skewed.de/apt buster main" \
      >> /etc/apt/sources.list && \
    apt-get update && apt-get install -qq --no-install-recommends \
      python3-graph-tool=2.33* && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH="${PYTHONPATH}:/usr/lib/python3/dist-packages/"

# Setup Application Environment
COPY requirements.txt .
RUN pip install --no-cache-dir --quiet --trusted-host pypi.python.org \
      -r requirements.txt

# Copy and Run Service
COPY LICENSE .
copy VERSION .
COPY config.yml .
COPY collaboration collaboration/
COPY run.sh .
ENTRYPOINT ["/samaritan/services/metrics/collaboration/run.sh"]
