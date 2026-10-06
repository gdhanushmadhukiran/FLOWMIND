# FLOWMIND DETECTION INTELLIGENCE

## Overview
Phase 6 introduces actual vehicle detection via YOLO (ultralytics). 

## Graceful Fallback
If the YOLO model or environment dependencies are unavailable, the `VehicleDetector` cleanly downgrades to a `status: unavailable` mode, and the system continues utilizing the deterministic `DEMO` simulator to drive traffic state.

## Vehicle Classification
The system filters COCO classes to focus purely on traffic-relevant entities:
- Car (2)
- Motorcycle (3)
- Bus (5)
- Truck (7)

## Junction Mapping & Density
Detected vehicles are aggregated into spatial bins (which serve as mock regions for junctions). The density is calculated as a bounded percentage based on an expected max capacity per region (e.g. 15 vehicles).

## Downstream Pipeline
Once `REAL_VIDEO` mode is active, the simulator injects the real detected densities and queues directly into the `TrafficSimulator` state. From there, the real state naturally flows into the forecasting, routing, and signal optimization engines seamlessly, preserving the intelligent pipeline.