from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import pybind11
import sys

class BuildExt(build_ext):
    def build_extensions(self):
        # Platform-specific flags
        cpp_flags = ["-std=c++17"]
        link_flags = []
        if sys.platform == "darwin":
            cpp_flags += ["-mmacosx-version-min=11.0"]
            link_flags += ["-stdlib=libc++", "-mmacosx-version-min=11.0"]

        # Patch the compiler to only add c++ flags to .cpp files
        original_compile = self.compiler._compile

        def custom_compile(obj, src, ext, cc_args, extra_postargs, pp_opts):
            extra = list(extra_postargs) if extra_postargs else []
            if src.endswith(".cpp"):
                extra += cpp_flags
            # Only apply link flags when linking, not compiling
            original_compile(obj, src, ext, cc_args, extra, pp_opts)

        self.compiler._compile = custom_compile

        for ext in self.extensions:
            ext.extra_compile_args = []  # Let our patch handle it
            ext.extra_link_args = link_flags

        super().build_extensions()
        # Restore the original _compile method (good practice)
        self.compiler._compile = original_compile

ext_modules = [
    Extension(
        "gpmf_parser",
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
    ),
]

setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": BuildExt},
)