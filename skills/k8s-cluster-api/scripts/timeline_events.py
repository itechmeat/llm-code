#!/usr/bin/env python3
"""Build provisioning event timeline for CAPI clusters.

Aggregates and displays events from Cluster API resources in
chronological order to help understand provisioning sequence.

Usage:
    python timeline_events.py <cluster-name> [options]

Examples:
    python timeline_events.py my-cluster -n clusters
    python timeline_events.py my-cluster --since 1h
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any


@dataclass
class TimelineEvent:
    """Event in the timeline."""

    timestamp: datetime
    kind: str
    name: str
    event_type: str  # Normal, Warning
    reason: str
    message: str

    @property
    def time_str(self) -> str:
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def icon(self) -> str:
        if self.event_type == "Warning":
            return "⚠️ "
        if self.reason in ["Provisioned", "Ready", "Created", "Completed"]:
            return "✓ "
        if self.reason in ["Deleting", "Deleted"]:
            return "✗ "
        return "· "


def find_kubectl() -> str | None:
    """Find kubectl binary."""
    return shutil.which("kubectl")


def run_kubectl(args: list[str]) -> tuple[bool, str, str]:
    """Run kubectl command."""
    kubectl = find_kubectl()
    if not kubectl:
        return False, "", "kubectl not found"

    cmd = [kubectl] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"


def parse_duration(duration_str: str) -> timedelta:
    """Parse duration string like '1h', '30m', '2d'."""
    match = re.match(r"(\d+)([smhd])", duration_str.lower())
    if not match:
        return timedelta(hours=1)  # Default

    value = int(match.group(1))
    unit = match.group(2)

    if unit == "s":
        return timedelta(seconds=value)
    elif unit == "m":
        return timedelta(minutes=value)
    elif unit == "h":
        return timedelta(hours=value)
    elif unit == "d":
        return timedelta(days=value)

    return timedelta(hours=1)


def get_events(
    cluster_name: str,
    namespace: str,
    since: timedelta | None = None,
) -> list[TimelineEvent]:
    """Get events for cluster resources."""
    events: list[TimelineEvent] = []

    # Get events in namespace
    success, stdout, _ = run_kubectl(
        ["get", "events", "-n", namespace, "-o", "json"]
    )
    if not success:
        return events

    try:
        data = json.loads(stdout)
        items = data.get("items", [])
    except json.JSONDecodeError:
        return events

    # Filter cutoff time
    cutoff = None
    if since:
        cutoff = datetime.utcnow() - since

    for event in items:
        # Check if event relates to cluster
        involved = event.get("involvedObject", {})
        involved_name = involved.get("name", "")
        involved_kind = involved.get("kind", "")

        # Check labels if available
        labels = event.get("metadata", {}).get("labels", {})
        event_cluster = labels.get("cluster.x-k8s.io/cluster-name", "")

        # Match by cluster name in involved object or labels
        is_related = (
            event_cluster == cluster_name
            or involved_name == cluster_name
            or involved_name.startswith(f"{cluster_name}-")
        )

        if not is_related:
            continue

        # Parse timestamp
        last_timestamp = event.get("lastTimestamp") or event.get("eventTime", "")
        if not last_timestamp:
            metadata = event.get("metadata", {})
            last_timestamp = metadata.get("creationTimestamp", "")

        if not last_timestamp:
            continue

        try:
            # Handle different timestamp formats
            if "." in last_timestamp:
                # Remove microseconds beyond 6 digits and Z
                ts_clean = re.sub(r"\.(\d{6})\d*Z$", r".\1Z", last_timestamp)
                timestamp = datetime.strptime(ts_clean, "%Y-%m-%dT%H:%M:%S.%fZ")
            else:
                timestamp = datetime.strptime(last_timestamp, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            continue

        # Apply time filter
        if cutoff and timestamp < cutoff:
            continue

        events.append(
            TimelineEvent(
                timestamp=timestamp,
                kind=involved_kind,
                name=involved_name,
                event_type=event.get("type", "Normal"),
                reason=event.get("reason", ""),
                message=event.get("message", ""),
            )
        )

    # Also get condition transitions from CAPI resources
    condition_events = get_condition_events(cluster_name, namespace, cutoff)
    events.extend(condition_events)

    # Sort by timestamp
    events.sort(key=lambda e: e.timestamp)

    return events


def get_condition_events(
    cluster_name: str,
    namespace: str,
    cutoff: datetime | None,
) -> list[TimelineEvent]:
    """Extract pseudo-events from condition transitions."""
    events: list[TimelineEvent] = []

    resources = [
        ("clusters.cluster.x-k8s.io", cluster_name),
        ("machines.cluster.x-k8s.io", None),
        ("machinedeployments.cluster.x-k8s.io", None),
        ("kubeadmcontrolplanes.controlplane.cluster.x-k8s.io", None),
    ]

    for resource_type, specific_name in resources:
        if specific_name:
            success, stdout, _ = run_kubectl(
                ["get", f"{resource_type}/{specific_name}", "-n", namespace, "-o", "json"]
            )
            items = [json.loads(stdout)] if success and stdout else []
        else:
            success, stdout, _ = run_kubectl(
                [
                    "get",
                    resource_type,
                    "-n",
                    namespace,
                    "-l",
                    f"cluster.x-k8s.io/cluster-name={cluster_name}",
                    "-o",
                    "json",
                ]
            )
            try:
                items = json.loads(stdout).get("items", []) if success else []
            except json.JSONDecodeError:
                items = []

        for item in items:
            kind = item.get("kind", "Unknown")
            name = item.get("metadata", {}).get("name", "unknown")
            status = item.get("status", {})

            # Get conditions
            conditions = status.get("conditions", [])
            if not conditions:
                conditions = status.get("v1beta2", {}).get("conditions", [])

            for cond in conditions:
                last_transition = cond.get("lastTransitionTime", "")
                if not last_transition:
                    continue

                try:
                    if "." in last_transition:
                        ts_clean = re.sub(r"\.(\d{6})\d*Z$", r".\1Z", last_transition)
                        timestamp = datetime.strptime(ts_clean, "%Y-%m-%dT%H:%M:%S.%fZ")
                    else:
                        timestamp = datetime.strptime(last_transition, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    continue

                if cutoff and timestamp < cutoff:
                    continue

                cond_type = cond.get("type", "")
                cond_status = cond.get("status", "")
                reason = cond.get("reason", "")
                message = cond.get("message", "")

                # Create event-like entry
                events.append(
                    TimelineEvent(
                        timestamp=timestamp,
                        kind=kind,
                        name=name,
                        event_type="Normal" if cond_status == "True" else "Warning",
                        reason=f"{cond_type}={cond_status}",
                        message=message or reason,
                    )
                )

    return events


def print_timeline(events: list[TimelineEvent], verbose: bool = False) -> None:
    """Print timeline to console."""
    if not events:
        print("No events found")
        return

    # Group events by time (minute buckets)
    current_time = None

    for event in events:
        time_bucket = event.timestamp.strftime("%Y-%m-%d %H:%M")

        if time_bucket != current_time:
            current_time = time_bucket
            print(f"\n{current_time}")
            print("-" * 40)

        # Format event line
        seconds = event.timestamp.strftime(":%S")
        type_color = "⚠️ " if event.event_type == "Warning" else ""

        print(f"  {seconds} {event.icon}{event.kind}/{event.name}")
        print(f"       {type_color}{event.reason}: {event.message[:80]}")

        if verbose and len(event.message) > 80:
            # Print full message wrapped
            for i in range(80, len(event.message), 80):
                print(f"       {event.message[i:i+80]}")


def print_summary(events: list[TimelineEvent]) -> None:
    """Print timeline summary."""
    if not events:
        return

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    total = len(events)
    warnings = sum(1 for e in events if e.event_type == "Warning")

    print(f"Total events: {total}")
    print(f"Warnings: {warnings}")

    if events:
        first = events[0]
        last = events[-1]
        duration = last.timestamp - first.timestamp

        print(f"\nTime range: {first.time_str} - {last.time_str}")
        print(f"Duration: {duration}")

    # Count by kind
    by_kind: dict[str, int] = {}
    for e in events:
        by_kind[e.kind] = by_kind.get(e.kind, 0) + 1

    print("\nEvents by resource type:")
    for kind, count in sorted(by_kind.items(), key=lambda x: -x[1]):
        print(f"  {kind}: {count}")


def export_json(events: list[TimelineEvent]) -> str:
    """Export timeline to JSON."""
    return json.dumps(
        [
            {
                "timestamp": e.timestamp.isoformat() + "Z",
                "kind": e.kind,
                "name": e.name,
                "type": e.event_type,
                "reason": e.reason,
                "message": e.message,
            }
            for e in events
        ],
        indent=2,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build provisioning event timeline for CAPI clusters",
    )
    parser.add_argument(
        "cluster",
        help="Cluster name",
    )
    parser.add_argument(
        "--namespace",
        "-n",
        default="default",
        help="Namespace (default: default)",
    )
    parser.add_argument(
        "--since",
        default=None,
        help="Show events since duration (e.g., 1h, 30m, 2d)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show full event messages",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write output to file",
    )
    args = parser.parse_args()

    if not find_kubectl():
        print("Error: kubectl not found in PATH", file=sys.stderr)
        return 1

    since = parse_duration(args.since) if args.since else None

    print(f"Building timeline for cluster '{args.cluster}'...")
    events = get_events(args.cluster, args.namespace, since)

    if args.format == "json" or args.output:
        output = export_json(events)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Timeline written to: {args.output}")
        else:
            print(output)
    else:
        print_timeline(events, args.verbose)
        print_summary(events)

    return 0


if __name__ == "__main__":
    sys.exit(main())
