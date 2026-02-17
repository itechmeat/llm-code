// analyze-conditions collects and reports conditions from CAPI resources.
//
// Usage:
//
//	go run ./analyze-conditions [flags]
//
// Examples:
//
//	go run ./analyze-conditions -c my-cluster -n default
//	go run ./analyze-conditions -A --format json
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"sort"
	"strings"

	"k8s-cluster-api-tools/internal/kubectl"
)

type conditionInfo struct {
	ResourceKind      string
	ResourceName      string
	ResourceNamespace string
	ConditionType     string
	Status            string
	Reason            string
	Message           string
	LastTransition    string
}

func (c *conditionInfo) isHealthy() bool {
	positive := map[string]bool{
		"Ready": true, "Available": true, "InfrastructureReady": true,
		"ControlPlaneReady": true, "BootstrapReady": true,
		"Provisioned": true, "Initialized": true, "UpToDate": true,
	}
	negative := map[string]bool{
		"Stalled": true, "Deleting": true, "Paused": true,
	}
	if positive[c.ConditionType] {
		return c.Status == "True"
	}
	if negative[c.ConditionType] {
		return c.Status == "False"
	}
	return true
}

func (c *conditionInfo) toRow() []string {
	icons := map[string]string{"True": "✓", "False": "✗", "Unknown": "?"}
	icon := icons[c.Status]
	if icon == "" {
		icon = "?"
	}
	reason := c.Reason
	if reason == "" {
		reason = "-"
	}
	return []string{
		c.ResourceKind,
		c.ResourceNamespace + "/" + c.ResourceName,
		c.ConditionType,
		icon + " " + c.Status,
		reason,
	}
}

func extractConditions(item map[string]interface{}) []conditionInfo {
	kind := getString(item, "kind", "Unknown")
	metadata := getMap(item, "metadata")
	name := getString(metadata, "name", "unknown")
	namespace := getString(metadata, "namespace", "default")
	status := getMap(item, "status")

	conds := getSlice(status, "conditions")
	if len(conds) == 0 {
		v1b2 := getMap(status, "v1beta2")
		conds = getSlice(v1b2, "conditions")
	}

	var result []conditionInfo
	for _, c := range conds {
		cm, ok := c.(map[string]interface{})
		if !ok {
			continue
		}
		result = append(result, conditionInfo{
			ResourceKind:      kind,
			ResourceName:      name,
			ResourceNamespace: namespace,
			ConditionType:     getString(cm, "type", ""),
			Status:            getString(cm, "status", "Unknown"),
			Reason:            getString(cm, "reason", ""),
			Message:           getString(cm, "message", ""),
			LastTransition:    getString(cm, "lastTransitionTime", ""),
		})
	}
	return result
}

func collectAllConditions(namespace, clusterName string, allNamespaces bool) []conditionInfo {
	resources := []string{
		"clusters.cluster.x-k8s.io",
		"machines.cluster.x-k8s.io",
		"machinesets.cluster.x-k8s.io",
		"machinedeployments.cluster.x-k8s.io",
		"machinepools.cluster.x-k8s.io",
		"machinehealthchecks.cluster.x-k8s.io",
		"kubeadmconfigs.bootstrap.cluster.x-k8s.io",
		"kubeadmcontrolplanes.controlplane.cluster.x-k8s.io",
	}

	labelSel := ""
	if clusterName != "" {
		labelSel = "cluster.x-k8s.io/cluster-name=" + clusterName
	}

	var all []conditionInfo
	ns := namespace
	allNS := allNamespaces && namespace == ""

	for _, res := range resources {
		items, err := kubectl.RunJSON(res, ns, labelSel, allNS)
		if err != nil {
			continue
		}
		for _, item := range items {
			all = append(all, extractConditions(item)...)
		}
	}

	// Also get Cluster directly if filtering
	if clusterName != "" {
		items, err := kubectl.RunJSON("clusters.cluster.x-k8s.io/"+clusterName, ns, "", false)
		if err == nil {
			for _, item := range items {
				if getString(item, "kind", "") == "Cluster" {
					all = append(all, extractConditions(item)...)
				}
			}
		}
	}

	return all
}

