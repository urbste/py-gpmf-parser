#!/bin/bash
set -e -x

# Convert the space-separated string into an array
IFS=' ' read -ra PYTHON_VERSIONS <<< "$PYTHON_VERSIONS"

# Compile wheels for multiple Python versions
for version in "${PYTHON_VERSIONS[@]}"; do
    PYBIN="/opt/python/${version}/bin"
    "${PYBIN}/pip" wheel /io/ -w wheelhouse/
done

# Repair wheels
for whl in wheelhouse/*.whl; do
    auditwheel repair "$whl" -w /io/wheelhouse/
done