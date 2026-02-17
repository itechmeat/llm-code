// scaffold-provider generates a complete Cluster API provider project scaffold.
//
// Usage:
//
//	go run ./scaffold-provider [flags]
//
// Examples:
//
//	go run ./scaffold-provider -n mycloud -t infrastructure
//	go run ./scaffold-provider -n mycloud -t bootstrap --module github.com/org/cluster-api-bootstrap-provider-mycloud
//	go run ./scaffold-provider -n mycloud -t controlplane --output-dir ./capi-provider-mycloud
package main

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"text/template"
)

type providerConfig struct {
	Name         string
	Type         string // infrastructure, bootstrap, controlplane
	Module       string
	OutputDir    string
	APIGroup     string
	APIVersion   string
	ClusterKind  string
	MachineKind  string
	TemplateKind string
	ExtraKinds   []string
}

func (c *providerConfig) CapName() string {
	return strings.ToUpper(c.Name[:1]) + c.Name[1:]
}

func (c *providerConfig) TypeCap() string {
	return strings.ToUpper(c.Type[:1]) + c.Type[1:]
}

func defaultConfig(name, provType string) *providerConfig {
	cfg := &providerConfig{
		Name:       name,
		Type:       provType,
		APIVersion: "v1beta1",
	}

	capName := cfg.CapName()

	switch provType {
	case "infrastructure":
		cfg.APIGroup = "infrastructure.cluster.x-k8s.io"
		cfg.ClusterKind = capName + "Cluster"
		cfg.MachineKind = capName + "Machine"
		cfg.TemplateKind = capName + "MachineTemplate"
		cfg.ExtraKinds = []string{capName + "ClusterTemplate"}
	case "bootstrap":
		cfg.APIGroup = "bootstrap.cluster.x-k8s.io"
		cfg.ClusterKind = capName + "Config"
		cfg.MachineKind = capName + "Config"
		cfg.TemplateKind = capName + "ConfigTemplate"
	case "controlplane":
		cfg.APIGroup = "controlplane.cluster.x-k8s.io"
		cfg.ClusterKind = capName + "ControlPlane"
		cfg.MachineKind = capName + "ControlPlane"
		cfg.TemplateKind = capName + "ControlPlaneTemplate"
	}

	if cfg.Module == "" {
		var prefix string
		switch provType {
		case "infrastructure":
			prefix = "cluster-api-provider-"
		case "bootstrap":
			prefix = "cluster-api-bootstrap-provider-"
		case "controlplane":
			prefix = "cluster-api-controlplane-provider-"
		}
		cfg.Module = "github.com/example/" + prefix + name
	}

	return cfg
}

// Template data struct for Go templates
type templateData struct {
	Name         string
	CapName      string
	Type         string
	TypeCap      string
	Module       string
	APIGroup     string
	APIVersion   string
	ClusterKind  string
	MachineKind  string
	TemplateKind string
	ExtraKinds   []string
}

func newTemplateData(cfg *providerConfig) templateData {
	return templateData{
		Name:         cfg.Name,
		CapName:      cfg.CapName(),
		Type:         cfg.Type,
		TypeCap:      cfg.TypeCap(),
		Module:       cfg.Module,
		APIGroup:     cfg.APIGroup,
		APIVersion:   cfg.APIVersion,
		ClusterKind:  cfg.ClusterKind,
		MachineKind:  cfg.MachineKind,
		TemplateKind: cfg.TemplateKind,
		ExtraKinds:   cfg.ExtraKinds,
	}
}

func writeFile(path, content string) error {
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return err
	}
	return os.WriteFile(path, []byte(content), 0644)
}

func renderTemplate(name, tmplStr string, data templateData) string {
	t, err := template.New(name).Parse(tmplStr)
	if err != nil {
		panic(fmt.Sprintf("template %s parse error: %v", name, err))
	}
	var sb strings.Builder
	if err := t.Execute(&sb, data); err != nil {
		panic(fmt.Sprintf("template %s exec error: %v", name, err))
	}
	return sb.String()
}

// --- Templates ---

