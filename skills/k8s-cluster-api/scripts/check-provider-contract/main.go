// check-provider-contract verifies provider CRD compliance with CAPI contracts.
//
// Usage:
//
//	go run ./check-provider-contract [flags]
//
// Examples:
//
//	go run ./check-provider-contract -p aws
//	go run ./check-provider-contract -t infrastructure --format json
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strings"

	"k8s-cluster-api-tools/internal/kubectl"
)

type contractSpec struct {
	RequiredSpec    []string
	RequiredStatus  []string
	OptionalSpec    []string
	OptionalStatus  []string
	Behaviors       []string
}

var infraClusterContract = contractSpec{
	RequiredSpec:   []string{"controlPlaneEndpoint"},
	RequiredStatus: []string{"ready", "failureReason", "failureMessage"},
	Behaviors: []string{
		"Must set OwnerReference to Cluster",
		"Must set status.ready=true when infrastructure is ready",
		"Must populate spec.controlPlaneEndpoint when available",
		"Must report failureReason/failureMessage on terminal errors",
	},
}

var infraMachineContract = contractSpec{
	RequiredSpec:   []string{"providerID"},
	RequiredStatus: []string{"ready", "addresses"},
	Behaviors: []string{
		"Must set spec.providerID for node correlation",
		"Must set status.ready=true when machine is provisioned",
		"Must report status.addresses for node registration",
	},
}

var bootstrapConfigContract = contractSpec{
	RequiredStatus: []string{"ready", "dataSecretName"},
	Behaviors: []string{
		"Must set status.ready=true when bootstrap data is generated",
		"Must populate status.dataSecretName pointing to Secret",
	},
}

var controlPlaneContract = contractSpec{
	RequiredSpec:   []string{"replicas", "version", "machineTemplate"},
	RequiredStatus: []string{"ready", "initialized", "replicas", "updatedReplicas", "readyReplicas", "conditions"},
	Behaviors: []string{
		"Must set OwnerReference to Cluster",
		"Must manage control plane Machines",
		"Must report initialized=true after first control plane node",
		"Must populate kubeconfig Secret",
		"Must support rolling updates",
	},
}

type violation struct {
	Severity    string `json:"severity"`
	Category    string `json:"category"`
	CRD         string `json:"crd"`
	Message     string `json:"message"`
	Requirement string `json:"requirement,omitempty"`
}

type contractReport struct {
	Provider     string      `json:"provider"`
	ProviderType string      `json:"type"`
	Violations   []violation `json:"violations"`
	CheckedCRDs  []string    `json:"crds"`
}

func (r *contractReport) addViolation(sev, cat, crd, msg, req string) {
	r.Violations = append(r.Violations, violation{sev, cat, crd, msg, req})
}

func (r *contractReport) errorCount() int {
	n := 0
	for _, v := range r.Violations {
		if v.Severity == "error" {
			n++
		}
	}
	return n
}

func (r *contractReport) isCompliant() bool {
	return r.errorCount() == 0
}

func getCRDs(apiGroup string) []map[string]interface{} {
	ok, stdout, _ := kubectl.Run([]string{"get", "crds", "-o", "json"}, 0)
	if !ok {
		return nil
	}
	var data map[string]interface{}
	if err := json.Unmarshal([]byte(stdout), &data); err != nil {
		return nil
	}
	items, _ := data["items"].([]interface{})
	var result []map[string]interface{}
	for _, item := range items {
		crd, ok := item.(map[string]interface{})
		if !ok {
			continue
		}
		spec := kubectl.GetMap(crd, "spec")
		group, _ := spec["group"].(string)
		if strings.HasSuffix(group, apiGroup) {
			result = append(result, crd)
		}
	}
	return result
}

func getCRDSchema(crd map[string]interface{}) map[string]interface{} {
	spec := kubectl.GetMap(crd, "spec")
	versions := kubectl.GetSlice(spec, "versions")
	for _, v := range versions {
		vm, ok := v.(map[string]interface{})
		if !ok {
			continue
		}
		if served, _ := vm["served"].(bool); served {
			schema := kubectl.GetMap(vm, "schema")
			return kubectl.GetMap(schema, "openAPIV3Schema")
		}
	}
	return nil
}

func checkSchemaFields(schema map[string]interface{}, required []string, path string) []string {
	current := schema
	if path != "" {
		for _, part := range strings.Split(path, ".") {
			if part == "" {
				continue
			}
			props := kubectl.GetMap(current, "properties")
			next, ok := props[part].(map[string]interface{})
			if !ok {
				return required // path not found
			}
			current = next
		}
	}

	props := kubectl.GetMap(current, "properties")
	var missing []string
	for _, field := range required {
		parts := strings.SplitN(field, ".", 2)
		if _, ok := props[parts[0]]; !ok {
			missing = append(missing, field)
		}
	}
	return missing
}

