FROM python:3

WORKDIR /samaritan/services/project

# Install Dependencies
RUN apt-get update && apt-get -y install netcat && apt-get clean

# Setup Application Environment
COPY requirements.txt .
RUN pip install --no-cache-dir --quiet --trusted-host pypi.python.org \
  -r requirements.txt

# Copy and Run Service
COPY config.yml .
COPY projects.sqlite3 .
COPY project project/
COPY run.sh .
RUN chmod +x run.sh
CMD . /samaritan/services/project/run.sh
