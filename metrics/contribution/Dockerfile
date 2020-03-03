FROM ubuntu

WORKDIR /samaritan/services/metrics/contribution
ENV GPGKEY 612DEFB798507F25
ENV DEB "http://downloads.skewed.de/apt/bionic bionic universe"
ENV DEBSRC "http://downloads.skewed.de/apt/bionic bionic universe"
ENV PYTHON_PIP_VERSION 18.1

# Install Dependencies
RUN apt-get update && \
  # Install gpg to allow key from publishers of Graph Tool
  apt-get install -y gnupg && \
  apt-key adv --batch --keyserver keyserver.ubuntu.com --recv-key $GPGKEY && \
  echo "deb $DEB" >> /etc/apt/sources.list && \
  echo "deb-src $DEBSRC" >> /etc/apt/sources.list && \
  # Install Python 3.7 and Graph Tool
  apt-get update && \
  apt-get -y install netcat netbase wget python3.7 python3-distutils \ 
    python3-graph-tool && \
  apt-get clean && \
  ln -s /usr/bin/python3.7 /usr/local/bin/python && \
  # Install pip
  wget -O get-pip.py 'https://bootstrap.pypa.io/get-pip.py' && \
  python get-pip.py --disable-pip-version-check --no-cache-dir \
    "pip==$PYTHON_PIP_VERSION" && \
  rm -f get-pip.py && \
  pip install numpy scipy --upgrade

# Setup Application Environment
COPY requirements.txt .
RUN pip install pip --upgrade && \
  pip install --no-cache-dir --quiet --trusted-host pypi.python.org \
    -r requirements.txt

# Copy and Run Service
COPY config.yml .
COPY contribution contribution/
COPY run.sh .
CMD . /samaritan/services/metrics/contribution/run.sh
