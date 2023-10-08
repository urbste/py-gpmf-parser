from py_gpmf_parser.gopro_telemetry_extractor import GoProTelemetryExtractor
import os

if __name__ == "__main__":
    # Usage
    import glob

    for filepath in glob.iglob('gpmf-parser/samples/*.mp4'):
        # print the filename:
        extractor = GoProTelemetryExtractor(filepath)
        extractor.open_source()
        accl, accl_t = extractor.extract_data("ACCL")
        gyro, gyro_t = extractor.extract_data("GYRO")
        gps, gps_t = extractor.extract_data("GPS5")
        grav, grav_t = extractor.extract_data("GRAV")

        extractor.extract_data_to_json(os.path.basename(filepath)+".json", ["ACCL", "GYRO", "GPS5", "GRAV"])

        extractor.close_source()
