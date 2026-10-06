from backend.router import TrafficRouter

def test_router_graph_construction():
    router=TrafficRouter()
    assert len(router.nodes)==8
    assert len(router.edges)==10
    assert len(router.graph["J01"])>0

def test_edge_cost():
    router=TrafficRouter()
    edge={"target":"J02","length_km":1.0,"speed_limit_kmh":60,"capacity":100}
    traffic_state=[{"id":"J02","density":0}]
    cost=router.get_edge_cost(edge,traffic_state,[])
    assert abs(cost-1.0)<0.1

def test_congestion_penalty():
    router=TrafficRouter()
    edge={"target":"J02","length_km":1.0,"speed_limit_kmh":60,"capacity":100}
    traffic_state_high=[{"id":"J02","density":100}]
    assert router.get_edge_cost(edge,traffic_state_high,[])>1.0

def test_shortest_path_routing():
    router=TrafficRouter()
    traffic_state=[{"id":f"J0{i+1}","density":0} for i in range(8)]
    res=router.find_routes("J01","J08",traffic_state,[])
    assert res is not None
    assert res["origin"]=="J01"
    assert res["destination"]=="J08"
    assert len(res["alternatives"])>0
    assert res["recommended"]["distance_km"]==4.5

def test_congested_route_avoidance():
    router=TrafficRouter()
    traffic_state=[{"id":f"J0{i+1}","density":100 if i+1 in [2,4] else 0} for i in range(8)]
    res=router.find_routes("J01","J08",traffic_state,[])
    assert res["recommended"]["distance_km"]>4.5
    assert "J05" in res["recommended"]["nodes"]