// lint-cluster-templates lints Cluster API manifests for issues and best practices.
//
// Usage:
//
//	go run ./lint-cluster-templates [files...] [flags]
//
// Examples:
//
//	go run ./lint-cluster-templates manifest.yaml
//	go run ./lint-cluster-templates -d ./manifests/ --strict
//	go run ./lint-cluster-templates --assets
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"gopkg.in/yaml.v3"
)

type severity int

const (
	sevError severity = iota
	sevWarning
	sevInfo
)

func (s severity) String() string {
	switch s {
	case sevError:
		return "error"
	case sevWarning:
		return "warning"
	case sevInfo:
		return "info"
	}
	return "unknown"
}

type lintIssue struct {
	Sev        severity `json:"-"`
	SevStr     string   `json:"severity"`
	Message    string   `json:"message"`
	File       string   `json:"file"`
	Line       int      `json:"line,omitempty"`
	Suggestion string   `json:"suggestion,omitempty"`
}

func (i lintIssue) String() string {
	icon := map[severity]string{sevError: "❌", sevWarning: "⚠️", sevInfo: "ℹ️"}[i.Sev]
	loc := i.File
	if i.Line > 0 {
		loc = fmt.Sprintf("%s:%d", i.File, i.Line)
	}
	s := fmt.Sprintf("%s %s %s", icon, loc, i.Message)
	if i.Suggestion != "" {
		s += " → " + i.Suggestion
	}
	return s
}

type lintResult struct {
	File   string      `json:"file"`
	Issues []lintIssue `json:"issues"`
}

func (r lintResult) hasErrors() bool {
	for _, i := range r.Issues {
		if i.Sev == sevError {
			return true
		}
	}
	return false
}

func (r lintResult) hasWarnings() bool {
	for _, i := range r.Issues {
		if i.Sev == sevWarning {
			return true
		}
	}
	return false
}

var capiAPIVersions = map[string]struct {
	deprecated  bool
	replacement string
}{
	"cluster.x-k8s.io/v1alpha3":              {true, "v1beta1"},
	"cluster.x-k8s.io/v1alpha4":              {true, "v1beta1"},
	"infrastructure.cluster.x-k8s.io/v1alpha3": {true, "v1beta1"},
	"infrastructure.cluster.x-k8s.io/v1alpha4": {true, "v1beta1"},
	"bootstrap.cluster.x-k8s.io/v1alpha3":      {true, "v1beta1"},
	"bootstrap.cluster.x-k8s.io/v1alpha4":      {true, "v1beta1"},
	"controlplane.cluster.x-k8s.io/v1alpha3":   {true, "v1beta1"},
	"controlplane.cluster.x-k8s.io/v1alpha4":   {true, "v1beta1"},
}

var capiKinds = map[string][]string{
	"Cluster":            {"clusterName:opt", "infrastructureRef", "controlPlaneRef"},
	"Machine":            {"clusterName", "bootstrap"},
	"MachineDeployment":  {"clusterName", "template"},
	"MachineSet":         {"clusterName", "template"},
	"ClusterClass":       {"infrastructure", "controlPlane"},
	"MachineHealthCheck": {"clusterName", "selector", "unhealthyConditions"},
	"MachinePool":        {"clusterName", "template"},
}

var deprecatedFieldsMap = map[string]map[string]struct {
	since   string
	message string
}{
	"Cluster": {
		"spec.paused": {"v1.4.0", "Use spec.topology.controlPlane/workers for managed clusters"},
	},
	"Machine": {
		"spec.version": {"v1.5.0", "Version is now inherited from control plane or topology"},
	},
}

var credentialPatterns = []*regexp.Regexp{
	regexp.MustCompile(`(?i)password:\s*['"]?[^${\s]+['"]?`),
	regexp.MustCompile(`(?i)secret:\s*['"]?[^${\s]+['"]?`),
	regexp.MustCompile(`(?i)token:\s*['"]?[a-zA-Z0-9+/=]{20,}['"]?`),
}

