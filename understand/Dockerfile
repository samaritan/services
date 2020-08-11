FROM python:3.7-slim-buster

WORKDIR /samaritan/services/understand

# Install Dependencies
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && apt-get install -qq --no-install-recommends \
      netcat=1.10-* \
      wget=1.20.* && \
    rm -rf /var/lib/apt/lists/* && \
    wget --quiet -O - \
      http://builds.scitools.com/all_builds/b1007/Understand/Understand-5.1.1007-Linux-64bit.tgz | \
      tar zxf -

ENV PYTHONPATH=/samaritan/services/understand/scitools/bin/linux64/Python/ \
    PATH="${PATH}:/samaritan/services/understand/scitools/bin/linux64"

# Setup Application Environment
COPY requirements.txt .
RUN pip install --no-cache-dir --quiet --trusted-host pypi.python.org \
      -r requirements.txt

# Copy and Run Service
COPY config.yml .
COPY undrstand undrstand/
COPY run.sh .
ENTRYPOINT [".", "/samaritan/services/understand/run.sh"]
