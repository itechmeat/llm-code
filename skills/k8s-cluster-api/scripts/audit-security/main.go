// audit-security audits the security posture of CAPI clusters.
//
// Usage:
//
//	go run ./audit-security [flags]
//
// Examples:
//
//	go run ./audit-security -c my-cluster -n default
//	go run ./audit-security -A --format json -o report.json
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strings"

	"k8s-cluster-api-tools/internal/kubectl"
)

type finding struct {
	Severity       string `json:"severity"`
	Category       string `json:"category"`
	Resource       string `json:"resource"`
	Message        string `json:"message"`
	Recommendation string `json:"recommendation"`
}

type auditReport struct {
	ClusterName string    `json:"cluster"`
	Findings    []finding `json:"findings"`
}

func (r *auditReport) add(sev, cat, res, msg, rec string) {
	r.Findings = append(r.Findings, finding{sev, cat, res, msg, rec})
}

func (r *auditReport) highCount() int {
	n := 0
	for _, f := range r.Findings {
		if f.Severity == "high" {
			n++
		}
	}
	return n
}

func (r *auditReport) mediumCount() int {
	n := 0
	for _, f := range r.Findings {
		if f.Severity == "medium" {
			n++
		}
	}
	return n
}

func (r *auditReport) lowCount() int {
	n := 0
	for _, f := range r.Findings {
		if f.Severity == "low" {
			n++
		}
	}
	return n
}

func resName(item map[string]interface{}, kind string) string {
	meta := kubectl.GetMap(item, "metadata")
	name, _ := meta["name"].(string)
	if name == "" {
		name = "unknown"
	}
	ns, _ := meta["namespace"].(string)
	if ns == "" {
		ns = "default"
	}
	return fmt.Sprintf("%s/%s/%s", kind, ns, name)
}

func checkPSS(cluster map[string]interface{}, report *auditReport) {
	res := resName(cluster, "Cluster")
	spec := kubectl.GetMap(cluster, "spec")
	topo := kubectl.GetMap(spec, "topology")
	vars := kubectl.GetSlice(topo, "variables")

	var pssVar map[string]interface{}
	for _, v := range vars {
		vm, ok := v.(map[string]interface{})
		if !ok {
			continue
		}
		if name, _ := vm["name"].(string); name == "podSecurityStandard" {
			pssVar, _ = vm["value"].(map[string]interface{})
			break
		}
	}

	if pssVar == nil {
		report.add("medium", "Pod Security", res, "No podSecurityStandard variable configured", "Set podSecurityStandard variable with enforce level")
		return
	}

	enforce, _ := pssVar["enforce"].(string)
	if enforce == "" || enforce == "privileged" {
		report.add("high", "Pod Security", res, fmt.Sprintf("PSS enforce level is '%s' (should be baseline or restricted)", enforce), "Set podSecurityStandard.enforce to 'baseline' or 'restricted'")
	} else if enforce == "baseline" {
		report.add("low", "Pod Security", res, "PSS enforce level is 'baseline' (consider 'restricted' for production)", "Consider 'restricted' level for higher security")
	}

	audit, _ := pssVar["audit"].(string)
	if audit == "" {
		report.add("low", "Pod Security", res, "PSS audit level not configured", "Set podSecurityStandard.audit for violation logging")
	}
}

func checkKubeadmSecurity(kcp map[string]interface{}, report *auditReport) {
	res := resName(kcp, "KubeadmControlPlane")
	spec := kubectl.GetMap(kcp, "spec")
	kcs := kubectl.GetMap(spec, "kubeadmConfigSpec")
	cc := kubectl.GetMap(kcs, "clusterConfiguration")
	api := kubectl.GetMap(cc, "apiServer")
	extraArgs := kubectl.GetMap(api, "extraArgs")

	if _, ok := extraArgs["encryption-provider-config"]; !ok {
		report.add("medium", "Encryption", res, "etcd encryption at rest not configured", "Configure encryption-provider-config for secret encryption")
	}

	if _, ok := extraArgs["audit-policy-file"]; !ok {
		report.add("medium", "Audit", res, "Kubernetes audit policy not configured", "Configure audit-policy-file for API audit logging")
	}

	authMode, _ := extraArgs["authorization-mode"].(string)
	if !strings.Contains(authMode, "RBAC") {
		report.add("high", "Authorization", res, "RBAC not explicitly enabled in authorization-mode", "Ensure authorization-mode includes RBAC")
	}

	if anonAuth, _ := extraArgs["anonymous-auth"].(string); anonAuth == "true" {
		report.add("high", "Authentication", res, "Anonymous authentication is enabled", "Set anonymous-auth=false")
	}

	kubelet := kubectl.GetMap(cc, "kubeletConfiguration")
	if v, ok := kubelet["serverTLSBootstrap"]; !ok || v != true {
		report.add("low", "TLS", res, "Kubelet server TLS bootstrap not enabled", "Enable serverTLSBootstrap for automatic certificate management")
	}
}

