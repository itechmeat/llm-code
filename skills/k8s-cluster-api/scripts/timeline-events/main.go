// timeline-events builds a chronological provisioning event timeline for CAPI clusters.
//
// Usage:
//
//	go run ./timeline-events <cluster-name> [flags]
//
// Examples:
//
//	go run ./timeline-events my-cluster -n default
//	go run ./timeline-events my-cluster --since 1h --format json
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"

	"k8s-cluster-api-tools/internal/kubectl"
)

type timelineEvent struct {
	Timestamp time.Time `json:"-"`
	Kind      string    `json:"kind"`
	Name      string    `json:"name"`
	EventType string    `json:"type"`
	Reason    string    `json:"reason"`
	Message   string    `json:"message"`
}

func (e timelineEvent) icon() string {
	switch {
	case e.EventType == "Warning":
		return "⚠️ "
	case strings.Contains(e.Reason, "=True"):
		return "✓ "
	case strings.Contains(e.Reason, "=False"):
		return "✗ "
	default:
		return "  "
	}
}

func (e timelineEvent) timeStr() string {
	return e.Timestamp.Format("2006-01-02T15:04:05Z")
}

func parseDuration(s string) time.Duration {
	re := regexp.MustCompile(`^(\d+)([smhd])$`)
	m := re.FindStringSubmatch(s)
	if m == nil {
		return 0
	}
	val, _ := strconv.Atoi(m[1])
	switch m[2] {
	case "s":
		return time.Duration(val) * time.Second
	case "m":
		return time.Duration(val) * time.Minute
	case "h":
		return time.Duration(val) * time.Hour
	case "d":
		return time.Duration(val) * 24 * time.Hour
	}
	return 0
}

func parseTimestamp(s string) (time.Time, bool) {
	// Try with microseconds
	re := regexp.MustCompile(`\.(\d{6})\d*Z$`)
	cleaned := re.ReplaceAllString(s, ".${1}Z")

	for _, layout := range []string{
		"2006-01-02T15:04:05.000000Z",
		"2006-01-02T15:04:05Z",
		time.RFC3339,
	} {
		if t, err := time.Parse(layout, cleaned); err == nil {
			return t, true
		}
	}
	return time.Time{}, false
}

func getEvents(clusterName, namespace string, since time.Duration) []timelineEvent {
	var events []timelineEvent

	ok, stdout, _ := kubectl.Run([]string{"get", "events", "-n", namespace, "-o", "json"}, 0)
	if !ok {
		return events
	}

	var data map[string]interface{}
	if err := json.Unmarshal([]byte(stdout), &data); err != nil {
		return events
	}
	items, _ := data["items"].([]interface{})

	var cutoff time.Time
	if since > 0 {
		cutoff = time.Now().UTC().Add(-since)
	}

	for _, e := range items {
		event, ok := e.(map[string]interface{})
		if !ok {
			continue
		}

		involved := kubectl.GetMap(event, "involvedObject")
		involvedName, _ := involved["name"].(string)
		involvedKind, _ := involved["kind"].(string)

		labels := kubectl.GetMap(kubectl.GetMap(event, "metadata"), "labels")
		eventCluster, _ := labels["cluster.x-k8s.io/cluster-name"].(string)

		isRelated := eventCluster == clusterName ||
			involvedName == clusterName ||
			strings.HasPrefix(involvedName, clusterName+"-")
		if !isRelated {
			continue
		}

		lastTS, _ := event["lastTimestamp"].(string)
		if lastTS == "" {
			lastTS, _ = event["eventTime"].(string)
		}
		if lastTS == "" {
			meta := kubectl.GetMap(event, "metadata")
			lastTS, _ = meta["creationTimestamp"].(string)
		}
		if lastTS == "" {
			continue
		}

		ts, ok := parseTimestamp(lastTS)
		if !ok {
			continue
		}
		if !cutoff.IsZero() && ts.Before(cutoff) {
			continue
		}

		evType, _ := event["type"].(string)
		if evType == "" {
			evType = "Normal"
		}
		reason, _ := event["reason"].(string)
		message, _ := event["message"].(string)

		events = append(events, timelineEvent{
			Timestamp: ts,
			Kind:      involvedKind,
			Name:      involvedName,
			EventType: evType,
			Reason:    reason,
			Message:   message,
		})
	}

	// Condition transitions
	condEvents := getConditionEvents(clusterName, namespace, cutoff)
	events = append(events, condEvents...)

	sort.Slice(events, func(i, j int) bool { return events[i].Timestamp.Before(events[j].Timestamp) })
	return events
}

