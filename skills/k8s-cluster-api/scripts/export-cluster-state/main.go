// export-cluster-state exports Cluster API resources for backup/migration.
//
// Usage:
//
//	go run ./export-cluster-state [flags]
//
// Examples:
//
//	go run ./export-cluster-state -n my-cluster
//	go run ./export-cluster-state -n my-cluster -o ./backup/ --include-secrets
//	go run ./export-cluster-state --all-clusters -o ./backup/
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	kubectl "k8s-cluster-api-tools/internal/kubectl"

	"gopkg.in/yaml.v3"
)

var capiResourceTypes = []string{
	"clusters.cluster.x-k8s.io",
	"machines.cluster.x-k8s.io",
	"machinesets.cluster.x-k8s.io",
	"machinedeployments.cluster.x-k8s.io",
	"machinepools.cluster.x-k8s.io",
	"machinehealthchecks.cluster.x-k8s.io",
	"clusterclasses.cluster.x-k8s.io",
	"clusterresourcesets.addons.cluster.x-k8s.io",
	"clusterresourcesetbindings.addons.cluster.x-k8s.io",
	"kubeadmconfigs.bootstrap.cluster.x-k8s.io",
	"kubeadmconfigtemplates.bootstrap.cluster.x-k8s.io",
	"kubeadmcontrolplanes.controlplane.cluster.x-k8s.io",
	"kubeadmcontrolplanetemplates.controlplane.cluster.x-k8s.io",
	"ipaddressclaims.ipam.cluster.x-k8s.io",
}

var managedFieldAnnotations = []string{
	"kubectl.kubernetes.io/last-applied-configuration",
}

func cleanResource(resource map[string]interface{}) map[string]interface{} {
	cleaned := deepCopy(resource)

	// Remove server-generated metadata
	if metadata, ok := cleaned["metadata"].(map[string]interface{}); ok {
		delete(metadata, "uid")
		delete(metadata, "resourceVersion")
		delete(metadata, "generation")
		delete(metadata, "creationTimestamp")
		delete(metadata, "managedFields")
		delete(metadata, "selfLink")

		// Clean annotations
		if annotations, ok := metadata["annotations"].(map[string]interface{}); ok {
			for _, key := range managedFieldAnnotations {
				delete(annotations, key)
			}
			if len(annotations) == 0 {
				delete(metadata, "annotations")
			}
		}

		// Remove ownerReferences (they will be re-created)
		delete(metadata, "ownerReferences")
	}

	// Remove status section
	delete(cleaned, "status")
	return cleaned
}

func deepCopy(in map[string]interface{}) map[string]interface{} {
	data, _ := json.Marshal(in)
	var out map[string]interface{}
	_ = json.Unmarshal(data, &out)
	return out
}

func getResources(resourceType, namespace, kubeconfig, clusterFilter string) []map[string]interface{} {
	args := []string{"get", resourceType, "-o", "json"}
	if namespace != "" {
		args = append(args, "-n", namespace)
	} else {
		args = append(args, "--all-namespaces")
	}
	if kubeconfig != "" {
		args = append(args, "--kubeconfig", kubeconfig)
	}

	items, err := kubectl.RunJSON(args...)
	if err != nil {
		return nil
	}

	if clusterFilter == "" {
		return items
	}

	var filtered []map[string]interface{}
	for _, item := range items {
		labels := kubectl.GetMap(item, "metadata", "labels")
		clusterName, _ := labels["cluster.x-k8s.io/cluster-name"].(string)

		// Also check spec.clusterName for core resources
		specCluster := kubectl.GetString(item, "spec", "clusterName")

		// Check metadata.name for Cluster resources
		name := kubectl.GetString(item, "metadata", "name")
		kind := kubectl.GetString(item, "kind")

		if clusterName == clusterFilter || specCluster == clusterFilter ||
			(kind == "Cluster" && name == clusterFilter) {
			filtered = append(filtered, item)
		}
	}
	return filtered
}

func discoverProviderTypes(namespace, kubeconfig string) []string {
	args := []string{"api-resources", "--api-group=infrastructure.cluster.x-k8s.io", "-o", "name"}
	if kubeconfig != "" {
		args = append(args, "--kubeconfig", kubeconfig)
	}
	out, err := kubectl.Run(args...)
	if err != nil {
		return nil
	}

	var types []string
	for _, line := range strings.Split(strings.TrimSpace(out), "\n") {
		line = strings.TrimSpace(line)
		if line != "" {
			types = append(types, line)
		}
	}
	return types
}

