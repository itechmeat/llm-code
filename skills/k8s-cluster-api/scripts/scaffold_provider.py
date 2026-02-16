#!/usr/bin/env python3
"""Scaffold a new Cluster API provider structure.

This script generates the basic directory structure and boilerplate files
for a new CAPI infrastructure, bootstrap, or control plane provider.

Usage:
    python scaffold_provider.py <provider-name> [--type infra|bootstrap|controlplane]

Examples:
    python scaffold_provider.py myprovider --type infra
    python scaffold_provider.py mycloud --type infra --output ./cluster-api-provider-mycloud
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any


# Provider type configurations
PROVIDER_CONFIGS = {
    "infra": {
        "short": "infra",
        "long": "infrastructure",
        "api_group": "infrastructure.cluster.x-k8s.io",
        "kinds": ["Cluster", "Machine", "MachineTemplate", "ClusterTemplate"],
        "controller_kinds": ["Cluster", "Machine"],
    },
    "bootstrap": {
        "short": "bootstrap",
        "long": "bootstrap",
        "api_group": "bootstrap.cluster.x-k8s.io",
        "kinds": ["Config", "ConfigTemplate"],
        "controller_kinds": ["Config"],
    },
    "controlplane": {
        "short": "controlplane",
        "long": "controlplane",
        "api_group": "controlplane.cluster.x-k8s.io",
        "kinds": ["ControlPlane", "ControlPlaneTemplate"],
        "controller_kinds": ["ControlPlane"],
    },
}


def create_file(path: Path, content: str) -> None:
    """Create file with content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")


