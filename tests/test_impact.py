from backend.impact import ImpactCalculator

def test_impact_calculation():
    calc=ImpactCalculator()
    baseline={"total_queue":1000,"samples":10,"processed":50}
    adaptive={"total_queue":500,"samples":10,"processed":60}
    impact=calc.calculate_impact(baseline,adaptive)
    assert impact["baseline"]["avg_queue_m"]==100
    assert impact["baseline"]["throughput"]==50
    assert impact["baseline"]["fuel_l"]>0
    assert impact["baseline"]["co2_kg"]>0
    imp=impact["improvement"]
    assert imp["queue_reduction_pct"]==50.0
    assert imp["throughput_increase_pct"]==20.0
    assert imp["fuel_saved_l"]>0
    assert imp["co2_reduced_kg"]>0

def test_impact_zero_samples():
    calc=ImpactCalculator()
    baseline={"total_queue":0,"samples":0,"processed":0}
    adaptive={"total_queue":0,"samples":0,"processed":0}
    impact=calc.calculate_impact(baseline,adaptive)
    assert impact["baseline"]["avg_queue_m"]==0
    assert impact["improvement"]["queue_reduction_pct"]==0.0