from py_gpmf_parser.gopro_telemetry_extractor import GoProTelemetryExtractor
import os

if __name__ == "__main__":
    # Usage
    import glob

    for filepath in glob.iglob('/home/steffen/projects/py-gpmf-parser/gpmf-parser/samples/*.mp4'):
        # print the filename:
        print(os.path.basename(filepath))
        if "max-heromode" not in filepath:
            continue
        extractor = GoProTelemetryExtractor(filepath)
        extractor.open_source()
        # accl, accl_t = extractor.extract_data("ACCL")
        # gyro, gyro_t = extractor.extract_data("GYRO")
        # gps, gps_t = extractor.extract_data("GPS5")
        grav, grav_t = extractor.extract_data("GRAV")
        extractor.close_source()


