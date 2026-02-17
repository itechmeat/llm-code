// compare-versions compares CAPI version specifications and API changes.
//
// Usage:
//
//	go run ./compare-versions <from> <to> [flags]
//	go run ./compare-versions --list
//
// Examples:
//
//	go run ./compare-versions v1.6.0 v1.12.0
//	go run ./compare-versions v1.6.0 v1.12.0 --checklist
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"sort"
	"strconv"
	"strings"
)

type versionInfo struct {
	ReleaseDate string
	Kubernetes  struct{ Min, Max string }
	GoVersion   string
	APIVersion  string
	Features    []string
	Deprecations []string
	Breaking    []string
}

type apiChange struct {
	Type        string `json:"type"`
	Kind        string `json:"kind"`
	Old         string `json:"old"`
	New         string `json:"new"`
	Description string `json:"description"`
}

type comparison struct {
	From            string
	To              string
	KubernetesChange map[string]string
	GoChange         map[string]string
	NewFeatures      []string
	Deprecations     []string
	BreakingChanges  []string
	APIChanges       []apiChange
	VersionsBetween  []string
}

var versionDB = map[string]versionInfo{
	"v1.6.0": {ReleaseDate: "2024-03-26", Kubernetes: struct{ Min, Max string }{"v1.26.0", "v1.30.x"}, GoVersion: "1.21", APIVersion: "v1beta1",
		Features: []string{"ClusterClass stable", "MachinePool support improvements", "clusterctl upgrade enhancements"},
		Deprecations: []string{"v1alpha3 API removal planned", "Cluster.spec.paused deprecated for managed topologies"},
	},
	"v1.7.0": {ReleaseDate: "2024-04-23", Kubernetes: struct{ Min, Max string }{"v1.27.0", "v1.31.x"}, GoVersion: "1.21", APIVersion: "v1beta1",
		Features:    []string{"In-place propagation for ClusterClass", "MachineDeployment rollout improvements", "Enhanced MachineHealthCheck"},
		Deprecations: []string{"v1alpha4 API removal planned"},
		Breaking:    []string{"Minimum Kubernetes version raised to v1.27.0"},
	},
	"v1.8.0": {ReleaseDate: "2024-10-08", Kubernetes: struct{ Min, Max string }{"v1.28.0", "v1.32.x"}, GoVersion: "1.22", APIVersion: "v1beta1",
		Features:    []string{"v1beta2 conditions (experimental)", "ClusterClass variable discovery", "Improved topology mutation hooks"},
		Deprecations: []string{"v1beta1 conditions (planned migration to v1beta2)"},
		Breaking:    []string{"Go 1.22 required", "Minimum Kubernetes version raised to v1.28.0"},
	},
	"v1.9.0": {ReleaseDate: "2025-01-14", Kubernetes: struct{ Min, Max string }{"v1.29.0", "v1.33.x"}, GoVersion: "1.22", APIVersion: "v1beta1",
		Features:    []string{"MachinePool machines for CAPD", "Node deletion tracking improvements", "Enhanced ClusterResourceSet bindings"},
	},
	"v1.10.0": {ReleaseDate: "2025-04-08", Kubernetes: struct{ Min, Max string }{"v1.30.0", "v1.34.x"}, GoVersion: "1.23", APIVersion: "v1beta1",
		Features:    []string{"Managed topologies improvements", "Extended provider contract", "Improved machine remediation"},
	},
	"v1.11.0": {ReleaseDate: "2025-07-08", Kubernetes: struct{ Min, Max string }{"v1.30.0", "v1.34.x"}, GoVersion: "1.24", APIVersion: "v1beta1",
		Features: []string{"ClusterClass variable discovery", "Improved rollout controls"},
		Breaking: []string{"Go 1.24 required"},
	},
	"v1.12.0": {ReleaseDate: "2025-10-07", Kubernetes: struct{ Min, Max string }{"v1.31.0", "v1.35.x"}, GoVersion: "1.24", APIVersion: "v1beta1",
		Features:     []string{"v1beta2 conditions GA", "Enhanced topology validation", "Improved observability"},
		Deprecations: []string{"v1beta1 conditions (use v1beta2)"},
	},
}

var apiChangesDB = []apiChange{
	{Type: "field_rename", Kind: "Cluster", Old: "spec.infrastructureRef", New: "spec.infrastructureRef (TypedObjectReference)", Description: "InfrastructureRef now uses TypedObjectReference type"},
	{Type: "field_rename", Kind: "Cluster", Old: "spec.controlPlaneRef", New: "spec.controlPlaneRef (TypedObjectReference)", Description: "ControlPlaneRef now uses TypedObjectReference type"},
	{Type: "field_change", Kind: "Machine", Old: "status.phase", New: "status.conditions", Description: "Phase deprecated; use conditions for state"},
	{Type: "field_add", Kind: "Cluster", Old: "", New: "status.v1beta2.conditions", Description: "New v1beta2 conditions location"},
	{Type: "field_add", Kind: "MachineDeployment", Old: "", New: "spec.strategy.rollingUpdate.deletePolicy", Description: "New delete policy for rollouts"},
	{Type: "behavior_change", Kind: "All", Old: "Integer durations (seconds)", New: "String durations (e.g., '10m')", Description: "Duration fields now use string format"},
}

