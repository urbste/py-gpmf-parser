FROM quay.io/pypa/manylinux2014_x86_64

COPY . ./io

RUN chmod +x /io/pypackage/build-wheels-linux.sh && bash /io/pypackage/build-wheels-linux.sh