func lintDocument(doc map[string]interface{}, filePath string, startLine int) []lintIssue {
	var issues []lintIssue

	// Required top-level fields
	if _, ok := doc["apiVersion"]; !ok {
		issues = append(issues, lintIssue{sevError, "error", "Missing required field: apiVersion", filePath, startLine, ""})
	}
	if _, ok := doc["kind"]; !ok {
		issues = append(issues, lintIssue{sevError, "error", "Missing required field: kind", filePath, startLine, ""})
	}
	metadata, _ := doc["metadata"].(map[string]interface{})
	if metadata == nil {
		issues = append(issues, lintIssue{sevError, "error", "Missing required field: metadata", filePath, startLine, ""})
	} else if _, ok := metadata["name"]; !ok {
		issues = append(issues, lintIssue{sevError, "error", "Missing required field: metadata.name", filePath, startLine, ""})
	}

	// Check API version
	av, _ := doc["apiVersion"].(string)
	if info, ok := capiAPIVersions[av]; ok && info.deprecated {
		issues = append(issues, lintIssue{sevWarning, "warning",
			fmt.Sprintf("Deprecated API version: %s", av), filePath, startLine,
			fmt.Sprintf("Use cluster.x-k8s.io/%s", info.replacement)})
	}

	// Kind-specific checks
	kind, _ := doc["kind"].(string)
	if fields, ok := capiKinds[kind]; ok {
		spec, _ := doc["spec"].(map[string]interface{})
		if spec == nil {
			spec = map[string]interface{}{}
		}
		for _, field := range fields {
			if strings.HasSuffix(field, ":opt") {
				continue
			}
			if kind == "Cluster" {
				if _, hasTopo := spec["topology"]; hasTopo {
					if field == "infrastructureRef" || field == "controlPlaneRef" {
						continue
					}
				}
			}
			if _, ok := spec[field]; !ok {
				issues = append(issues, lintIssue{sevError, "error",
					fmt.Sprintf("Missing required spec field for %s: %s", kind, field),
					filePath, startLine, ""})
			}
		}
	}

	// Deprecated fields
	if depFields, ok := deprecatedFieldsMap[kind]; ok {
		for fieldPath, info := range depFields {
			if getNestedValue(doc, fieldPath) != nil {
				issues = append(issues, lintIssue{sevWarning, "warning",
					fmt.Sprintf("Deprecated field '%s' (since %s)", fieldPath, info.since),
					filePath, startLine, info.message})
			}
		}
	}

	// Namespace check
	if metadata != nil {
		if _, ok := metadata["namespace"]; !ok {
			issues = append(issues, lintIssue{sevInfo, "info",
				"No namespace specified - will use default", filePath, startLine, ""})
		}
	}

	return issues
}

func getNestedValue(data map[string]interface{}, path string) interface{} {
	parts := strings.Split(path, ".")
	var current interface{} = data
	for _, p := range parts {
		m, ok := current.(map[string]interface{})
		if !ok {
			return nil
		}
		current = m[p]
	}
	return current
}

func lintContent(content, filePath string) lintResult {
	result := lintResult{File: filePath}

	// Best practice: credential detection
	lines := strings.Split(content, "\n")
	for i, line := range lines {
		for _, pat := range credentialPatterns {
			if pat.MatchString(line) {
				result.Issues = append(result.Issues, lintIssue{
					sevWarning, "warning", "Possible hardcoded credential detected",
					filePath, i + 1, "",
				})
			}
		}
	}

	// Parse YAML documents
	decoder := yaml.NewDecoder(strings.NewReader(content))
	docIndex := 0
	for {
		var doc map[string]interface{}
		if err := decoder.Decode(&doc); err != nil {
			if err.Error() != "EOF" {
				result.Issues = append(result.Issues, lintIssue{
					sevError, "error", fmt.Sprintf("YAML syntax error: %v", err),
					filePath, 0, "",
				})
			}
			break
		}
		if doc == nil {
			docIndex++
			continue
		}
		docIndex++

		issues := lintDocument(doc, filePath, 0)
		result.Issues = append(result.Issues, issues...)
	}

	return result
}

func lintFile(filePath string) lintResult {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return lintResult{
			File: filePath,
			Issues: []lintIssue{{sevError, "error", fmt.Sprintf("File error: %v", err), filePath, 0, ""}},
		}
	}
	return lintContent(string(data), filePath)
}

func getAssetsDir() string {
	exe, _ := os.Executable()
	scriptDir := filepath.Dir(exe)
	// Try from working directory
	if cwd, err := os.Getwd(); err == nil {
		assets := filepath.Join(cwd, "..", "assets")
		if info, err := os.Stat(assets); err == nil && info.IsDir() {
			return assets
		}
		assets = filepath.Join(filepath.Dir(cwd), "assets")
		if info, err := os.Stat(assets); err == nil && info.IsDir() {
			return assets
		}
	}
	return filepath.Join(filepath.Dir(scriptDir), "assets")
}

