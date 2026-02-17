// check-cluster-health analyzes CAPI conditions and reports cluster health.
//
// Usage:
//
//	go run ./check-cluster-health <cluster-name> [flags]
//
// Examples:
//
//	go run ./check-cluster-health my-cluster
//	go run ./check-cluster-health my-cluster -n clusters --json
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strings"
	"time"

	"k8s-cluster-api-tools/internal/kubectl"
)

type healthIssue struct {
	Resource      string `json:"resource"`
	Name          string `json:"name"`
	ConditionType string `json:"condition_type"`
	Status        string `json:"status"`
	Reason        string `json:"reason"`
	Message       string `json:"message"`
	Severity      string `json:"severity"`
}

func (h healthIssue) String() string {
	icon := "⚠️"
	if h.Severity == "error" {
		icon = "❌"
	}
	var b strings.Builder
	fmt.Fprintf(&b, "%s [%s] %s/%s\n", icon, h.Severity, h.Resource, h.Name)
	fmt.Fprintf(&b, "  Condition: %s = %s\n", h.ConditionType, h.Status)
	if h.Reason != "" {
		fmt.Fprintf(&b, "  Reason: %s\n", h.Reason)
	}
	if h.Message != "" {
		fmt.Fprintf(&b, "  Message: %s\n", h.Message)
	}
	return b.String()
}

var criticalConditions = map[string]string{
	"Ready":               "error",
	"Available":           "error",
	"InfrastructureReady": "error",
	"ControlPlaneReady":   "error",
	"BootstrapReady":      "warning",
	"Provisioned":         "error",
	"Initialized":         "warning",
}

var expectedTrue = []string{
	"Ready", "Available", "InfrastructureReady", "ControlPlaneReady",
	"BootstrapReady", "Provisioned", "Initialized", "UpToDate",
}

var errorReasons = map[string]bool{
	"ProvisioningFailed":         true,
	"InvalidConfiguration":       true,
	"WaitingForInfrastructure":   true,
	"WaitingForControlPlane":     true,
	"ScalingDown":                true,
	"Deleting":                   true,
	"Failed":                     true,
	"ProviderError":              true,
}

func analyzeConditions(resourceType, name string, conditions []interface{}) []healthIssue {
	var issues []healthIssue
	expectedSet := map[string]bool{}
	for _, e := range expectedTrue {
		expectedSet[e] = true
	}

	for _, c := range conditions {
		cm, ok := c.(map[string]interface{})
		if !ok {
			continue
		}
		condType, _ := cm["type"].(string)
		status, _ := cm["status"].(string)
		reason, _ := cm["reason"].(string)
		message, _ := cm["message"].(string)

		if expectedSet[condType] && status != "True" {
			sev := criticalConditions[condType]
			if sev == "" {
				sev = "warning"
			}
			issues = append(issues, healthIssue{
				Resource: resourceType, Name: name,
				ConditionType: condType, Status: status,
				Reason: reason, Message: message, Severity: sev,
			})
		}

		if errorReasons[reason] {
			issues = append(issues, healthIssue{
				Resource: resourceType, Name: name,
				ConditionType: condType, Status: status,
				Reason: reason, Message: message, Severity: "warning",
			})
		}
	}
	return issues
}

func getConditions(item map[string]interface{}) []interface{} {
	status := kubectl.GetMap(item, "status")
	conds := kubectl.GetSlice(status, "conditions")
	if len(conds) == 0 {
		v1b2 := kubectl.GetMap(status, "v1beta2")
		conds = kubectl.GetSlice(v1b2, "conditions")
	}
	return conds
}

func getClusterResources(clusterName, namespace string) map[string][]map[string]interface{} {
	resources := map[string][]map[string]interface{}{}
	ns := namespace
	if ns == "" {
		ns = "default"
	}

	// Cluster
	items, _ := kubectl.RunJSON("clusters.cluster.x-k8s.io/"+clusterName, ns, "", false)
	if len(items) > 0 {
		resources["Cluster"] = items
	}

	label := "cluster.x-k8s.io/cluster-name=" + clusterName
	for _, rt := range []struct{ name, resource string }{
		{"Machine", "machines.cluster.x-k8s.io"},
		{"MachineSet", "machinesets.cluster.x-k8s.io"},
		{"MachineDeployment", "machinedeployments.cluster.x-k8s.io"},
	} {
		items, _ := kubectl.RunJSON(rt.resource, ns, label, false)
		if len(items) > 0 {
			resources[rt.name] = items
		}
	}

	// KubeadmControlPlane
	if len(resources["Cluster"]) > 0 {
		cluster := resources["Cluster"][0]
		spec := kubectl.GetMap(cluster, "spec")
		cpRef := kubectl.GetMap(spec, "controlPlaneRef")
		if kind, _ := cpRef["kind"].(string); kind == "KubeadmControlPlane" {
			if cpName, _ := cpRef["name"].(string); cpName != "" {
				items, _ := kubectl.RunJSON("kubeadmcontrolplanes.controlplane.cluster.x-k8s.io/"+cpName, ns, "", false)
				if len(items) > 0 {
					resources["KubeadmControlPlane"] = items
				}
			}
		}
	}

	return resources
}

