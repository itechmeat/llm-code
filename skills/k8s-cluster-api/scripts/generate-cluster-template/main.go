// generate-cluster-template generates CAPI cluster manifests from ClusterClass
// or from scratch.
//
// Usage:
//
//	go run ./generate-cluster-template [flags]
//
// Examples:
//
//	go run ./generate-cluster-template -n my-cluster --class default
//	go run ./generate-cluster-template -n my-cluster --from-scratch --infra docker
//	go run ./generate-cluster-template --list-classes
//	go run ./generate-cluster-template --class default --info
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	kubectl "k8s-cluster-api-tools/internal/kubectl"
)

type clusterClassInfo struct {
	Name       string
	Namespace  string
	InfraKind  string
	CPKind     string
	Workers    []workerClass
	Variables  []classVariable
}

type workerClass struct {
	Name      string
	InfraKind string
	BootKind  string
}

type classVariable struct {
	Name     string
	Required bool
	Schema   string
}

var infraProviderTemplates = map[string]struct {
	ClusterKind   string
	MachineKind   string
	TemplateKind  string
	APIGroup      string
	APIVersion    string
}{
	"docker": {
		"DockerCluster", "DockerMachine", "DockerMachineTemplate",
		"infrastructure.cluster.x-k8s.io", "v1beta1",
	},
	"aws": {
		"AWSCluster", "AWSMachine", "AWSMachineTemplate",
		"infrastructure.cluster.x-k8s.io", "v1beta2",
	},
	"azure": {
		"AzureCluster", "AzureMachine", "AzureMachineTemplate",
		"infrastructure.cluster.x-k8s.io", "v1beta1",
	},
	"vsphere": {
		"VSphereCluster", "VSphereMachine", "VSphereMachineTemplate",
		"infrastructure.cluster.x-k8s.io", "v1beta1",
	},
	"metal3": {
		"Metal3Cluster", "Metal3Machine", "Metal3MachineTemplate",
		"infrastructure.cluster.x-k8s.io", "v1beta1",
	},
	"openstack": {
		"OpenStackCluster", "OpenStackMachine", "OpenStackMachineTemplate",
		"infrastructure.cluster.x-k8s.io", "v1beta1",
	},
}

func listClusterClasses(namespace, kubeconfig string) {
	args := []string{"get", "clusterclasses.cluster.x-k8s.io", "-o", "json"}
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
		fmt.Fprintln(os.Stderr, "Error listing ClusterClasses:", err)
		os.Exit(1)
	}

	if len(items) == 0 {
		fmt.Println("No ClusterClasses found")
		return
	}

	fmt.Println("Available ClusterClasses:")
	fmt.Println(strings.Repeat("-", 60))
	fmt.Printf("%-25s %-20s %s\n", "NAME", "NAMESPACE", "INFRASTRUCTURE")
	for _, item := range items {
		name := kubectl.GetString(item, "metadata", "name")
		ns := kubectl.GetString(item, "metadata", "namespace")
		infraRef := kubectl.GetMap(item, "spec", "infrastructure")
		infraKind := ""
		if ref, ok := infraRef["ref"].(map[string]interface{}); ok {
			infraKind, _ = ref["kind"].(string)
		}
		fmt.Printf("%-25s %-20s %s\n", name, ns, infraKind)
	}
}

