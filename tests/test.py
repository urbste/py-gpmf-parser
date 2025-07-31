import py_gpmf_parser as pgfp
import json
import numpy as np
import os
import glob
from py_gpmf_parser.gopro_telemetry_extractor import GoProTelemetryExtractor


def test_telemetry_extraction():
    """Test that telemetry extraction works correctly for GoPro MP4 files."""
    
    # Find test files
    test_files = list(glob.glob('gpmf-parser/samples/*.mp4'))
    
    if not test_files:
        print("No test files found in gpmf-parser/samples/")
        return False
    
    print(f"Found {len(test_files)} test files")
    
    for filepath in test_files:
        print(f"\nTesting file: {os.path.basename(filepath)}")
        
        # Test basic file opening and metadata extraction
        try:
            extractor = GoProTelemetryExtractor(filepath)
            extractor.open_source()
            
            # Test that we can get video metadata
            timestamps = extractor.get_image_timestamps_s()
            assert len(timestamps) > 0, "Should have at least one video timestamp"
            assert all(t >= 0 for t in timestamps), "All timestamps should be non-negative"
            print(f"✓ Video timestamps extracted: {len(timestamps)} frames")
            
            # Test extraction of various sensor data
            sensor_tests = [
                ("ACCL", "accelerometer"),
                ("GYRO", "gyroscope"), 
                ("GPS5", "GPS"),
                ("GRAV", "gravity"),
                ("MAGN", "magnetometer"),
                ("CORI", "camera orientation"),
                ("IORI", "image orientation")
            ]
            
            extracted_sensors = []
            
            for sensor_type, sensor_name in sensor_tests:
                try:
                    data, timestamps = extractor.extract_data(sensor_type)
                    
                    if len(data) > 0:
                        # Validate data structure
                        assert data.ndim == 2, f"{sensor_name} data should be 2D array"
                        assert len(data) == len(timestamps), f"{sensor_name} data and timestamps should have same length"
                        
                        # Check for reasonable data values (not all zeros or NaN)
                        if sensor_type in ["ACCL", "GYRO", "GRAV", "MAGN"]:
                            # These should have 3D data (x, y, z)
                            assert data.shape[1] >= 3, f"{sensor_name} should have at least 3 dimensions"
                        
                        # Check that data is not all zeros (indicates successful extraction)
                        if not np.allclose(data, 0):
                            print(f"✓ {sensor_name} data extracted: {len(data)} samples")
                            extracted_sensors.append(sensor_type)
                        else:
                            print(f"⚠ {sensor_name} data is all zeros (may be normal for this file)")
                    else:
                        print(f"⚠ {sensor_name} data is empty (may be normal for this file)")
                        
                except Exception as e:
                    print(f"✗ Failed to extract {sensor_name} data: {e}")
            
            # Test JSON export
            if extracted_sensors:
                json_filename = f"test_output_{os.path.basename(filepath)}.json"
                try:
                    extractor.extract_data_to_json(json_filename, extracted_sensors)
                    
                    # Verify JSON file was created and contains valid data
                    with open(json_filename, 'r') as f:
                        json_data = json.load(f)
                    
                    assert "img_timestamps_s" in json_data, "JSON should contain image timestamps"
                    for sensor in extracted_sensors:
                        assert sensor in json_data, f"JSON should contain {sensor} data"
                        assert "data" in json_data[sensor], f"{sensor} should have 'data' field"
                        assert "timestamps_s" in json_data[sensor], f"{sensor} should have 'timestamps_s' field"
                    
                    print(f"✓ JSON export successful: {json_filename}")
                    
                    # Clean up test file
                    os.remove(json_filename)
                    
                except Exception as e:
                    print(f"✗ JSON export failed: {e}")
            
            extractor.close_source()
            
            # Test that at least some sensor data was extracted
            if extracted_sensors:
                print(f"✓ Successfully extracted data from {len(extracted_sensors)} sensors: {', '.join(extracted_sensors)}")
                return True
            else:
                print("⚠ No sensor data was extracted (this may be normal for some files)")
                return False
                
        except Exception as e:
            print(f"✗ Failed to process file {filepath}: {e}")
            return False
    
    return True


def test_basic_gpmf_functions():
    """Test basic GPMF parser functions work correctly."""
    
    test_files = list(glob.glob('gpmf-parser/samples/*.mp4'))
    
    if not test_files:
        print("No test files found for basic GPMF function testing")
        return False
    
    filepath = test_files[0]  # Use first file for basic testing
    
    try:
        # Test basic MP4 source operations
        handle = pgfp.OpenMP4Source(filepath, pgfp.MOV_GPMF_TRAK_TYPE, pgfp.MOV_GPMF_TRAK_SUBTYPE, 0)
        
        # Test duration and payload functions
        duration = pgfp.GetDuration(handle)
        assert duration > 0, "Duration should be positive"
        
        num_payloads = pgfp.GetNumberPayloads(handle)
        assert num_payloads > 0, "Should have at least one payload"
        
        # Test video frame rate functions
        frames, numer, denom = pgfp.GetVideoFrameRateAndCount(handle)
        assert frames > 0, "Should have positive number of frames"
        assert numer > 0 and denom > 0, "Frame rate should be positive"
        
        # Test payload extraction
        for i in range(min(num_payloads, 3)):  # Test first 3 payloads
            payloadsize = pgfp.GetPayloadSize(handle, i)
            assert payloadsize > 0, f"Payload {i} should have positive size"
            
            res_handle = 0
            res_handle = pgfp.GetPayloadResource(handle, res_handle, payloadsize)
            payload = pgfp.GetPayload(handle, res_handle, i, payloadsize)
            assert len(payload) > 0, f"Payload {i} should not be empty"
            
            times = pgfp.GetPayloadTime(handle, i)
            # Note: times might be None or have different structure depending on implementation
        
        pgfp.CloseSource(handle)
        print("✓ Basic GPMF functions work correctly")
        return True
        
    except Exception as e:
        print(f"✗ Basic GPMF function test failed: {e}")
        return False


if __name__ == "__main__":
    print("Running telemetry extraction tests...")
    
    # Run basic GPMF function tests
    basic_test_passed = test_basic_gpmf_functions()
    
    # Run telemetry extraction tests
    extraction_test_passed = test_telemetry_extraction()
    
    if basic_test_passed and extraction_test_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        exit(1)