func lintAssets() []lintResult {
	var results []lintResult
	assetsDir := getAssetsDir()

	matches, _ := filepath.Glob(filepath.Join(assetsDir, "*.yaml"))
	for _, f := range matches {
		results = append(results, lintFile(f))
	}
	return results
}

func printResults(results []lintResult, verbose bool) (int, int) {
	totalErrors, totalWarnings := 0, 0

	for _, r := range results {
		errors, warnings := 0, 0
		for _, i := range r.Issues {
			if i.Sev == sevError {
				errors++
			} else if i.Sev == sevWarning {
				warnings++
			}
		}
		totalErrors += errors
		totalWarnings += warnings

		if len(r.Issues) > 0 || verbose {
			if len(r.Issues) == 0 {
				fmt.Printf("✓ %s\n", r.File)
			} else {
				for _, issue := range r.Issues {
					fmt.Println(issue.String())
				}
			}
		}
	}
	return totalErrors, totalWarnings
}

func main() {
	dir := flag.String("d", "", "Directory to lint (*.yaml files)")
	assets := flag.Bool("assets", false, "Lint all asset templates")
	strict := flag.Bool("strict", false, "Treat warnings as errors")
	verbose := flag.Bool("v", false, "Show passed files")
	format := flag.String("format", "text", "Output format: text, json")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s [files...] [flags]\n\nLint Cluster API manifests.\n\nFlags:\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()

	files := flag.Args()
	if len(files) == 0 && *dir == "" && !*assets {
		flag.Usage()
		os.Exit(1)
	}

	var results []lintResult

	if *assets {
		results = append(results, lintAssets()...)
	}

	if *dir != "" {
		if info, err := os.Stat(*dir); err == nil && info.IsDir() {
			_ = filepath.Walk(*dir, func(path string, info os.FileInfo, err error) error {
				if err != nil {
					return nil
				}
				if filepath.Ext(path) == ".yaml" {
					results = append(results, lintFile(path))
				}
				return nil
			})
		} else {
			fmt.Fprintf(os.Stderr, "Directory not found: %s\n", *dir)
			os.Exit(1)
		}
	}

	for _, f := range files {
		if strings.Contains(f, "*") {
			matches, _ := filepath.Glob(f)
			for _, m := range matches {
				results = append(results, lintFile(m))
			}
		} else {
			results = append(results, lintFile(f))
		}
	}

	if len(results) == 0 {
		fmt.Fprintln(os.Stderr, "No files to lint")
		os.Exit(1)
	}

	if *format == "json" {
		type jsonIssue struct {
			Severity   string `json:"severity"`
			Message    string `json:"message"`
			Line       int    `json:"line,omitempty"`
			Suggestion string `json:"suggestion,omitempty"`
		}
		type jsonResult struct {
			File   string      `json:"file"`
			Issues []jsonIssue `json:"issues"`
		}
		var output []jsonResult
		for _, r := range results {
			jr := jsonResult{File: r.File}
			for _, i := range r.Issues {
				jr.Issues = append(jr.Issues, jsonIssue{i.Sev.String(), i.Message, i.Line, i.Suggestion})
			}
			if jr.Issues == nil {
				jr.Issues = []jsonIssue{}
			}
			output = append(output, jr)
		}
		data, _ := json.MarshalIndent(output, "", "  ")
		fmt.Println(string(data))
	} else {
		errors, warnings := printResults(results, *verbose)

		totalFiles := len(results)
		passed := 0
		for _, r := range results {
			if !r.hasErrors() {
				passed++
			}
		}
		fmt.Printf("\n%d/%d files passed\n", passed, totalFiles)
		if errors > 0 {
			fmt.Printf("%d error(s)\n", errors)
		}
		if warnings > 0 {
			fmt.Printf("%d warning(s)\n", warnings)
		}
	}

	hasErrors := false
	hasWarnings := false
	for _, r := range results {
		if r.hasErrors() {
			hasErrors = true
		}
		if r.hasWarnings() {
			hasWarnings = true
		}
	}
	if hasErrors {
		os.Exit(1)
	}
	if *strict && hasWarnings {
		os.Exit(1)
	}
}
