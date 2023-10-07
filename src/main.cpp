#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "GPMF_parser.h"
#include "GPMF_mp4reader.h"

namespace py = pybind11;

PYBIND11_MODULE(gpmf_parser, m) {
    m.doc() = "pybind11 GPMF parser bindings";

    // Expose the necessary functions
    m.def("OpenMP4Source", &OpenMP4Source, "Open an MP4 source");
    m.def("CloseMP4Source", &CloseMP4Source, "Close an MP4 source");
    m.def("GetMP4PayloadSize", &GetMP4PayloadSize, "Get MP4 payload size");
    m.def("GetMP4Payload", &GetMP4Payload, "Get MP4 payload");
    
    m.def("GetGPMFTrackCount", &GetGPMFTrackCount, "Get count of GPMF tracks in MP4");
    m.def("GetGPMFPayloadCount", &GetGPMFPayloadCount, "Get count of GPMF payloads within a track");
    
    // Expose GPMF_stream data structure
    py::class_<GPMF_stream>(m, "GPMF_stream")
    .def(py::init<>())
    .def_readwrite("buffer", &GPMF_stream::buffer)
    .def_readwrite("buffer_size", &GPMF_stream::buffer_size)
    .def_readwrite("pos", &GPMF_stream::pos);
    
    // Expose other structures and functions if needed...
}
