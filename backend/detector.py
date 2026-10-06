import logging

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

logger = logging.getLogger(__name__)

class VehicleDetector:
    def __init__(self, model_name="yolov8n.pt"):
        self.available = YOLO_AVAILABLE
        self.model = None
        if self.available:
            try:
                self.model = YOLO(model_name)
            except Exception as e:
                logger.error(f"Failed to load YOLO model: {e}")
                self.available = False
                
        self.vehicle_classes = {
            2: "car",
            3: "motorcycle",
            5: "bus",
            7: "truck"
        }

    def detect_frame(self, frame_path=None):
        if not self.available or not self.model:
            return {"status": "unavailable", "detections": []}

        try:
            results = self.model(frame_path)
            
            detections = []
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    if cls_id in self.vehicle_classes:
                        conf = box.conf[0].item()
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        center_x = (x1 + x2) / 2
                        center_y = (y1 + y2) / 2
                        
                        detections.append({
                            "class_name": self.vehicle_classes[cls_id],
                            "confidence": round(conf, 3),
                            "bounding_box": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                            "center_x": round(center_x, 1),
                            "center_y": round(center_y, 1)
                        })
            
            return {"status": "success", "detections": detections}
            
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return {"status": "error", "message": str(e), "detections": []}

    def aggregate_detections(self, detections, image_width=1280, image_height=720):
        classes = {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0}
        total = len(detections)
        for d in detections:
            classes[d["class_name"]] += 1
            
        junctions = {f"J0{i+1}": {"vehicle_count": 0, "car": 0, "motorcycle": 0, "bus": 0, "truck": 0} for i in range(8)}
        
        for d in detections:
            cx = d["center_x"]
            cy = d["center_y"]
            
            col = int(cx / (image_width / 4))
            row = int(cy / (image_height / 2))
            
            col = min(col, 3)
            row = min(row, 1)
            
            j_id = f"J0{row * 4 + col + 1}"
            
            junctions[j_id]["vehicle_count"] += 1
            junctions[j_id][d["class_name"]] += 1
            
        for jid, data in junctions.items():
            data["density"] = min(100, int((data["vehicle_count"] / 15.0) * 100))
            
        return {
            "total_vehicles": total,
            "classes": classes,
            "junctions": junctions
        }
