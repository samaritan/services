FROM docker.pkg.github.com/samaritan/supplements/clang:0.1.0-alpha

WORKDIR /samaritan/services/parser
ENV PYTHON_PIP_VERSION 18.1

# Install Dependencies
RUN apt-get update && \
  # Install Python 3.7
  apt-get update && \
  apt-get -y install netcat netbase wget python3.7 python3-distutils && \
  apt-get clean && \
  ln -s /usr/bin/python3.7 /usr/local/bin/python && \
  # Install pip
  wget -qO get-pip.py "https://bootstrap.pypa.io/get-pip.py" && \
  python get-pip.py --disable-pip-version-check --no-cache-dir \
    "pip==$PYTHON_PIP_VERSION" && \
  rm -f get-pip.py && \
  # Install clang Python Bindings
  cd /tmp/ && \
  wget -q "https://github.com/llvm/llvm-project/releases/download/llvmorg-8.0.1/cfe-8.0.1.src.tar.xz.sig" && \
  wget -q "https://github.com/llvm/llvm-project/releases/download/llvmorg-8.0.1/cfe-8.0.1.src.tar.xz" && \
  gpg --verify cfe-8.0.1.src.tar.xz.sig cfe-8.0.1.src.tar.xz && \
  mkdir clang && tar xf cfe-8.0.1.src.tar.xz -C clang --strip-components=1 && \
  cp -r clang/bindings/python/clang /usr/lib/python3.7/ && \
  rm -rf cfe-8.0.1.src.tar.xz.sig cfe-8.0.1.src.tar.xz clang

# Setup Application Environment
COPY requirements.txt .
RUN pip install --no-cache-dir --quiet --trusted-host pypi.python.org \
  -r requirements.txt

# Copy and Run Service
COPY config.yml .
COPY parser parser/
COPY run.sh .
CMD . /samaritan/services/parser/run.sh
