FROM python:3.9-slim-buster
WORKDIR /prsr

RUN apt-get update && apt-get install -qq --no-install-recommends \
      netcat=1.10-* \
      wget=1.20.* && \
    wget --quiet -O /tmp/srcml.deb \
      "http://131.123.42.38/lmcrs/v1.0.0/srcml_1.0.0-1_ubuntu18.04.deb" && \
    apt-get install -qq --no-install-recommends /tmp/srcml.deb && \
    rm /tmp/srcml.deb && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH="${PYTHONPATH}:/usr/lib/python3/dist-packages/"

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY LICENSE .
COPY VERSION .
COPY config.yml .
COPY prsr prsr/
COPY run.sh .

ENTRYPOINT ["/bin/bash", "./run.sh"]

