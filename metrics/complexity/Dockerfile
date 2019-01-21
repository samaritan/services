FROM python:3

# Utilities
WORKDIR /samaritan/utilities

# Install Dependencies
RUN apt-get update && \
  apt-get -y install libparallel-forkmanager-perl netcat wget && \
  apt-get clean && \
  wget --quiet -O - \
    http://builds.scitools.com/all_builds/b955/Understand/Understand-5.0.955-Linux-64bit.tgz | \
    tar zxf -

ENV PYTHONPATH=/samaritan/utilities/scitools/bin/linux64/Python/ \
  PATH="${PATH}:/samaritan/utilities/scitools/bin/linux64"

# Application
WORKDIR /samaritan/services/metrics/complexity

# Setup Application Environment
COPY requirements.txt .
RUN pip install --no-cache-dir --quiet --trusted-host pypi.python.org \
  -r requirements.txt

# Copy and Run Service
COPY config.yml .
COPY complexity complexity/
COPY run.sh .
RUN chmod +x run.sh
CMD . /samaritan/services/metrics/complexity/run.sh