func getConditionEvents(clusterName, namespace string, cutoff time.Time) []timelineEvent {
	var events []timelineEvent
	label := "cluster.x-k8s.io/cluster-name=" + clusterName

	type query struct {
		resource string
		specific string
	}
	queries := []query{
		{"clusters.cluster.x-k8s.io/" + clusterName, ""},
		{"machines.cluster.x-k8s.io", label},
		{"machinedeployments.cluster.x-k8s.io", label},
		{"kubeadmcontrolplanes.controlplane.cluster.x-k8s.io", label},
	}

	for _, q := range queries {
		var items []map[string]interface{}
		if q.specific == "" {
			items, _ = kubectl.RunJSON(q.resource, namespace, "", false)
		} else {
			items, _ = kubectl.RunJSON(q.resource, namespace, q.specific, false)
		}

		for _, item := range items {
			kind, _ := item["kind"].(string)
			if kind == "" {
				kind = "Unknown"
			}
			meta := kubectl.GetMap(item, "metadata")
			name, _ := meta["name"].(string)
			if name == "" {
				name = "unknown"
			}

			status := kubectl.GetMap(item, "status")
			conds := kubectl.GetSlice(status, "conditions")
			if len(conds) == 0 {
				v1b2 := kubectl.GetMap(status, "v1beta2")
				conds = kubectl.GetSlice(v1b2, "conditions")
			}

			for _, c := range conds {
				cm, ok := c.(map[string]interface{})
				if !ok {
					continue
				}
				lastT, _ := cm["lastTransitionTime"].(string)
				if lastT == "" {
					continue
				}
				ts, ok := parseTimestamp(lastT)
				if !ok {
					continue
				}
				if !cutoff.IsZero() && ts.Before(cutoff) {
					continue
				}

				condType, _ := cm["type"].(string)
				condStatus, _ := cm["status"].(string)
				reason, _ := cm["reason"].(string)
				message, _ := cm["message"].(string)

				evType := "Normal"
				if condStatus != "True" {
					evType = "Warning"
				}
				if message == "" {
					message = reason
				}

				events = append(events, timelineEvent{
					Timestamp: ts,
					Kind:      kind,
					Name:      name,
					EventType: evType,
					Reason:    condType + "=" + condStatus,
					Message:   message,
				})
			}
		}
	}
	return events
}

func printTimeline(events []timelineEvent, verbose bool) {
	if len(events) == 0 {
		fmt.Println("No events found")
		return
	}

	currentTime := ""
	for _, ev := range events {
		bucket := ev.Timestamp.Format("2006-01-02 15:04")
		if bucket != currentTime {
			currentTime = bucket
			fmt.Printf("\n%s\n", currentTime)
			fmt.Println(strings.Repeat("-", 40))
		}

		secs := ev.Timestamp.Format(":05")
		warn := ""
		if ev.EventType == "Warning" {
			warn = "⚠️ "
		}
		fmt.Printf("  %s %s%s/%s\n", secs, ev.icon(), ev.Kind, ev.Name)

		msg := ev.Message
		if !verbose && len(msg) > 80 {
			msg = msg[:80]
		}
		fmt.Printf("       %s%s: %s\n", warn, ev.Reason, msg)
	}
}

func printSummary(events []timelineEvent) {
	if len(events) == 0 {
		return
	}
	sep := strings.Repeat("=", 50)
	fmt.Printf("\n%s\nSUMMARY\n%s\n", sep, sep)

	total := len(events)
	warnings := 0
	for _, e := range events {
		if e.EventType == "Warning" {
			warnings++
		}
	}
	fmt.Printf("Total events: %d\n", total)
	fmt.Printf("Warnings: %d\n", warnings)

	first := events[0]
	last := events[len(events)-1]
	duration := last.Timestamp.Sub(first.Timestamp)
	fmt.Printf("\nTime range: %s - %s\n", first.timeStr(), last.timeStr())
	fmt.Printf("Duration: %s\n", duration)

	byKind := map[string]int{}
	for _, e := range events {
		byKind[e.Kind]++
	}
	fmt.Println("\nEvents by resource type:")
	type kc struct {
		k string
		c int
	}
	sorted := make([]kc, 0, len(byKind))
	for k, c := range byKind {
		sorted = append(sorted, kc{k, c})
	}
	sort.Slice(sorted, func(i, j int) bool { return sorted[i].c > sorted[j].c })
	for _, s := range sorted {
		fmt.Printf("  %s: %d\n", s.k, s.c)
	}
}

func exportJSON(events []timelineEvent) string {
	type entry struct {
		Timestamp string `json:"timestamp"`
		Kind      string `json:"kind"`
		Name      string `json:"name"`
		Type      string `json:"type"`
		Reason    string `json:"reason"`
		Message   string `json:"message"`
	}
	var out []entry
	for _, e := range events {
		out = append(out, entry{
			Timestamp: e.Timestamp.Format(time.RFC3339),
			Kind:      e.Kind,
			Name:      e.Name,
			Type:      e.EventType,
			Reason:    e.Reason,
			Message:   e.Message,
		})
	}
	data, _ := json.MarshalIndent(out, "", "  ")
	return string(data)
}

func main() {
	namespace := flag.String("n", "default", "Namespace")
	sinceStr := flag.String("since", "", "Show events since duration (e.g., 1h, 30m, 2d)")
	verbose := flag.Bool("v", false, "Show full event messages")
	format := flag.String("format", "text", "Output format: text, json")
	output := flag.String("o", "", "Write output to file")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s <cluster-name> [flags]\n\nBuild provisioning event timeline.\n\nFlags:\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()

	if flag.NArg() < 1 {
		flag.Usage()
		os.Exit(1)
	}
	clusterName := flag.Arg(0)

	if kubectl.Find() == "" {
		fmt.Fprintln(os.Stderr, "Error: kubectl not found in PATH")
		os.Exit(1)
	}

	var since time.Duration
	if *sinceStr != "" {
		since = parseDuration(*sinceStr)
	}

	fmt.Printf("Building timeline for cluster '%s'...\n", clusterName)
	events := getEvents(clusterName, *namespace, since)

	if *format == "json" || *output != "" {
		out := exportJSON(events)
		if *output != "" {
			if err := os.WriteFile(*output, []byte(out), 0o644); err != nil {
				fmt.Fprintf(os.Stderr, "Error: %v\n", err)
				os.Exit(1)
			}
			fmt.Printf("Timeline written to: %s\n", *output)
		} else {
			fmt.Println(out)
		}
	} else {
		printTimeline(events, *verbose)
		printSummary(events)
	}
}