func checkInfraCluster(crd map[string]interface{}, report *contractReport) {
	crdName, _ := kubectl.GetMap(crd, "metadata")["name"].(string)
	schema := getCRDSchema(crd)
	if schema == nil {
		report.addViolation("error", "Schema", crdName, "No OpenAPI schema found in CRD", "")
		return
	}

	missing := checkSchemaFields(schema, infraClusterContract.RequiredSpec, "spec")
	for _, f := range missing {
		report.addViolation("error", "Spec", crdName, "Missing required spec field: "+f, "Contract requires spec."+f)
	}

	missing = checkSchemaFields(schema, infraClusterContract.RequiredStatus, "status")
	for _, f := range missing {
		report.addViolation("error", "Status", crdName, "Missing required status field: "+f, "Contract requires status."+f)
	}

	statusProps := kubectl.GetMap(kubectl.GetMap(kubectl.GetMap(schema, "properties"), "status"), "properties")
	if _, ok := statusProps["conditions"]; !ok {
		report.addViolation("warning", "Conditions", crdName, "No conditions field in status", "Conditions recommended for observability")
	}
}

func checkInfraMachine(crd map[string]interface{}, report *contractReport) {
	crdName, _ := kubectl.GetMap(crd, "metadata")["name"].(string)
	schema := getCRDSchema(crd)
	if schema == nil {
		report.addViolation("error", "Schema", crdName, "No OpenAPI schema found in CRD", "")
		return
	}

	specProps := kubectl.GetMap(kubectl.GetMap(kubectl.GetMap(schema, "properties"), "spec"), "properties")
	if _, ok := specProps["providerID"]; !ok {
		report.addViolation("error", "Spec", crdName, "Missing providerID field in spec", "Contract requires spec.providerID for node correlation")
	}

	statusProps := kubectl.GetMap(kubectl.GetMap(kubectl.GetMap(schema, "properties"), "status"), "properties")
	if _, ok := statusProps["ready"]; !ok {
		report.addViolation("error", "Status", crdName, "Missing ready field in status", "")
	}
	if _, ok := statusProps["addresses"]; !ok {
		report.addViolation("error", "Status", crdName, "Missing addresses field in status", "Contract requires status.addresses for node registration")
	}
}

func checkBootstrap(crd map[string]interface{}, report *contractReport) {
	crdName, _ := kubectl.GetMap(crd, "metadata")["name"].(string)
	schema := getCRDSchema(crd)
	if schema == nil {
		report.addViolation("error", "Schema", crdName, "No OpenAPI schema found in CRD", "")
		return
	}

	statusProps := kubectl.GetMap(kubectl.GetMap(kubectl.GetMap(schema, "properties"), "status"), "properties")
	if _, ok := statusProps["ready"]; !ok {
		report.addViolation("error", "Status", crdName, "Missing ready field in status", "")
	}
	if _, ok := statusProps["dataSecretName"]; !ok {
		report.addViolation("error", "Status", crdName, "Missing dataSecretName field in status", "Contract requires status.dataSecretName pointing to bootstrap data Secret")
	}
}

func checkControlPlane(crd map[string]interface{}, report *contractReport) {
	crdName, _ := kubectl.GetMap(crd, "metadata")["name"].(string)
	schema := getCRDSchema(crd)
	if schema == nil {
		report.addViolation("error", "Schema", crdName, "No OpenAPI schema found in CRD", "")
		return
	}

	specProps := kubectl.GetMap(kubectl.GetMap(kubectl.GetMap(schema, "properties"), "spec"), "properties")
	for _, f := range controlPlaneContract.RequiredSpec {
		if _, ok := specProps[f]; !ok {
			report.addViolation("error", "Spec", crdName, "Missing required spec field: "+f, "")
		}
	}

	statusProps := kubectl.GetMap(kubectl.GetMap(kubectl.GetMap(schema, "properties"), "status"), "properties")
	for _, f := range controlPlaneContract.RequiredStatus {
		if _, ok := statusProps[f]; !ok {
			report.addViolation("error", "Status", crdName, "Missing required status field: "+f, "")
		}
	}
}

func detectProviderType(crdName string) string {
	lower := strings.ToLower(crdName)
	switch {
	case strings.Contains(lower, "cluster") && strings.Contains(lower, "infrastructure"):
		return "infrastructure-cluster"
	case strings.Contains(lower, "machine") && strings.Contains(lower, "infrastructure"):
		return "infrastructure-machine"
	case strings.Contains(lower, "bootstrap"):
		return "bootstrap"
	case strings.Contains(lower, "controlplane"):
		return "controlplane"
	}
	return "unknown"
}

