#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "GPMF_parser.h"
#include "GPMF_mp4reader.h"
#include <iostream>
namespace py = pybind11;

class GPMF_stream_wrapper {
public:

    GPMF_stream_wrapper() : stream{}, buffer_reference{} {}
    GPMF_stream_wrapper(py::array_t<uint32_t> buffer_array) 
        : buffer_reference(buffer_array) // Store a reference to the numpy array
    {
        auto buffer_info = buffer_array.request();
        stream.buffer = static_cast<uint32_t*>(buffer_info.ptr);
    }

    GPMF_stream_wrapper(const GPMF_stream_wrapper& other)
        : stream(other.stream), buffer_reference(other.buffer_reference) {}


    GPMF_stream* get() {
        return &stream;
    }

    // Add other necessary member functions and operators to access the underlying GPMF_stream

private:
    GPMF_stream stream;
    py::object buffer_reference; // This keeps the numpy array alive as long as the GPMF_stream_wrapper is alive
};

py::tuple GetVideoFrameRateAndCountWrapper(size_t handle) {
    uint32_t numer = 0;
    uint32_t demon = 0;
    uint32_t frames = GetVideoFrameRateAndCount(handle, &numer, &demon);
    
    return py::make_tuple(frames, numer, demon);
}

// Wrapping GetPayload function
std::vector<uint32_t> GetPayloadWrapper(
    size_t mp4handle, size_t resHandle, uint32_t index, uint32_t payloadsize)
{
    uint32_t* payload = GetPayload(mp4handle, resHandle, index);
    if (payload)
    {
        // Assuming the payload has a fixed size or you have a way to determine its size.
        return std::vector<uint32_t>(payload, payload + payloadsize);
    }
    return std::vector<uint32_t>();
}

std::tuple<double, double> GetPayloadTimeWrapper(size_t handle, uint32_t index) {
    double in_time = 0.0;
    double out_time = 0.0;
    
    uint32_t result = GetPayloadTime(handle, index, &in_time, &out_time);
    if (result == MP4_ERROR_OK) {
        return std::make_tuple(in_time, out_time);
    }

    throw std::runtime_error("Error getting payload time");
}

std::tuple<GPMF_ERR, GPMF_stream_wrapper> GPMF_InitWrapper(py::array_t<uint32_t> buffer_array, uint32_t datasize)
{       
    GPMF_stream_wrapper stream_wrapper(buffer_array);
    GPMF_ERR err = GPMF_Init(stream_wrapper.get(), stream_wrapper.get()->buffer, datasize);

    return {err, stream_wrapper};
}

inline uint32_t Str2FourCC(const std::string& s)
{
    if (s.size() < 4)
        throw std::runtime_error("Input string must have at least 4 characters.");

    return ((s[0] << 0) | (s[1] << 8) | (s[2] << 16) | (s[3] << 24));
}

inline std::string fourCC_to_string(uint32_t k) {
    char chars[5] = {
        static_cast<char>((k >> 0) & 0xff),
        static_cast<char>((k >> 8) & 0xff),
        static_cast<char>((k >> 16) & 0xff),
        static_cast<char>((k >> 24) & 0xff),
        '\0' // Null terminator
    };
    return std::string(chars);
}

bool IsValidFourCC(uint32_t a)
{
    return (
        ((((a>>24)&0xff)>='a'&&((a>>24)&0xff)<='z') || (((a>>24)&0xff)>='A'&&((a>>24)&0xff)<='Z') || (((a>>24)&0xff)>='0'&&((a>>24)&0xff)<='9') || (((a>>24)&0xff)==' ')) &&
        ((((a>>16)&0xff)>='a'&&((a>>16)&0xff)<='z') || (((a>>16)&0xff)>='A'&&((a>>16)&0xff)<='Z') || (((a>>16)&0xff)>='0'&&((a>>16)&0xff)<='9') || (((a>>16)&0xff)==' ')) &&
        ((((a>>8)&0xff)>='a'&&((a>>8)&0xff)<='z') || (((a>>8)&0xff)>='A'&&((a>>8)&0xff)<='Z') || (((a>>8)&0xff)>='0'&&((a>>8)&0xff)<='9') || (((a>>8)&0xff)==' ')) &&
        ((((a>>0)&0xff)>='a'&&((a>>0)&0xff)<='z') || (((a>>0)&0xff)>='A'&&((a>>0)&0xff)<='Z') || (((a>>0)&0xff)>='0'&&((a>>0)&0xff)<='9') || (((a>>0)&0xff)==' '))
    );
}

