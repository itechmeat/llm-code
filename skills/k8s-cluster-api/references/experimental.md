# Experimental Features

**WARNING**: Experimental features may be modified or removed without notice.

## Enabling Experimental Features

### Via Environment Variables

```bash
export CLUSTER_TOPOLOGY=true
export EXP_RUNTIME_SDK=true
export EXP_MACHINE_POOL=true
clusterctl init --infrastructure docker
```

### Via clusterctl Config

```yaml
# ~/.cluster-api/clusterctl.yaml
variables:
  CLUSTER_TOPOLOGY: "true"
  EXP_RUNTIME_SDK: "true"
  EXP_MACHINE_POOL: "true"
```

### Via Controller Arguments

```bash
kubectl edit -n capi-system deployment.apps/capi-controller-manager
```

```yaml
args: --leader-elect
  --feature-gates=MachinePool=true,ClusterResourceSet=true
```

## Feature Gates

| Feature                        | Env Var                                 | Description                         |
| ------------------------------ | --------------------------------------- | ----------------------------------- |
| ClusterTopology                | `CLUSTER_TOPOLOGY`                      | ClusterClass and managed topologies |
| InPlaceUpdates                 | `EXP_IN_PLACE_UPDATES`                  | Update machines without replacement |
| MachinePool                    | `EXP_MACHINE_POOL`                      | MachinePool resources               |
| MachineSetPreflightChecks      | `EXP_MACHINE_SET_PREFLIGHT_CHECKS`      | Pre-creation validation             |
| MachineTaintPropagation        | `EXP_MACHINE_TAINT_PROPAGATION`         | Propagate taints to nodes           |
| RuntimeSDK                     | `EXP_RUNTIME_SDK`                       | Runtime extensions/hooks            |
| KubeadmBootstrapFormatIgnition | `EXP_KUBEADM_BOOTSTRAP_FORMAT_IGNITION` | Ignition bootstrap                  |

---

## ClusterClass

### Overview

ClusterClass reduces boilerplate and enables flexible cluster customization. Creates clusters from templates with variables and patches.

**Feature Gate**: `CLUSTER_TOPOLOGY=true`  
**Requires**: Kubernetes >= 1.22.0 on management cluster

### Basic ClusterClass

```yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: ClusterClass
metadata:
  name: docker-clusterclass-v0.1.0
spec:
  controlPlane:
    templateRef:
      apiVersion: controlplane.cluster.x-k8s.io/v1beta2
      kind: KubeadmControlPlaneTemplate
      name: docker-clusterclass-v0.1.0
    machineInfrastructure:
      templateRef:
        apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
        kind: DockerMachineTemplate
        name: docker-clusterclass-v0.1.0
  infrastructure:
    templateRef:
      apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
      kind: DockerClusterTemplate
      name: docker-clusterclass-v0.1.0-control-plane
  workers:
    machineDeployments:
      - class: default-worker
        bootstrap:
          templateRef:
            apiVersion: bootstrap.cluster.x-k8s.io/v1beta2
            kind: KubeadmConfigTemplate
            name: docker-clusterclass-v0.1.0-default-worker
        infrastructure:
          templateRef:
            apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
            kind: DockerMachineTemplate
            name: docker-clusterclass-v0.1.0-default-worker
```

### Cluster Using ClusterClass

```yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: Cluster
metadata:
  name: my-docker-cluster
spec:
  topology:
    classRef:
      name: docker-clusterclass-v0.1.0
    version: v1.32.0
    controlPlane:
      replicas: 3
      metadata:
        labels:
          cpLabel: cpLabelValue
    workers:
      machineDeployments:
        - class: default-worker
          name: md-0
          replicas: 4
          failureDomain: region
```

### Variables and Patches

Define variables in ClusterClass:

```yaml
spec:
  variables:
    - name: imageRepository
      required: true
      schema:
        openAPIV3Schema:
          type: string
          description: Container registry for images
          default: registry.k8s.io
```

Define patches to use variables:

```yaml
spec:
  patches:
    - name: imageRepository
      definitions:
        - selector:
            apiVersion: controlplane.cluster.x-k8s.io/v1beta2
            kind: KubeadmControlPlaneTemplate
            matchResources:
              controlPlane: true
          jsonPatches:
            - op: add
              path: /spec/template/spec/kubeadmConfigSpec/clusterConfiguration/imageRepository
              valueFrom:
                variable: imageRepository
```

Set variable values in Cluster:

```yaml
spec:
  topology:
    variables:
      - name: imageRepository
        value: my.custom.registry
```

### ClusterClass with MachineHealthChecks

