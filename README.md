# py-gpmf-parser

Python bindings for the GoPro Metadata Format (GPMF) parser, allowing for easy extraction of telemetry data from GoPro videos. 

## Overview

This repository offers a Pythonic interface to the GPMF parser, enabling users to extract sensor data like ACCL, GYRO, GPS5, GRAV, and more from GoPro videos.

It provides access to most of the low-level functions (have a look at the **src/gpmf_bindings.cpp**), but also includes a simple python class to extract the telemetry data. Extending it to more low-level stuff should be easy, just follow the structure that I used.

## Installation

To install the package, navigate to the root directory of the repository and run:
```bash
git clone --recursive https://github.com/urbste/py-gpmf-parser/
pip install .
```

## Usage

Either extract single streams
```python
filepath 'gpmf-parser/samples/max-heromode.mp4'
from py_gpmf_parser.gopro_telemetry_extractor import GoProTelemetryExtractor
extractor = GoProTelemetryExtractor(filepath)
extractor.open_source()
accl, accl_t = extractor.extract_data("ACCL")
gps, gps_t = extractor.extract_data("GPS5")
extractor.close_source()
```
or write multiple of them to a json file
```python
extractor = GoProTelemetryExtractor(filepath)
extractor.extract_data_to_json(os.path.basename(filepath)+".json", 
                                ["ACCL", "GYRO", "GPS5", "GRAV", "MAGN", "CORI", "IORI"])
extractor.close_source()
```

## To-Do List

- [ ] publish package
- [ ] document 
- [ ] check timestamps for GRAV and ACCL, not sure yet


## Acknowledgements
This is my first project using ChatGPT4 to create Python bindings for a C library. I learned a lot in the process. I do have some experience with pybind11, however, this C library was challenging due to the use of pointers (especially the GPMF_stream struct). ChatGPT4 was able to solve all the hurdles in the process. I had to iterate some prompts and also prompt with specific errors, but in the end we figured it out ;)
It also created the pip-publish.yml file to automatically publish the wheel on PyPI.
It took me about 6-7 hours to write the library, which I would say is probably half of the time it would have taken me without ChatGPT.