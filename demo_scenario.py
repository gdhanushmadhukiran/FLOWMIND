import time
from backend.sim import simulator_instance

def run_demo():
    print("Starting FLOWMIND Demo Scenario Audit")
    for _ in range(10):
        simulator_instance.update()
    print("Injecting congestion at J02 and J04...")
    for j in simulator_instance.junctions:
        if j["id"] in ["J02","J04"]:
            j["density"]=95
            j["queue_m"]=100
    for _ in range(5):
        simulator_instance.update()
    state=simulator_instance.get_state()
    j04_forecast=next(f for f in state["forecast"] if f["junction"]=="J04")
    assert j04_forecast["forecast"]["15m"]["density"]>70
    print("PASS: Congestion successfully predicted.")
    j04_signal=next((s for s in state["signal_ai"]["decisions"] if s["junction"]=="J04"),None)
    if j04_signal:
        assert j04_signal["priority"] in ["HIGH","CRITICAL"]
        print("PASS: Signals successfully adapted.")
    route=state["route"]
    assert route["recommended"]["distance_km"]>4.5
    print(f"PASS: Router correctly chose alternative route: {route['recommended']['nodes']}")
    has_alert=any(a["type"] in ["CRITICAL_JUNCTION","PREDICTED_CONGESTION","QUEUE_GROWTH","SIGNAL_INTERVENTION"] for a in state["alerts"])
    assert has_alert
    print("PASS: Alert successfully generated.")
    impact=state["impact"]
    assert impact["baseline"]["avg_queue_m"]>0 or impact["adaptive"]["avg_queue_m"]>0
    print("PASS: Impact metrics correctly updating.")
    print("\n--- DEMO SCENARIO PASSED ---")

if __name__=="__main__":
    run_demo()