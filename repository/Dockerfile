FROM python:3.7-slim-bullseye

WORKDIR /samaritan/services/repository

# Install Dependencies
RUN apt-get update && apt-get install -qq --no-install-recommends \
      git=1:2.30.* \
      netcat=1.10-* && \
    rm -rf /var/lib/apt/lists/* && \
    git config --global diff.renameLimit 10000

# Setup Application Environment
COPY requirements.txt .
RUN pip install --no-cache-dir --quiet --trusted-host pypi.python.org \
      -r requirements.txt

# Copy and Run Service
COPY LICENSE .
copy VERSION .
COPY config.yml .
COPY repository repository/
COPY run.sh .
ENTRYPOINT ["/samaritan/services/repository/run.sh"]
