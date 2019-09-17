FROM python:3

WORKDIR /samaritan/services/metrics/churn

# Install Dependencies
RUN apt-get update && apt-get -y install netcat && apt-get clean

# Setup Application Environment
COPY requirements.txt .
RUN pip install --no-cache-dir --quiet --trusted-host pypi.python.org \
  -r requirements.txt

# Copy and Run Service
COPY config.yml .
COPY churn churn/
COPY run.sh .
CMD . /samaritan/services/metrics/churn/run.sh