func parseVersion(v string) [3]int {
	v = strings.TrimPrefix(v, "v")
	parts := strings.SplitN(v, ".", 3)
	var r [3]int
	for i, p := range parts {
		if i < 3 {
			r[i], _ = strconv.Atoi(p)
		}
	}
	return r
}

func versionLess(a, b string) bool {
	av, bv := parseVersion(a), parseVersion(b)
	if av[0] != bv[0] {
		return av[0] < bv[0]
	}
	if av[1] != bv[1] {
		return av[1] < bv[1]
	}
	return av[2] < bv[2]
}

func sortedVersions() []string {
	keys := make([]string, 0, len(versionDB))
	for k := range versionDB {
		keys = append(keys, k)
	}
	sort.Slice(keys, func(i, j int) bool { return versionLess(keys[i], keys[j]) })
	return keys
}

func getVersionsBetween(from, to string) []string {
	var result []string
	for _, v := range sortedVersions() {
		if versionLess(from, v) && !versionLess(to, v) {
			result = append(result, v)
		}
	}
	return result
}

func compare(from, to string) comparison {
	c := comparison{
		From:            from,
		To:              to,
		KubernetesChange: map[string]string{},
		GoChange:         map[string]string{},
	}
	c.VersionsBetween = getVersionsBetween(from, to)

	for _, v := range c.VersionsBetween {
		info := versionDB[v]
		c.NewFeatures = append(c.NewFeatures, info.Features...)
		c.Deprecations = append(c.Deprecations, info.Deprecations...)
		c.BreakingChanges = append(c.BreakingChanges, info.Breaking...)
	}

	fromInfo, fromOK := versionDB[from]
	toInfo, toOK := versionDB[to]
	if fromOK && toOK {
		c.KubernetesChange["from_min"] = fromInfo.Kubernetes.Min
		c.KubernetesChange["from_max"] = fromInfo.Kubernetes.Max
		c.KubernetesChange["to_min"] = toInfo.Kubernetes.Min
		c.KubernetesChange["to_max"] = toInfo.Kubernetes.Max
		c.GoChange["from"] = fromInfo.GoVersion
		c.GoChange["to"] = toInfo.GoVersion
	}
	c.APIChanges = apiChangesDB
	return c
}

func printComparison(c comparison) {
	sep := strings.Repeat("=", 60)
	fmt.Printf("\n%s\n", sep)
	fmt.Printf("CAPI Version Comparison: %s → %s\n", c.From, c.To)
	fmt.Println(sep)

	if len(c.VersionsBetween) > 0 {
		fmt.Printf("\nVersions in range: %s\n", strings.Join(c.VersionsBetween, ", "))
	}

	if len(c.KubernetesChange) > 0 {
		fmt.Println("\n📦 Kubernetes Version Requirements:")
		fmt.Printf("   From: %s - %s\n", c.KubernetesChange["from_min"], c.KubernetesChange["from_max"])
		fmt.Printf("   To:   %s - %s\n", c.KubernetesChange["to_min"], c.KubernetesChange["to_max"])
	}

	if c.GoChange["from"] != c.GoChange["to"] {
		fmt.Println("\n🔧 Go Version:")
		fmt.Printf("   %s → %s\n", c.GoChange["from"], c.GoChange["to"])
	}

	if len(c.BreakingChanges) > 0 {
		fmt.Println("\n🔴 Breaking Changes:")
		for _, ch := range c.BreakingChanges {
			fmt.Printf("   • %s\n", ch)
		}
	}

	if len(c.Deprecations) > 0 {
		fmt.Println("\n⚠️  Deprecations:")
		for _, d := range c.Deprecations {
			fmt.Printf("   • %s\n", d)
		}
	}

	if len(c.NewFeatures) > 0 {
		fmt.Println("\n✨ New Features:")
		for _, f := range c.NewFeatures {
			fmt.Printf("   • %s\n", f)
		}
	}

	if len(c.APIChanges) > 0 {
		fmt.Println("\n📝 API Changes (v1beta1 → v1beta2):")
		icons := map[string]string{
			"field_rename":    "↔️",
			"field_change":    "🔄",
			"field_add":       "➕",
			"field_remove":    "➖",
			"behavior_change": "⚙️",
		}
		for _, ch := range c.APIChanges {
			icon := icons[ch.Type]
			if icon == "" {
				icon = "·"
			}
			fmt.Printf("\n   %s [%s] %s\n", icon, ch.Kind, ch.Description)
			if ch.Old != "" {
				fmt.Printf("      Old: %s\n", ch.Old)
			}
			if ch.New != "" {
				fmt.Printf("      New: %s\n", ch.New)
			}
		}
	}
}