func getClusterClassInfo(className, namespace, kubeconfig string) *clusterClassInfo {
	args := []string{"get", "clusterclasses.cluster.x-k8s.io", className, "-o", "json"}
	if namespace != "" {
		args = append(args, "-n", namespace)
	}
	if kubeconfig != "" {
		args = append(args, "--kubeconfig", kubeconfig)
	}

	out, err := kubectl.Run(args...)
	if err != nil {
		return nil
	}

	var cc map[string]interface{}
	if err := json.Unmarshal([]byte(out), &cc); err != nil {
		return nil
	}

	info := &clusterClassInfo{
		Name:      className,
		Namespace: namespace,
	}

	spec, _ := cc["spec"].(map[string]interface{})
	if spec == nil {
		return info
	}

	// Infrastructure
	if infra, ok := spec["infrastructure"].(map[string]interface{}); ok {
		if ref, ok := infra["ref"].(map[string]interface{}); ok {
			info.InfraKind, _ = ref["kind"].(string)
		}
	}

	// Control plane
	if cp, ok := spec["controlPlane"].(map[string]interface{}); ok {
		if ref, ok := cp["ref"].(map[string]interface{}); ok {
			info.CPKind, _ = ref["kind"].(string)
		}
	}

	// Workers
	if workers, ok := spec["workers"].(map[string]interface{}); ok {
		if mds, ok := workers["machineDeployments"].([]interface{}); ok {
			for _, md := range mds {
				mdMap, ok := md.(map[string]interface{})
				if !ok {
					continue
				}
				wc := workerClass{Name: mdMap["class"].(string)}
				if tmpl, ok := mdMap["template"].(map[string]interface{}); ok {
					if infra, ok := tmpl["infrastructure"].(map[string]interface{}); ok {
						if ref, ok := infra["ref"].(map[string]interface{}); ok {
							wc.InfraKind, _ = ref["kind"].(string)
						}
					}
					if boot, ok := tmpl["bootstrap"].(map[string]interface{}); ok {
						if ref, ok := boot["ref"].(map[string]interface{}); ok {
							wc.BootKind, _ = ref["kind"].(string)
						}
					}
				}
				info.Workers = append(info.Workers, wc)
			}
		}
	}

	// Variables
	if vars, ok := spec["variables"].([]interface{}); ok {
		for _, v := range vars {
			vMap, ok := v.(map[string]interface{})
			if !ok {
				continue
			}
			cv := classVariable{
				Name: vMap["name"].(string),
			}
			req, _ := vMap["required"].(bool)
			cv.Required = req

			if schema, ok := vMap["schema"].(map[string]interface{}); ok {
				if oas, ok := schema["openAPIV3Schema"].(map[string]interface{}); ok {
					t, _ := oas["type"].(string)
					cv.Schema = t
				}
			}
			info.Variables = append(info.Variables, cv)
		}
	}

	return info
}

func printClassInfo(info *clusterClassInfo) {
	fmt.Printf("ClusterClass: %s\n", info.Name)
	fmt.Printf("Namespace: %s\n", info.Namespace)
	fmt.Printf("Infrastructure: %s\n", info.InfraKind)
	fmt.Printf("Control Plane: %s\n", info.CPKind)

	fmt.Println("\nWorker Classes:")
	for _, w := range info.Workers {
		fmt.Printf("  - %s (infra: %s, bootstrap: %s)\n", w.Name, w.InfraKind, w.BootKind)
	}

	fmt.Println("\nVariables:")
	for _, v := range info.Variables {
		req := ""
		if v.Required {
			req = " [required]"
		}
		fmt.Printf("  - %s (%s)%s\n", v.Name, v.Schema, req)
	}
}