const readmeTmpl = `# Cluster API {{.TypeCap}} Provider {{.CapName}}

Kubernetes Cluster API {{.Type}} provider for {{.CapName}}.

## Overview

This provider implements the Cluster API contract for {{.Type}} provisioning
with {{.CapName}}.

## Quick Start

1. Initialize the management cluster:
` + "```bash" + `
clusterctl init --{{.Type}} {{.Name}}
` + "```" + `

2. Create a workload cluster:
` + "```bash" + `
kubectl apply -f templates/cluster-template.yaml
` + "```" + `

## API Reference

| Kind | API Group | Description |
|------|-----------|-------------|
| {{.ClusterKind}} | {{.APIGroup}} | Cluster-level configuration |
| {{.MachineKind}} | {{.APIGroup}} | Machine-level configuration |
| {{.TemplateKind}} | {{.APIGroup}} | Reusable machine template |

## Development

` + "```bash" + `
make generate    # Generate code
make manifests   # Generate CRD manifests
make test        # Run tests
make docker-build # Build container image
` + "```" + `
`

const makefileTmpl = `# Image URL to use all building/pushing image targets
IMG ?= controller:latest
CRD_OPTIONS ?= "crd:generateEmbeddedObjectMeta=true"

# Get the currently used golang install path
GOBIN := $(shell go env GOBIN)
ifeq ($(GOBIN),)
GOBIN := $(shell go env GOPATH)/bin
endif

.PHONY: all
all: build

##@ General
.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

##@ Development
.PHONY: generate
generate: ## Generate code (DeepCopy, etc.)
	controller-gen object:headerFile="hack/boilerplate.go.txt" paths="./..."

.PHONY: manifests
manifests: ## Generate CRD manifests
	controller-gen $(CRD_OPTIONS) rbac:roleName=manager-role webhook paths="./..." output:crd:artifacts:config=config/crd/bases

.PHONY: fmt
fmt: ## Run go fmt
	go fmt ./...

.PHONY: vet
vet: ## Run go vet
	go vet ./...

.PHONY: test
test: generate fmt vet ## Run tests
	go test ./... -coverprofile cover.out

##@ Build
.PHONY: build
build: generate fmt vet ## Build manager binary
	go build -o bin/manager main.go

.PHONY: run
run: generate fmt vet ## Run controller from host
	go run ./main.go

.PHONY: docker-build
docker-build: ## Build docker image
	docker build -t ${IMG} .

.PHONY: docker-push
docker-push: ## Push docker image
	docker push ${IMG}

##@ Deployment
.PHONY: install
install: manifests ## Install CRDs
	kubectl apply -f config/crd/bases/

.PHONY: uninstall
uninstall: manifests ## Uninstall CRDs
	kubectl delete -f config/crd/bases/

.PHONY: deploy
deploy: manifests ## Deploy controller
	kubectl apply -k config/default

.PHONY: undeploy
undeploy: ## Undeploy controller
	kubectl delete -k config/default

##@ Tools
CONTROLLER_GEN = $(GOBIN)/controller-gen
.PHONY: controller-gen
controller-gen:
	go install sigs.k8s.io/controller-tools/cmd/controller-gen@latest
`

const dockerfileTmpl = `# Build stage
FROM golang:1.22 AS builder
WORKDIR /workspace
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -o manager main.go

# Runtime stage
FROM gcr.io/distroless/static:nonroot
WORKDIR /
COPY --from=builder /workspace/manager .
USER 65532:65532
ENTRYPOINT ["/manager"]
`

const goModTmpl = `module {{.Module}}

go 1.22

require (
	k8s.io/api v0.29.0
	k8s.io/apimachinery v0.29.0
	k8s.io/client-go v0.29.0
	sigs.k8s.io/cluster-api v1.6.0
	sigs.k8s.io/controller-runtime v0.17.0
)
`

