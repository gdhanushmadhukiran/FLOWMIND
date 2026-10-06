import time
import random
from .signal_opt import SignalOptimizer
from .forecast import CongestionForecaster
from .alerts import TrafficAlertEngine
from .router import TrafficRouter
from .impact import ImpactCalculator

class TrafficSimulator:
    def __init__(self, seed=42):
        random.seed(seed)
        self.mode = "adaptive"
        self.optimizer = SignalOptimizer()
        self.forecaster = CongestionForecaster()
        self.alert_engine = TrafficAlertEngine()
        self.router = TrafficRouter()
        self.impact_calc = ImpactCalculator()
        self.signal_decisions = {}
        self.forecasts = []
        self.alerts = []
        self.route_info = None
        self.source_mode = "DEMO"
        self.latest_detection = None
        self.junctions = [
            {"id": f"J0{i+1}", "density": random.randint(30, 80), "queue_m": random.randint(10, 80), "average_speed": 40, "signal": "RED", "signal_remaining": random.randint(5, 30), "severity": 1, "suggestion": "Maintain", "current_green_time": 30}
            for i in range(8)
        ]
        self.vehicles = []
        for i in range(120):
            self.vehicles.append({
                "id": f"V{i}", "type": random.choice(["car", "bus", "truck", "motorcycle"]),
                "speed": random.randint(0, 60), "lane": random.randint(1, 4),
                "junction": random.choice([j["id"] for j in self.junctions])
            })
        self.last_update = time.time()
        self.metrics = {
            "baseline": {"total_queue": 0, "samples": 0, "processed": 0},
            "adaptive": {"total_queue": 0, "samples": 0, "processed": 0}
        }

    def set_mode(self, mode):
        if mode in ["baseline", "adaptive"]:
            self.mode = mode

    def update(self):
        now = time.time()
        dt = now - self.last_update
        self.last_update = now
        total_q = 0
        for j in self.junctions:
            decision = self.optimizer.optimize(j)
            self.signal_decisions[j["id"]] = decision
            if self.mode == "adaptive":
                j["suggestion"] = decision["reason"]
                if j["signal"] == "GREEN":
                    j["current_green_time"] = decision["recommended_green_time"]
            else:
                j["suggestion"] = "Baseline fixed timing"
                j["current_green_time"] = 30
            j["signal_remaining"] -= dt
            if j["signal_remaining"] <= 0:
                phases = ["GREEN", "YELLOW", "RED"]
                current_idx = phases.index(j["signal"])
                next_idx = (current_idx + 1) % len(phases)
                j["signal"] = phases[next_idx]
                j["signal_remaining"] = j["current_green_time"] if j["signal"] == "GREEN" else (5 if j["signal"] == "YELLOW" else 40)
            if self.source_mode == "REAL_VIDEO" and self.latest_detection:
                det = self.latest_detection["junctions"].get(j["id"])
                if det:
                    j["density"] = det["density"]
                    j["queue_m"] = int(det["vehicle_count"] * 5)
            else:
                j["density"] = max(0, min(100, j["density"] + random.randint(-5, 5)))
            arrival_rate = j["density"] / 10.0
            j["queue_m"] = max(0, j["queue_m"] + arrival_rate * dt)
            if j["signal"] == "GREEN":
                depart_rate = 15.0
                departed = min(j["queue_m"], depart_rate * dt)
                j["queue_m"] = max(0, j["queue_m"] - departed)
                self.metrics[self.mode]["processed"] += departed
            j["average_speed"] = max(0, min(60, 60 - j["density"] * 0.5))
            if j["density"] > 85 or j["queue_m"] > 100:
                j["severity"] = 4
            elif j["density"] > 65 or j["queue_m"] > 60:
                j["severity"] = 3
            elif j["density"] > 40:
                j["severity"] = 2
            else:
                j["severity"] = 1
            total_q += j["queue_m"]
            self.forecaster.add_observation(j)
        self.metrics[self.mode]["total_queue"] += total_q
        self.metrics[self.mode]["samples"] += 1
        self.forecasts = self.forecaster.forecast()
        self.alert_engine.evaluate(self.junctions, self.forecasts, list(self.signal_decisions.values()))
        self.alerts = self.alert_engine.get_active_alerts()
        if self.metrics[self.mode]["samples"] % 5 == 1:
            self.route_info = self.router.find_routes("J01", "J08", self.junctions, self.forecasts)
        for v in self.vehicles:
            v["speed"] = max(0, min(60, v["speed"] + random.randint(-5, 5)))

    def get_state(self):
        avg_density = sum(j["density"] for j in self.junctions) / len(self.junctions)
        avg_speed = sum(j["average_speed"] for j in self.junctions) / len(self.junctions)
        congestion = "LOW"
        if avg_density > 80: congestion = "CRITICAL"
        elif avg_density > 60: congestion = "HIGH"
        elif avg_density > 40: congestion = "MODERATE"
        impact_data = self.impact_calc.calculate_impact(self.metrics["baseline"], self.metrics["adaptive"])
        return {
            "timestamp": time.time(), "mode": "simulation", "source": self.source_mode, "control_mode": self.mode,
            "summary": {
                "vehicles": self.latest_detection["total_vehicles"] if self.source_mode == "REAL_VIDEO" and self.latest_detection else len(self.vehicles),
                "classes": self.latest_detection["classes"] if self.source_mode == "REAL_VIDEO" and self.latest_detection else None,
                "density": round(avg_density), "average_speed": round(avg_speed), "congestion": congestion
            },
            "junctions": self.junctions, "vehicles": self.vehicles,
            "signal_ai": {"mode": self.mode, "decisions": list(self.signal_decisions.values())},
            "impact": impact_data, "forecast": self.forecasts, "alerts": self.alerts, "route": self.route_info
        }

simulator_instance = TrafficSimulator()
