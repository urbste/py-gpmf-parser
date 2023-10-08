import py_gpmf_parser as pgfp
import numpy as np

class GoProTelemetryExtractor:
    def __init__(self, mp4_filepath):
        self.mp4_filepath = mp4_filepath
        self.handle = None

        self.reshape_dict = {
            "ACCL": (-1, 3),
            "GYRO": (-1, 3),
            "GPS5": (-1, 5),
            "GRAV": (-1, 3),
        }

    def open_source(self):
        if self.handle is None:
            self.handle = pgfp.OpenMP4Source(self.mp4_filepath, pgfp.MOV_GPMF_TRAK_TYPE, pgfp.MOV_GPMF_TRAK_SUBTYPE, 0)
        else:
            raise ValueError("Source is already opened!")

    def close_source(self):
        if self.handle is not None:
            pgfp.CloseSource(self.handle)
            self.handle = None
        else:
            raise ValueError("No source to close!")

    def extract_data(self, sensor_type):
        if self.handle is None:
            raise ValueError("Source is not opened!")

        results = []
        timestamps = []

        rate, start, end = pgfp.GetGPMFSampleRate(self.handle, pgfp.Str2FourCC(sensor_type), pgfp.Str2FourCC("SHUT"))

        num_payloads = pgfp.GetNumberPayloads(self.handle)
        for i in range(num_payloads):
            payloadsize = pgfp.GetPayloadSize(self.handle, i)
            res_handle = 0
            res_handle = pgfp.GetPayloadResource(self.handle, res_handle, payloadsize)
            payload = pgfp.GetPayload(self.handle, res_handle, i, payloadsize)
            
            ret, t_in, t_out = pgfp.GetPayloadTime(self.handle, i)

            delta_t = t_out - t_in

            ret, stream = pgfp.GPMF_Init(payload, payloadsize)
            if ret != pgfp.GPMF_ERROR.GPMF_OK:
                continue

            while pgfp.GPMF_ERROR.GPMF_OK == pgfp.GPMF_FindNext(stream, pgfp.Str2FourCC("STRM"), pgfp.GPMF_RECURSE_LEVELS_AND_TOLERANT):
                if pgfp.GPMF_ERROR.GPMF_OK != pgfp.GPMF_FindNext(stream, pgfp.Str2FourCC(sensor_type), pgfp.GPMF_RECURSE_LEVELS_AND_TOLERANT):
                    continue

                key = pgfp.GPMF_Key(stream)
                elements = pgfp.GPMF_ElementsInStruct(stream)
                rawdata = pgfp.GPMF_RawData(stream)
                samples = pgfp.GPMF_Repeat(stream)
                if samples:
                    buffersize = samples * elements * 8
                    ret, data = pgfp.GPMF_ScaledData(stream, buffersize, 0, samples, pgfp.GPMF_SampleType.DOUBLE)
                    data = data[:samples*elements]
                    if pgfp.GPMF_ERROR.GPMF_OK == ret:
                        results.extend(np.reshape(data, self.reshape_dict[sensor_type]))
                        timestamps.extend([t_in + i*delta_t/samples for i in range(samples)])
            pgfp.GPMF_ResetState(stream)

        return np.array(results), np.array(timestamps) + start
    

    def extract_data_to_json(self, json_file, sensor_types=["ACCL", "GYRO", "GPS5", "GRAV"]):
        import json
        out_dict = {}
        for sensor in sensor_types:
            data, timestamps = self.extract_data(sensor)
            out_dict.update({sensor: {"data": data.tolist(), "timestamps_s": timestamps.tolist()}})
        with open(json_file, "w") as f:
            json.dump(out_dict, f)

    def close(self):
        self.close_source()