const mainGoTmpl = `package main

import (
	"flag"
	"os"

	"k8s.io/apimachinery/pkg/runtime"
	utilruntime "k8s.io/apimachinery/pkg/util/runtime"
	clientgoscheme "k8s.io/client-go/kubernetes/scheme"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/healthz"
	"sigs.k8s.io/controller-runtime/pkg/log/zap"

	{{.APIVersion}} "{{.Module}}/api/{{.APIVersion}}"
	"{{.Module}}/controllers"
)

var (
	scheme   = runtime.NewScheme()
	setupLog = ctrl.Log.WithName("setup")
)

func init() {
	utilruntime.Must(clientgoscheme.AddToScheme(scheme))
	utilruntime.Must({{.APIVersion}}.AddToScheme(scheme))
}

func main() {
	var metricsAddr string
	var enableLeaderElection bool
	var probeAddr string

	flag.StringVar(&metricsAddr, "metrics-bind-address", ":8080", "The address for metrics endpoint.")
	flag.StringVar(&probeAddr, "health-probe-bind-address", ":8081", "The address for health probes.")
	flag.BoolVar(&enableLeaderElection, "leader-elect", false, "Enable leader election.")

	opts := zap.Options{Development: true}
	opts.BindFlags(flag.CommandLine)
	flag.Parse()

	ctrl.SetLogger(zap.New(zap.UseFlagOptions(&opts)))

	mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{
		Scheme:                 scheme,
		MetricsBindAddress:     metricsAddr,
		HealthProbeBindAddress: probeAddr,
		LeaderElection:         enableLeaderElection,
		LeaderElectionID:       "{{.Name}}-provider-leader-election",
	})
	if err != nil {
		setupLog.Error(err, "unable to start manager")
		os.Exit(1)
	}

	if err = (&controllers.{{.ClusterKind}}Reconciler{
		Client: mgr.GetClient(),
		Scheme: mgr.GetScheme(),
	}).SetupWithManager(mgr); err != nil {
		setupLog.Error(err, "unable to create controller", "controller", "{{.ClusterKind}}")
		os.Exit(1)
	}

	if err = (&controllers.{{.MachineKind}}Reconciler{
		Client: mgr.GetClient(),
		Scheme: mgr.GetScheme(),
	}).SetupWithManager(mgr); err != nil {
		setupLog.Error(err, "unable to create controller", "controller", "{{.MachineKind}}")
		os.Exit(1)
	}

	if err := mgr.AddHealthzCheck("healthz", healthz.Ping); err != nil {
		setupLog.Error(err, "unable to set up health check")
		os.Exit(1)
	}
	if err := mgr.AddReadyzCheck("readyz", healthz.Ping); err != nil {
		setupLog.Error(err, "unable to set up ready check")
		os.Exit(1)
	}

	setupLog.Info("starting manager")
	if err := mgr.Start(ctrl.SetupSignalHandler()); err != nil {
		setupLog.Error(err, "problem running manager")
		os.Exit(1)
	}
}
`

const clusterTypeTmpl = `package {{.APIVersion}}

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	clusterv1 "sigs.k8s.io/cluster-api/api/v1beta1"
)

// {{.ClusterKind}}Spec defines the desired state of {{.ClusterKind}}.
type {{.ClusterKind}}Spec struct {
	// ControlPlaneEndpoint represents the endpoint for the cluster control plane.
	// +optional
	ControlPlaneEndpoint clusterv1.APIEndpoint ` + "`" + `json:"controlPlaneEndpoint,omitempty"` + "`" + `

	// TODO: Add provider-specific fields here
}

// {{.ClusterKind}}Status defines the observed state of {{.ClusterKind}}.
type {{.ClusterKind}}Status struct {
	// Ready denotes that the infrastructure is ready.
	// +optional
	Ready bool ` + "`" + `json:"ready"` + "`" + `

	// FailureReason indicates a fatal error on the infrastructure.
	// +optional
	FailureReason *string ` + "`" + `json:"failureReason,omitempty"` + "`" + `

	// FailureMessage describes the FailureReason in more detail.
	// +optional
	FailureMessage *string ` + "`" + `json:"failureMessage,omitempty"` + "`" + `

	// Conditions defines current service state of the {{.ClusterKind}}.
	// +optional
	Conditions clusterv1.Conditions ` + "`" + `json:"conditions,omitempty"` + "`" + `
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:printcolumn:name="Ready",type="boolean",JSONPath=".status.ready"
// +kubebuilder:printcolumn:name="Endpoint",type="string",JSONPath=".spec.controlPlaneEndpoint.host"

// {{.ClusterKind}} is the Schema for the {{.Name}} cluster API.
type {{.ClusterKind}} struct {
	metav1.TypeMeta   ` + "`" + `json:",inline"` + "`" + `
	metav1.ObjectMeta ` + "`" + `json:"metadata,omitempty"` + "`" + `

	Spec   {{.ClusterKind}}Spec   ` + "`" + `json:"spec,omitempty"` + "`" + `
	Status {{.ClusterKind}}Status ` + "`" + `json:"status,omitempty"` + "`" + `
}

// +kubebuilder:object:root=true

// {{.ClusterKind}}List contains a list of {{.ClusterKind}}.
type {{.ClusterKind}}List struct {
	metav1.TypeMeta ` + "`" + `json:",inline"` + "`" + `
	metav1.ListMeta ` + "`" + `json:"metadata,omitempty"` + "`" + `
	Items           []{{.ClusterKind}} ` + "`" + `json:"items"` + "`" + `
}

func init() {
	SchemeBuilder.Register(&{{.ClusterKind}}{}, &{{.ClusterKind}}List{})
}
`