func generateFromClass(clusterName, className, namespace, k8sVersion string, cpReplicas, workerReplicas int, vars map[string]string) string {
	var sb strings.Builder

	sb.WriteString("apiVersion: cluster.x-k8s.io/v1beta1\n")
	sb.WriteString("kind: Cluster\n")
	sb.WriteString("metadata:\n")
	sb.WriteString(fmt.Sprintf("  name: %s\n", clusterName))
	if namespace != "" {
		sb.WriteString(fmt.Sprintf("  namespace: %s\n", namespace))
	}
	sb.WriteString("spec:\n")
	sb.WriteString("  topology:\n")
	sb.WriteString(fmt.Sprintf("    class: %s\n", className))
	sb.WriteString(fmt.Sprintf("    version: %s\n", k8sVersion))
	sb.WriteString("    controlPlane:\n")
	sb.WriteString(fmt.Sprintf("      replicas: %d\n", cpReplicas))
	sb.WriteString("    workers:\n")
	sb.WriteString("      machineDeployments:\n")
	sb.WriteString("      - class: default-worker\n")
	sb.WriteString(fmt.Sprintf("        name: %s-md-0\n", clusterName))
	sb.WriteString(fmt.Sprintf("        replicas: %d\n", workerReplicas))

	if len(vars) > 0 {
		sb.WriteString("    variables:\n")
		for k, v := range vars {
			sb.WriteString(fmt.Sprintf("    - name: %s\n", k))
			sb.WriteString(fmt.Sprintf("      value: %s\n", v))
		}
	}

	return sb.String()
}

