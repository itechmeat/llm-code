// migration-checker checks v1beta1 to v1beta2 migration readiness.
//
// Usage:
//
//	go run ./migration-checker [flags]
//
// Examples:
//
//	go run ./migration-checker -f manifest.yaml
//	go run ./migration-checker -d ./manifests/ -r
//	go run ./migration-checker --live -n clusters
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"k8s-cluster-api-tools/internal/kubectl"

	"gopkg.in/yaml.v3"
)

type migrationIssue struct {
	Path     string `json:"path"`
	Field    string `json:"field"`
	Reason   string `json:"reason"`
	Action   string `json:"action"`
	Severity string `json:"severity"`
}

func (m migrationIssue) String() string {
	icon := "⚠️"
	if m.Severity == "info" {
		icon = "ℹ️"
	}
	return fmt.Sprintf("%s %s\n   Reason: %s\n   Action: %s", icon, m.Field, m.Reason, m.Action)
}

type deprecatedField struct {
	Reason string
	Action string
}

var deprecatedFields = map[string]map[string]deprecatedField{
	"Cluster": {
		"spec.paused": {
			Reason: "Replaced by .spec.topology.controlPlane and .spec.topology.workers",
			Action: "Remove spec.paused and use topology-level pause",
		},
	},
	"Machine": {
		"status.phase": {
			Reason: "Phase deprecated in v1beta2; use conditions instead",
			Action: "Migrate to reading status.conditions for machine state",
		},
		"spec.version": {
			Reason: "Version is now inherited from control plane or topology",
			Action: "Remove spec.version if using topology-based cluster",
		},
	},
	"MachineDeployment": {
		"spec.template.spec.version": {
			Reason: "Version now inherited from topology or control plane",
			Action: "Remove if using ClusterClass topology",
		},
	},
	"MachineSet": {
		"spec.template.spec.version": {
			Reason: "Version now inherited from owning MachineDeployment",
			Action: "Remove and let MachineDeployment propagate version",
		},
	},
	"KubeadmControlPlane": {
		"spec.kubeadmConfigSpec.clusterConfiguration.clusterName": {
			Reason: "Inferred from top level, removed to avoid confusion",
			Action: "Remove this field",
		},
	},
}

var objectRefFields = []string{
	"spec.infrastructureRef",
	"spec.controlPlaneRef",
	"spec.bootstrap.configRef",
	"spec.template.spec.infrastructureRef",
	"spec.template.spec.bootstrap.configRef",
}

func getNested(data map[string]interface{}, path string) interface{} {
	keys := strings.Split(path, ".")
	var current interface{} = data
	for _, key := range keys {
		m, ok := current.(map[string]interface{})
		if !ok {
			return nil
		}
		current = m[key]
	}
	return current
}

func checkDeprecatedFields(doc map[string]interface{}, filePath string) []migrationIssue {
	var issues []migrationIssue
	kind, _ := doc["kind"].(string)

	fields, ok := deprecatedFields[kind]
	if !ok {
		return issues
	}

	for field, info := range fields {
		if getNested(doc, field) != nil {
			issues = append(issues, migrationIssue{
				Path:     filePath,
				Field:    field,
				Reason:   info.Reason,
				Action:   info.Action,
				Severity: "warning",
			})
		}
	}
	return issues
}

func checkObjectRefs(doc map[string]interface{}, filePath string) []migrationIssue {
	var issues []migrationIssue

	for _, refPath := range objectRefFields {
		ref := getNested(doc, refPath)
		rm, ok := ref.(map[string]interface{})
		if !ok {
			continue
		}
		if _, hasAV := rm["apiVersion"]; hasAV {
			if _, hasAG := rm["apiGroup"]; !hasAG {
				issues = append(issues, migrationIssue{
					Path:     filePath,
					Field:    refPath + ".apiVersion",
					Reason:   "v1beta2 uses apiGroup instead of apiVersion in object references",
					Action:   "Replace apiVersion with apiGroup (e.g., 'infrastructure.cluster.x-k8s.io')",
					Severity: "info",
				})
			}
		}
		if _, hasNS := rm["namespace"]; hasNS {
			issues = append(issues, migrationIssue{
				Path:     filePath,
				Field:    refPath + ".namespace",
				Reason:   "namespace field removed from object references in v1beta2",
				Action:   "Remove namespace field from object reference",
				Severity: "warning",
			})
		}
	}
	return issues
}

