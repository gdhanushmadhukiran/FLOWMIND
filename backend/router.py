class TrafficRouter:
    def __init__(self):
        self.nodes = [f"J0{i+1}" for i in range(8)]
        self.edges = [
            {"id": "R01", "source": "J01", "target": "J02", "length_km": 1.0, "speed_limit_kmh": 50, "capacity": 80},
            {"id": "R02", "source": "J02", "target": "J03", "length_km": 1.0, "speed_limit_kmh": 50, "capacity": 80},
            {"id": "R03", "source": "J03", "target": "J04", "length_km": 1.0, "speed_limit_kmh": 50, "capacity": 80},
            {"id": "R04", "source": "J04", "target": "J08", "length_km": 1.5, "speed_limit_kmh": 50, "capacity": 80},
            {"id": "R05", "source": "J01", "target": "J05", "length_km": 1.5, "speed_limit_kmh": 70, "capacity": 100},
            {"id": "R06", "source": "J05", "target": "J06", "length_km": 2.0, "speed_limit_kmh": 70, "capacity": 100},
            {"id": "R07", "source": "J06", "target": "J07", "length_km": 2.0, "speed_limit_kmh": 70, "capacity": 100},
            {"id": "R08", "source": "J07", "target": "J08", "length_km": 1.5, "speed_limit_kmh": 70, "capacity": 100},
            {"id": "R09", "source": "J03", "target": "J06", "length_km": 1.2, "speed_limit_kmh": 50, "capacity": 80},
            {"id": "R10", "source": "J04", "target": "J07", "length_km": 1.2, "speed_limit_kmh": 50, "capacity": 80},
        ]
        self.graph = {n: [] for n in self.nodes}
        for e in self.edges:
            self.graph[e["source"]].append(e)
            self.graph[e["target"]].append({
                "id": e["id"] + "_rev", "source": e["target"], "target": e["source"],
                "length_km": e["length_km"], "speed_limit_kmh": e["speed_limit_kmh"], "capacity": e["capacity"]
            })

    def get_edge_cost(self, edge, traffic_state, forecast):
        target_j = edge["target"]
        j_state = next((j for j in traffic_state if j["id"] == target_j), None)
        current_density = j_state["density"] if j_state else 0
        predicted_density = current_density
        if forecast:
            fc = next((f for f in forecast if f["junction"] == target_j), None)
            if fc:
                predicted_density = fc["forecast"]["15m"]["density"]
        blended_density = (current_density * 0.6) + (predicted_density * 0.4)
        speed_factor = max(0.2, 1.0 - (blended_density / 100.0) * 0.8)
        effective_speed = edge["speed_limit_kmh"] * speed_factor
        time_hours = edge["length_km"] / effective_speed
        return time_hours * 60

    def find_routes(self, origin, destination, traffic_state, forecast):
        if origin not in self.nodes or destination not in self.nodes or origin == destination:
            return None
        def dijkstra_k():
            paths = []
            queue = [(0, origin, [origin])]
            while queue and len(paths) < 100:
                queue.sort(key=lambda x: x[0])
                cost, current, path = queue.pop(0)
                if current == destination:
                    paths.append({"nodes": path, "travel_time_min": cost})
                    continue
                for edge in self.graph[current]:
                    nxt = edge["target"]
                    if nxt not in path:
                        edge_cost = self.edge_costs.get((current, nxt), self.get_edge_cost(edge, traffic_state, forecast))
                        queue.append((cost + edge_cost, nxt, path + [nxt]))
            return paths
        self.edge_costs = {}
        for current in self.nodes:
            for edge in self.graph[current]:
                self.edge_costs[(current, edge["target"])] = self.get_edge_cost(edge, traffic_state, forecast)
        all_paths = dijkstra_k()
        if not all_paths: return None
        all_paths.sort(key=lambda x: x["travel_time_min"])
        def get_dist(path):
            d = 0
            for i in range(len(path)-1):
                edge = next(e for e in self.graph[path[i]] if e["target"] == path[i+1])
                d += edge["length_km"]
            return d
        for p in all_paths:
            p["distance_km"] = get_dist(p["nodes"])
        baseline_path = min(all_paths, key=lambda x: x["distance_km"])
        baseline_time = baseline_path["travel_time_min"]
        results = []
        for i, p in enumerate(all_paths[:3]):
            savings = max(0, baseline_time - p["travel_time_min"])
            reason = "Alternative route."
            if i == 0:
                reason = "Avoids predicted congestion on the primary route." if p["distance_km"] > baseline_path["distance_km"] else "Primary route is optimal."
            results.append({
                "rank": i + 1, "route_id": f"R-{i+1}", "nodes": p["nodes"],
                "distance_km": round(p["distance_km"], 1), "travel_time_min": round(p["travel_time_min"], 1),
                "time_saved_min": round(savings, 1), "congestion": "MODERATE", "reason": reason
            })
        return {"origin": origin, "destination": destination, "recommended": results[0], "alternatives": results[1:]}
