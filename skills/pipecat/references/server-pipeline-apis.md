# Server APIs: pipeline/task/params

This reference summarizes the Server API pages for operating pipelines.

## PipelineParams (task-wide knobs)

Highlights from the reference:

- Audio:
  - `audio_in_sample_rate` (input)
  - `audio_out_sample_rate` (output)
    Setting these at the pipeline/task level helps keep all services consistent.

- Metrics:
  - `enable_metrics`
  - `enable_usage_metrics`
  - `report_only_initial_ttfb`
  - `send_initial_empty_metrics`

- Heartbeats:
  - `enable_heartbeats`
  - `heartbeats_period_secs`

- `start_metadata`: arbitrary serializable metadata attached to the start frame.

- `allow_interruptions`: deprecated (use user turn strategies / `enable_interruptions` on start strategies instead).

## PipelineTask (execution + lifecycle)

The Server API describes `PipelineTask` as the center of execution:

- Queue work:
  - `queue_frame()` / `queue_frames()`
- Stop and cancel:
  - `stop_when_done()` (graceful end after queued frames)
  - `cancel()` (immediate shutdown)
  - `has_finished()`

### Idle detection settings (task-level)

The task supports:

- `idle_timeout_secs` (disable by setting to `None`)
- `idle_timeout_frames` (what counts as “activity”)
- `cancel_on_idle_timeout` (if true, auto-cancel after handler runs)

### Event handlers

Docs list events such as:

- `on_pipeline_started` / `on_pipeline_finished`
- `on_pipeline_error` (fatal errors may cancel after handler)
- `on_idle_timeout`
- reached-upstream / reached-downstream events for registered frame types

This is useful for cleanup, logging, instrumentation, and debugging frame flow.

## Pipeline idle detection (semantics)

Server docs describe idle detection as a safeguard against leaked sessions:

- Activity is determined by a set of frame types.
- Timer resets when an activity frame occurs.
- You can choose to auto-cancel or handle it yourself (e.g., speak a prompt then end gracefully).

## Heartbeats (stall detection)

Server docs describe periodic `HeartbeatFrame`s traversing the entire pipeline:

- Enable via PipelineParams.
- Warnings are logged when heartbeats stop returning within a threshold, indicating a stall/blockage.

## ParallelPipeline (branching)

Server docs describe `ParallelPipeline` as:

- multiple branches that each receive the same downstream frames
- branch results merged back into a single stream
- system frames (start/end) synchronized across branches

Common patterns:

- multi-agent branching
- redundancy/failover paths
- cross-branch communication via producer/consumer style processors

## Practical checklist

- Turn on metrics/usage metrics early in development to spot latency regressions.
- Use heartbeats when you suspect stalls or processors blocking.
- Keep idle detection enabled unless you have a managed external lifecycle.
- Prefer turn strategies for interruption behavior (do not rely on deprecated flags).
