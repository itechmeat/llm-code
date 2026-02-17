// Package kubectl provides shared helpers for executing kubectl commands
// and parsing their JSON output.
package kubectl

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"time"
)

// DefaultTimeout is the default command timeout.
const DefaultTimeout = 30 * time.Second

// Find returns the path to kubectl binary, or empty string if not found.
func Find() string {
	path, err := exec.LookPath("kubectl")
	if err != nil {
		return ""
	}
	return path
}

// Run executes a kubectl command and returns (success, stdout, stderr).
func Run(args []string, timeout time.Duration) (bool, string, string) {
	kubectl := Find()
	if kubectl == "" {
		return false, "", "kubectl not found"
	}
	if timeout == 0 {
		timeout = DefaultTimeout
	}
	cmd := exec.Command(kubectl, args...)
	var stdout, stderr []byte
	var err error
	done := make(chan struct{})
	go func() {
		stdout, err = cmd.Output()
		if exitErr, ok := err.(*exec.ExitError); ok {
			stderr = exitErr.Stderr
		}
		close(done)
	}()
	select {
	case <-done:
		if err != nil {
			return false, string(stdout), string(stderr)
		}
		return true, string(stdout), ""
	case <-time.After(timeout):
		_ = cmd.Process.Kill()
		return false, "", "Command timed out"
	}
}

// RunJSON executes kubectl and parses the JSON output as a list of items.
// If the output is a List, returns the items. If it's a single resource, wraps it.
func RunJSON(resource string, namespace string, labelSelector string, allNamespaces bool) ([]map[string]interface{}, error) {
	args := []string{"get", resource, "-o", "json"}
	if namespace != "" && !allNamespaces {
		args = append(args, "-n", namespace)
	}
	if allNamespaces {
		args = append(args, "--all-namespaces")
	}
	if labelSelector != "" {
		args = append(args, "-l", labelSelector)
	}

	ok, stdout, errMsg := Run(args, DefaultTimeout)
	if !ok {
		if errMsg != "" {
			return nil, fmt.Errorf("%s", errMsg)
		}
		return nil, nil // Resource not found is not an error
	}

	var raw map[string]interface{}
	if err := json.Unmarshal([]byte(stdout), &raw); err != nil {
		return nil, fmt.Errorf("JSON parse error: %w", err)
	}

	if kind, _ := raw["kind"].(string); kind != "" && len(kind) > 4 && kind[len(kind)-4:] == "List" {
		items, _ := raw["items"].([]interface{})
		result := make([]map[string]interface{}, 0, len(items))
		for _, item := range items {
			if m, ok := item.(map[string]interface{}); ok {
				result = append(result, m)
			}
		}
		return result, nil
	}

	return []map[string]interface{}{raw}, nil
}

// GetNested retrieves a nested value from a map using dot notation.
func GetNested(data map[string]interface{}, path string) interface{} {
	keys := splitDotPath(path)
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

// GetString retrieves a string from a nested map.
func GetString(data map[string]interface{}, path string) string {
	v := GetNested(data, path)
	if s, ok := v.(string); ok {
		return s
	}
	return ""
}

// GetMap retrieves a sub-map from a nested map.
func GetMap(data map[string]interface{}, key string) map[string]interface{} {
	v, _ := data[key].(map[string]interface{})
	if v == nil {
		return map[string]interface{}{}
	}
	return v
}

// GetSlice retrieves a slice of interfaces from a map.
func GetSlice(data map[string]interface{}, key string) []interface{} {
	v, _ := data[key].([]interface{})
	return v
}

// Errorf prints an error message to stderr.
func Errorf(format string, args ...interface{}) {
	fmt.Fprintf(os.Stderr, format+"\n", args...)
}

func splitDotPath(path string) []string {
	var parts []string
	current := ""
	for _, c := range path {
		if c == '.' {
			if current != "" {
				parts = append(parts, current)
			}
			current = ""
		} else {
			current += string(c)
		}
	}
	if current != "" {
		parts = append(parts, current)
	}
	return parts
}