func printChecklist(c comparison) {
	sep := strings.Repeat("=", 60)
	fmt.Printf("\n%s\n", sep)
	fmt.Println("MIGRATION CHECKLIST")
	fmt.Println(sep)

	fmt.Println("\n□ Pre-migration:")
	if toMin, ok := c.KubernetesChange["to_min"]; ok {
		fmt.Printf("   □ Verify Kubernetes version meets %s+ requirement\n", toMin)
	}
	if c.GoChange["from"] != c.GoChange["to"] {
		fmt.Printf("   □ Update Go to %s\n", c.GoChange["to"])
	}
	fmt.Println("   □ Backup cluster state (clusterctl move or export)")
	fmt.Println("   □ Review release notes for all versions in range")

	if len(c.BreakingChanges) > 0 {
		fmt.Println("\n□ Breaking changes to address:")
		for i, ch := range c.BreakingChanges {
			fmt.Printf("   □ %d. %s\n", i+1, ch)
		}
	}

	if len(c.Deprecations) > 0 {
		fmt.Println("\n□ Deprecated features to migrate:")
		for i, d := range c.Deprecations {
			fmt.Printf("   □ %d. %s\n", i+1, d)
		}
	}

	fmt.Println("\n□ Post-migration:")
	fmt.Println("   □ Run clusterctl upgrade plan")
	fmt.Println("   □ Verify all clusters Ready")
	fmt.Println("   □ Check conditions for any warnings")
	fmt.Println("   □ Update provider versions if needed")
}

func listVersions() {
	fmt.Println("\nKnown CAPI Versions:")
	fmt.Println(strings.Repeat("-", 60))
	fmt.Printf("%-10s %-12s %-10s %-10s %-6s\n", "Version", "Release", "K8s Min", "K8s Max", "Go")
	fmt.Println(strings.Repeat("-", 60))
	for _, v := range sortedVersions() {
		info := versionDB[v]
		fmt.Printf("%-10s %-12s %-10s %-10s %-6s\n", v, info.ReleaseDate, info.Kubernetes.Min, info.Kubernetes.Max, info.GoVersion)
	}
}

func main() {
	listFlag := flag.Bool("list", false, "List all known versions")
	checklist := flag.Bool("checklist", false, "Include migration checklist")
	format := flag.String("format", "text", "Output format: text, json")
	output := flag.String("o", "", "Write output to file")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s <from-version> <to-version> [flags]\n\nCompare CAPI version specifications.\n\nFlags:\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()

	if *listFlag {
		listVersions()
		os.Exit(0)
	}

	if flag.NArg() < 2 {
		fmt.Fprintln(os.Stderr, "Error: Both from_version and to_version required")
		fmt.Fprintln(os.Stderr, "Use --list to see available versions")
		os.Exit(1)
	}

	fromV := flag.Arg(0)
	toV := flag.Arg(1)
	if !strings.HasPrefix(fromV, "v") {
		fromV = "v" + fromV
	}
	if !strings.HasPrefix(toV, "v") {
		toV = "v" + toV
	}

	if _, ok := versionDB[fromV]; !ok {
		fmt.Fprintf(os.Stderr, "Warning: Version %s not in database\n", fromV)
	}
	if _, ok := versionDB[toV]; !ok {
		fmt.Fprintf(os.Stderr, "Warning: Version %s not in database\n", toV)
	}

	comp := compare(fromV, toV)

	if *format == "json" || *output != "" {
		data := map[string]interface{}{
			"from_version":     comp.From,
			"to_version":       comp.To,
			"versions_between": comp.VersionsBetween,
			"kubernetes_change": comp.KubernetesChange,
			"go_change":        comp.GoChange,
			"breaking_changes": comp.BreakingChanges,
			"deprecations":     comp.Deprecations,
			"new_features":     comp.NewFeatures,
			"api_changes":      comp.APIChanges,
		}
		out, _ := json.MarshalIndent(data, "", "  ")
		if *output != "" {
			if err := os.WriteFile(*output, out, 0o644); err != nil {
				fmt.Fprintf(os.Stderr, "Error: %v\n", err)
				os.Exit(1)
			}
			fmt.Printf("Comparison written to: %s\n", *output)
		} else {
			fmt.Println(string(out))
		}
	} else {
		printComparison(comp)
		if *checklist {
			printChecklist(comp)
		}
	}
}