const machineTypeTmpl = `package {{.APIVersion}}

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	clusterv1 "sigs.k8s.io/cluster-api/api/v1beta1"
)

// {{.MachineKind}}Spec defines the desired state of {{.MachineKind}}.
type {{.MachineKind}}Spec struct {
	// ProviderID is the unique identifier as specified by the cloud provider.
	// +optional
	ProviderID *string ` + "`" + `json:"providerID,omitempty"` + "`" + `

	// TODO: Add provider-specific fields here
}

// {{.MachineKind}}Status defines the observed state of {{.MachineKind}}.
type {{.MachineKind}}Status struct {
	// Ready denotes that the machine is ready.
	// +optional
	Ready bool ` + "`" + `json:"ready"` + "`" + `

	// Addresses contains the machine's associated addresses.
	// +optional
	Addresses []clusterv1.MachineAddress ` + "`" + `json:"addresses,omitempty"` + "`" + `

	// FailureReason indicates a fatal error on the machine.
	// +optional
	FailureReason *string ` + "`" + `json:"failureReason,omitempty"` + "`" + `

	// FailureMessage describes the FailureReason.
	// +optional
	FailureMessage *string ` + "`" + `json:"failureMessage,omitempty"` + "`" + `

	// Conditions defines current service state.
	// +optional
	Conditions clusterv1.Conditions ` + "`" + `json:"conditions,omitempty"` + "`" + `
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:printcolumn:name="Ready",type="boolean",JSONPath=".status.ready"
// +kubebuilder:printcolumn:name="ProviderID",type="string",JSONPath=".spec.providerID"

// {{.MachineKind}} is the Schema for the {{.Name}} machine API.
type {{.MachineKind}} struct {
	metav1.TypeMeta   ` + "`" + `json:",inline"` + "`" + `
	metav1.ObjectMeta ` + "`" + `json:"metadata,omitempty"` + "`" + `

	Spec   {{.MachineKind}}Spec   ` + "`" + `json:"spec,omitempty"` + "`" + `
	Status {{.MachineKind}}Status ` + "`" + `json:"status,omitempty"` + "`" + `
}

// +kubebuilder:object:root=true

// {{.MachineKind}}List contains a list of {{.MachineKind}}.
type {{.MachineKind}}List struct {
	metav1.TypeMeta ` + "`" + `json:",inline"` + "`" + `
	metav1.ListMeta ` + "`" + `json:"metadata,omitempty"` + "`" + `
	Items           []{{.MachineKind}} ` + "`" + `json:"items"` + "`" + `
}

func init() {
	SchemeBuilder.Register(&{{.MachineKind}}{}, &{{.MachineKind}}List{})
}
`

