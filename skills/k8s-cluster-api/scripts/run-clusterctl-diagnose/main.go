// run-clusterctl-diagnose runs clusterctl describe and saves a diagnostic report.
//
// Usage:
//
//	go run ./run-clusterctl-diagnose <cluster-name> [flags]
//
// Examples:
//
//	go run ./run-clusterctl-diagnose my-cluster
//	go run ./run-clusterctl-diagnose my-cluster -n clusters -o report.txt
package main

import (
	"flag"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

func findClusterctl() string {
	path, err := exec.LookPath("clusterctl")
	if err != nil {
		return ""
	}
	return path
}

func resolveRepoRoot(start string) string {
	dir := start
	for {
		if _, err := os.Stat(filepath.Join(dir, ".git")); err == nil {
			return dir
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			return start
		}
		dir = parent
	}
}

func ensureOutputDir(repoRoot string) (string, error) {
	dir := filepath.Join(repoRoot, ".cluster-diagnostics")
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return "", err
	}
	gitignore := filepath.Join(dir, ".gitignore")
	if _, err := os.Stat(gitignore); os.IsNotExist(err) {
		_ = os.WriteFile(gitignore, []byte("*\n"), 0o644)
	}
	return dir, nil
}

func runClusterctlDescribe(clusterName, namespace, kubeconfig string, timeout int) (string, int) {
	clusterctl := findClusterctl()
	if clusterctl == "" {
		return "Error: clusterctl not found in PATH", 1
	}

	args := []string{"describe", "cluster", clusterName, "--show-conditions=all"}
	if namespace != "" {
		args = append(args, "--namespace", namespace)
	}
	if kubeconfig != "" {
		args = append(args, "--kubeconfig", kubeconfig)
	}

	cmd := exec.Command(clusterctl, args...)
	out, err := cmd.CombinedOutput()
	if err != nil {
		if exitErr, ok := err.(*exec.ExitError); ok {
			return string(out), exitErr.ExitCode()
		}
		return fmt.Sprintf("Error running clusterctl: %v\n%s", err, string(out)), 1
	}
	return string(out), 0
}

func runAdditionalDiagnostics(clusterName, namespace, kubeconfig string) string {
	clusterctl := findClusterctl()
	if clusterctl == "" {
		return ""
	}

	var sections []string

	// Topology
	topoArgs := []string{"describe", "cluster", clusterName, "--show-topology"}
	if namespace != "" {
		topoArgs = append(topoArgs, "--namespace", namespace)
	}
	if kubeconfig != "" {
		topoArgs = append(topoArgs, "--kubeconfig", kubeconfig)
	}
	cmd := exec.Command(clusterctl, topoArgs...)
	out, err := cmd.Output()
	if err == nil && len(strings.TrimSpace(string(out))) > 0 {
		sections = append(sections, "=== CLUSTER TOPOLOGY ===\n"+string(out))
	}

	// Move dry-run
	moveArgs := []string{"move", "--dry-run", "-v", "0", "--filter-cluster", clusterName}
	if namespace != "" {
		moveArgs = append(moveArgs, "--namespace", namespace)
	}
	if kubeconfig != "" {
		moveArgs = append(moveArgs, "--kubeconfig", kubeconfig)
	}
	cmd = exec.Command(clusterctl, moveArgs...)
	out, _ = cmd.Output()
	if len(strings.TrimSpace(string(out))) > 0 {
		sections = append(sections, "=== MOVE DRY-RUN (objects) ===\n"+string(out))
	}

	return strings.Join(sections, "\n\n")
}

func generateReport(clusterName, namespace, descOutput, additional string) string {
	ts := time.Now().Format("2006-01-02 15:04:05")
	if namespace == "" {
		namespace = "default"
	}

	var b strings.Builder
	sep := strings.Repeat("=", 60)
	b.WriteString(sep + "\n")
	b.WriteString("CLUSTER API DIAGNOSTIC REPORT\n")
	b.WriteString(sep + "\n")
	fmt.Fprintf(&b, "Cluster: %s\n", clusterName)
	fmt.Fprintf(&b, "Namespace: %s\n", namespace)
	fmt.Fprintf(&b, "Generated: %s\n", ts)
	b.WriteString(sep + "\n\n")
	b.WriteString("=== CLUSTER DESCRIPTION ===\n")
	b.WriteString(descOutput)

	if additional != "" {
		b.WriteString("\n\n" + additional)
	}

	b.WriteString("\n\n" + sep + "\n")
	b.WriteString("END OF REPORT\n")
	b.WriteString(sep + "\n")

	return b.String()
}

func main() {
	namespace := flag.String("n", "", "Namespace of the cluster")
	kubeconfig := flag.String("k", "", "Path to kubeconfig file")
	output := flag.String("o", "", "Output filename")
	timeout := flag.Int("t", 120, "Timeout in seconds")
	skipAdditional := flag.Bool("skip-additional", false, "Skip additional diagnostics")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s <cluster-name> [flags]\n\nRun clusterctl describe and save diagnostic report.\n\nFlags:\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()

	if flag.NArg() < 1 {
		flag.Usage()
		os.Exit(1)
	}
	clusterName := flag.Arg(0)

	fmt.Printf("Running clusterctl describe for cluster '%s'...\n", clusterName)
	descOutput, exitCode := runClusterctlDescribe(clusterName, *namespace, *kubeconfig, *timeout)

	additional := ""
	if !*skipAdditional {
		fmt.Println("Running additional diagnostics...")
		additional = runAdditionalDiagnostics(clusterName, *namespace, *kubeconfig)
	}

	report := generateReport(clusterName, *namespace, descOutput, additional)

	// Resolve output path
	exe, _ := os.Executable()
	repoRoot := resolveRepoRoot(filepath.Dir(exe))
	if cwd, err := os.Getwd(); err == nil {
		repoRoot = resolveRepoRoot(cwd)
	}
	outputDir, err := ensureOutputDir(repoRoot)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error creating output directory: %v\n", err)
		os.Exit(1)
	}

	outName := *output
	if outName == "" {
		outName = clusterName + "-diagnostic.txt"
	}
	outPath := filepath.Join(outputDir, outName)

	if err := os.WriteFile(outPath, []byte(report), 0o644); err != nil {
		fmt.Fprintf(os.Stderr, "Error writing report: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("\n✅ Diagnostic report saved to: %s\n", outPath)
	if exitCode != 0 {
		fmt.Fprintf(os.Stderr, "⚠️  clusterctl exited with code %d\n", exitCode)
	}
	os.Exit(exitCode)
}
