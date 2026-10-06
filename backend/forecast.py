class CongestionForecaster:
    def __init__(self):
        self.history = {}
        self.max_history = 60
        
    def add_observation(self, state):
        jid = state["id"]
        if jid not in self.history:
            self.history[jid] = []
        self.history[jid].append(state.copy())
        if len(self.history[jid]) > self.max_history:
            self.history[jid].pop(0)

    def _linear_trend(self, values):
        if len(values) < 2: return 0.0
        n = len(values)
        x = list(range(n))
        y = values
        sum_x = sum(x)
        sum_y = sum(y)
        sum_x2 = sum(xi * xi for xi in x)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        
        denominator = (n * sum_x2 - sum_x * sum_x)
        if denominator == 0:
            return 0.0
        m = (n * sum_xy - sum_x * sum_y) / denominator
        return m

    def forecast(self):
        forecasts = []
        for jid, history in self.history.items():
            if not history: continue
            
            recent = history[-10:]
            densities = [s["density"] for s in recent]
            queues = [s["queue_m"] for s in recent]
            speeds = [s["average_speed"] for s in recent]
            
            density_trend = self._linear_trend(densities)
            queue_trend = self._linear_trend(queues)
            speed_trend = self._linear_trend(speeds)
            
            curr = history[-1]
            
            def bounded(val, trend, t_steps, min_v, max_v):
                return max(min_v, min(max_v, val + trend * t_steps))
            
            f15 = {
                "density": int(bounded(curr["density"], density_trend, 15, 0, 100)),
                "queue_m": int(bounded(curr["queue_m"], queue_trend, 15, 0, 500)),
                "average_speed": int(bounded(curr["average_speed"], speed_trend, 15, 0, 60))
            }
            f30 = {
                "density": int(bounded(curr["density"], density_trend, 30, 0, 100)),
                "queue_m": int(bounded(curr["queue_m"], queue_trend, 30, 0, 500)),
                "average_speed": int(bounded(curr["average_speed"], speed_trend, 30, 0, 60))
            }
            f60 = {
                "density": int(bounded(curr["density"], density_trend, 60, 0, 100)),
                "queue_m": int(bounded(curr["queue_m"], queue_trend, 60, 0, 500)),
                "average_speed": int(bounded(curr["average_speed"], speed_trend, 60, 0, 60))
            }
            
            def map_severity(d, q):
                if d > 85 or q > 100: return 4
                if d > 65 or q > 60: return 3
                if d > 40: return 2
                return 1
            
            f15["severity"] = map_severity(f15["density"], f15["queue_m"])
            f30["severity"] = map_severity(f30["density"], f30["queue_m"])
            f60["severity"] = map_severity(f60["density"], f60["queue_m"])
            
            confidence = min(0.95, len(history) / float(self.max_history))
            
            if density_trend > 0.5:
                reason = "Density increasing consistently."
            elif queue_trend > 0.5 and speed_trend < 0:
                reason = "Queue rising while average speed declines."
            elif density_trend < -0.5:
                reason = "Traffic conditions improving."
            else:
                reason = "Traffic conditions stable."

            forecasts.append({
                "junction": jid,
                "current": {
                    "density": int(curr["density"]),
                    "queue_m": int(curr["queue_m"]),
                    "average_speed": int(curr["average_speed"])
                },
                "forecast": {
                    "15m": f15,
                    "30m": f30,
                    "60m": f60
                },
                "confidence": round(confidence, 2),
                "trend": "RISING" if queue_trend > 0.2 else ("FALLING" if queue_trend < -0.2 else "STABLE"),
                "reason": reason
            })
            
        return forecasts
