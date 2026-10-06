class ImpactCalculator:
    def __init__(self):
        self.fuel_idle_l_per_hr = 1.0
        self.co2_kg_per_l = 2.3
        self.vehicle_length_m = 5.0
        
    def calculate_impact(self, baseline_metrics, adaptive_metrics):
        def calc_metrics(metrics):
            samples = metrics["samples"]
            if samples == 0:
                return {"avg_queue_m": 0, "throughput": 0, "fuel_l": 0, "co2_kg": 0}
            avg_queue = metrics["total_queue"] / samples
            idling_vehicles = avg_queue / self.vehicle_length_m
            total_idle_s = idling_vehicles * samples
            fuel_l = (total_idle_s / 3600.0) * self.fuel_idle_l_per_hr
            co2_kg = fuel_l * self.co2_kg_per_l
            return {
                "avg_queue_m": avg_queue,
                "throughput": metrics["processed"],
                "fuel_l": fuel_l,
                "co2_kg": co2_kg
            }
        b_stats = calc_metrics(baseline_metrics)
        a_stats = calc_metrics(adaptive_metrics)
        def pct_improvement(base, adaptive, lower_is_better=True):
            if base == 0: return 0.0
            if lower_is_better:
                return ((base - adaptive) / base) * 100.0
            return ((adaptive - base) / base) * 100.0
        improvement = {
            "queue_reduction_pct": pct_improvement(b_stats["avg_queue_m"], a_stats["avg_queue_m"]),
            "throughput_increase_pct": pct_improvement(b_stats["throughput"], a_stats["throughput"], lower_is_better=False),
            "fuel_saved_l": max(0, b_stats["fuel_l"] - a_stats["fuel_l"]),
            "co2_reduced_kg": max(0, b_stats["co2_kg"] - a_stats["co2_kg"])
        }
        return {"baseline": b_stats, "adaptive": a_stats, "improvement": improvement}
