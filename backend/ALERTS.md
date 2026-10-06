# FLOWMIND ALERT ENGINE

## Overview
The `TrafficAlertEngine` produces deterministic, meaningful alerts based on live traffic events and forecasts, avoiding random alert generation.

## Alert Types
- `CURRENT_CONGESTION`
- `PREDICTED_CONGESTION`
- `QUEUE_GROWTH`
- `SIGNAL_INTERVENTION`
- `CRITICAL_JUNCTION`

## Severity Mapping
- `INFO` (blue): Stable or AI interventions
- `WARNING` (yellow): Predicted congestion within 30m
- `HIGH` (orange): Rapid current growth or queue spikes
- `CRITICAL` (red): Ongoing extreme congestion

## Deduplication
Alerts are filtered using a time-based cooldown (e.g. 30 seconds real-time) to prevent flooding the UI with the same alert for the same junction continuously.