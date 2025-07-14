from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import pybind11
import sys
import os

class BuildExt(build_ext):
    def build_extensions(self):
        # C flags (if any) and C++ flags
        c_opts = []
        cpp_opts = ["-std=c++17"]
        link_opts = []
        if sys.platform == "darwin":
            cpp_opts += ["-mmacosx-version-min=11.0"]
            link_opts += ["-stdlib=libc++", "-mmacosx-version-min=11.0"]

        for ext in self.extensions:
            # Clear and re-add per source
            ext.extra_compile_args = []
            for source in ext.sources:
                if source.endswith('.cpp'):
                    ext.extra_compile_args += cpp_opts
                else:
                    ext.extra_compile_args += c_opts
            ext.extra_link_args = link_opts

        super().build_extensions()

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
        # extra_compile_args=[],  # Leave empty, will be set in BuildExt
    ),
]

setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": BuildExt},
)