py::bytes GPMF_RawDataWrapper(GPMF_stream_wrapper &ms_wrapper) {
    GPMF_stream* ms = ms_wrapper.get();
    if (ms && ms->buffer) {
        char* data_ptr = (char*)&ms->buffer[ms->pos + 2];
        
        // Assuming you know the size of the data. If it's dynamic, adjust accordingly.
        uint32_t size_of_data = GPMF_RawDataSize(ms); // Assuming such a function exists
        
        return py::bytes(data_ptr, size_of_data);
    }
    throw py::value_error("Invalid GPMF_stream");
}


std::pair<GPMF_ERR, std::vector<double>> GPMF_ScaledDataWrapper(GPMF_stream_wrapper &ms_wrapper, uint32_t buffersize, uint32_t sample_offset, uint32_t read_samples, GPMF_SampleType outputType) {
    GPMF_stream* ms = ms_wrapper.get();
    std::vector<double> output_buffer(buffersize, 0);
    GPMF_ERR ret = GPMF_ScaledData(ms, output_buffer.data(), buffersize, sample_offset, read_samples, outputType);
    return {ret, output_buffer};
}



PYBIND11_MODULE(gpmf_parser, m) {
    m.doc() = "pybind11 GPMF parser bindings";

    // Expose the necessary functions
    m.def("OpenMP4Source", &OpenMP4Source, "Open an MP4 source");
    m.def("GetDuration", &GetDuration, "Get duration of the MP4");
    m.def("CloseSource", &CloseSource, "Close and free resources associated with the handle");
    m.def("GetNumberPayloads", &GetNumberPayloads, "Get the number of payloads for a given MP4 handle");
    
    py::class_<GPMF_stream_wrapper>(m, "GPMFStreamWrapper")
        .def(py::init<>())
        .def(py::init<py::array_t<uint32_t>>())
        .def("get", &GPMF_stream_wrapper::get)
        .def(py::init<const GPMF_stream_wrapper &>());

    m.def("Str2FourCC", &Str2FourCC, "Convert a string to a 32-bit FOURCC code.",
          py::arg("s"));
    m.def("IsValidFourCC", &IsValidFourCC, "Check if a given fourcc is valid");
    m.def("fourCC_to_string", &fourCC_to_string, "Convert a 4-byte integer to a string representation");


    m.def("GetVideoFrameRateAndCount", &GetVideoFrameRateAndCountWrapper, 
        py::arg("handle"),
        "Get the video frame rate and count for a given handle. Returns a tuple (frames, numer, demon).");
    
    m.def("GetPayloadSize", &GetPayloadSize, 
        py::arg("handle"), py::arg("index"),
        "Get the payload size for a given handle and index.");

    m.def("GetPayloadResource", &GetPayloadResource, 
      py::arg("mp4handle"), py::arg("resHandle"), py::arg("payloadsize"),
      "Get or allocate a payload resource for a given MP4 handle.");

    m.def("GetPayload", &GetPayloadWrapper, 
        py::arg("mp4handle"), py::arg("resHandle"), py::arg("index"), py::arg("payloadsize"),
        "Get the payload for a given MP4 handle, resource handle, and index. Returns the payload as a bytes object.");
        
    m.def("GetPayloadTime", &GetPayloadTimeWrapper, 
        py::arg("handle"), py::arg("index"),
        "Get the in and out times for a given handle and index. Returns a tuple (in_time, out_time).");

    m.def("GPMF_Init", &GPMF_InitWrapper, "Initialize GPMF stream");

    // // Wrapping GPMF_CopyState function
    // m.def("GPMF_CopyState", [](GPMF_stream_wrapper& src, GPMF_stream_wrapper& dst) {
    //     return GPMF_CopyState(src.get(), dst.get());
    // }, "Copy the state from one stream wrapper to another");

    m.def("GPMF_Next", [](GPMF_stream_wrapper& stream_wrapper, GPMF_LEVELS recurse) {
        return GPMF_Next(stream_wrapper.get(), recurse);
    }, "Move to the next data structure within the current level");

    // Wrapping GPMF_FindNext function
    m.def("GPMF_FindNext", [](GPMF_stream_wrapper& wrapper, uint32_t fourcc, GPMF_LEVELS recurse) {
        return GPMF_FindNext(wrapper.get(), fourcc, recurse);
    }, "Find next GPMF data using the stream wrapper");

    m.def("GPMF_ResetState", [](GPMF_stream_wrapper& wrapper) {
        return GPMF_ResetState(wrapper.get());
    }, "Reset the state of the stream wrapper");

    m.def("GPMF_FindPrev", [](GPMF_stream_wrapper& wrapper, uint32_t fourcc, GPMF_LEVELS recurse) {
        return GPMF_FindPrev(wrapper.get(), fourcc, recurse);
    }, "Description for GPMF_FindPrev");

    m.def("GPMF_Key", [](GPMF_stream_wrapper& wrapper) {
        return GPMF_Key(wrapper.get());
    }, "Description for GPMF_Key");

    m.def("GPMF_Type", [](GPMF_stream_wrapper& wrapper) {
        return GPMF_Type(wrapper.get());
    }, "Description for GPMF_Type");

    m.def("GPMF_StructSize", [](GPMF_stream_wrapper& wrapper) {
        return GPMF_StructSize(wrapper.get());
    }, "Description for GPMF_StructSize");

    m.def("GPMF_ElementsInStruct", [](GPMF_stream_wrapper& wrapper) {
        return GPMF_ElementsInStruct(wrapper.get());
    }, "Description for GPMF_ElementsInStruct");

    m.def("GPMF_Repeat", [](GPMF_stream_wrapper& wrapper) {
        return GPMF_Repeat(wrapper.get());
    }, "Description for GPMF_Repeat");


    m.def("GPMF_RawDataSize", &GPMF_RawDataSize,
          "Description for GPMF_RawDataSize",
          py::arg("ms"));

    m.def("GPMF_FormattedDataSize", &GPMF_FormattedDataSize,
          "Description for GPMF_FormattedDataSize",
          py::arg("ms"));

    m.def("GPMF_ScaledDataSize", &GPMF_ScaledDataSize,
          "Description for GPMF_ScaledDataSize",
          py::arg("ms"),
          py::arg("type"));

    m.def("GPMF_NestLevel", &GPMF_NestLevel,
          "Description for GPMF_NestLevel",
          py::arg("ms"));

    m.def("GPMF_DeviceID", &GPMF_DeviceID,
          "Description for GPMF_DeviceID",
          py::arg("ms"));

    m.def("GPMF_ResetState", &GPMF_ResetState,
          "Reset the state of the GPMF_stream",
          py::arg("ms"));

    m.def("GPMF_RawData", &GPMF_RawDataWrapper, "A function that returns raw data as bytes");

    m.def("GPMF_ScaledData", &GPMF_ScaledDataWrapper, "Wrapped GPMF_ScaledData function.");


    m.attr("MOV_GPMF_TRAK_TYPE") = MOV_GPMF_TRAK_TYPE;
    m.attr("MOV_GPMF_TRAK_SUBTYPE") = MOV_GPMF_TRAK_SUBTYPE;
    m.attr("MOV_VIDE_TRAK_TYPE") = MOV_VIDE_TRAK_TYPE;
    m.attr("MOV_SOUN_TRAK_TYPE") = MOV_SOUN_TRAK_TYPE;
    m.attr("MOV_AVC1_SUBTYPE") = MOV_AVC1_SUBTYPE;
    m.attr("MOV_HVC1_SUBTYPE") = MOV_HVC1_SUBTYPE;
    m.attr("MOV_MP4A_SUBTYPE") = MOV_MP4A_SUBTYPE;
    m.attr("MOV_CFHD_SUBTYPE") = MOV_CFHD_SUBTYPE;
    m.attr("AVI_VIDS_TRAK_TYPE") = AVI_VIDS_TRAK_TYPE;
    m.attr("AVI_CFHD_SUBTYPE") = AVI_CFHD_SUBTYPE;

    py::enum_<MP4READER_ERROR>(m, "MP4READER_ERROR")
        .value("MP4_ERROR_OK", MP4_ERROR_OK)
        .value("MP4_ERROR_MEMORY", MP4_ERROR_MEMORY)
        .export_values();

    py::enum_<GPMF_LEVELS>(m, "GPMF_LEVELS")
        .value("GPMF_CURRENT_LEVEL", GPMF_CURRENT_LEVEL)
        .value("GPMF_CURRENT_LEVEL_AND_TOLERANT", static_cast<GPMF_LEVELS>(GPMF_CURRENT_LEVEL | GPMF_TOLERANT))
        .value("GPMF_RECURSE_LEVELS", GPMF_RECURSE_LEVELS)
        .value("GPMF_RECURSE_LEVELS_AND_TOLERANT", static_cast<GPMF_LEVELS>(GPMF_RECURSE_LEVELS | GPMF_TOLERANT))
        .value("GPMF_TOLERANT", GPMF_TOLERANT)
        .export_values();

    py::enum_<GPMF_ERROR>(m, "GPMF_ERROR")
        .value("GPMF_OK", GPMF_OK)
        .value("GPMF_ERROR_MEMORY", GPMF_ERROR_MEMORY)
        .value("GPMF_ERROR_BAD_STRUCTURE", GPMF_ERROR_BAD_STRUCTURE)
        .value("GPMF_ERROR_BUFFER_END", GPMF_ERROR_BUFFER_END)
        .value("GPMF_ERROR_FIND", GPMF_ERROR_FIND)
        .value("GPMF_ERROR_LAST", GPMF_ERROR_LAST)
        .value("GPMF_ERROR_TYPE_NOT_SUPPORTED", GPMF_ERROR_TYPE_NOT_SUPPORTED)
        .value("GPMF_ERROR_SCALE_NOT_SUPPORTED", GPMF_ERROR_SCALE_NOT_SUPPORTED)
        .value("GPMF_ERROR_SCALE_COUNT", GPMF_ERROR_SCALE_COUNT)
        .value("GPMF_ERROR_UNKNOWN_TYPE", GPMF_ERROR_UNKNOWN_TYPE)
        .value("GPMF_ERROR_RESERVED", GPMF_ERROR_RESERVED)
        .export_values();

    py::enum_<GPMF_SampleType>(m, "GPMF_SampleType")
        .value("STRING_ASCII", GPMF_TYPE_STRING_ASCII)
        .value("SIGNED_BYTE", GPMF_TYPE_SIGNED_BYTE)
        .value("UNSIGNED_BYTE", GPMF_TYPE_UNSIGNED_BYTE)
        .value("SIGNED_SHORT", GPMF_TYPE_SIGNED_SHORT)
        .value("UNSIGNED_SHORT", GPMF_TYPE_UNSIGNED_SHORT)
        .value("FLOAT", GPMF_TYPE_FLOAT)
        .value("FOURCC", GPMF_TYPE_FOURCC)
        .value("SIGNED_LONG", GPMF_TYPE_SIGNED_LONG)
        .value("UNSIGNED_LONG", GPMF_TYPE_UNSIGNED_LONG)
        .value("Q15_16_FIXED_POINT", GPMF_TYPE_Q15_16_FIXED_POINT)
        .value("Q31_32_FIXED_POINT", GPMF_TYPE_Q31_32_FIXED_POINT)
        .value("SIGNED_64BIT_INT", GPMF_TYPE_SIGNED_64BIT_INT)
        .value("UNSIGNED_64BIT_INT", GPMF_TYPE_UNSIGNED_64BIT_INT)
        .value("DOUBLE", GPMF_TYPE_DOUBLE)
        .value("STRING_UTF8", GPMF_TYPE_STRING_UTF8)
        .value("UTC_DATE_TIME", GPMF_TYPE_UTC_DATE_TIME)
        .value("GUID", GPMF_TYPE_GUID)
        .value("COMPLEX", GPMF_TYPE_COMPLEX)
        .value("COMPRESSED", GPMF_TYPE_COMPRESSED)
        .value("NEST", GPMF_TYPE_NEST)
        .value("EMPTY", GPMF_TYPE_EMPTY)
        .value("ERROR", GPMF_TYPE_ERROR)
        .export_values();

    py::enum_<GPMFKey>(m, "GPMFKey")
        .value("DEVICE", GPMF_KEY_DEVICE)
        .value("DEVICE_ID", GPMF_KEY_DEVICE_ID)
        .value("DEVICE_NAME", GPMF_KEY_DEVICE_NAME)
        .value("STREAM", GPMF_KEY_STREAM)
        .value("STREAM_NAME", GPMF_KEY_STREAM_NAME)
        .value("SI_UNITS", GPMF_KEY_SI_UNITS)
        .value("UNITS", GPMF_KEY_UNITS)
        .value("MATRIX", GPMF_KEY_MATRIX)
        .value("ORIENTATION_IN", GPMF_KEY_ORIENTATION_IN)
        .value("ORIENTATION_OUT", GPMF_KEY_ORIENTATION_OUT)
        .value("SCALE", GPMF_KEY_SCALE)
        .value("TYPE", GPMF_KEY_TYPE)
        .value("TOTAL_SAMPLES", GPMF_KEY_TOTAL_SAMPLES)
        .value("TICK", GPMF_KEY_TICK)
        .value("TOCK", GPMF_KEY_TOCK)
        .value("TIME_OFFSET", GPMF_KEY_TIME_OFFSET)
        .value("TIMING_OFFSET", GPMF_KEY_TIMING_OFFSET)
        .value("TIME_STAMP", GPMF_KEY_TIME_STAMP)
        .value("TIME_STAMPS", GPMF_KEY_TIME_STAMPS)
        .value("PREFORMATTED", GPMF_KEY_PREFORMATTED)
        .value("TEMPERATURE_C", GPMF_KEY_TEMPERATURE_C)
        .value("EMPTY_PAYLOADS", GPMF_KEY_EMPTY_PAYLOADS)
        .value("QUANTIZE", GPMF_KEY_QUANTIZE)
        .value("VERSION", GPMF_KEY_VERSION)
        .value("FREESPACE", GPMF_KEY_FREESPACE)
        .value("REMARK", GPMF_KEY_REMARK)
        .value("END", GPMF_KEY_END)
        .export_values();

    py::class_<GPMF_stream>(m, "GPMF_stream")
        .def(py::init<>())
        .def_readwrite("buffer_size_longs", &GPMF_stream::buffer_size_longs)
        .def_readwrite("pos", &GPMF_stream::pos)
        .def_readwrite("nest_level", &GPMF_stream::nest_level)
        .def_readwrite("device_count", &GPMF_stream::device_count)
        .def_readwrite("device_id", &GPMF_stream::device_id)
        .def_readwrite("cbhandle", &GPMF_stream::cbhandle)
        .def("get_last_level_pos", [](const GPMF_stream &s) {
            return std::vector<uint32_t>(s.last_level_pos, s.last_level_pos + GPMF_NEST_LIMIT);
        })
        .def("set_last_level_pos", [](GPMF_stream &s, const std::vector<uint32_t> &v) {
            std::copy(v.begin(), v.end(), s.last_level_pos);
        })
        // Repeat similar getter-setter pairs for nest_size and last_seek
        .def("get_device_name", [](const GPMF_stream &s) {
            return std::string(s.device_name);
        })
        .def("set_device_name", [](GPMF_stream &s, const std::string &name) {
            strncpy(s.device_name, name.c_str(), sizeof(s.device_name));
        });
}