```yaml
spec:
  controlPlane:
    healthCheck:
      checks:
        nodeStartupTimeoutSeconds: 900
        unhealthyNodeConditions:
          - type: Ready
            status: Unknown
            timeoutSeconds: 300
      remediation:
        triggerIf:
          unhealthyLessThanOrEqualTo: 33%
  workers:
    machineDeployments:
      - class: default-worker
        healthCheck:
          checks:
            unhealthyNodeConditions:
              - type: Ready
                status: "False"
                timeoutSeconds: 300
          remediation:
            triggerIf:
              unhealthyInRange: "[0-2]"
```

### ClusterClass with MachinePools

```yaml
spec:
  workers:
    machinePools:
      - class: default-worker
        bootstrap:
          templateRef:
            apiVersion: bootstrap.cluster.x-k8s.io/v1beta2
            kind: KubeadmConfigTemplate
            name: quick-start-default-worker-bootstraptemplate
        infrastructure:
          templateRef:
            apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
            kind: DockerMachinePoolTemplate
            name: quick-start-default-worker-machinepooltemplate
```

### JSON Patches Rules

- Only fields below `/spec` can be patched
- Only `add`, `remove`, `replace` operations supported
- Append/prepend to arrays only (no specific index insert)
- Supported types: `string`, `integer`, `number`, `boolean`

### Best Practices

1. Use generic ClusterClass names (not cluster-specific)
2. Include version suffix in name (e.g., `docker-clusterclass-v0.1.0`)
3. Prefix templates with ClusterClass name
4. Don't reuse templates across ClusterClasses

---

## MachinePools

### Overview

MachinePool is a declarative spec for a group of machines, similar to MachineDeployment but provider-specific implementation.

**Feature Gate**: `EXP_MACHINE_POOL=true`

### Requirements

- Enable in CAPI, CABPK, and infrastructure provider
- Provider must implement `MachinePool` CRD

### Example

```yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: MachinePool
metadata:
  name: my-pool
spec:
  clusterName: my-cluster
  replicas: 3
  template:
    spec:
      bootstrap:
        configRef:
          apiVersion: bootstrap.cluster.x-k8s.io/v1beta2
          kind: KubeadmConfig
          name: my-pool-config
      infrastructureRef:
        apiVersion: infrastructure.cluster.x-k8s.io/v1beta2
        kind: AzureMachinePool
        name: my-pool
      version: v1.32.0
```

---

## Runtime SDK

### Overview

Provides extensibility mechanism to hook into workload cluster lifecycle.

**Feature Gate**: `EXP_RUNTIME_SDK=true`  
**Requires**: ClusterClass enabled

**WARNING**: Incorrectly implemented extensions can severely impact CAPI runtime.

### Hook Types

| Hook              | Purpose                                                 |
| ----------------- | ------------------------------------------------------- |
| Lifecycle Hooks   | BeforeClusterCreate, AfterControlPlaneInitialized, etc. |
| Topology Mutation | Modify topology before reconciliation                   |
| In-Place Update   | Custom update logic                                     |
| Upgrade Plan      | Custom upgrade planning                                 |

### Runtime Extension Deployment

Extensions are deployed as separate services and registered via `ExtensionConfig`:

```yaml
apiVersion: runtime.cluster.x-k8s.io/v1alpha1
kind: ExtensionConfig
metadata:
  name: my-extension
spec:
  clientConfig:
    service:
      name: my-extension-service
      namespace: my-extension-system
      port: 443
```

---

## Ignition Bootstrap

### Overview

Alternative to cloud-init using Ignition (used by Flatcar, FCOS, RHCOS).

**Feature Gate**: `EXP_KUBEADM_BOOTSTRAP_FORMAT_IGNITION=true`

### Configuration

Set format in KubeadmConfig:

```yaml
apiVersion: bootstrap.cluster.x-k8s.io/v1beta2
kind: KubeadmConfig
spec:
  format: ignition
  ignition:
    containerLinuxConfig:
      additionalConfig: |
        storage:
          files:
          - path: /etc/myconfig
            contents:
              inline: "my-content"
```

---

## MachineSetPreflightChecks

### Overview

Validates conditions before creating machines.

**Feature Gate**: `EXP_MACHINE_SET_PREFLIGHT_CHECKS=true`

### Checks Performed

- Control plane initialized
- Kubernetes version skew (max 2 minor versions from control plane)
- Infrastructure provider readiness

---

## In-Place Updates

### Overview

Allows updating existing machines without delete/recreate cycle.

**Feature Gate**: `EXP_IN_PLACE_UPDATES=true`

### Use Cases

- Certificate rotation
- Configuration changes that don't require new infrastructure
- OS patching

---

## Controller Deployments to Edit

| Feature      | Controllers                          |
| ------------ | ------------------------------------ |
| MachinePools | CAPI, CABPK, Infrastructure Provider |
| ClusterClass | CAPI, KCP, Infrastructure Provider   |
| Ignition     | CABPK, KCP                           |
| Runtime SDK  | CAPI                                 |
