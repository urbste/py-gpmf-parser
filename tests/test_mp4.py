import gpmf_parser
import json

def extract_payloads_from_mp4(mp4_filepath):

    handle = gpmf_parser.OpenMP4Source(mp4_filepath, gpmf_parser.MOV_GPMF_TRAK_TYPE, gpmf_parser.MOV_GPMF_TRAK_SUBTYPE, 0)
    dur = gpmf_parser.GetDuration(handle)
    print("duration: " + str(dur))
    num_payloads = gpmf_parser.GetNumberPayloads(handle)
    print("num_payloads: " + str(num_payloads))
    frames, numer, demon = gpmf_parser.GetVideoFrameRateAndCount(handle)
    print("frames: " + str(frames))
    print("numer: " + str(numer))
    print("demon: " + str(demon))

    for i in range(num_payloads):
        payloadsize = gpmf_parser.GetPayloadSize(handle, i)
        res_handle = 0
        res_handle = gpmf_parser.GetPayloadResource(handle, res_handle, payloadsize)
        payload = gpmf_parser.GetPayload(handle, res_handle, i, payloadsize)
        times = gpmf_parser.GetPayloadTime(handle, i)
        ret, stream = gpmf_parser.GPMF_Init(payload, payloadsize)
        if ret != gpmf_parser.GPMF_ERROR.GPMF_OK:
            print("GPMF_Init failed")
            return

        while gpmf_parser.GPMF_ERROR.GPMF_OK == gpmf_parser.GPMF_FindNext(stream, gpmf_parser.Str2FourCC("STRM"), gpmf_parser.GPMF_RECURSE_LEVELS_AND_TOLERANT):
            print("here")
            sensortype = gpmf_parser.Str2FourCC("ACCL")
            if gpmf_parser.IsValidFourCC(sensortype):
                if gpmf_parser.GPMF_ERROR.GPMF_OK != gpmf_parser.GPMF_FindNext(stream, sensortype, gpmf_parser.GPMF_RECURSE_LEVELS_AND_TOLERANT):
                    continue
            else:
                ret = gpmf_parser.SeekToSamples(stream)
                if gpmf_parser.GPMF_ERROR.GPMF_OK != ret:
                    continue
            print("here")
            key = gpmf_parser.GPMF_Key(stream)
            type = gpmf_parser.GPMF_Type(stream)
            samples = gpmf_parser.GPMF_Repeat(stream)
            elements = gpmf_parser.GPMF_ElementsInStruct(stream)
            rawdata = gpmf_parser.GPMF_RawData(stream)
            
            # Constants and initializations
            MAX_UNITS = 64
            MAX_UNITLEN = 8
            units = [["" for _ in range(MAX_UNITLEN)] for _ in range(MAX_UNITS)]
            complextype = [""] * MAX_UNITS
            
            # Search for TYPE if Complex
            find_stream = gpmf_parser.GPMFStreamWrapper(stream)
            type_samples = 0
            if gpmf_parser.GPMF_FindPrev(find_stream, gpmf_parser.GPMFKey.TYPE, gpmf_parser.GPMF_CURRENT_LEVEL_AND_TOLERANT) == gpmf_parser.GPMF_OK:
                data = gpmf_parser.GPMF_RawData(find_stream)
                ssize = gpmf_parser.GPMF_StructSize(find_stream)
                if ssize > MAX_UNITLEN - 1:
                    ssize = MAX_UNITLEN - 1
                type_samples = gpmf_parser.GPMF_Repeat(find_stream)
                
                for i in range(type_samples):
                    if i >= MAX_UNITS:
                        break
                    complextype[i] = data[i]

            if samples:
                buffersize = samples * elements * 8  # sizeof(double)
                ret, data = gpmf_parser.GPMF_ScaledData(stream, buffersize, 0, samples, gpmf_parser.GPMF_SampleType.DOUBLE)
                print(ret)
                if gpmf_parser.GPMF_ERROR.GPMF_OK == ret:
                    ptr = 0
                    pos = 0
                    for i in range(samples):
                        print("  {} ".format(gpmf_parser.fourCC_to_string(key)), end="")
                        for j in range(elements):
                            if type ==gpmf_parser.GPMF_SampleType.STRING_ASCII:
                                print(rawdata[pos], end="")
                                pos += 1
                                ptr += 1
                            elif type_samples == 0:
                                print("{:.3f}, ".format(data[ptr]), end="")
                                ptr += 1
                            elif type_samples and complextype[j] == gpmf_parser.GPMF_SampleType.FOURCC:
                                ptr += 1
                                print("{}, ".format(rawdata[pos:pos+4]), end="")
                                pos += 4

        gpmf_parser.GPMF_ResetState(stream)

    gpmf_parser.CloseSource(handle)

# Usage
extract_payloads_from_mp4("/media/steffen/Data/VideoData/1/GH019523_1696340337370.MP4")