func generateFromScratch(clusterName, infraProvider, namespace, k8sVersion string, cpReplicas, workerReplicas int) string {
	infra, ok := infraProviderTemplates[infraProvider]
	if !ok {
		fmt.Fprintf(os.Stderr, "Unknown infra provider: %s\nAvailable: ", infraProvider)
		for k := range infraProviderTemplates {
			fmt.Fprintf(os.Stderr, "%s ", k)
		}
		fmt.Fprintln(os.Stderr)
		os.Exit(1)
	}

	var sb strings.Builder
	nsLine := ""
	if namespace != "" {
		nsLine = fmt.Sprintf("  namespace: %s\n", namespace)
	}

	// Cluster
	sb.WriteString("apiVersion: cluster.x-k8s.io/v1beta1\n")
	sb.WriteString("kind: Cluster\n")
	sb.WriteString("metadata:\n")
	sb.WriteString(fmt.Sprintf("  name: %s\n", clusterName))
	sb.WriteString(nsLine)
	sb.WriteString("spec:\n")
	sb.WriteString("  clusterNetwork:\n")
	sb.WriteString("    pods:\n")
	sb.WriteString("      cidrBlocks:\n")
	sb.WriteString("      - 192.168.0.0/16\n")
	sb.WriteString("    services:\n")
	sb.WriteString("      cidrBlocks:\n")
	sb.WriteString("      - 10.128.0.0/12\n")
	sb.WriteString("  infrastructureRef:\n")
	sb.WriteString(fmt.Sprintf("    apiVersion: %s/%s\n", infra.APIGroup, infra.APIVersion))
	sb.WriteString(fmt.Sprintf("    kind: %s\n", infra.ClusterKind))
	sb.WriteString(fmt.Sprintf("    name: %s\n", clusterName))
	sb.WriteString(nsLine)
	sb.WriteString("  controlPlaneRef:\n")
	sb.WriteString("    apiVersion: controlplane.cluster.x-k8s.io/v1beta1\n")
	sb.WriteString("    kind: KubeadmControlPlane\n")
	sb.WriteString(fmt.Sprintf("    name: %s-control-plane\n", clusterName))
	sb.WriteString(nsLine)

	// Infra cluster
	sb.WriteString("---\n")
	sb.WriteString(fmt.Sprintf("apiVersion: %s/%s\n", infra.APIGroup, infra.APIVersion))
	sb.WriteString(fmt.Sprintf("kind: %s\n", infra.ClusterKind))
	sb.WriteString("metadata:\n")
	sb.WriteString(fmt.Sprintf("  name: %s\n", clusterName))
	sb.WriteString(nsLine)
	sb.WriteString("spec: {}\n")

	// KubeadmControlPlane
	sb.WriteString("---\n")
	sb.WriteString("apiVersion: controlplane.cluster.x-k8s.io/v1beta1\n")
	sb.WriteString("kind: KubeadmControlPlane\n")
	sb.WriteString("metadata:\n")
	sb.WriteString(fmt.Sprintf("  name: %s-control-plane\n", clusterName))
	sb.WriteString(nsLine)
	sb.WriteString("spec:\n")
	sb.WriteString(fmt.Sprintf("  replicas: %d\n", cpReplicas))
	sb.WriteString(fmt.Sprintf("  version: %s\n", k8sVersion))
	sb.WriteString("  machineTemplate:\n")
	sb.WriteString("    infrastructureRef:\n")
	sb.WriteString(fmt.Sprintf("      apiVersion: %s/%s\n", infra.APIGroup, infra.APIVersion))
	sb.WriteString(fmt.Sprintf("      kind: %s\n", infra.TemplateKind))
	sb.WriteString(fmt.Sprintf("      name: %s-control-plane\n", clusterName))
	sb.WriteString(nsLine)
	sb.WriteString("  kubeadmConfigSpec:\n")
	sb.WriteString("    initConfiguration:\n")
	sb.WriteString("      nodeRegistration:\n")
	sb.WriteString("        kubeletExtraArgs: {}\n")
	sb.WriteString("    joinConfiguration:\n")
	sb.WriteString("      nodeRegistration:\n")
	sb.WriteString("        kubeletExtraArgs: {}\n")

	// Control plane machine template
	sb.WriteString("---\n")
	sb.WriteString(fmt.Sprintf("apiVersion: %s/%s\n", infra.APIGroup, infra.APIVersion))
	sb.WriteString(fmt.Sprintf("kind: %s\n", infra.TemplateKind))
	sb.WriteString("metadata:\n")
	sb.WriteString(fmt.Sprintf("  name: %s-control-plane\n", clusterName))
	sb.WriteString(nsLine)
	sb.WriteString("spec:\n")
	sb.WriteString("  template:\n")
	sb.WriteString("    spec: {}\n")

	// MachineDeployment
	sb.WriteString("---\n")
	sb.WriteString("apiVersion: cluster.x-k8s.io/v1beta1\n")
	sb.WriteString("kind: MachineDeployment\n")
	sb.WriteString("metadata:\n")
	sb.WriteString(fmt.Sprintf("  name: %s-md-0\n", clusterName))
	sb.WriteString(nsLine)
	sb.WriteString("spec:\n")
	sb.WriteString(fmt.Sprintf("  clusterName: %s\n", clusterName))
	sb.WriteString(fmt.Sprintf("  replicas: %d\n", workerReplicas))
	sb.WriteString("  selector:\n")
	sb.WriteString("    matchLabels: {}\n")
	sb.WriteString("  template:\n")
	sb.WriteString("    spec:\n")
	sb.WriteString(fmt.Sprintf("      clusterName: %s\n", clusterName))
	sb.WriteString(fmt.Sprintf("      version: %s\n", k8sVersion))
	sb.WriteString("      bootstrap:\n")
	sb.WriteString("        configRef:\n")
	sb.WriteString("          apiVersion: bootstrap.cluster.x-k8s.io/v1beta1\n")
	sb.WriteString("          kind: KubeadmConfigTemplate\n")
	sb.WriteString(fmt.Sprintf("          name: %s-md-0\n", clusterName))
	sb.WriteString(nsLine)
	sb.WriteString("      infrastructureRef:\n")
	sb.WriteString(fmt.Sprintf("        apiVersion: %s/%s\n", infra.APIGroup, infra.APIVersion))
	sb.WriteString(fmt.Sprintf("        kind: %s\n", infra.TemplateKind))
	sb.WriteString(fmt.Sprintf("        name: %s-md-0\n", clusterName))
	sb.WriteString(nsLine)

	// Worker machine template
	sb.WriteString("---\n")
	sb.WriteString(fmt.Sprintf("apiVersion: %s/%s\n", infra.APIGroup, infra.APIVersion))
	sb.WriteString(fmt.Sprintf("kind: %s\n", infra.TemplateKind))
	sb.WriteString("metadata:\n")
	sb.WriteString(fmt.Sprintf("  name: %s-md-0\n", clusterName))
	sb.WriteString(nsLine)
	sb.WriteString("spec:\n")
	sb.WriteString("  template:\n")
	sb.WriteString("    spec: {}\n")

	// KubeadmConfigTemplate
	sb.WriteString("---\n")
	sb.WriteString("apiVersion: bootstrap.cluster.x-k8s.io/v1beta1\n")
	sb.WriteString("kind: KubeadmConfigTemplate\n")
	sb.WriteString("metadata:\n")
	sb.WriteString(fmt.Sprintf("  name: %s-md-0\n", clusterName))
	sb.WriteString(nsLine)
	sb.WriteString("spec:\n")
	sb.WriteString("  template:\n")
	sb.WriteString("    spec:\n")
	sb.WriteString("      joinConfiguration:\n")
	sb.WriteString("        nodeRegistration:\n")
	sb.WriteString("          kubeletExtraArgs: {}\n")

	return sb.String()
}