def generate_structure(
    name: str,
    provider_type: str,
    output_dir: Path,
) -> None:
    """Generate provider directory structure."""
    config = PROVIDER_CONFIGS[provider_type]
    provider_name = name.lower()
    provider_name_cap = name.capitalize()
    short_type = config["short"]

    print(f"\nScaffolding {config['long']} provider: {provider_name}")
    print(f"Output directory: {output_dir}")
    print("-" * 50)

    # Root files
    create_file(
        output_dir / "README.md",
        f"""# Cluster API Provider {provider_name_cap}

Kubernetes Cluster API {config['long']} provider for {provider_name_cap}.

## Description

This provider enables Cluster API to provision and manage Kubernetes clusters
on {provider_name_cap}.

## Quick Start

```bash
# Initialize the management cluster with this provider
clusterctl init --{short_type} {provider_name}

# Generate a cluster template
clusterctl generate cluster my-cluster \\
  --{short_type} {provider_name} \\
  --target-namespace default
```

## Development

```bash
# Run tests
make test

# Build manager
make build

# Run locally
make run
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [Configuration](docs/configuration.md)

## License

Apache License 2.0
""",
    )

    create_file(
        output_dir / "Makefile",
        f"""# Makefile for {provider_name} provider

IMG ?= ghcr.io/example/cluster-api-provider-{provider_name}:dev
KUBEBUILDER_VERSION ?= 3.11.0

.PHONY: all build test run generate manifests install deploy

all: build

build:
\tgo build -o bin/manager ./main.go

test:
\tgo test ./... -coverprofile cover.out

run: generate
\tgo run ./main.go

generate: controller-gen
\t$(CONTROLLER_GEN) object:headerFile="hack/boilerplate.go.txt" paths="./..."

manifests: controller-gen
\t$(CONTROLLER_GEN) rbac:roleName=manager-role crd webhook paths="./..." output:crd:artifacts:config=config/crd/bases

install: manifests
\tkubectl apply -f config/crd/bases

deploy: manifests
\tkustomize build config/default | kubectl apply -f -

docker-build:
\tdocker build -t $(IMG) .

docker-push:
\tdocker push $(IMG)

CONTROLLER_GEN = $(shell pwd)/bin/controller-gen
controller-gen:
\ttest -s $(CONTROLLER_GEN) || GOBIN=$(shell pwd)/bin go install sigs.k8s.io/controller-tools/cmd/controller-gen@latest
""",
    )

    create_file(
        output_dir / "Dockerfile",
        f"""# Build the manager binary
FROM golang:1.21 as builder
ARG TARGETOS
ARG TARGETARCH

WORKDIR /workspace
COPY go.mod go.sum ./
RUN go mod download

COPY ./ ./
RUN CGO_ENABLED=0 GOOS=${{TARGETOS:-linux}} GOARCH=${{TARGETARCH:-amd64}} go build -a -o manager main.go

FROM gcr.io/distroless/static:nonroot
WORKDIR /
COPY --from=builder /workspace/manager .
USER 65532:65532

ENTRYPOINT ["/manager"]
""",
    )

    create_file(
        output_dir / "go.mod",
        f"""module github.com/example/cluster-api-provider-{provider_name}

go 1.21

require (
\tk8s.io/api v0.28.0
\tk8s.io/apimachinery v0.28.0
\tk8s.io/client-go v0.28.0
\tsigs.k8s.io/cluster-api v1.6.0
\tsigs.k8s.io/controller-runtime v0.16.0
)
""",
    )

    # API types
    api_base = output_dir / f"api/{short_type}/v1beta1"

    create_file(
        api_base / "doc.go",
        f"""// Package v1beta1 contains API Schema definitions for the {config['long']} v1beta1 API group.
// +kubebuilder:object:generate=true
// +groupName={config['api_group']}
package v1beta1
""",
    )

    create_file(
        api_base / "groupversion_info.go",
        f"""package v1beta1

import (
\t"k8s.io/apimachinery/pkg/runtime/schema"
\t"sigs.k8s.io/controller-runtime/pkg/scheme"
)

var (
\tGroupVersion = schema.GroupVersion{{Group: "{config['api_group']}", Version: "v1beta1"}}
\tSchemeBuilder = &scheme.Builder{{GroupVersion: GroupVersion}}
\tAddToScheme = SchemeBuilder.AddToScheme
)
""",
    )

    # Generate type files for each kind
    for kind in config["kinds"]:
        kind_lower = kind.lower()
        kind_file = f"{provider_name}_{kind_lower}_types.go"

        if kind == "Cluster":
            create_file(
                api_base / kind_file,
                generate_cluster_types(provider_name, provider_name_cap, config),
            )
        elif kind == "Machine":
            create_file(
                api_base / kind_file,
                generate_machine_types(provider_name, provider_name_cap, config),
            )
        elif "Template" in kind:
            create_file(
                api_base / kind_file,
                generate_template_types(provider_name, provider_name_cap, kind, config),
            )
        else:
            create_file(
                api_base / kind_file,
                generate_generic_types(provider_name, provider_name_cap, kind, config),
            )

    # Controllers
    controller_base = output_dir / f"controllers/{short_type}"

    for kind in config["controller_kinds"]:
        kind_lower = kind.lower()
        create_file(
            controller_base / f"{provider_name}_{kind_lower}_controller.go",
            generate_controller(provider_name, provider_name_cap, kind, config),
        )

    # Main entry point
    create_file(
        output_dir / "main.go",
        generate_main(provider_name, provider_name_cap, config),
    )

    # Config/kustomize
    create_file(
        output_dir / "config/default/kustomization.yaml",
        f"""apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: {provider_name}-system
resources:
- ../crd
- ../rbac
- ../manager
""",
    )

    create_file(
        output_dir / "config/crd/kustomization.yaml",
        """apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- bases/
""",
    )

    create_file(
        output_dir / "config/manager/manager.yaml",
        f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: controller-manager
  namespace: {provider_name}-system
spec:
  replicas: 1
  selector:
    matchLabels:
      control-plane: controller-manager
  template:
    metadata:
      labels:
        control-plane: controller-manager
    spec:
      containers:
      - name: manager
        image: ghcr.io/example/cluster-api-provider-{provider_name}:latest
        args:
        - --leader-elect
        resources:
          limits:
            cpu: 500m
            memory: 128Mi
          requests:
            cpu: 10m
            memory: 64Mi
""",
    )

    # Hack directory
    create_file(
        output_dir / "hack/boilerplate.go.txt",
        f"""/*
Copyright {os.environ.get('USER', 'Authors')}.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/
""",
    )

    # Templates
    templates_dir = output_dir / "templates"
    create_file(
        templates_dir / "cluster-template.yaml",
        generate_cluster_template(provider_name, provider_name_cap, config),
    )

    print("-" * 50)
    print(f"\n✓ Provider scaffold complete!")
    print(f"\nNext steps:")
    print(f"  1. cd {output_dir}")
    print(f"  2. go mod tidy")
    print(f"  3. make generate manifests")
    print(f"  4. Implement controller logic in controllers/{short_type}/")
    print(f"  5. make test && make build")


def generate_cluster_types(name: str, name_cap: str, config: dict) -> str:
    """Generate cluster types file."""
    return f"""package v1beta1

import (
\tmetav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
\tclusterv1 "sigs.k8s.io/cluster-api/api/v1beta1"
)

// {name_cap}ClusterSpec defines the desired state of {name_cap}Cluster.
type {name_cap}ClusterSpec struct {{
\t// ControlPlaneEndpoint represents the endpoint used to communicate with the control plane.
\t// +optional
\tControlPlaneEndpoint clusterv1.APIEndpoint `json:"controlPlaneEndpoint"`

\t// Region is the region to deploy the cluster.
\t// +kubebuilder:validation:Required
\tRegion string `json:"region"`

\t// NetworkSpec defines the network configuration.
\t// +optional
\tNetworkSpec NetworkSpec `json:"networkSpec,omitempty"`
}}

// NetworkSpec defines network configuration.
type NetworkSpec struct {{
\t// VPC configuration.
\t// +optional
\tVPC VPCSpec `json:"vpc,omitempty"`
}}

// VPCSpec defines VPC configuration.
type VPCSpec struct {{
\t// ID is an existing VPC ID.
\t// +optional
\tID string `json:"id,omitempty"`

\t// CIDR block for the VPC.
\t// +optional
\tCIDRBlock string `json:"cidrBlock,omitempty"`
}}

// {name_cap}ClusterStatus defines the observed state of {name_cap}Cluster.
type {name_cap}ClusterStatus struct {{
\t// Ready denotes that the cluster is ready.
\tReady bool `json:"ready"`

\t// FailureReason indicates a fatal error during cluster reconciliation.
\t// +optional
\tFailureReason *string `json:"failureReason,omitempty"`

\t// FailureMessage provides more detail for FailureReason.
\t// +optional
\tFailureMessage *string `json:"failureMessage,omitempty"`

\t// Conditions defines current service state of the cluster.
\t// +optional
\tConditions clusterv1.Conditions `json:"conditions,omitempty"`
}}

//+kubebuilder:object:root=true
//+kubebuilder:subresource:status
//+kubebuilder:resource:path={name}clusters,scope=Namespaced,categories=cluster-api
//+kubebuilder:printcolumn:name="Ready",type="boolean",JSONPath=".status.ready"
//+kubebuilder:printcolumn:name="Endpoint",type="string",JSONPath=".spec.controlPlaneEndpoint.host"

// {name_cap}Cluster is the Schema for the {name}clusters API.
type {name_cap}Cluster struct {{
\tmetav1.TypeMeta   `json:",inline"`
\tmetav1.ObjectMeta `json:"metadata,omitempty"`

\tSpec   {name_cap}ClusterSpec   `json:"spec,omitempty"`
\tStatus {name_cap}ClusterStatus `json:"status,omitempty"`
}}

//+kubebuilder:object:root=true

// {name_cap}ClusterList contains a list of {name_cap}Cluster.
type {name_cap}ClusterList struct {{
\tmetav1.TypeMeta `json:",inline"`
\tmetav1.ListMeta `json:"metadata,omitempty"`
\tItems           []{name_cap}Cluster `json:"items"`
}}

func init() {{
\tSchemeBuilder.Register(&{name_cap}Cluster{{}}, &{name_cap}ClusterList{{}})
}}

// GetConditions returns the conditions for the {name_cap}Cluster.
func (c *{name_cap}Cluster) GetConditions() clusterv1.Conditions {{
\treturn c.Status.Conditions
}}

// SetConditions sets the conditions for the {name_cap}Cluster.
func (c *{name_cap}Cluster) SetConditions(conditions clusterv1.Conditions) {{
\tc.Status.Conditions = conditions
}}
"""


def generate_machine_types(name: str, name_cap: str, config: dict) -> str:
    """Generate machine types file."""
    return f"""package v1beta1

import (
\tcorev1 "k8s.io/api/core/v1"
\tmetav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
\tclusterv1 "sigs.k8s.io/cluster-api/api/v1beta1"
)

// {name_cap}MachineSpec defines the desired state of {name_cap}Machine.
type {name_cap}MachineSpec struct {{
\t// ProviderID is the unique identifier as specified by the cloud provider.
\t// +optional
\tProviderID *string `json:"providerID,omitempty"`

\t// InstanceType is the machine instance type.
\t// +kubebuilder:validation:Required
\tInstanceType string `json:"instanceType"`

\t// ImageID is the OS image to use.
\t// +optional
\tImageID string `json:"imageID,omitempty"`

\t// SSHKeyName is the name of the SSH key pair.
\t// +optional
\tSSHKeyName string `json:"sshKeyName,omitempty"`

\t// RootVolume defines root disk.
\t// +optional
\tRootVolume *Volume `json:"rootVolume,omitempty"`
}}

// Volume defines a disk volume.
type Volume struct {{
\t// Size in GiB.
\tSize int64 `json:"size"`

\t// Type of the disk.
\t// +optional
\tType string `json:"type,omitempty"`
}}

// {name_cap}MachineStatus defines the observed state of {name_cap}Machine.
type {name_cap}MachineStatus struct {{
\t// Ready is true when the provider resource is ready.
\tReady bool `json:"ready"`

\t// InstanceState is the state of the instance.
\t// +optional
\tInstanceState *string `json:"instanceState,omitempty"`

\t// Addresses contains the addresses assigned to the machine.
\t// +optional
\tAddresses []corev1.NodeAddress `json:"addresses,omitempty"`

\t// FailureReason indicates a fatal error.
\t// +optional
\tFailureReason *string `json:"failureReason,omitempty"`

\t// FailureMessage provides detail.
\t// +optional
\tFailureMessage *string `json:"failureMessage,omitempty"`

\t// Conditions defines current state.
\t// +optional
\tConditions clusterv1.Conditions `json:"conditions,omitempty"`
}}

//+kubebuilder:object:root=true
//+kubebuilder:subresource:status
//+kubebuilder:resource:path={name}machines,scope=Namespaced,categories=cluster-api
//+kubebuilder:printcolumn:name="Ready",type="boolean",JSONPath=".status.ready"
//+kubebuilder:printcolumn:name="ProviderID",type="string",JSONPath=".spec.providerID"

// {name_cap}Machine is the Schema for the {name}machines API.
type {name_cap}Machine struct {{
\tmetav1.TypeMeta   `json:",inline"`
\tmetav1.ObjectMeta `json:"metadata,omitempty"`

\tSpec   {name_cap}MachineSpec   `json:"spec,omitempty"`
\tStatus {name_cap}MachineStatus `json:"status,omitempty"`
}}

//+kubebuilder:object:root=true

// {name_cap}MachineList contains a list of {name_cap}Machine.
type {name_cap}MachineList struct {{
\tmetav1.TypeMeta `json:",inline"`
\tmetav1.ListMeta `json:"metadata,omitempty"`
\tItems           []{name_cap}Machine `json:"items"`
}}

func init() {{
\tSchemeBuilder.Register(&{name_cap}Machine{{}}, &{name_cap}MachineList{{}})
}}

// GetConditions returns the conditions.
func (m *{name_cap}Machine) GetConditions() clusterv1.Conditions {{
\treturn m.Status.Conditions
}}

// SetConditions sets the conditions.
func (m *{name_cap}Machine) SetConditions(conditions clusterv1.Conditions) {{
\tm.Status.Conditions = conditions
}}
"""


def generate_template_types(name: str, name_cap: str, kind: str, config: dict) -> str:
    """Generate template types file."""
    kind_lower = kind.lower()
    base_kind = kind.replace("Template", "")
    return f"""package v1beta1

import (
\tmetav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// {name_cap}{kind}Spec defines the desired state of {name_cap}{kind}.
type {name_cap}{kind}Spec struct {{
\tTemplate {name_cap}{base_kind}TemplateResource `json:"template"`
}}

// {name_cap}{base_kind}TemplateResource defines the template structure.
type {name_cap}{base_kind}TemplateResource struct {{
\t// Standard object's metadata.
\t// +optional
\tmetav1.ObjectMeta `json:"metadata,omitempty"`

\t// Spec defines the desired state.
\tSpec {name_cap}{base_kind}Spec `json:"spec"`
}}

//+kubebuilder:object:root=true
//+kubebuilder:resource:path={name}{kind_lower}s,scope=Namespaced,categories=cluster-api

// {name_cap}{kind} is the Schema for the {name}{kind_lower}s API.
type {name_cap}{kind} struct {{
\tmetav1.TypeMeta   `json:",inline"`
\tmetav1.ObjectMeta `json:"metadata,omitempty"`

\tSpec {name_cap}{kind}Spec `json:"spec,omitempty"`
}}

//+kubebuilder:object:root=true

// {name_cap}{kind}List contains a list of {name_cap}{kind}.
type {name_cap}{kind}List struct {{
\tmetav1.TypeMeta `json:",inline"`
\tmetav1.ListMeta `json:"metadata,omitempty"`
\tItems           []{name_cap}{kind} `json:"items"`
}}

func init() {{
\tSchemeBuilder.Register(&{name_cap}{kind}{{}}, &{name_cap}{kind}List{{}})
}}
"""


def generate_generic_types(name: str, name_cap: str, kind: str, config: dict) -> str:
    """Generate generic types file for non-standard kinds."""
    kind_lower = kind.lower()
    return f"""package v1beta1

import (
\tmetav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
\tclusterv1 "sigs.k8s.io/cluster-api/api/v1beta1"
)

// {name_cap}{kind}Spec defines the desired state of {name_cap}{kind}.
type {name_cap}{kind}Spec struct {{
\t// Add provider-specific fields here
}}

// {name_cap}{kind}Status defines the observed state of {name_cap}{kind}.
type {name_cap}{kind}Status struct {{
\t// Ready denotes readiness.
\tReady bool `json:"ready"`

\t// Conditions defines current state.
\t// +optional
\tConditions clusterv1.Conditions `json:"conditions,omitempty"`
}}

//+kubebuilder:object:root=true
//+kubebuilder:subresource:status
//+kubebuilder:resource:path={name}{kind_lower}s,scope=Namespaced,categories=cluster-api

// {name_cap}{kind} is the Schema for the {name}{kind_lower}s API.
type {name_cap}{kind} struct {{
\tmetav1.TypeMeta   `json:",inline"`
\tmetav1.ObjectMeta `json:"metadata,omitempty"`

\tSpec   {name_cap}{kind}Spec   `json:"spec,omitempty"`
\tStatus {name_cap}{kind}Status `json:"status,omitempty"`
}}

//+kubebuilder:object:root=true

// {name_cap}{kind}List contains a list of {name_cap}{kind}.
type {name_cap}{kind}List struct {{
\tmetav1.TypeMeta `json:",inline"`
\tmetav1.ListMeta `json:"metadata,omitempty"`
\tItems           []{name_cap}{kind} `json:"items"`
}}

func init() {{
\tSchemeBuilder.Register(&{name_cap}{kind}{{}}, &{name_cap}{kind}List{{}})
}}
"""


def generate_controller(name: str, name_cap: str, kind: str, config: dict) -> str:
    """Generate controller file."""
    kind_lower = kind.lower()
    short_type = config["short"]
    return f"""package {short_type}

import (
\t"context"

\t"github.com/go-logr/logr"
\t"k8s.io/apimachinery/pkg/runtime"
\tctrl "sigs.k8s.io/controller-runtime"
\t"sigs.k8s.io/controller-runtime/pkg/client"
\t"sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"

\t{short_type}v1beta1 "github.com/example/cluster-api-provider-{name}/api/{short_type}/v1beta1"
\t"sigs.k8s.io/cluster-api/util"
\t"sigs.k8s.io/cluster-api/util/predicates"
)

// {name_cap}{kind}Reconciler reconciles a {name_cap}{kind} object.
type {name_cap}{kind}Reconciler struct {{
\tclient.Client
\tLog    logr.Logger
\tScheme *runtime.Scheme
}}

// +kubebuilder:rbac:groups={config['api_group']},resources={name}{kind_lower}s,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups={config['api_group']},resources={name}{kind_lower}s/status,verbs=get;update;patch
// +kubebuilder:rbac:groups={config['api_group']},resources={name}{kind_lower}s/finalizers,verbs=update
// +kubebuilder:rbac:groups=cluster.x-k8s.io,resources=clusters;machines,verbs=get;list;watch

// Reconcile performs reconciliation for {name_cap}{kind}.
func (r *{name_cap}{kind}Reconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {{
\tlog := r.Log.WithValues("{kind_lower}", req.NamespacedName)

\t// Fetch the {name_cap}{kind} instance
\t{kind_lower} := &{short_type}v1beta1.{name_cap}{kind}{{}}
\tif err := r.Get(ctx, req.NamespacedName, {kind_lower}); err != nil {{
\t\treturn ctrl.Result{{}}, client.IgnoreNotFound(err)
\t}}

\t// Get the owner Cluster
\tcluster, err := util.GetOwnerCluster(ctx, r.Client, {kind_lower}.ObjectMeta)
\tif err != nil {{
\t\treturn ctrl.Result{{}}, err
\t}}
\tif cluster == nil {{
\t\tlog.Info("Waiting for Cluster Controller to set OwnerRef")
\t\treturn ctrl.Result{{}}, nil
\t}}

\t// Handle deletion
\tif !{kind_lower}.DeletionTimestamp.IsZero() {{
\t\treturn r.reconcileDelete(ctx, {kind_lower})
\t}}

\t// Add finalizer
\tif !controllerutil.ContainsFinalizer({kind_lower}, "{short_type}v1beta1.{name}") {{
\t\tcontrollerutil.AddFinalizer({kind_lower}, "{short_type}v1beta1.{name}")
\t\tif err := r.Update(ctx, {kind_lower}); err != nil {{
\t\t\treturn ctrl.Result{{}}, err
\t\t}}
\t}}

\treturn r.reconcileNormal(ctx, {kind_lower}, cluster)
}}

func (r *{name_cap}{kind}Reconciler) reconcileNormal(
\tctx context.Context,
\t{kind_lower} *{short_type}v1beta1.{name_cap}{kind},
\tcluster interface{{}},
) (ctrl.Result, error) {{
\t// TODO: Implement provider-specific reconciliation logic

\t// Update status
\t{kind_lower}.Status.Ready = true
\tif err := r.Status().Update(ctx, {kind_lower}); err != nil {{
\t\treturn ctrl.Result{{}}, err
\t}}

\treturn ctrl.Result{{}}, nil
}}

func (r *{name_cap}{kind}Reconciler) reconcileDelete(
\tctx context.Context,
\t{kind_lower} *{short_type}v1beta1.{name_cap}{kind},
) (ctrl.Result, error) {{
\t// TODO: Implement provider-specific deletion logic

\t// Remove finalizer
\tcontrollerutil.RemoveFinalizer({kind_lower}, "{short_type}v1beta1.{name}")
\tif err := r.Update(ctx, {kind_lower}); err != nil {{
\t\treturn ctrl.Result{{}}, err
\t}}

\treturn ctrl.Result{{}}, nil
}}

// SetupWithManager sets up the controller with the Manager.
func (r *{name_cap}{kind}Reconciler) SetupWithManager(mgr ctrl.Manager) error {{
\treturn ctrl.NewControllerManagedBy(mgr).
\t\tFor(&{short_type}v1beta1.{name_cap}{kind}{{}}).
\t\tWithEventFilter(predicates.ResourceNotPaused(r.Log)).
\t\tComplete(r)
}}
"""


def generate_main(name: str, name_cap: str, config: dict) -> str:
    """Generate main.go file."""
    short_type = config["short"]
    controllers = config["controller_kinds"]
    controller_setup = "\n".join(
        f"""\tif err = (&{short_type}controllers.{name_cap}{kind}Reconciler{{
\t\tClient: mgr.GetClient(),
\t\tLog:    ctrl.Log.WithName("controllers").WithName("{kind}"),
\t\tScheme: mgr.GetScheme(),
\t}}).SetupWithManager(mgr); err != nil {{
\t\tsetupLog.Error(err, "unable to create controller", "controller", "{kind}")
\t\tos.Exit(1)
\t}}"""
        for kind in controllers
    )

    return f"""package main

import (
\t"flag"
\t"os"

\t"k8s.io/apimachinery/pkg/runtime"
\tutilruntime "k8s.io/apimachinery/pkg/util/runtime"
\tclientgoscheme "k8s.io/client-go/kubernetes/scheme"
\tctrl "sigs.k8s.io/controller-runtime"
\t"sigs.k8s.io/controller-runtime/pkg/healthz"
\t"sigs.k8s.io/controller-runtime/pkg/log/zap"

\tclusterv1 "sigs.k8s.io/cluster-api/api/v1beta1"

\t{short_type}v1beta1 "github.com/example/cluster-api-provider-{name}/api/{short_type}/v1beta1"
\t{short_type}controllers "github.com/example/cluster-api-provider-{name}/controllers/{short_type}"
)

var (
\tscheme   = runtime.NewScheme()
\tsetupLog = ctrl.Log.WithName("setup")
)

func init() {{
\tutilruntime.Must(clientgoscheme.AddToScheme(scheme))
\tutilruntime.Must(clusterv1.AddToScheme(scheme))
\tutilruntime.Must({short_type}v1beta1.AddToScheme(scheme))
}}

func main() {{
\tvar metricsAddr string
\tvar enableLeaderElection bool
\tvar probeAddr string

\tflag.StringVar(&metricsAddr, "metrics-bind-address", ":8080", "The address the metric endpoint binds to.")
\tflag.StringVar(&probeAddr, "health-probe-bind-address", ":8081", "The address the probe endpoint binds to.")
\tflag.BoolVar(&enableLeaderElection, "leader-elect", false, "Enable leader election.")
\tflag.Parse()

\tctrl.SetLogger(zap.New(zap.UseDevMode(true)))

\tmgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{{
\t\tScheme:                 scheme,
\t\tMetricsBindAddress:     metricsAddr,
\t\tHealthProbeBindAddress: probeAddr,
\t\tLeaderElection:         enableLeaderElection,
\t\tLeaderElectionID:       "{name}-controller-leader-election",
\t}})
\tif err != nil {{
\t\tsetupLog.Error(err, "unable to start manager")
\t\tos.Exit(1)
\t}}

{controller_setup}

\tif err := mgr.AddHealthzCheck("healthz", healthz.Ping); err != nil {{
\t\tsetupLog.Error(err, "unable to set up health check")
\t\tos.Exit(1)
\t}}
\tif err := mgr.AddReadyzCheck("readyz", healthz.Ping); err != nil {{
\t\tsetupLog.Error(err, "unable to set up ready check")
\t\tos.Exit(1)
\t}}

\tsetupLog.Info("starting manager")
\tif err := mgr.Start(ctrl.SetupSignalHandler()); err != nil {{
\t\tsetupLog.Error(err, "problem running manager")
\t\tos.Exit(1)
\t}}
}}
"""


def generate_cluster_template(name: str, name_cap: str, config: dict) -> str:
    """Generate sample cluster template."""
    if config["short"] == "infra":
        return f"""apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  name: ${{CLUSTER_NAME}}
  namespace: ${{NAMESPACE}}
spec:
  clusterNetwork:
    pods:
      cidrBlocks:
      - 192.168.0.0/16
    services:
      cidrBlocks:
      - 10.96.0.0/12
  controlPlaneRef:
    apiVersion: controlplane.cluster.x-k8s.io/v1beta1
    kind: KubeadmControlPlane
    name: ${{CLUSTER_NAME}}-control-plane
  infrastructureRef:
    apiVersion: {config['api_group']}/v1beta1
    kind: {name_cap}Cluster
    name: ${{CLUSTER_NAME}}
---
apiVersion: {config['api_group']}/v1beta1
kind: {name_cap}Cluster
metadata:
  name: ${{CLUSTER_NAME}}
  namespace: ${{NAMESPACE}}
spec:
  region: ${{REGION}}
  networkSpec:
    vpc:
      cidrBlock: 10.0.0.0/16
---
apiVersion: controlplane.cluster.x-k8s.io/v1beta1
kind: KubeadmControlPlane
metadata:
  name: ${{CLUSTER_NAME}}-control-plane
  namespace: ${{NAMESPACE}}
spec:
  replicas: ${{CONTROL_PLANE_MACHINE_COUNT}}
  version: ${{KUBERNETES_VERSION}}
  machineTemplate:
    infrastructureRef:
      apiVersion: {config['api_group']}/v1beta1
      kind: {name_cap}MachineTemplate
      name: ${{CLUSTER_NAME}}-control-plane
  kubeadmConfigSpec:
    initConfiguration:
      nodeRegistration: {{}}
    joinConfiguration:
      nodeRegistration: {{}}
---
apiVersion: {config['api_group']}/v1beta1
kind: {name_cap}MachineTemplate
metadata:
  name: ${{CLUSTER_NAME}}-control-plane
  namespace: ${{NAMESPACE}}
spec:
  template:
    spec:
      instanceType: ${{CONTROL_PLANE_MACHINE_TYPE}}
"""
    return f"""# Template for {config['long']} provider
apiVersion: {config['api_group']}/v1beta1
kind: {name_cap}{config['kinds'][0]}
metadata:
  name: example
  namespace: ${{NAMESPACE}}
spec:
  # Add spec fields here
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a new CAPI provider",
    )
    parser.add_argument(
        "name",
        help="Provider name (e.g., 'mycloud')",
    )
    parser.add_argument(
        "--type",
        "-t",
        choices=list(PROVIDER_CONFIGS.keys()),
        default="infra",
        help="Provider type (default: infra)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output directory (default: ./cluster-api-provider-<name>)",
    )
    args = parser.parse_args()

    name = args.name.lower()
    output_dir = Path(args.output or f"./cluster-api-provider-{name}")

    if output_dir.exists():
        print(f"Error: Output directory already exists: {output_dir}", file=sys.stderr)
        return 1

    generate_structure(name, args.type, output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
