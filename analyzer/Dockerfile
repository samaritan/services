FROM python:3

WORKDIR /samaritan/services/analyzer

# Install Dependencies
RUN apt-get update && apt-get -y install netcat && apt-get clean

# Setup Application Environment
COPY requirements.txt .
RUN pip install --no-cache-dir --quiet --trusted-host pypi.python.org \
  -r requirements.txt

# Copy and Run Service
COPY config.yml .
COPY analyzer analyzer/
COPY run.sh .
CMD . /samaritan/services/analyzer/run.sh
