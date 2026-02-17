// validate-manifests validates CAPI YAML manifests against schema requirements.
//
// Usage:
//
//	go run ./validate-manifests [paths...] [flags]
//
// Examples:
//
//	go run ./validate-manifests manifest.yaml
//	go run ./validate-manifests -d ./manifests/ -r
package main

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"gopkg.in/yaml.v3"
)

type validationError struct {
	Field    string `json:"field"`
	Message  string `json:"message"`
	Severity string `json:"severity"`
}

func (e validationError) String() string {
	icon := "❌"
	if e.Severity == "warning" {
		icon = "⚠️"
	}
	return fmt.Sprintf("  %s [%s] %s: %s", icon, e.Severity, e.Field, e.Message)
}

var capiResources = map[string]string{
	"Cluster":               "cluster.x-k8s.io",
	"Machine":               "cluster.x-k8s.io",
	"MachineSet":            "cluster.x-k8s.io",
	"MachineDeployment":     "cluster.x-k8s.io",
	"MachinePool":           "cluster.x-k8s.io",
	"MachineHealthCheck":    "cluster.x-k8s.io",
	"ClusterClass":          "cluster.x-k8s.io",
	"ClusterResourceSet":    "addons.cluster.x-k8s.io",
	"KubeadmConfig":         "bootstrap.cluster.x-k8s.io",
	"KubeadmConfigTemplate": "bootstrap.cluster.x-k8s.io",
	"KubeadmControlPlane":   "controlplane.cluster.x-k8s.io",
	"KubeadmControlPlaneTemplate": "controlplane.cluster.x-k8s.io",
	"IPAddressClaim":        "ipam.cluster.x-k8s.io",
	"IPAddress":             "ipam.cluster.x-k8s.io",
	"ClusterResourceSetBinding": "addons.cluster.x-k8s.io",
	"MachinePoolMachine":    "cluster.x-k8s.io",
}

var requiredFields = map[string][]string{
	"Cluster":            {"clusterName:false", "infrastructureRef", "controlPlaneRef"},
	"Machine":            {"clusterName", "bootstrap"},
	"MachineDeployment":  {"clusterName", "template"},
	"MachineSet":         {"clusterName", "template"},
	"ClusterClass":       {"infrastructure", "controlPlane"},
	"MachineHealthCheck": {"clusterName", "selector", "unhealthyConditions"},
	"MachinePool":        {"clusterName", "template"},
}

func validateAPIVersion(doc map[string]interface{}) []validationError {
	var errs []validationError
	av, _ := doc["apiVersion"].(string)
	kind, _ := doc["kind"].(string)

	if av == "" {
		return errs
	}

	if group, ok := capiResources[kind]; ok {
		if !strings.HasPrefix(av, group) {
			errs = append(errs, validationError{"apiVersion", fmt.Sprintf("Expected group '%s', got '%s'", group, av), "warning"})
		}
	}

	if strings.Contains(av, "v1alpha") {
		errs = append(errs, validationError{"apiVersion", fmt.Sprintf("v1alpha API versions are deprecated: %s", av), "warning"})
	}
	return errs
}

func validateMetadata(doc map[string]interface{}) []validationError {
	var errs []validationError
	metadata, ok := doc["metadata"].(map[string]interface{})
	if !ok || metadata == nil {
		errs = append(errs, validationError{"metadata", "Missing metadata field", "error"})
		return errs
	}

	if name, _ := metadata["name"].(string); name == "" {
		errs = append(errs, validationError{"metadata.name", "Missing name field", "error"})
	}

	kind, _ := doc["kind"].(string)
	labels, _ := metadata["labels"].(map[string]interface{})

	machineKinds := map[string]bool{"Machine": true, "MachineSet": true, "MachineDeployment": true, "MachinePool": true}
	if machineKinds[kind] {
		if labels == nil || labels["cluster.x-k8s.io/cluster-name"] == nil {
			spec, _ := doc["spec"].(map[string]interface{})
			clusterName, _ := spec["clusterName"].(string)
			if clusterName == "" {
				errs = append(errs, validationError{"metadata.labels", "Missing cluster.x-k8s.io/cluster-name label", "warning"})
			}
		}
	}
	return errs
}

func validateSpec(doc map[string]interface{}) []validationError {
	var errs []validationError
	kind, _ := doc["kind"].(string)
	spec, _ := doc["spec"].(map[string]interface{})

	if spec == nil {
		errs = append(errs, validationError{"spec", "Missing spec field", "error"})
		return errs
	}

	if fields, ok := requiredFields[kind]; ok {
		for _, field := range fields {
			// topology-based clusters don't need some fields
			if kind == "Cluster" {
				if _, hasTopo := spec["topology"]; hasTopo {
					if field == "infrastructureRef" || field == "controlPlaneRef" {
						continue
					}
				}
			}
			if _, ok := spec[field]; !ok {
				errs = append(errs, validationError{
					"spec." + field,
					fmt.Sprintf("Missing required field: %s", field),
					"error",
				})
			}
		}
	}

	// Kind-specific validations
	switch kind {
	case "Cluster":
		errs = append(errs, validateClusterSpec(spec)...)
	case "Machine":
		errs = append(errs, validateMachineSpec(spec)...)
	case "MachineDeployment":
		errs = append(errs, validateMDSpec(spec)...)
	case "ClusterClass":
		errs = append(errs, validateCCSpec(spec)...)
	}
	return errs
}

