FROM python:3

WORKDIR /samaritan/services/repository

# Install Dependencies
RUN apt-get update && apt-get -y install netcat && apt-get clean && \
  git config --global diff.renameLimit 10000

# Setup Application Environment
COPY requirements.txt .
RUN pip install --no-cache-dir --quiet --trusted-host pypi.python.org \
  -r requirements.txt

# Copy and Run Service
COPY config.yml .
COPY repository repository/
COPY run.sh .
RUN chmod +x run.sh
CMD . /samaritan/services/repository/run.sh
