import py_gpmf_parser as pgfp
import json


def extract_payloads_from_mp4(mp4_filepath):

    handle = pgfp.OpenMP4Source(mp4_filepath, pgfp.MOV_GPMF_TRAK_TYPE, pgfp.MOV_GPMF_TRAK_SUBTYPE, 0)
    dur = pgfp.GetDuration(handle)
    print("duration: " + str(dur))
    num_payloads = pgfp.GetNumberPayloads(handle)
    print("num_payloads: " + str(num_payloads))
    frames, numer, demon = pgfp.GetVideoFrameRateAndCount(handle)
    print("frames: " + str(frames))
    print("numer: " + str(numer))
    print("demon: " + str(demon))

    for i in range(num_payloads):
        payloadsize = pgfp.GetPayloadSize(handle, i)
        res_handle = 0
        res_handle = pgfp.GetPayloadResource(handle, res_handle, payloadsize)
        payload = pgfp.GetPayload(handle, res_handle, i, payloadsize)
        times = pgfp.GetPayloadTime(handle, i)
        ret, stream = pgfp.GPMF_Init(payload, payloadsize)
        if ret != pgfp.GPMF_ERROR.GPMF_OK:
            print("GPMF_Init failed")
            return

        while pgfp.GPMF_ERROR.GPMF_OK == pgfp.GPMF_FindNext(stream, pgfp.Str2FourCC("STRM"), pgfp.GPMF_RECURSE_LEVELS_AND_TOLERANT):

            sensortype = pgfp.Str2FourCC("ACCL")
            if pgfp.IsValidFourCC(sensortype):
                if pgfp.GPMF_ERROR.GPMF_OK != pgfp.GPMF_FindNext(stream, sensortype, pgfp.GPMF_RECURSE_LEVELS_AND_TOLERANT):
                    continue
            else:
                ret = pgfp.SeekToSamples(stream)
                if pgfp.GPMF_ERROR.GPMF_OK != ret:
                    continue

            key = pgfp.GPMF_Key(stream)
            type = pgfp.GPMF_Type(stream)
            samples = pgfp.GPMF_Repeat(stream)
            elements = pgfp.GPMF_ElementsInStruct(stream)
            rawdata = pgfp.GPMF_RawData(stream)
            
            # Constants and initializations
            MAX_UNITS = 64
            MAX_UNITLEN = 8
            units = [["" for _ in range(MAX_UNITLEN)] for _ in range(MAX_UNITS)]
            complextype = [""] * MAX_UNITS
            
            # Search for TYPE if Complex
            find_stream = pgfp.GPMFStreamWrapper(stream)
            type_samples = 0
            if pgfp.GPMF_FindPrev(find_stream, pgfp.GPMFKey.TYPE, pgfp.GPMF_CURRENT_LEVEL_AND_TOLERANT) == pgfp.GPMF_OK:
                data = pgfp.GPMF_RawData(find_stream)
                ssize = pgfp.GPMF_StructSize(find_stream)
                if ssize > MAX_UNITLEN - 1:
                    ssize = MAX_UNITLEN - 1
                type_samples = pgfp.GPMF_Repeat(find_stream)
                
                for i in range(type_samples):
                    if i >= MAX_UNITS:
                        break
                    complextype[i] = data[i]

            if samples:
                buffersize = samples * elements * 8  # sizeof(double)
                ret, data = pgfp.GPMF_ScaledData(stream, buffersize, 0, samples, pgfp.GPMF_SampleType.DOUBLE)
                print(ret)
                if pgfp.GPMF_ERROR.GPMF_OK == ret:
                    ptr = 0
                    pos = 0
                    for i in range(samples):
                        print("  {} ".format(pgfp.fourCC_to_string(key)), end="")
                        for j in range(elements):
                            if type ==pgfp.GPMF_SampleType.STRING_ASCII:
                                print(rawdata[pos], end="")
                                pos += 1
                                ptr += 1
                            elif type_samples == 0:
                                print("{:.3f}, ".format(data[ptr]), end="")
                                ptr += 1
                            elif type_samples and complextype[j] == pgfp.GPMF_SampleType.FOURCC:
                                ptr += 1
                                print("{}, ".format(rawdata[pos:pos+4]), end="")
                                pos += 4

        pgfp.GPMF_ResetState(stream)

    pgfp.CloseSource(handle)



if __name__ == "__main__":
    # Usage
    import glob

    for filepath in glob.iglob('../gpmf-parser/samples/*.mp4'):
        print(filepath)
        extract_payloads_from_mp4(filepath)