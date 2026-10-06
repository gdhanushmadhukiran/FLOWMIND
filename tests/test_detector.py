from backend.detector import VehicleDetector

def test_detector_fallback():
    detector = VehicleDetector(model_name="nonexistent.pt")
    res = detector.detect_frame(frame_path=None)
    assert res["status"] in ["unavailable", "error"]

def test_aggregation():
    detector = VehicleDetector()
    detections = [
        {"class_name": "car", "center_x": 100, "center_y": 100},
        {"class_name": "car", "center_x": 110, "center_y": 110},
        {"class_name": "truck", "center_x": 300, "center_y": 100},
        {"class_name": "bus", "center_x": 1000, "center_y": 500}
    ]
    agg = detector.aggregate_detections(detections)
    assert agg["total_vehicles"] == 4
    assert agg["classes"]["car"] == 2
    assert agg["classes"]["truck"] == 1
    assert agg["classes"]["bus"] == 1
    assert agg["classes"]["motorcycle"] == 0
    assert agg["junctions"]["J01"]["vehicle_count"] == 3
    assert agg["junctions"]["J01"]["car"] == 2
    assert agg["junctions"]["J08"]["vehicle_count"] == 1
    assert agg["junctions"]["J08"]["bus"] == 1