const templateTypeTmpl = `package {{.APIVersion}}

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// {{.TemplateKind}}Resource describes the data for the {{.MachineKind}} template.
type {{.TemplateKind}}Resource struct {
	// Spec is the {{.MachineKind}}Spec for the template.
	Spec {{.MachineKind}}Spec ` + "`" + `json:"spec"` + "`" + `
}

// {{.TemplateKind}}Spec defines the desired state of {{.TemplateKind}}.
type {{.TemplateKind}}Spec struct {
	Template {{.TemplateKind}}Resource ` + "`" + `json:"template"` + "`" + `
}

// +kubebuilder:object:root=true

// {{.TemplateKind}} is the Schema for the {{.Name}} machine template API.
type {{.TemplateKind}} struct {
	metav1.TypeMeta   ` + "`" + `json:",inline"` + "`" + `
	metav1.ObjectMeta ` + "`" + `json:"metadata,omitempty"` + "`" + `

	Spec {{.TemplateKind}}Spec ` + "`" + `json:"spec,omitempty"` + "`" + `
}

// +kubebuilder:object:root=true

// {{.TemplateKind}}List contains a list of {{.TemplateKind}}.
type {{.TemplateKind}}List struct {
	metav1.TypeMeta ` + "`" + `json:",inline"` + "`" + `
	metav1.ListMeta ` + "`" + `json:"metadata,omitempty"` + "`" + `
	Items           []{{.TemplateKind}} ` + "`" + `json:"items"` + "`" + `
}

func init() {
	SchemeBuilder.Register(&{{.TemplateKind}}{}, &{{.TemplateKind}}List{})
}
`

const groupVersionInfoTmpl = `// Package {{.APIVersion}} contains API Schema definitions for the {{.APIGroup}} API group.
// +kubebuilder:object:generate=true
// +groupName={{.APIGroup}}
package {{.APIVersion}}

import (
	"k8s.io/apimachinery/pkg/runtime/schema"
	"sigs.k8s.io/controller-runtime/pkg/scheme"
)

var (
	// GroupVersion is group version used to register these objects.
	GroupVersion = schema.GroupVersion{Group: "{{.APIGroup}}", Version: "{{.APIVersion}}"}

	// SchemeBuilder is used to add go types to the GroupVersionResource scheme.
	SchemeBuilder = &scheme.Builder{GroupVersion: GroupVersion}

	// AddToScheme adds the types in this group-version to the given scheme.
	AddToScheme = SchemeBuilder.AddToScheme
)
`

const clusterControllerTmpl = `package controllers

import (
	"context"

	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
	"sigs.k8s.io/controller-runtime/pkg/log"

	{{.APIVersion}} "{{.Module}}/api/{{.APIVersion}}"
)

// {{.ClusterKind}}Reconciler reconciles a {{.ClusterKind}} object.
type {{.ClusterKind}}Reconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

// +kubebuilder:rbac:groups={{.APIGroup}},resources={{.Name}}clusters,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups={{.APIGroup}},resources={{.Name}}clusters/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=cluster.x-k8s.io,resources=clusters;clusters/status,verbs=get;list;watch

func (r *{{.ClusterKind}}Reconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := log.FromContext(ctx)

	// Fetch the {{.ClusterKind}} instance
	{{.Name}}Cluster := &{{.APIVersion}}.{{.ClusterKind}}{}
	if err := r.Get(ctx, req.NamespacedName, {{.Name}}Cluster); err != nil {
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	log.Info("Reconciling {{.ClusterKind}}", "name", {{.Name}}Cluster.Name)

	// Add finalizer
	if !controllerutil.ContainsFinalizer({{.Name}}Cluster, "{{.APIGroup}}/cluster") {
		controllerutil.AddFinalizer({{.Name}}Cluster, "{{.APIGroup}}/cluster")
		if err := r.Update(ctx, {{.Name}}Cluster); err != nil {
			return ctrl.Result{}, err
		}
	}

	// Handle deletion
	if !{{.Name}}Cluster.DeletionTimestamp.IsZero() {
		return r.reconcileDelete(ctx, {{.Name}}Cluster)
	}

	return r.reconcileNormal(ctx, {{.Name}}Cluster)
}

func (r *{{.ClusterKind}}Reconciler) reconcileNormal(ctx context.Context, cluster *{{.APIVersion}}.{{.ClusterKind}}) (ctrl.Result, error) {
	log := log.FromContext(ctx)
	log.Info("Reconciling {{.ClusterKind}} (normal)")

	// TODO: Implement provider-specific cluster provisioning logic

	// Mark cluster as ready
	cluster.Status.Ready = true
	if err := r.Status().Update(ctx, cluster); err != nil {
		return ctrl.Result{}, err
	}

	return ctrl.Result{}, nil
}

func (r *{{.ClusterKind}}Reconciler) reconcileDelete(ctx context.Context, cluster *{{.APIVersion}}.{{.ClusterKind}}) (ctrl.Result, error) {
	log := log.FromContext(ctx)
	log.Info("Reconciling {{.ClusterKind}} (delete)")

	// TODO: Implement provider-specific cluster deletion logic

	controllerutil.RemoveFinalizer(cluster, "{{.APIGroup}}/cluster")
	if err := r.Update(ctx, cluster); err != nil {
		return ctrl.Result{}, err
	}

	return ctrl.Result{}, nil
}

func (r *{{.ClusterKind}}Reconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&{{.APIVersion}}.{{.ClusterKind}}{}).
		Complete(r)
}
`