func checkDurationFields(doc map[string]interface{}, filePath string) []migrationIssue {
	var issues []migrationIssue

	type durationPair struct{ old, new string }
	pairs := []durationPair{
		{"spec.nodeDeletionTimeout", "spec.deletion.nodeDeletionTimeoutSeconds"},
		{"spec.nodeDrainTimeout", "spec.deletion.nodeDrainTimeoutSeconds"},
		{"spec.nodeVolumeDetachTimeout", "spec.deletion.nodeVolumeDetachTimeoutSeconds"},
		{"spec.template.spec.nodeDeletionTimeout", "spec.template.spec.deletion.nodeDeletionTimeoutSeconds"},
		{"spec.topology.controlPlane.nodeDeletionTimeout", "spec.topology.controlPlane.deletion.nodeDeletionTimeoutSeconds"},
	}

	for _, p := range pairs {
		val := getNested(doc, p.old)
		if val == nil {
			continue
		}
		if s, ok := val.(string); ok {
			hasAlpha := false
			for _, c := range s {
				if (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') {
					hasAlpha = true
					break
				}
			}
			if hasAlpha {
				issues = append(issues, migrationIssue{
					Path:     filePath,
					Field:    p.old,
					Reason:   "Duration fields changed from string to int32 seconds",
					Action:   fmt.Sprintf("Convert to integer seconds and rename to %s", p.new),
					Severity: "warning",
				})
			}
		}
	}
	return issues
}

func checkAPIVersion(doc map[string]interface{}, filePath string) []migrationIssue {
	var issues []migrationIssue
	av, _ := doc["apiVersion"].(string)

	if strings.Contains(av, "v1beta1") {
		issues = append(issues, migrationIssue{
			Path:     filePath,
			Field:    "apiVersion",
			Reason:   "v1beta1 is deprecated, will be removed in August 2026",
			Action:   "Migrate to v1beta2 API version",
			Severity: "warning",
		})
	} else if strings.Contains(av, "v1alpha") {
		issues = append(issues, migrationIssue{
			Path:     filePath,
			Field:    "apiVersion",
			Reason:   "v1alpha versions are deprecated",
			Action:   "Migrate to v1beta2 API version",
			Severity: "warning",
		})
	}
	return issues
}

func analyzeDocument(doc map[string]interface{}, filePath string) []migrationIssue {
	var issues []migrationIssue
	issues = append(issues, checkAPIVersion(doc, filePath)...)
	issues = append(issues, checkDeprecatedFields(doc, filePath)...)
	issues = append(issues, checkObjectRefs(doc, filePath)...)
	issues = append(issues, checkDurationFields(doc, filePath)...)
	return issues
}

func analyzeFile(path string) []migrationIssue {
	var allIssues []migrationIssue

	data, err := os.ReadFile(path)
	if err != nil {
		fmt.Fprintf(os.Stderr, "File read error %s: %v\n", path, err)
		return nil
	}

	decoder := yaml.NewDecoder(strings.NewReader(string(data)))
	for {
		var doc map[string]interface{}
		if err := decoder.Decode(&doc); err != nil {
			break
		}
		if doc == nil {
			continue
		}
		allIssues = append(allIssues, analyzeDocument(doc, path)...)
	}
	return allIssues
}

func analyzeLiveResources(namespace string) []migrationIssue {
	if kubectl.Find() == "" {
		fmt.Fprintln(os.Stderr, "kubectl not found, skipping live analysis")
		return nil
	}

	var allIssues []migrationIssue
	resourceTypes := []string{
		"clusters.cluster.x-k8s.io",
		"machines.cluster.x-k8s.io",
		"machinesets.cluster.x-k8s.io",
		"machinedeployments.cluster.x-k8s.io",
		"machinepools.cluster.x-k8s.io",
		"kubeadmconfigs.bootstrap.cluster.x-k8s.io",
		"kubeadmcontrolplanes.controlplane.cluster.x-k8s.io",
	}

	allNS := namespace == ""
	for _, rt := range resourceTypes {
		items, err := kubectl.RunJSON(rt, namespace, "", allNS)
		if err != nil {
			continue
		}
		for _, item := range items {
			meta := kubectl.GetMap(item, "metadata")
			name, _ := meta["name"].(string)
			ns, _ := meta["namespace"].(string)
			if name == "" {
				name = "unknown"
			}
			if ns == "" {
				ns = "default"
			}
			path := fmt.Sprintf("%s/%s/%s", rt, ns, name)
			allIssues = append(allIssues, analyzeDocument(item, path)...)
		}
	}
	return allIssues
}