func validateClusterSpec(spec map[string]interface{}) []validationError {
	var errs []validationError
	if ref, ok := spec["infrastructureRef"].(map[string]interface{}); ok {
		if _, ok := ref["kind"].(string); !ok {
			errs = append(errs, validationError{"spec.infrastructureRef.kind", "Missing kind in infrastructureRef", "error"})
		}
		if _, ok := ref["name"].(string); !ok {
			errs = append(errs, validationError{"spec.infrastructureRef.name", "Missing name in infrastructureRef", "error"})
		}
	}
	if ref, ok := spec["controlPlaneRef"].(map[string]interface{}); ok {
		if _, ok := ref["kind"].(string); !ok {
			errs = append(errs, validationError{"spec.controlPlaneRef.kind", "Missing kind in controlPlaneRef", "error"})
		}
	}
	return errs
}

func validateMachineSpec(spec map[string]interface{}) []validationError {
	var errs []validationError
	if bootstrap, ok := spec["bootstrap"].(map[string]interface{}); ok {
		if bootstrap["configRef"] == nil && bootstrap["dataSecretName"] == nil {
			errs = append(errs, validationError{"spec.bootstrap", "Must have either configRef or dataSecretName", "error"})
		}
	}
	return errs
}

func validateMDSpec(spec map[string]interface{}) []validationError {
	var errs []validationError
	if tmpl, ok := spec["template"].(map[string]interface{}); ok {
		tmplSpec, _ := tmpl["spec"].(map[string]interface{})
		if tmplSpec != nil {
			if tmplSpec["bootstrap"] == nil {
				errs = append(errs, validationError{"spec.template.spec.bootstrap", "Missing bootstrap in template", "error"})
			}
			if tmplSpec["infrastructureRef"] == nil {
				errs = append(errs, validationError{"spec.template.spec.infrastructureRef", "Missing infrastructureRef in template", "error"})
			}
		}
	}
	return errs
}

func validateCCSpec(spec map[string]interface{}) []validationError {
	var errs []validationError
	if infra, ok := spec["infrastructure"].(map[string]interface{}); ok {
		if infra["ref"] == nil {
			errs = append(errs, validationError{"spec.infrastructure.ref", "Missing ref in infrastructure", "error"})
		}
	}
	if cp, ok := spec["controlPlane"].(map[string]interface{}); ok {
		if cp["ref"] == nil {
			errs = append(errs, validationError{"spec.controlPlane.ref", "Missing ref in controlPlane", "error"})
		}
	}
	return errs
}

func validateDocument(doc map[string]interface{}, filePath string) []validationError {
	var errs []validationError

	kind, _ := doc["kind"].(string)
	if kind == "" {
		errs = append(errs, validationError{"kind", "Missing kind field", "error"})
	}

	errs = append(errs, validateAPIVersion(doc)...)
	errs = append(errs, validateMetadata(doc)...)
	errs = append(errs, validateSpec(doc)...)
	return errs
}

func validateFile(filePath string) (int, int, []validationError) {
	var allErrs []validationError
	docCount := 0

	data, err := os.ReadFile(filePath)
	if err != nil {
		return 0, 1, []validationError{{filePath, fmt.Sprintf("File read error: %v", err), "error"}}
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
		docCount++
		allErrs = append(allErrs, validateDocument(doc, filePath)...)
	}

	errorCount := 0
	for _, e := range allErrs {
		if e.Severity == "error" {
			errorCount++
		}
	}
	return docCount, errorCount, allErrs
}

func findYAMLFiles(root string, recursive bool) []string {
	var files []string
	info, err := os.Stat(root)
	if err != nil {
		return nil
	}
	if !info.IsDir() {
		ext := filepath.Ext(root)
		if ext == ".yaml" || ext == ".yml" {
			return []string{root}
		}
		return nil
	}

	if recursive {
		_ = filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return nil
			}
			ext := filepath.Ext(path)
			if ext == ".yaml" || ext == ".yml" {
				files = append(files, path)
			}
			return nil
		})
	} else {
		for _, ext := range []string{"*.yaml", "*.yml"} {
			matches, _ := filepath.Glob(filepath.Join(root, ext))
			files = append(files, matches...)
		}
	}
	return files
}

func main() {
	dir := flag.String("d", "", "Directory containing manifests")
	recursive := flag.Bool("r", false, "Search directories recursively")
	strict := flag.Bool("s", false, "Treat warnings as errors")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s [paths...] [flags]\n\nValidate Cluster API YAML manifests.\n\nFlags:\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()

	var paths []string
	if *dir != "" {
		paths = []string{*dir}
	} else if flag.NArg() > 0 {
		paths = flag.Args()
	} else {
		paths = []string{"."}
	}

	var allFiles []string
	for _, p := range paths {
		allFiles = append(allFiles, findYAMLFiles(p, *recursive)...)
	}

	if len(allFiles) == 0 {
		fmt.Fprintln(os.Stderr, "No YAML files found")
		os.Exit(1)
	}

	totalDocs, totalErrors, totalWarnings := 0, 0, 0

	for _, f := range allFiles {
		docs, errCount, errs := validateFile(f)
		totalDocs += docs
		totalErrors += errCount
		for _, e := range errs {
			if e.Severity == "warning" {
				totalWarnings++
			}
		}

		if len(errs) > 0 {
			fmt.Printf("\n%s:\n", f)
			for _, e := range errs {
				fmt.Println(e.String())
			}
		}
	}

	sep := strings.Repeat("=", 50)
	fmt.Printf("\n%s\n", sep)
	fmt.Printf("Files scanned: %d\n", len(allFiles))
	fmt.Printf("Documents validated: %d\n", totalDocs)
	fmt.Printf("Errors: %d\n", totalErrors)
	fmt.Printf("Warnings: %d\n", totalWarnings)

	if totalErrors > 0 {
		os.Exit(1)
	}
	if *strict && totalWarnings > 0 {
		os.Exit(1)
	}
}
