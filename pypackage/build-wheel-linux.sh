#!/bin/bash

function repair_wheel {
    wheel="$1"
    if ! auditwheel show "$wheel"; then
        echo "Skipping non-platform wheel $wheel"
    else
         auditwheel repair "$wheel" -w /io/wheelhouse/
    fi
}

set -e -u -x

cd /io
mkdir -p wheelhouse

# we cannot simply use `pip` or `python`, since points to old 2.7 version
PYBIN="/opt/python/$PYTHON_VERSION/bin"
PYVER_NUM=$($PYBIN/python -c "import sys;print(sys.version.split(\" \")[0])")
PYTHONVER="$(basename $(dirname $PYBIN))"

echo "Python bin path: $PYBIN"
echo "Python version number: $PYVER_NUM"
echo "Python version: $PYTHONVER"

export PATH=$PYBIN:$PATH

${PYBIN}/pip install --upgrade pip setuptools wheel auditwheel pybind11 numpy

PLAT=manylinux_2_28_x86_64
"${PYBIN}/python" setup.py bdist_wheel --plat-name=$PLAT

cp /io/dist/*.whl /io/wheelhouse
rm -rf /io/dist

# Bundle external shared libraries into the wheels
for whl in /io/wheelhouse/*.whl; do
    repair_wheel "$whl"
done