func main() {
	clusterName := flag.String("n", "my-cluster", "Cluster name")
	className := flag.String("class", "", "ClusterClass name")
	namespace := flag.String("ns", "default", "Target namespace")
	kubeconfig := flag.String("kubeconfig", "", "Path to kubeconfig")
	k8sVersion := flag.String("k8s-version", "v1.28.0", "Kubernetes version")
	cpReplicas := flag.Int("cp-replicas", 3, "Control plane replicas")
	workerReplicas := flag.Int("worker-replicas", 3, "Worker replicas")
	infraProvider := flag.String("infra", "docker", "Infrastructure provider (for --from-scratch)")
	fromScratch := flag.Bool("from-scratch", false, "Generate without ClusterClass")
	listClasses := flag.Bool("list-classes", false, "List available ClusterClasses")
	showInfo := flag.Bool("info", false, "Show ClusterClass info (requires --class)")
	output := flag.String("o", "", "Output file (default: stdout)")
	varsStr := flag.String("vars", "", "ClusterClass variables as key=value,key=value")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "CAPI Cluster Template Generator\nUsage: %s [flags]\n\nFlags:\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()

	if *listClasses {
		listClusterClasses(*namespace, *kubeconfig)
		return
	}

	if *showInfo {
		if *className == "" {
			fmt.Fprintln(os.Stderr, "Error: --class required with --info")
			os.Exit(1)
		}
		info := getClusterClassInfo(*className, *namespace, *kubeconfig)
		if info == nil {
			fmt.Fprintf(os.Stderr, "ClusterClass '%s' not found\n", *className)
			os.Exit(1)
		}
		printClassInfo(info)
		return
	}

	var result string
	if *fromScratch {
		result = generateFromScratch(*clusterName, *infraProvider, *namespace, *k8sVersion, *cpReplicas, *workerReplicas)
	} else if *className != "" {
		vars := map[string]string{}
		if *varsStr != "" {
			for _, pair := range strings.Split(*varsStr, ",") {
				kv := strings.SplitN(pair, "=", 2)
				if len(kv) == 2 {
					vars[kv[0]] = kv[1]
				}
			}
		}
		result = generateFromClass(*clusterName, *className, *namespace, *k8sVersion, *cpReplicas, *workerReplicas, vars)
	} else {
		fmt.Fprintln(os.Stderr, "Error: specify --class or --from-scratch")
		flag.Usage()
		os.Exit(1)
	}

	if *output != "" {
		dir := filepath.Dir(*output)
		if dir != "." {
			_ = os.MkdirAll(dir, 0755)
		}
		if err := os.WriteFile(*output, []byte(result), 0644); err != nil {
			fmt.Fprintf(os.Stderr, "Error writing file: %v\n", err)
			os.Exit(1)
		}
		fmt.Fprintf(os.Stderr, "Template written to %s\n", *output)
	} else {
		fmt.Print(result)
	}
}