const machineControllerTmpl = `package controllers

import (
	"context"

	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
	"sigs.k8s.io/controller-runtime/pkg/log"

	{{.APIVersion}} "{{.Module}}/api/{{.APIVersion}}"
)

// {{.MachineKind}}Reconciler reconciles a {{.MachineKind}} object.
type {{.MachineKind}}Reconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

// +kubebuilder:rbac:groups={{.APIGroup}},resources={{.Name}}machines,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups={{.APIGroup}},resources={{.Name}}machines/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=cluster.x-k8s.io,resources=machines;machines/status,verbs=get;list;watch

func (r *{{.MachineKind}}Reconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := log.FromContext(ctx)

	// Fetch the {{.MachineKind}} instance
	{{.Name}}Machine := &{{.APIVersion}}.{{.MachineKind}}{}
	if err := r.Get(ctx, req.NamespacedName, {{.Name}}Machine); err != nil {
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	log.Info("Reconciling {{.MachineKind}}", "name", {{.Name}}Machine.Name)

	// Add finalizer
	if !controllerutil.ContainsFinalizer({{.Name}}Machine, "{{.APIGroup}}/machine") {
		controllerutil.AddFinalizer({{.Name}}Machine, "{{.APIGroup}}/machine")
		if err := r.Update(ctx, {{.Name}}Machine); err != nil {
			return ctrl.Result{}, err
		}
	}

	// Handle deletion
	if !{{.Name}}Machine.DeletionTimestamp.IsZero() {
		return r.reconcileDelete(ctx, {{.Name}}Machine)
	}

	return r.reconcileNormal(ctx, {{.Name}}Machine)
}

func (r *{{.MachineKind}}Reconciler) reconcileNormal(ctx context.Context, machine *{{.APIVersion}}.{{.MachineKind}}) (ctrl.Result, error) {
	log := log.FromContext(ctx)
	log.Info("Reconciling {{.MachineKind}} (normal)")

	// TODO: Implement provider-specific machine provisioning logic
	// 1. Create/ensure infrastructure (VM, bare-metal, etc.)
	// 2. Set ProviderID
	// 3. Mark as ready

	machine.Status.Ready = true
	if err := r.Status().Update(ctx, machine); err != nil {
		return ctrl.Result{}, err
	}

	return ctrl.Result{}, nil
}

func (r *{{.MachineKind}}Reconciler) reconcileDelete(ctx context.Context, machine *{{.APIVersion}}.{{.MachineKind}}) (ctrl.Result, error) {
	log := log.FromContext(ctx)
	log.Info("Reconciling {{.MachineKind}} (delete)")

	// TODO: Implement provider-specific machine deletion logic

	controllerutil.RemoveFinalizer(machine, "{{.APIGroup}}/machine")
	if err := r.Update(ctx, machine); err != nil {
		return ctrl.Result{}, err
	}

	return ctrl.Result{}, nil
}

func (r *{{.MachineKind}}Reconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&{{.APIVersion}}.{{.MachineKind}}{}).
		Complete(r)
}
`

const kustomizationTmpl = `apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: {{.Name}}-system

resources:
- ../crd
- ../rbac
- ../manager

namePrefix: {{.Name}}-
`

const managerKustomizeTmpl = `apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- manager.yaml
`