func checkMachineSecurity(machine map[string]interface{}, report *auditReport) {
	res := resName(machine, "Machine")
	spec := kubectl.GetMap(machine, "spec")
	bootstrap := kubectl.GetMap(spec, "bootstrap")

	if _, ok := bootstrap["dataSecretName"]; !ok {
		report.add("low", "Secrets", res, "Bootstrap data secret reference not found", "Ensure bootstrap data is stored in Secret")
	}
}

func checkNetworkSecurity(cluster map[string]interface{}, report *auditReport) {
	res := resName(cluster, "Cluster")
	spec := kubectl.GetMap(cluster, "spec")
	network := kubectl.GetMap(spec, "clusterNetwork")

	if len(network) == 0 {
		report.add("info", "Network", res, "No explicit clusterNetwork configuration", "Define clusterNetwork with appropriate CIDR ranges")
	}

	topo := kubectl.GetMap(spec, "topology")
	vars := kubectl.GetSlice(topo, "variables")
	cniConfigured := false
	cniNames := map[string]bool{"cni": true, "networkPlugin": true, "calico": true, "cilium": true}
	for _, v := range vars {
		vm, ok := v.(map[string]interface{})
		if !ok {
			continue
		}
		if name, _ := vm["name"].(string); cniNames[name] {
			cniConfigured = true
			break
		}
	}
	if !cniConfigured {
		report.add("info", "Network", res, "CNI configuration not found in cluster variables", "Ensure CNI plugin is configured (calico, cilium, etc.)")
	}
}

func checkSecretExposure(secrets []map[string]interface{}, report *auditReport) {
	for _, secret := range secrets {
		meta := kubectl.GetMap(secret, "metadata")
		name, _ := meta["name"].(string)
		if strings.Contains(strings.ToLower(name), "kubeconfig") {
			labels := kubectl.GetMap(meta, "labels")
			if _, ok := labels["cluster.x-k8s.io/cluster-name"]; !ok {
				res := resName(secret, "Secret")
				report.add("medium", "Secrets", res, "Kubeconfig secret without cluster label (may be orphaned)", "Verify secret ownership and clean up if orphaned")
			}
		}
	}
}

func checkReplicas(cluster map[string]interface{}, report *auditReport) {
	res := resName(cluster, "Cluster")
	spec := kubectl.GetMap(cluster, "spec")
	topo := kubectl.GetMap(spec, "topology")
	cp := kubectl.GetMap(topo, "controlPlane")

	cpReplicas := 1
	if v, ok := cp["replicas"].(float64); ok {
		cpReplicas = int(v)
	}

	if cpReplicas < 3 {
		sev := "low"
		if cpReplicas == 1 {
			sev = "medium"
		}
		report.add(sev, "Availability", res, fmt.Sprintf("Control plane has %d replica(s) (recommend 3 for HA)", cpReplicas), "Use 3 control plane replicas for production HA")
	}

	if cpReplicas%2 == 0 {
		report.add("low", "Availability", res, fmt.Sprintf("Control plane has even number of replicas (%d)", cpReplicas), "Use odd number of replicas for proper etcd quorum")
	}
}

func runAudit(clusterFilter, namespace string, allNamespaces bool) []auditReport {
	var reports []auditReport

	var clusters []map[string]interface{}
	if clusterFilter != "" {
		items, _ := kubectl.RunJSON("clusters.cluster.x-k8s.io/"+clusterFilter, namespace, "", false)
		clusters = items
	} else {
		items, _ := kubectl.RunJSON("clusters.cluster.x-k8s.io", namespace, "", allNamespaces)
		clusters = items
	}

	for _, cluster := range clusters {
		meta := kubectl.GetMap(cluster, "metadata")
		cName, _ := meta["name"].(string)
		cNS, _ := meta["namespace"].(string)
		if cName == "" {
			cName = "unknown"
		}
		if cNS == "" {
			cNS = "default"
		}

		report := auditReport{ClusterName: cNS + "/" + cName}

		checkPSS(cluster, &report)
		checkNetworkSecurity(cluster, &report)
		checkReplicas(cluster, &report)

		// KubeadmControlPlane
		kcps, _ := kubectl.RunJSON("kubeadmcontrolplanes.controlplane.cluster.x-k8s.io", cNS, "", false)
		for _, kcp := range kcps {
			ownerRefs := kubectl.GetSlice(kubectl.GetMap(kcp, "metadata"), "ownerReferences")
			for _, ref := range ownerRefs {
				rm, ok := ref.(map[string]interface{})
				if !ok {
					continue
				}
				if rn, _ := rm["name"].(string); rn == cName {
					checkKubeadmSecurity(kcp, &report)
					break
				}
			}
		}

		// Machines
		machines, _ := kubectl.RunJSON("machines.cluster.x-k8s.io", cNS, "", false)
		for _, machine := range machines {
			labels := kubectl.GetMap(kubectl.GetMap(machine, "metadata"), "labels")
			if cn, _ := labels["cluster.x-k8s.io/cluster-name"].(string); cn == cName {
				checkMachineSecurity(machine, &report)
			}
		}

		// Secrets
		secrets, _ := kubectl.RunJSON("secrets", cNS, "", false)
		var clusterSecrets []map[string]interface{}
		for _, s := range secrets {
			labels := kubectl.GetMap(kubectl.GetMap(s, "metadata"), "labels")
			if cn, _ := labels["cluster.x-k8s.io/cluster-name"].(string); cn == cName {
				clusterSecrets = append(clusterSecrets, s)
			}
		}
		checkSecretExposure(clusterSecrets, &report)

		reports = append(reports, report)
	}
	return reports
}