func checkClusterHealth(clusterName, namespace string) (map[string]interface{}, []healthIssue) {
	resources := getClusterResources(clusterName, namespace)
	var allIssues []healthIssue

	ns := namespace
	if ns == "" {
		ns = "default"
	}
	summary := map[string]interface{}{
		"cluster_name": clusterName,
		"namespace":    ns,
		"timestamp":    time.Now().Format(time.RFC3339),
		"resources":    map[string]int{},
	}

	resCount := summary["resources"].(map[string]int)
	for rt, items := range resources {
		resCount[rt] = len(items)
		for _, item := range items {
			name := kubectl.GetString(item, "metadata.name")
			if name == "" {
				name = "unknown"
			}
			conds := getConditions(item)
			if len(conds) > 0 {
				issues := analyzeConditions(rt, name, conds)
				allIssues = append(allIssues, issues...)
			}
		}
	}

	errors := 0
	warnings := 0
	for _, i := range allIssues {
		if i.Severity == "error" {
			errors++
		} else {
			warnings++
		}
	}
	summary["total_issues"] = len(allIssues)
	summary["errors"] = errors
	summary["warnings"] = warnings

	return summary, allIssues
}

func printHealthReport(summary map[string]interface{}, issues []healthIssue) {
	sep := strings.Repeat("=", 60)
	fmt.Println(sep)
	fmt.Println("CLUSTER HEALTH REPORT")
	fmt.Println(sep)
	fmt.Printf("Cluster: %v\n", summary["cluster_name"])
	fmt.Printf("Namespace: %v\n", summary["namespace"])
	fmt.Printf("Timestamp: %v\n", summary["timestamp"])
	fmt.Println()

	fmt.Println("Resources found:")
	if res, ok := summary["resources"].(map[string]int); ok {
		for k, v := range res {
			fmt.Printf("  %s: %d\n", k, v)
		}
	}

	fmt.Print("\nHealth Status: ")
	errors, _ := summary["errors"].(int)
	warnings, _ := summary["warnings"].(int)

	if errors > 0 {
		fmt.Println("❌ UNHEALTHY")
	} else if warnings > 0 {
		fmt.Println("⚠️ DEGRADED")
	} else {
		fmt.Println("✅ HEALTHY")
	}
	fmt.Printf("  Errors: %d\n", errors)
	fmt.Printf("  Warnings: %d\n", warnings)

	if len(issues) > 0 {
		fmt.Printf("\nIssues:\n%s\n", strings.Repeat("-", 40))
		for _, issue := range issues {
			fmt.Println(issue.String())
		}
	}
}

func main() {
	namespace := flag.String("n", "", "Namespace of the cluster")
	outputFile := flag.String("o", "", "Output JSON file for results")
	jsonOut := flag.Bool("json", false, "Output as JSON only")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s <cluster-name> [flags]\n\nCheck cluster health by analyzing CAPI conditions.\n\nFlags:\n", os.Args[0])
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

	summary, issues := checkClusterHealth(clusterName, *namespace)

	if *jsonOut {
		out := map[string]interface{}{
			"summary": summary,
			"issues":  issues,
		}
		data, _ := json.MarshalIndent(out, "", "  ")
		fmt.Println(string(data))
	} else {
		printHealthReport(summary, issues)
	}

	if *outputFile != "" {
		out := map[string]interface{}{
			"summary": summary,
			"issues":  issues,
		}
		data, _ := json.MarshalIndent(out, "", "  ")
		if err := os.WriteFile(*outputFile, data, 0o644); err != nil {
			fmt.Fprintf(os.Stderr, "Error writing to %s: %v\n", *outputFile, err)
		} else {
			fmt.Printf("\nResults saved to: %s\n", *outputFile)
		}
	}

	errors, _ := summary["errors"].(int)
	warnings, _ := summary["warnings"].(int)
	if errors > 0 {
		os.Exit(2)
	}
	if warnings > 0 {
		os.Exit(1)
	}
}