const managerDeploymentTmpl = `apiVersion: apps/v1
kind: Deployment
metadata:
  name: controller-manager
  namespace: system
  labels:
    control-plane: controller-manager
spec:
  selector:
    matchLabels:
      control-plane: controller-manager
  replicas: 1
  template:
    metadata:
      labels:
        control-plane: controller-manager
    spec:
      containers:
      - name: manager
        image: controller:latest
        args:
        - "--leader-elect"
        - "--metrics-bind-address=:8080"
        - "--health-probe-bind-address=:8081"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8081
          initialDelaySeconds: 15
          periodSeconds: 20
        readinessProbe:
          httpGet:
            path: /readyz
            port: 8081
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          limits:
            cpu: 500m
            memory: 128Mi
          requests:
            cpu: 10m
            memory: 64Mi
      terminationGracePeriodSeconds: 10
      serviceAccountName: controller-manager
`

const rbacKustomizeTmpl = `apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- role.yaml
- role_binding.yaml
- service_account.yaml
`

const serviceAccountTmpl = `apiVersion: v1
kind: ServiceAccount
metadata:
  name: controller-manager
  namespace: system
`

const clusterRoleTmpl = `apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: manager-role
rules:
- apiGroups: ["{{.APIGroup}}"]
  resources: ["*"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["cluster.x-k8s.io"]
  resources: ["clusters", "machines"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list", "watch"]
`

const clusterRoleBindingTmpl = `apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: manager-rolebinding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: manager-role
subjects:
- kind: ServiceAccount
  name: controller-manager
  namespace: system
`

const crdKustomizeTmpl = `apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- bases/
`

const boilerplateTmpl = `/*
Copyright 2024.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
*/
`

const clusterTemplateTmpl = `apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  name: ${CLUSTER_NAME}
  namespace: ${NAMESPACE}
spec:
  clusterNetwork:
    pods:
      cidrBlocks: ["192.168.0.0/16"]
    services:
      cidrBlocks: ["10.128.0.0/12"]
  infrastructureRef:
    apiVersion: {{.APIGroup}}/{{.APIVersion}}
    kind: {{.ClusterKind}}
    name: ${CLUSTER_NAME}
  controlPlaneRef:
    apiVersion: controlplane.cluster.x-k8s.io/v1beta1
    kind: KubeadmControlPlane
    name: ${CLUSTER_NAME}-control-plane
---
apiVersion: {{.APIGroup}}/{{.APIVersion}}
kind: {{.ClusterKind}}
metadata:
  name: ${CLUSTER_NAME}
  namespace: ${NAMESPACE}
spec: {}
---
apiVersion: controlplane.cluster.x-k8s.io/v1beta1
kind: KubeadmControlPlane
metadata:
  name: ${CLUSTER_NAME}-control-plane
  namespace: ${NAMESPACE}
spec:
  replicas: ${CONTROL_PLANE_MACHINE_COUNT}
  version: ${KUBERNETES_VERSION}
  machineTemplate:
    infrastructureRef:
      apiVersion: {{.APIGroup}}/{{.APIVersion}}
      kind: {{.TemplateKind}}
      name: ${CLUSTER_NAME}-control-plane
  kubeadmConfigSpec:
    initConfiguration:
      nodeRegistration:
        kubeletExtraArgs: {}
    joinConfiguration:
      nodeRegistration:
        kubeletExtraArgs: {}
`

