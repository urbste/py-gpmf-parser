FROM quay.io/pypa/manylinux2014_x86_64

COPY . /io

ENV PYTHON_VERSION=cp312-cp312

WORKDIR /io

RUN chmod +x /io/pypackage/build-wheel-linux.sh && /io/pypackage/build-wheel-linux.sh