func printReport(report auditReport) {
	sep := strings.Repeat("=", 60)
	fmt.Printf("\n%s\nSecurity Audit: %s\n%s\n", sep, report.ClusterName, sep)

	if len(report.Findings) == 0 {
		fmt.Println("\n✓ No security findings!")
		return
	}

	fmt.Printf("\nSummary: %d high, %d medium, %d low\n", report.highCount(), report.mediumCount(), report.lowCount())

	severities := []string{"high", "medium", "low", "info"}
	icons := map[string]string{"high": "🔴", "medium": "🟠", "low": "🟡", "info": "🔵"}

	for _, sev := range severities {
		var filtered []finding
		for _, f := range report.Findings {
			if f.Severity == sev {
				filtered = append(filtered, f)
			}
		}
		if len(filtered) == 0 {
			continue
		}

		fmt.Printf("\n%s %s (%d)\n%s\n", icons[sev], strings.ToUpper(sev), len(filtered), strings.Repeat("-", 40))
		for _, f := range filtered {
			fmt.Printf("\n  [%s] %s\n    %s\n", f.Category, f.Resource, f.Message)
			if f.Recommendation != "" {
				fmt.Printf("    → %s\n", f.Recommendation)
			}
		}
	}
}

func exportJSON(reports []auditReport) string {
	type entry struct {
		Cluster  string `json:"cluster"`
		Summary  struct {
			High   int `json:"high"`
			Medium int `json:"medium"`
			Low    int `json:"low"`
		} `json:"summary"`
		Findings []finding `json:"findings"`
	}
	var out []entry
	for _, r := range reports {
		e := entry{Cluster: r.ClusterName, Findings: r.Findings}
		e.Summary.High = r.highCount()
		e.Summary.Medium = r.mediumCount()
		e.Summary.Low = r.lowCount()
		if e.Findings == nil {
			e.Findings = []finding{}
		}
		out = append(out, e)
	}
	data, _ := json.MarshalIndent(out, "", "  ")
	return string(data)
}

func main() {
	cluster := flag.String("c", "", "Specific cluster to audit")
	namespace := flag.String("n", "", "Namespace to audit")
	allNS := flag.Bool("A", false, "Audit all namespaces")
	output := flag.String("o", "", "Write JSON report to file")
	format := flag.String("format", "text", "Output format: text, json")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s [flags]\n\nAudit security posture of CAPI clusters.\n\nFlags:\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()

	if kubectl.Find() == "" {
		fmt.Fprintln(os.Stderr, "Error: kubectl not found in PATH")
		os.Exit(1)
	}

	fmt.Println("Running security audit...")
	reports := runAudit(*cluster, *namespace, *allNS)

	if len(reports) == 0 {
		fmt.Println("No clusters found to audit")
		os.Exit(0)
	}

	if *format == "json" || *output != "" {
		jsonOut := exportJSON(reports)
		if *output != "" {
			if err := os.WriteFile(*output, []byte(jsonOut), 0o644); err != nil {
				fmt.Fprintf(os.Stderr, "Error: %v\n", err)
				os.Exit(1)
			}
			fmt.Printf("Report written to: %s\n", *output)
		} else {
			fmt.Println(jsonOut)
		}
	} else {
		for _, r := range reports {
			printReport(r)
		}
	}

	hasHigh := false
	for _, r := range reports {
		if r.highCount() > 0 {
			hasHigh = true
			break
		}
	}
	if hasHigh {
		os.Exit(1)
	}
}
