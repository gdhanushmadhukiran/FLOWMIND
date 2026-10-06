from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .sim import simulator_instance
from .detector import VehicleDetector
import asyncio

app = FastAPI()
detector = VehicleDetector()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ModeUpdateRequest(BaseModel):
    mode: str

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "flowmind", "mode": "simulation"}

@app.get("/api/state")
def get_state():
    simulator_instance.update()
    return simulator_instance.get_state()

@app.get("/api/signals")
def get_signals():
    simulator_instance.update()
    state = simulator_instance.get_state()
    return state["signal_ai"]

@app.get("/api/forecast")
def get_forecast():
    simulator_instance.update()
    state = simulator_instance.get_state()
    return state["forecast"]

@app.get("/api/alerts")
def get_alerts():
    simulator_instance.update()
    state = simulator_instance.get_state()
    return state["alerts"]

@app.get("/api/impact")
def get_impact():
    simulator_instance.update()
    state = simulator_instance.get_state()
    return state["impact"]

@app.get("/api/routes")
def get_routes(origin: str = "J01", destination: str = "J08"):
    simulator_instance.update()
    state = simulator_instance.get_state()
    route = simulator_instance.router.find_routes(origin, destination, state["junctions"], state["forecast"])
    if not route:
        raise HTTPException(status_code=400, detail="Invalid origin or destination")
    return route

@app.post("/api/signals/mode")
def set_signals_mode(req: ModeUpdateRequest):
    if req.mode not in ["baseline", "adaptive"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Allowed: baseline, adaptive")
    simulator_instance.set_mode(req.mode)
    return {"status": "success", "mode": req.mode}

class SourceModeRequest(BaseModel):
    source: str

@app.post("/api/source")
def set_source_mode(req: SourceModeRequest):
    if req.source not in ["DEMO", "REAL_VIDEO"]:
        raise HTTPException(status_code=400, detail="Invalid source")
    simulator_instance.source_mode = req.source
    return {"status": "ok", "source": simulator_instance.source_mode}

@app.get("/api/detection/status")
def get_detection_status():
    return {
        "available": detector.available,
        "model": "YOLOv8n" if detector.available else None,
        "reason": None if detector.available else "ultralytics/model unavailable"
    }

class ImageRequest(BaseModel):
    image_path: str

@app.post("/api/detection/image")
def detect_image(req: ImageRequest):
    res = detector.detect_frame(frame_path=req.image_path)
    if res["status"] == "success":
        agg = detector.aggregate_detections(res["detections"])
        if simulator_instance.source_mode == "REAL_VIDEO":
            simulator_instance.latest_detection = agg
        return {"status": "success", "aggregation": agg, "detections": res["detections"]}
    return res

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            simulator_instance.update()
            await websocket.send_json(simulator_instance.get_state())
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        pass