func exportSecrets(namespace, kubeconfig, clusterName string, includeSecrets bool) []map[string]interface{} {
	args := []string{"get", "secrets", "-o", "json"}
	if namespace != "" {
		args = append(args, "-n", namespace)
	} else {
		args = append(args, "--all-namespaces")
	}
	if kubeconfig != "" {
		args = append(args, "--kubeconfig", kubeconfig)
	}

	items, err := kubectl.RunJSON(args...)
	if err != nil {
		return nil
	}

	var secrets []map[string]interface{}
	for _, item := range items {
		labels := kubectl.GetMap(item, "metadata", "labels")
		clusterLabel, _ := labels["cluster.x-k8s.io/cluster-name"].(string)

		ownerRefs := kubectl.GetSlice(item, "metadata", "ownerReferences")
		isCapiOwned := false
		for _, ref := range ownerRefs {
			if refMap, ok := ref.(map[string]interface{}); ok {
				av, _ := refMap["apiVersion"].(string)
				if strings.Contains(av, "cluster.x-k8s.io") {
					isCapiOwned = true
					break
				}
			}
		}

		if clusterLabel == clusterName || isCapiOwned {
			cleaned := cleanResource(item)

			if !includeSecrets {
				if data, ok := cleaned["data"].(map[string]interface{}); ok {
					for k := range data {
						data[k] = "REDACTED"
					}
				}
			}
			secrets = append(secrets, cleaned)
		}
	}
	return secrets
}

func exportReferencedResources(items []map[string]interface{}, namespace, kubeconfig string) []map[string]interface{} {
	var referenced []map[string]interface{}
	seen := map[string]bool{}

	for _, item := range items {
		spec, _ := item["spec"].(map[string]interface{})
		if spec == nil {
			continue
		}

		refs := []map[string]interface{}{}
		for _, refKey := range []string{"infrastructureRef", "controlPlaneRef"} {
			if ref, ok := spec[refKey].(map[string]interface{}); ok {
				refs = append(refs, ref)
			}
		}
		if bootstrap, ok := spec["bootstrap"].(map[string]interface{}); ok {
			if ref, ok := bootstrap["configRef"].(map[string]interface{}); ok {
				refs = append(refs, ref)
			}
		}

		for _, ref := range refs {
			kind, _ := ref["kind"].(string)
			name, _ := ref["name"].(string)
			ns, _ := ref["namespace"].(string)
			if ns == "" {
				ns = namespace
			}
			key := fmt.Sprintf("%s/%s/%s", kind, ns, name)
			if seen[key] || kind == "" || name == "" {
				continue
			}
			seen[key] = true

			// Try to get the referenced resource
			lowerKind := strings.ToLower(kind) + "s"
			av, _ := ref["apiVersion"].(string)
			if av == "" {
				if apiGroup, ok := ref["apiGroup"].(string); ok && apiGroup != "" {
					av = apiGroup
				}
			}

			// Try fetching via api group if available
			resourceName := lowerKind
			if av != "" {
				parts := strings.Split(av, "/")
				if len(parts) > 0 {
					resourceName = lowerKind + "." + parts[0]
				}
			}

			getArgs := []string{"get", resourceName, name, "-o", "json"}
			if ns != "" {
				getArgs = append(getArgs, "-n", ns)
			}
			if kubeconfig != "" {
				getArgs = append(getArgs, "--kubeconfig", kubeconfig)
			}
			out, err := kubectl.Run(getArgs...)
			if err != nil {
				continue
			}
			var obj map[string]interface{}
			if err := json.Unmarshal([]byte(out), &obj); err == nil {
				referenced = append(referenced, cleanResource(obj))
			}
		}
	}
	return referenced
}

func writeManifest(resources []map[string]interface{}, filePath string) error {
	dir := filepath.Dir(filePath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return err
	}

	var docs []string
	for _, r := range resources {
		data, err := yaml.Marshal(r)
		if err != nil {
			continue
		}
		docs = append(docs, string(data))
	}

	content := strings.Join(docs, "---\n")
	return os.WriteFile(filePath, []byte(content), 0644)
}

