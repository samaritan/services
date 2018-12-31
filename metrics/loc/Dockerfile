FROM python:3

WORKDIR /samaritan/services/metrics/loc

# Install Dependencies
RUN apt-get update && \
  apt-get -y install libparallel-forkmanager-perl netcat wget && \
  apt-get clean && \
  wget --quiet --output-document /usr/bin/cloc \
    https://github.com/AlDanial/cloc/releases/download/1.80/cloc-1.80.pl && \
  chmod +x /usr/bin/cloc

# Setup Application Environment
COPY requirements.txt .
RUN pip install --no-cache-dir --quiet --trusted-host pypi.python.org \
  -r requirements.txt

# Copy and Run Service
COPY config.yml .
COPY loc loc/
COPY run.sh .
RUN chmod +x run.sh
CMD . /samaritan/services/metrics/loc/run.sh