func printTable(conditions []conditionInfo, showAll bool) {
	filtered := conditions
	if !showAll {
		filtered = nil
		for i := range conditions {
			if !conditions[i].isHealthy() {
				filtered = append(filtered, conditions[i])
			}
		}
	}

	if len(filtered) == 0 {
		fmt.Println("No unhealthy conditions found ✅")
		return
	}

	headers := []string{"KIND", "RESOURCE", "CONDITION", "STATUS", "REASON"}
	rows := make([][]string, len(filtered))
	for i := range filtered {
		rows[i] = filtered[i].toRow()
	}

	widths := make([]int, len(headers))
	for i, h := range headers {
		widths[i] = len(h)
	}
	for _, row := range rows {
		for i, cell := range row {
			if len(cell) > widths[i] {
				widths[i] = len(cell)
			}
		}
	}

	for i, h := range headers {
		fmt.Printf("%-*s  ", widths[i], h)
	}
	fmt.Println()
	totalW := 0
	for _, w := range widths {
		totalW += w + 2
	}
	fmt.Println(strings.Repeat("-", totalW))

	for _, row := range rows {
		for i, cell := range row {
			fmt.Printf("%-*s  ", widths[i], cell)
		}
		fmt.Println()
	}
}

func printSummary(conditions []conditionInfo) {
	total := len(conditions)
	healthy := 0
	for i := range conditions {
		if conditions[i].isHealthy() {
			healthy++
		}
	}
	unhealthy := total - healthy

	byKind := map[string][3]int{} // total, healthy, unhealthy
	for i := range conditions {
		k := conditions[i].ResourceKind
		counts := byKind[k]
		counts[0]++
		if conditions[i].isHealthy() {
			counts[1]++
		} else {
			counts[2]++
		}
		byKind[k] = counts
	}

	fmt.Printf("\n%s\n", strings.Repeat("=", 50))
	fmt.Println("CONDITIONS SUMMARY")
	fmt.Println(strings.Repeat("=", 50))
	fmt.Printf("Total conditions: %d\n", total)
	fmt.Printf("  Healthy: %d ✓\n", healthy)
	fmt.Printf("  Unhealthy: %d ✗\n", unhealthy)

	fmt.Println("\nBy resource type:")
	kinds := make([]string, 0, len(byKind))
	for k := range byKind {
		kinds = append(kinds, k)
	}
	sort.Strings(kinds)
	for _, k := range kinds {
		c := byKind[k]
		icon := "✓"
		if c[2] > 0 {
			icon = "✗"
		}
		fmt.Printf("  %s: %d/%d healthy %s\n", k, c[1], c[0], icon)
	}

	unhealthyTypes := map[string]bool{}
	for i := range conditions {
		if !conditions[i].isHealthy() {
			unhealthyTypes[conditions[i].ConditionType] = true
		}
	}
	if len(unhealthyTypes) > 0 {
		fmt.Println("\nUnhealthy condition types:")
		ts := make([]string, 0, len(unhealthyTypes))
		for t := range unhealthyTypes {
			ts = append(ts, t)
		}
		sort.Strings(ts)
		for _, t := range ts {
			fmt.Printf("  - %s\n", t)
		}
	}
}

// helpers
func getString(m map[string]interface{}, key, def string) string {
	if v, ok := m[key].(string); ok {
		return v
	}
	return def
}

func getMap(m map[string]interface{}, key string) map[string]interface{} {
	if v, ok := m[key].(map[string]interface{}); ok {
		return v
	}
	return map[string]interface{}{}
}

func getSlice(m map[string]interface{}, key string) []interface{} {
	if v, ok := m[key].([]interface{}); ok {
		return v
	}
	return nil
}

func main() {
	namespace := flag.String("n", "", "Namespace to analyze")
	cluster := flag.String("c", "", "Filter by cluster name")
	allNamespaces := flag.Bool("A", false, "Analyze all namespaces")
	showAll := flag.Bool("a", false, "Show all conditions, not just unhealthy")
	format := flag.String("format", "table", "Output format: table, json, summary")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s [flags]\n\nAnalyze conditions from CAPI resources.\n\nFlags:\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()

	if kubectl.Find() == "" {
		fmt.Fprintln(os.Stderr, "Error: kubectl not found in PATH")
		os.Exit(1)
	}

	fmt.Println("Collecting conditions from CAPI resources...")
	conditions := collectAllConditions(*namespace, *cluster, *allNamespaces)

	if len(conditions) == 0 {
		fmt.Println("No CAPI resources found")
		os.Exit(0)
	}

	switch *format {
	case "json":
		var output []map[string]interface{}
		for _, c := range conditions {
			output = append(output, map[string]interface{}{
				"resource":  c.ResourceKind + "/" + c.ResourceNamespace + "/" + c.ResourceName,
				"condition": c.ConditionType,
				"status":    c.Status,
				"reason":    c.Reason,
				"message":   c.Message,
				"healthy":   c.isHealthy(),
			})
		}
		data, _ := json.MarshalIndent(output, "", "  ")
		fmt.Println(string(data))
	case "summary":
		printSummary(conditions)
	default:
		printTable(conditions, *showAll)
		printSummary(conditions)
	}

	for _, c := range conditions {
		if !c.isHealthy() {
			os.Exit(1)
		}
	}
}
