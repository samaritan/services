FROM python:3

WORKDIR /samaritan/services/understand

# Install Dependencies
RUN apt-get update && \
  apt-get -y install netcat wget && \
  apt-get clean && \
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
CMD . /samaritan/services/understand/run.sh
