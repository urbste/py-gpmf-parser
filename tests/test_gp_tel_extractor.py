from py_gpmf_parser.gopro_telemetry_extractor import GoProTelemetryExtractor
import os

if __name__ == "__main__":
    # Usage
    import glob

    for filepath in glob.iglob('gpmf-parser/samples/*.mp4'):
        # print the filename:
        extractor = GoProTelemetryExtractor(filepath)
        extractor.open_source()
        shut, shut_t = extractor.extract_data("SHUT")
        timestamps = extractor.get_image_timestamps_s()
        accl, accl_t = extractor.extract_data("ACCL")
        gyro, gyro_t = extractor.extract_data("GYRO")
        gps, gps_t = extractor.extract_data("GPS5")
        grav, grav_t = extractor.extract_data("GRAV")
        magn, magn_t = extractor.extract_data("MAGN")
        cori, cori_t = extractor.extract_data("CORI")
        iori, iori_t = extractor.extract_data("IORI")
        gpsp, gpsp_t = extractor.extract_data("GPSP")
        gpsf, gpsf_t = extractor.extract_data("GPSF")
        gpsu, gpsu_t = extractor.extract_data("GPSU")

        extractor.extract_data_to_json(os.path.basename(filepath)+".json", 
                                       ["ACCL", "GYRO", "GPS5", "GPSP", "GPSF", "GPSU", "GRAV", "MAGN", "CORI", "IORI"])

        extractor.close_source()
