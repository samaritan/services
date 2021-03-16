FROM python:3.7-slim-buster

WORKDIR /samaritan/services/parser

# Install Dependencies
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && apt-get install -qq --no-install-recommends \
      netcat=1.10-* \
      wget=1.20.* && \
    wget --quiet -O /tmp/srcml.deb \
      "http://131.123.42.38/lmcrs/v1.0.0/srcml_1.0.0-1_ubuntu18.04.deb" && \
    apt-get install -qq --no-install-recommends /tmp/srcml.deb && \
    rm /tmp/srcml.deb && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH="${PYTHONPATH}:/usr/lib/python3/dist-packages/"

# Setup Application Environment
COPY requirements.txt .
RUN pip install --no-cache-dir --quiet --trusted-host pypi.python.org \
  -r requirements.txt

# Copy and Run Service
COPY LICENSE .
COPY config.yml .
COPY parser parser/
COPY run.sh .
ENTRYPOINT ["/samaritan/services/parser/run.sh"]
