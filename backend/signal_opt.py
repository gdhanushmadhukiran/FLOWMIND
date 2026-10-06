import time

class SignalOptimizer:
    def __init__(self):
        self.min_green = 10
        self.normal_green = 30
        self.max_green = 60
        self.cooldown = 15

    def optimize(self, junction_state):
        density_weight = 0.4
        queue_weight = 0.6
        normalized_density = min(junction_state["density"] / 100.0, 1.0)
        normalized_queue = min(junction_state["queue_m"] / 100.0, 1.0)
        score = (density_weight * normalized_density) + (queue_weight * normalized_queue)
        current_phase = junction_state["signal"]
        if score > 0.8:
            priority, extension, reason = "CRITICAL", 20, "Critical congestion requires extended green."
        elif score > 0.6:
            priority, extension, reason = "HIGH", 10, "High queue and density detected."
        elif score > 0.4:
            priority, extension, reason = "MODERATE", 5, "Moderate congestion; small extension."
        else:
            priority, extension, reason = "LOW", 0, "Traffic conditions stable; maintain normal timing."
        rec_green = min(self.max_green, self.normal_green + extension)
        return {
            "junction": junction_state["id"], "current_phase": current_phase, "recommended_phase": "GREEN",
            "current_green_time": junction_state.get("current_green_time", self.normal_green),
            "recommended_green_time": rec_green, "extension_seconds": extension,
            "priority": priority, "score": round(score, 2), "reason": reason,
            "method": "ADAPTIVE_RULE_BASED", "timestamp": time.time()
        }
