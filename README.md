# py-gpmf-parser

**Python bindings for the GoPro Metadata Format (GPMF) parser, with robust cross-platform build support (Linux, macOS, Apple Silicon).**

---

## Overview

This package offers a Pythonic interface to the [GoPro GPMF parser](https://github.com/gopro/gpmf-parser), allowing you to extract rich telemetry data (e.g., GPS, ACCL, GYRO, GRAV) from GoPro video files.  
You can access both low-level C functions (see `src/gpmf_bindings.cpp`) and high-level helpers for typical telemetry extraction.

---

## Features

- **Access all GoPro sensor data:** GPS5, ACCL, GYRO, GRAV, MAGN, and more
- **Easy, high-level interface:** extract streams as NumPy arrays or write telemetry to JSON
- **Low-level C API exposure** via pybind11
- **Robust build logic** for Linux, Intel macOS, and Apple Silicon macOS (M1/M2)
- **PEP 621 modern packaging**: only `pyproject.toml` required!
- **Actively maintained & community friendly!**

---

## Installation

### 1. Clone recursively

```bash
git clone --recursive https://github.com/moscamich/py-gpmf-parser.git
cd py-gpmf-parser
```

### 2. Build locally

```bash
python build.py build_ext --inplace
```

**Note:**  
Installing with pip install . will not build the C++ extension correctly with the current setup.
For reliable installation, always use the build command above.

---

## (Optional) Using uv
If you use uv for environment and dependency management:

```bash
uv run build.py build_ext --inplace
uv sync
```
## Usage

Extract a single telemetry stream:
```python
from py_gpmf_parser.gopro_telemetry_extractor import GoProTelemetryExtractor

filepath = "gpmf-parser/samples/max-heromode.mp4"
extractor = GoProTelemetryExtractor(filepath)
extractor.open_source()
accl, accl_t = extractor.extract_data("ACCL")
gps, gps_t = extractor.extract_data("GPS5")
extractor.close_source()
```

Write multiple streams to JSON:
```python
extractor = GoProTelemetryExtractor(filepath)
extractor.extract_data_to_json(
    "output.json",
    ["ACCL", "GYRO", "GPS5", "GRAV", "MAGN", "CORI", "IORI"]
)
extractor.close_source()
```

---

## Packaging: Only `pyproject.toml` Needed!

This project follows modern Python packaging standards ([PEP 621](https://packaging.python.org/en/latest/specifications/pyproject-toml/)).  
**You do NOT need `setup.cfg` or `setup.py`.**  
All metadata and build info lives in `pyproject.toml` and (optionally) `build.py` for custom C/C++ logic.

If you are contributing, just edit `pyproject.toml`—no more redundant files or deprecation warnings!

---

## Cross-Platform Build Details

### macOS (Apple Silicon, M1/M2)

- **No manual flag changes required!**
- If you encounter SDK or deployment target issues, set:
  ```bash
  export SDKROOT=$(xcrun --sdk macosx --show-sdk-path)
  export MACOSX_DEPLOYMENT_TARGET=11.0
  export CXXFLAGS="-isysroot $SDKROOT -mmacosx-version-min=11.0"
  export LDFLAGS="-isysroot $SDKROOT -mmacosx-version-min=11.0 -stdlib=libc++"
  ```

### Linux

- No special steps required if you have a C++ toolchain (`g++`), Python dev headers, and standard build tools.

---

## Troubleshooting

- If you get an error about `-std=c++17` not allowed with `C`, **make sure you're using the included `build.py`**, not a generic `setup.py`.
- Ensure you have the submodule checked out (`git submodule update --init --recursive`).

---

## Contributing

PRs and issues welcome!  
Tested and maintained on latest Python 3.8–3.12, Ubuntu 22+, and macOS 12+.

---

## Credits & Acknowledgements

- Original library: [urbste/py-gpmf-parser](https://github.com/urbste/py-gpmf-parser)
- Fork & cross-platform build: [moscamich](https://github.com/moscamich)
- Build system improved with help from ChatGPT4 and open-source community suggestions.

---

## License

Apache-2.0  
See [LICENSE](LICENSE).