func runComplianceCheck(providerFilter, typeFilter string) []contractReport {
	var reports []contractReport

	apiGroups := []string{
		"infrastructure.cluster.x-k8s.io",
		"bootstrap.cluster.x-k8s.io",
		"controlplane.cluster.x-k8s.io",
	}

	for _, group := range apiGroups {
		crds := getCRDs(group)
		for _, crd := range crds {
			crdName, _ := kubectl.GetMap(crd, "metadata")["name"].(string)
			spec := kubectl.GetMap(crd, "spec")
			names := kubectl.GetMap(spec, "names")
			kind, _ := names["kind"].(string)

			providerName := strings.ToLower(kind)
			for _, s := range []string{"cluster", "machine", "config", "controlplane"} {
				providerName = strings.ReplaceAll(providerName, s, "")
			}
			if providerFilter != "" && !strings.Contains(providerName, strings.ToLower(providerFilter)) {
				continue
			}

			crdType := detectProviderType(crdName)
			if typeFilter != "" && !strings.Contains(crdType, typeFilter) {
				continue
			}

			report := contractReport{
				Provider:     providerName,
				ProviderType: crdType,
				CheckedCRDs:  []string{crdName},
			}

			switch crdType {
			case "infrastructure-cluster":
				checkInfraCluster(crd, &report)
			case "infrastructure-machine":
				checkInfraMachine(crd, &report)
			case "bootstrap":
				checkBootstrap(crd, &report)
			case "controlplane":
				checkControlPlane(crd, &report)
			}

			if len(report.CheckedCRDs) > 0 {
				reports = append(reports, report)
			}
		}
	}
	return reports
}

func printContractReport(r contractReport) {
	status := "✓ COMPLIANT"
	if !r.isCompliant() {
		status = "✗ NON-COMPLIANT"
	}
	sep := strings.Repeat("=", 60)
	fmt.Printf("\n%s\nProvider: %s (%s)\nStatus: %s\n%s\n", sep, r.Provider, r.ProviderType, status, sep)

	fmt.Println("\nChecked CRDs:")
	for _, crd := range r.CheckedCRDs {
		fmt.Printf("  - %s\n", crd)
	}

	if len(r.Violations) == 0 {
		fmt.Println("\n✓ All contract requirements satisfied")
		return
	}

	icons := map[string]string{"error": "🔴", "warning": "⚠️", "info": "ℹ️"}
	for _, sev := range []string{"error", "warning", "info"} {
		var filtered []violation
		for _, v := range r.Violations {
			if v.Severity == sev {
				filtered = append(filtered, v)
			}
		}
		if len(filtered) == 0 {
			continue
		}
		fmt.Printf("\n%s %s (%d)\n", icons[sev], strings.ToUpper(sev), len(filtered))
		for _, v := range filtered {
			fmt.Printf("\n  [%s] %s\n", v.Category, v.Message)
			if v.Requirement != "" {
				fmt.Printf("    Requirement: %s\n", v.Requirement)
			}
		}
	}
}

func printContractSummary(reports []contractReport) {
	total := len(reports)
	compliant := 0
	for _, r := range reports {
		if r.isCompliant() {
			compliant++
		}
	}

	sep := strings.Repeat("=", 60)
	fmt.Printf("\n%s\nSUMMARY\n%s\n", sep, sep)
	fmt.Printf("Total providers checked: %d\n", total)
	fmt.Printf("Compliant: %d\n", compliant)
	fmt.Printf("Non-compliant: %d\n", total-compliant)

	if total-compliant > 0 {
		fmt.Println("\nNon-compliant providers:")
		for _, r := range reports {
			if !r.isCompliant() {
				fmt.Printf("  - %s (%s): %d errors\n", r.Provider, r.ProviderType, r.errorCount())
			}
		}
	}
}

func main() {
	provider := flag.String("p", "", "Filter by provider name (e.g., aws, azure)")
	providerType := flag.String("t", "", "Filter by provider type: infrastructure, bootstrap, controlplane")
	format := flag.String("format", "text", "Output format: text, json")
	output := flag.String("o", "", "Write output to file")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s [flags]\n\nVerify provider CRD compliance with CAPI contracts.\n\nFlags:\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()

	if kubectl.Find() == "" {
		fmt.Fprintln(os.Stderr, "Error: kubectl not found in PATH")
		os.Exit(1)
	}

	fmt.Println("Checking provider contract compliance...")
	reports := runComplianceCheck(*provider, *providerType)

	if len(reports) == 0 {
		fmt.Println("No provider CRDs found to check")
		os.Exit(0)
	}

	if *format == "json" || *output != "" {
		type jsonReport struct {
			Provider   string      `json:"provider"`
			Type       string      `json:"type"`
			Compliant  bool        `json:"compliant"`
			CRDs       []string    `json:"crds"`
			Violations []violation `json:"violations"`
		}
		var out []jsonReport
		for _, r := range reports {
			jr := jsonReport{r.Provider, r.ProviderType, r.isCompliant(), r.CheckedCRDs, r.Violations}
			if jr.Violations == nil {
				jr.Violations = []violation{}
			}
			out = append(out, jr)
		}
		data, _ := json.MarshalIndent(out, "", "  ")
		if *output != "" {
			if err := os.WriteFile(*output, data, 0o644); err != nil {
				fmt.Fprintf(os.Stderr, "Error: %v\n", err)
				os.Exit(1)
			}
			fmt.Printf("Report written to: %s\n", *output)
		} else {
			fmt.Println(string(data))
		}
	} else {
		for _, r := range reports {
			printContractReport(r)
		}
		printContractSummary(reports)
	}

	for _, r := range reports {
		if !r.isCompliant() {
			os.Exit(1)
		}
	}
}
