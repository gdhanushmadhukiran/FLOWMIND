from backend.signal_opt import SignalOptimizer

def test_optimizer_low_congestion():
    opt=SignalOptimizer()
    state={"id":"J01","density":20,"queue_m":10,"signal":"RED"}
    decision=opt.optimize(state)
    assert decision["priority"]=="LOW"
    assert decision["extension_seconds"]==0
    assert decision["recommended_green_time"]==30

def test_optimizer_high_congestion():
    opt=SignalOptimizer()
    state={"id":"J01","density":90,"queue_m":90,"signal":"RED"}
    decision=opt.optimize(state)
    assert decision["priority"]=="CRITICAL"
    assert decision["extension_seconds"]==20
    assert decision["recommended_green_time"]==50

def test_optimizer_moderate_congestion():
    opt=SignalOptimizer()
    state={"id":"J01","density":50,"queue_m":40,"signal":"RED"}
    decision=opt.optimize(state)
    assert decision["priority"] in ["MODERATE","HIGH"]
    assert decision["extension_seconds"]>0