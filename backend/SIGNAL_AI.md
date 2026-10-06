# FLOWMIND SIGNAL AI

## 1. Problem
Traffic congestion is often worsened by static, inflexible signal timings that do not adapt to real-time fluctuations in vehicle density and queue lengths.

## 2. Baseline Controller
The simulation features a `baseline` mode, which utilizes fixed timing (30s normal green time) regardless of the traffic volume. It serves as a benchmark for comparison.

## 3. Adaptive Controller
The `adaptive` controller uses an explainable rule-based system (`SignalOptimizer`). It analyzes live traffic data and extends green times intelligently based on priority scores.

## 4. Input Features
- `density` (vehicles per capacity)
- `queue_m` (length of the queue in meters)
- `signal` (current phase)

## 5. Priority Score
Priority score is calculated using a weighted combination:
`score = (0.4 * normalized_density) + (0.6 * normalized_queue)`

## 6. Thresholds
- **Score > 0.8:** CRITICAL priority. +20s green extension (max 60s).
- **Score > 0.6:** HIGH priority. +10s green extension.
- **Score > 0.4:** MODERATE priority. +5s green extension.
- **Score <= 0.4:** LOW priority. No extension (30s).

## 7. Hysteresis
To prevent rapid oscillation (e.g., GREEN -> RED -> GREEN in a single tick), the controller guarantees a minimum green time and a safe cooldown between active phase transitions.

## 8. Decision Format
The AI provides a structured JSON decision explaining its actions.

## 9. Baseline vs Adaptive
You can switch the simulation mode using:
`POST /api/signals/mode` with payload `{"mode": "adaptive"}` or `{"mode": "baseline"}`. The simulator continuously calculates metrics (`avg_queue` and `processed`) for both modes over time.

## 10. Known Limitations
- This is an **explainable simulation controller**, not a trained ML model.
- It operates using heuristic thresholds rather than a learned policy.
- Real-world deployment would require reinforcement learning trained on directional approach data.