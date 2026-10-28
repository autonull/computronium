# An Instrument, Not a Picture

- **Real-time telemetry.** FastAPI and WebSockets stream the campaign queue, cell state, and resource utilisation while the run is live.
- **A control plane.** Play, pause, step, and move the compute ceiling mid-flight. The campaign is steerable, not launched and abandoned.
- **Mission control.** Pareto views over <!-- gen:objective_count --> registered objectives — <!-- gen:measured_objective_count --> of them actually measured — so accuracy never gets to stand alone.

![Live campaign dashboard](screenshots/tour/dashboard-watch.png)

<!-- notes -->
The screenshot is captured from a real campaign by scripts/capture_dashboard_tour.py, not mocked. Panels shown are the live rail, the Pareto plot, and the control bar.

The point of the dashboard is auditing during the run: when a cell is promoted, the panel shows which cells it beat and under which budget. Do not demo the animation; demo a pause and a reallocation.
<!-- /notes -->
