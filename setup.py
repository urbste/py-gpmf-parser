# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup, find_packages
import pybind11

__version__ = "0.0.1"

# The main interface is through Pybind11Extension.
# * You can add cxx_std=11/14/17, and then build_ext can be removed.
# * You can set include_pybind11=false to add the include directory yourself,
#   say from a submodule.
#
# Note:
#   Sort input source files if you glob sources to ensure bit-for-bit
#   reproducible builds (https://github.com/pybind/python_example/pull/53)

ext_modules = [
    Pybind11Extension(
        "gpmf_parser",
        ['src/gpmf_bindings.cpp',
         'gpmf-parser/GPMF_parser.c',
         'gpmf-parser/GPMF_utils.c',
         'gpmf-parser/demo/GPMF_mp4reader.c'],
        include_dirs=[
            pybind11.get_include(),
            'gpmf-parser',
            'gpmf-parser/demo/',
        ],
        # Example: passing in the version to the compiled code
        define_macros = [('VERSION_INFO', __version__)],
        ),
]

setup(
    name="py_gpmf_parser",
    version=__version__,
    author="Steffen Urban",
    author_email="urbste@gmail.com",
    url="https://github.com/urbste/py-gpmf-parser",
    description="Python bindings for the gpmf-parser library using pybind",
    long_description="",
    ext_modules=ext_modules,
    packages=find_packages(),
    package_data={"gopro_telemetry_extractor": ["*"]},  # Include all files in py_gpmf_parser
    extras_require={"test": "pytest"},
    # Currently, build_ext only provides an optional "highest supported C++
    # level" feature, but in the future it may provide more features.
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
)