func findYAMLFiles(root string, recursive bool) []string {
	var files []string
	if info, err := os.Stat(root); err != nil {
		return nil
	} else if !info.IsDir() {
		ext := filepath.Ext(root)
		if ext == ".yaml" || ext == ".yml" {
			return []string{root}
		}
		return nil
	}

	pattern := "*.yaml"
	if recursive {
		err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return nil
			}
			ext := filepath.Ext(path)
			if ext == ".yaml" || ext == ".yml" {
				files = append(files, path)
			}
			return nil
		})
		if err != nil {
			return nil
		}
	} else {
		matches, _ := filepath.Glob(filepath.Join(root, pattern))
		files = append(files, matches...)
		matchesYml, _ := filepath.Glob(filepath.Join(root, "*.yml"))
		files = append(files, matchesYml...)
	}
	return files
}

func printMigrationSummary(issues []migrationIssue) {
	warnings := 0
	info := 0
	for _, i := range issues {
		if i.Severity == "warning" {
			warnings++
		} else {
			info++
		}
	}

	sep := strings.Repeat("=", 60)
	fmt.Printf("\n%s\nMIGRATION READINESS SUMMARY\n%s\n", sep, sep)
	fmt.Printf("Total issues: %d\n", len(issues))
	fmt.Printf("  Warnings: %d\n", warnings)
	fmt.Printf("  Info: %d\n", info)

	if warnings > 0 {
		fmt.Println("\nRequired changes before v1beta2 migration:")
		seen := map[string]bool{}
		for _, i := range issues {
			if i.Severity == "warning" && !seen[i.Field] {
				fmt.Printf("  - %s\n", i.Field)
				seen[i.Field] = true
			}
		}
	}

	fmt.Println("\nDeadlines:")
	fmt.Println("  - v1beta1 deprecated: NOW")
	fmt.Println("  - v1beta1 removal: August 2026")
	fmt.Println("  - Contract compatibility removal: August 2026")
}

func main() {
	file := flag.String("f", "", "Single file to analyze")
	dir := flag.String("d", "", "Directory containing manifests")
	recursive := flag.Bool("r", false, "Search directories recursively")
	live := flag.Bool("live", false, "Analyze live cluster resources")
	namespace := flag.String("n", "", "Namespace for live analysis (default: all)")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s [flags]\n\nCheck v1beta1 to v1beta2 migration readiness.\n\nFlags:\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()

	var allIssues []migrationIssue

	if *file != "" {
		allIssues = append(allIssues, analyzeFile(*file)...)
	} else if *dir != "" {
		files := findYAMLFiles(*dir, *recursive)
		for _, f := range files {
			allIssues = append(allIssues, analyzeFile(f)...)
		}
	}

	if *live {
		fmt.Println("Analyzing live cluster resources...")
		allIssues = append(allIssues, analyzeLiveResources(*namespace)...)
	}

	if len(allIssues) == 0 && !*live && *file == "" && *dir == "" {
		flag.Usage()
		os.Exit(0)
	}

	// Group by path
	byPath := map[string][]migrationIssue{}
	var paths []string
	for _, issue := range allIssues {
		if _, ok := byPath[issue.Path]; !ok {
			paths = append(paths, issue.Path)
		}
		byPath[issue.Path] = append(byPath[issue.Path], issue)
	}

	for _, path := range paths {
		fmt.Printf("\n%s:\n", path)
		for _, issue := range byPath[path] {
			fmt.Printf("  %s\n", issue.String())
		}
	}

	printMigrationSummary(allIssues)

	warnings := 0
	for _, i := range allIssues {
		if i.Severity == "warning" {
			warnings++
		}
	}
	if warnings > 0 {
		os.Exit(1)
	}
	_ = json.Marshal // keep import for potential future use
}