func scaffold(cfg *providerConfig) {
	data := newTemplateData(cfg)
	dir := cfg.OutputDir

	// Files to generate
	files := map[string]string{
		"README.md":                               renderTemplate("readme", readmeTmpl, data),
		"Makefile":                                 renderTemplate("makefile", makefileTmpl, data),
		"Dockerfile":                               renderTemplate("dockerfile", dockerfileTmpl, data),
		"go.mod":                                   renderTemplate("go.mod", goModTmpl, data),
		"main.go":                                  renderTemplate("main.go", mainGoTmpl, data),
		"api/" + cfg.APIVersion + "/groupversion_info.go":   renderTemplate("gv", groupVersionInfoTmpl, data),
		"api/" + cfg.APIVersion + "/cluster_types.go":       renderTemplate("cluster_types", clusterTypeTmpl, data),
		"api/" + cfg.APIVersion + "/machine_types.go":       renderTemplate("machine_types", machineTypeTmpl, data),
		"api/" + cfg.APIVersion + "/template_types.go":      renderTemplate("template_types", templateTypeTmpl, data),
		"controllers/cluster_controller.go":         renderTemplate("cluster_ctrl", clusterControllerTmpl, data),
		"controllers/machine_controller.go":         renderTemplate("machine_ctrl", machineControllerTmpl, data),
		"config/default/kustomization.yaml":         renderTemplate("kustomize", kustomizationTmpl, data),
		"config/manager/kustomization.yaml":         renderTemplate("mgr_kust", managerKustomizeTmpl, data),
		"config/manager/manager.yaml":               renderTemplate("mgr_deploy", managerDeploymentTmpl, data),
		"config/rbac/kustomization.yaml":            renderTemplate("rbac_kust", rbacKustomizeTmpl, data),
		"config/rbac/service_account.yaml":           renderTemplate("sa", serviceAccountTmpl, data),
		"config/rbac/role.yaml":                     renderTemplate("role", clusterRoleTmpl, data),
		"config/rbac/role_binding.yaml":              renderTemplate("role_binding", clusterRoleBindingTmpl, data),
		"config/crd/kustomization.yaml":             renderTemplate("crd_kust", crdKustomizeTmpl, data),
		"hack/boilerplate.go.txt":                   renderTemplate("boilerplate", boilerplateTmpl, data),
		"templates/cluster-template.yaml":           renderTemplate("cluster_tmpl", clusterTemplateTmpl, data),
	}

	created := 0
	for relPath, content := range files {
		fullPath := filepath.Join(dir, relPath)
		if err := writeFile(fullPath, content); err != nil {
			fmt.Fprintf(os.Stderr, "Error creating %s: %v\n", relPath, err)
			continue
		}
		created++
	}

	fmt.Printf("\n✅ Provider scaffold created: %s\n", dir)
	fmt.Printf("   Files created: %d\n", created)
	fmt.Printf("   Module: %s\n", cfg.Module)
	fmt.Printf("   API Group: %s\n", cfg.APIGroup)
	fmt.Printf("   Types: %s, %s, %s\n", cfg.ClusterKind, cfg.MachineKind, cfg.TemplateKind)

	fmt.Println("\nNext steps:")
	fmt.Println("  1. cd", dir)
	fmt.Println("  2. go mod tidy")
	fmt.Println("  3. make generate  # Generate DeepCopy methods")
	fmt.Println("  4. make manifests # Generate CRD YAML")
	fmt.Println("  5. Implement TODO sections in controllers/")
}

func main() {
	name := flag.String("n", "", "Provider name (e.g., 'mycloud')")
	provType := flag.String("t", "infrastructure", "Provider type: infrastructure, bootstrap, controlplane")
	module := flag.String("module", "", "Go module path (default: auto-generated)")
	outputDir := flag.String("output-dir", "", "Output directory (default: auto-generated)")
	apiVersion := flag.String("api-version", "v1beta1", "API version")

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "CAPI Provider Scaffolding Tool\nUsage: %s [flags]\n\nFlags:\n", os.Args[0])
		flag.PrintDefaults()
		fmt.Fprintf(os.Stderr, "\nExamples:\n")
		fmt.Fprintf(os.Stderr, "  %s -n mycloud -t infrastructure\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "  %s -n mycloud -t bootstrap --module github.com/org/capi-bootstrap-mycloud\n", os.Args[0])
	}
	flag.Parse()

	if *name == "" {
		fmt.Fprintln(os.Stderr, "Error: -n (provider name) is required")
		flag.Usage()
		os.Exit(1)
	}

	validTypes := map[string]bool{"infrastructure": true, "bootstrap": true, "controlplane": true}
	if !validTypes[*provType] {
		fmt.Fprintf(os.Stderr, "Error: invalid provider type: %s\n", *provType)
		os.Exit(1)
	}

	cfg := defaultConfig(*name, *provType)
	cfg.APIVersion = *apiVersion

	if *module != "" {
		cfg.Module = *module
	}

	if *outputDir != "" {
		cfg.OutputDir = *outputDir
	} else {
		var prefix string
		switch *provType {
		case "infrastructure":
			prefix = "cluster-api-provider-"
		case "bootstrap":
			prefix = "cluster-api-bootstrap-provider-"
		case "controlplane":
			prefix = "cluster-api-controlplane-provider-"
		}
		cfg.OutputDir = prefix + *name
	}

	scaffold(cfg)
}
