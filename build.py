from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import pybind11
import platform
import sys

extra_compile_args = ["-std=c++17"]
extra_link_args = []

# Add macOS-specific flags only if on macOS
if sys.platform == "darwin":
    extra_compile_args += ["-mmacosx-version-min=11.0"]
    extra_link_args += [
        "-stdlib=libc++",
        "-mmacosx-version-min=11.0",
    ]

ext_modules = [
    Extension(
        "py_gpmf_parser.gpmf_parser",
        sources=[
            "src/gpmf_bindings.cpp",
            "gpmf-parser/GPMF_parser.c",
            "gpmf-parser/GPMF_utils.c",
            "gpmf-parser/demo/GPMF_mp4reader.c",
        ],
        include_dirs=[
            pybind11.get_include(),
            "gpmf-parser",
            "gpmf-parser/demo",
        ],
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
]

setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