func main() {
	clusterName := flag.String("n", "", "Cluster name to export (required unless --all)")
	namespace := flag.String("ns", "", "Namespace to search")
	kubeconfig := flag.String("kubeconfig", "", "Path to kubeconfig")
	outputDir := flag.String("o", "", "Output directory (default: cluster-state-<timestamp>)")
	allClusters := flag.Bool("all", false, "Export all clusters")
	includeSecrets := flag.Bool("include-secrets", false, "Include secret data (default: redacted)")
	includeRefs := flag.Bool("include-refs", true, "Include referenced infra/bootstrap objects")
	singleFile := flag.Bool("single-file", false, "Write everything to one file")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "CAPI Cluster State Exporter\nUsage: %s [flags]\n\nFlags:\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()

	if *clusterName == "" && !*allClusters {
		fmt.Fprintln(os.Stderr, "Error: -n (cluster name) or --all required")
		flag.Usage()
		os.Exit(1)
	}

	clusterFilter := *clusterName
	if *allClusters {
		clusterFilter = ""
	}

	if *outputDir == "" {
		*outputDir = fmt.Sprintf("cluster-state-%s", time.Now().Format("20060102-150405"))
	}

	fmt.Println("=== CAPI Cluster State Export ===")
	if *allClusters {
		fmt.Println("Mode: all clusters")
	} else {
		fmt.Printf("Cluster: %s\n", *clusterName)
	}

	var allResources []map[string]interface{}

	// Export CAPI resources
	for _, rt := range capiResourceTypes {
		items := getResources(rt, *namespace, *kubeconfig, clusterFilter)
		if len(items) == 0 {
			continue
		}
		fmt.Printf("  Found %d %s\n", len(items), rt)
		for _, item := range items {
			allResources = append(allResources, cleanResource(item))
		}
	}

	// Export provider resources
	providerTypes := discoverProviderTypes(*namespace, *kubeconfig)
	for _, pt := range providerTypes {
		items := getResources(pt, *namespace, *kubeconfig, clusterFilter)
		if len(items) == 0 {
			continue
		}
		fmt.Printf("  Found %d %s (provider)\n", len(items), pt)
		for _, item := range items {
			allResources = append(allResources, cleanResource(item))
		}
	}

	// Export referenced resources
	if *includeRefs {
		refs := exportReferencedResources(allResources, *namespace, *kubeconfig)
		if len(refs) > 0 {
			fmt.Printf("  Found %d referenced resources\n", len(refs))
			allResources = append(allResources, refs...)
		}
	}

	// Export secrets
	cn := clusterFilter
	if cn == "" {
		cn = ""
	}
	secrets := exportSecrets(*namespace, *kubeconfig, cn, *includeSecrets)
	if len(secrets) > 0 {
		fmt.Printf("  Found %d CAPI secrets\n", len(secrets))
		allResources = append(allResources, secrets...)
	}

	if len(allResources) == 0 {
		fmt.Println("\nNo resources found to export.")
		os.Exit(0)
	}

	// Write output
	if *singleFile {
		outFile := filepath.Join(*outputDir, "cluster-state.yaml")
		if err := writeManifest(allResources, outFile); err != nil {
			fmt.Fprintf(os.Stderr, "Error writing file: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("\nExported %d resources to %s\n", len(allResources), outFile)
	} else {
		// Group by kind
		groups := map[string][]map[string]interface{}{}
		for _, r := range allResources {
			kind, _ := r["kind"].(string)
			if kind == "" {
				kind = "unknown"
			}
			groups[kind] = append(groups[kind], r)
		}

		for kind, items := range groups {
			fileName := strings.ToLower(kind) + "s.yaml"
			outFile := filepath.Join(*outputDir, fileName)
			if err := writeManifest(items, outFile); err != nil {
				fmt.Fprintf(os.Stderr, "Error writing %s: %v\n", outFile, err)
				continue
			}
			fmt.Printf("  Wrote %d %s → %s\n", len(items), kind, outFile)
		}
		fmt.Printf("\nExported %d resources to %s/\n", len(allResources), *outputDir)
	}
}
