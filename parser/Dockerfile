FROM python:3.7-slim-buster

WORKDIR /samaritan/services/parser

# Install Dependencies
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && apt-get install -qq --no-install-recommends \
      gnupg=2.2.* \
      netcat=1.10-* \
      wget=1.20.* && \
    wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - && \
    echo "deb http://apt.llvm.org/buster/ llvm-toolchain-buster main" >> \
      /etc/apt/sources.list && \
    echo "deb-src http://apt.llvm.org/buster/ llvm-toolchain-buster main" \
      >> /etc/apt/souces.list && \
    apt-get update && \
    apt-get install -qq --no-install-recommends \
      python3-clang-12=1:12* && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH="${PYTHONPATH}:/usr/lib/python3/dist-packages/"

# Setup Application Environment
COPY requirements.txt .
RUN pip install --no-cache-dir --quiet --trusted-host pypi.python.org \
  -r requirements.txt

# Copy and Run Service
COPY config.yml .
COPY parser parser/
COPY run.sh .
ENTRYPOINT ["/samaritan/services/parser/run.sh"]
