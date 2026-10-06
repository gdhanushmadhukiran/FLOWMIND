import time

class TrafficAlertEngine:
    def __init__(self):
        self.active_alerts = {}
        self.alert_history = []
        self.cooldown = 30 # seconds

    def evaluate(self, current_states, forecasts, signal_decisions):
        new_alerts = []
        now = time.time()
        
        forecast_dict = {f["junction"]: f for f in forecasts}
        signal_dict = {s["junction"]: s for s in signal_decisions}

        for state in current_states:
            jid = state["id"]
            fc = forecast_dict.get(jid)
            sig = signal_dict.get(jid)
            
            alert = None
            
            if state["severity"] == 4:
                alert = {
                    "id": f"alert-{jid}-crit",
                    "type": "CRITICAL_JUNCTION",
                    "severity": "CRITICAL",
                    "title": "Critical Congestion",
                    "message": f"Severe congestion at {jid}.",
                    "horizon_minutes": 0,
                    "recommendation": "Activate emergency signal overrides."
                }
            elif fc and fc["forecast"]["30m"]["severity"] >= 3 and state["severity"] < 3:
                alert = {
                    "id": f"alert-{jid}-pred",
                    "type": "PREDICTED_CONGESTION",
                    "severity": "WARNING",
                    "title": "Congestion Predicted",
                    "message": f"Queue expected to reach {fc['forecast']['30m']['queue_m']}m in 30 minutes.",
                    "horizon_minutes": 30,
                    "recommendation": "Prepare adaptive signal extension."
                }
            elif fc and fc["trend"] == "RISING" and fc["current"]["queue_m"] > 30:
                alert = {
                    "id": f"alert-{jid}-grow",
                    "type": "QUEUE_GROWTH",
                    "severity": "HIGH",
                    "title": "Rapid Queue Growth",
                    "message": f"Queue at {jid} is rising rapidly.",
                    "horizon_minutes": 0,
                    "recommendation": "Monitor approach density."
                }
            elif sig and sig["priority"] in ["HIGH", "CRITICAL"]:
                alert = {
                    "id": f"alert-{jid}-sig",
                    "type": "SIGNAL_INTERVENTION",
                    "severity": "INFO",
                    "title": "AI Signal Intervention",
                    "message": f"Adaptive green extended +{sig['extension_seconds']}s.",
                    "horizon_minutes": 0,
                    "recommendation": "None"
                }
            
            if alert:
                alert["timestamp"] = now
                alert["junction"] = jid
                
                last_alert = self.active_alerts.get(alert["id"])
                if not last_alert or (now - last_alert["timestamp"] > self.cooldown):
                    self.active_alerts[alert["id"]] = alert
                    new_alerts.append(alert)
                    self.alert_history.append(alert)

        return new_alerts

    def get_active_alerts(self):
        now = time.time()
        self.active_alerts = {k: v for k, v in self.active_alerts.items() if now - v["timestamp"] < 60}
        
        return list(self.active_alerts.values())
