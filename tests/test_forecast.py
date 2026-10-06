from backend.forecast import CongestionForecaster

def test_forecast_generation():
    forecaster = CongestionForecaster()
    for i in range(15):
        forecaster.add_observation({"id":"J01","density":40+i,"queue_m":20+i,"average_speed":40-i})
    forecasts=forecaster.forecast()
    assert len(forecasts)==1
    fc=forecasts[0]
    assert fc["junction"]=="J01"
    assert fc["trend"]=="RISING"
    assert fc["forecast"]["15m"]["density"]>40
    assert fc["forecast"]["15m"]["queue_m"]>20
    assert fc["confidence"]>0.0

def test_forecast_bounds():
    forecaster=CongestionForecaster()
    for i in range(10):
        forecaster.add_observation({"id":"J01","density":95+i,"queue_m":480+i*5,"average_speed":5})
    fc=forecaster.forecast()[0]
    assert fc["forecast"]["15m"]["density"]<=100
    assert fc["forecast"]["15m"]["queue_m"]<=500