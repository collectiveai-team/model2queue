FROM ubuntu:22.04
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV DEBIAN_FRONTEND noninteractive

ARG PYTHON_VERSION
ARG PIP_VERSION
# OS packages
RUN sed -i 's/# deb-src/deb-src/' /etc/apt/sources.list \
    && apt-get update --fix-missing; exit 0

# OS packages
RUN apt-get install -y --no-install-recommends \
    curl \
    wget \
    git-core \
    htop \
    unzip \
    zsh \
    vim \
    parallel \
    gcc \
    python3-setuptools \
    ${PYTHON_VERSION} \
    ${PYTHON_VERSION}-dev \
    ${PYTHON_VERSION}-distutils \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/tmp/* /var/lib/apt/lists/*

# Set default python version
RUN update-alternatives --install /usr/bin/python python /usr/bin/${PYTHON_VERSION} 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/${PYTHON_VERSION} 1


WORKDIR /tmp

# Install pip
RUN wget https://github.com/pypa/pip/archive/refs/tags/${PIP_VERSION}.zip --no-check-certificate \
    && unzip ${PIP_VERSION}.zip \
    && cd pip-${PIP_VERSION} \
    && python setup.py install

# Install pytorch


# Install model2queue
COPY ./src/model2queue  /tmp/model2queue

RUN --mount=type=cache,target=/root/.cache \
    pip install ./model2queue

# Clean
RUN rm -rf /tmp/*

WORKDIR /root
