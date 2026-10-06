import time
from backend.alerts import TrafficAlertEngine

def test_alert_engine_critical():
    engine = TrafficAlertEngine()
    current_states = [{"id": "J01", "severity": 4, "density": 90, "queue_m": 120, "average_speed": 10}]
    forecasts = []
    signals = []
    
    alerts = engine.evaluate(current_states, forecasts, signals)
    assert len(alerts) == 1
    assert alerts[0]["type"] == "CRITICAL_JUNCTION"

def test_alert_engine_deduplication():
    engine = TrafficAlertEngine()
    current_states = [{"id": "J01", "severity": 4, "density": 90, "queue_m": 120, "average_speed": 10}]
    
    alerts1 = engine.evaluate(current_states, [], [])
    assert len(alerts1) == 1
    
    alerts2 = engine.evaluate(current_states, [], [])
    assert len(alerts2) == 0