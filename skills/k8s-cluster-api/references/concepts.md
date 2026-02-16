# Cluster API Concepts

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  Management Cluster                      │
│  ┌────────────────┐  ┌──────────────────────────────┐   │
│  │   CAPI Core    │  │     Provider Controllers      │   │
│  │   Controllers  │  │  (Infra, Bootstrap, CP)       │   │
│  └────────────────┘  └──────────────────────────────┘   │
│                                                          │
│  Custom Resources: Cluster, Machine, MachineDeployment   │
│  MachineSet, MachineHealthCheck, ClusterClass            │
└─────────────────────────┬────────────────────────────────┘
                          │ manages
            ┌─────────────┴─────────────┐
            ▼                           ▼
    ┌───────────────┐           ┌───────────────┐
    │   Workload    │           │   Workload    │
    │   Cluster 1   │           │   Cluster N   │
    └───────────────┘           └───────────────┘
```

## Core Concepts

### Management Cluster

Kubernetes cluster where Cluster API and providers run. Manages workload cluster lifecycle via custom resources (Cluster, Machine, etc.).

### Workload Cluster

Kubernetes cluster whose lifecycle is managed by Cluster API. Represented by a `Cluster` custom resource.

## Core Resources

### Cluster

Represents a Kubernetes cluster managed by CAPI.

```yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: Cluster
metadata:
  name: my-cluster
spec:
  clusterNetwork:
    pods:
      cidrBlocks:
        - 192.168.0.0/16
  infrastructureRef:
    apiGroup: infrastructure.cluster.x-k8s.io
    kind: VSphereCluster
    name: my-cluster-infrastructure
  controlPlaneRef:
    apiGroup: controlplane.cluster.x-k8s.io
    kind: KubeadmControlPlane
    name: my-control-plane
```

Key fields:

- `clusterNetwork` - Common network settings (portable)
- `infrastructureRef` - Provider-specific cluster config (not portable)
- `controlPlaneRef` - Control plane implementation

### Machine

Declarative spec for infrastructure hosting a Kubernetes Node (e.g., VM).

```yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: Machine
metadata:
  name: my-machine
spec:
  clusterName: my-cluster
  version: v1.35.0
  infrastructureRef:
    apiGroup: infrastructure.cluster.x-k8s.io
    kind: VSphereMachineTemplate
    name: my-machine-infrastructure
  bootstrap:
    configRef:
      apiGroup: bootstrap.cluster.x-k8s.io
      kind: KubeadmConfigTemplate
      name: my-bootstrap-config
status:
  nodeRef:
    name: the-node-running-on-my-machine
```

Behavior:

- Create Machine → Provider provisions host → Node registered
- Delete Machine → Infrastructure and Node deleted

### Machine Immutability

**Key principle**: All Machines are immutable - once created, never updated (except labels, annotations, status), only deleted.

| Approach                     | Description                                                  |
| ---------------------------- | ------------------------------------------------------------ |
| **Replace (default)**        | MachineDeployment rolls out changes by creating new machines |
| **In-place update (v1.12+)** | Extensions can enable updates under specific circumstances   |

User experience remains the same - define desired state, CAPI chooses strategy.

### MachineDeployment

Provides declarative updates for Machines. Works like core Kubernetes Deployment.

- Manages changes via rolling updates to MachineSets
- Preferred over managing single Machines
- Controls rollout strategy (max unavailable, max surge)

### MachineSet

Maintains stable set of Machines. Works like core Kubernetes ReplicaSet.

**Do not use directly** - MachineDeployments manage MachineSets.

### MachinePool

Declarative spec for group of Machines, specific to Infrastructure Provider.

- Similar to MachineDeployment
- Provider-specific implementation
- Experimental feature

### MachineHealthCheck

Defines conditions for unhealthy nodes and triggers remediation.

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineHealthCheck
metadata:
  name: my-cluster-mhc
spec:
  clusterName: my-cluster
  maxUnhealthy: 40%
  nodeStartupTimeout: 10m
  selector:
    matchLabels:
      cluster.x-k8s.io/cluster-name: my-cluster
  unhealthyConditions:
    - type: Ready
      status: "False"
      timeout: 5m
    - type: Ready
      status: Unknown
      timeout: 5m
```

**Requirement**: Machines must be owned by MachineSet (ensures capacity by creating replacement).

## Provider Types

### Infrastructure Provider

Provisions infrastructure/computational resources (VMs, networking, etc.).

| Category       | Providers                                   |
| -------------- | ------------------------------------------- |
| Cloud          | AWS, Azure, GCP, DigitalOcean, Linode, etc. |
| Virtualization | VMware vSphere, KubeVirt, Nutanix, Proxmox  |
| Bare Metal     | Metal3, MAAS, Packet/Equinix Metal          |
| Development    | Docker (CAPD)                               |

**Variants**: Different ways to obtain resources from same provider (e.g., AWS EC2 vs EKS).

### Bootstrap Provider

Turns server into Kubernetes node. Responsibilities:

1. Generate cluster certificates (if not specified)
2. Initialize control plane
3. Gate node creation until control plane ready
4. Join control plane and worker nodes

Generates **BootstrapData** (usually cloud-init) used by Infrastructure Provider.

| Provider | Description                             |
| -------- | --------------------------------------- |
| Kubeadm  | Default, uses kubeadm for bootstrapping |
| MicroK8s | Uses MicroK8s                           |
| K0s      | Uses k0s                                |
| Talos    | Uses Talos Linux                        |

### Control Plane Provider

Provisions and manages Kubernetes control plane.

| Type             | Description                            | Examples            |
| ---------------- | -------------------------------------- | ------------------- |
| Self-provisioned | Pods/machines managed by CAPI          | KubeadmControlPlane |
| Pod-based        | Components as Deployments/StatefulSets | k0smotron           |
| External/Managed | Hosted by cloud provider               | GKE, AKS, EKS       |

### KubeadmControlPlane

Default control plane provider. Manages set of control plane Machines using kubeadm.

Features:

- Manages static pods (apiserver, controller-manager, scheduler)
- Handles etcd (stacked or external)
- Certificate management
- Rolling updates for control plane

## Resource Relationships

```
Cluster
├── infrastructureRef → InfraCluster (provider-specific)
├── controlPlaneRef → KubeadmControlPlane
│   └── owns → Machines (control plane nodes)
└── MachineDeployments
    └── owns → MachineSets
        └── owns → Machines (worker nodes)
            ├── infrastructureRef → InfraMachine
            └── bootstrap.configRef → BootstrapConfig
```

## Key CRDs

| CRD                | API Group        | Purpose                         |
| ------------------ | ---------------- | ------------------------------- |
| Cluster            | cluster.x-k8s.io | Workload cluster definition     |
| Machine            | cluster.x-k8s.io | Single node definition          |
| MachineSet         | cluster.x-k8s.io | Replica set of machines         |
| MachineDeployment  | cluster.x-k8s.io | Declarative machine updates     |
| MachinePool        | cluster.x-k8s.io | Provider-specific machine group |
| MachineHealthCheck | cluster.x-k8s.io | Node health monitoring          |
| ClusterClass       | cluster.x-k8s.io | Cluster template (experimental) |

## Best Practices

1. **Never manage single Machines directly** - use MachineDeployment or KubeadmControlPlane
2. **Use MachineHealthCheck** - automatic remediation prevents degraded clusters
3. **Understand immutability** - changes trigger machine replacement
4. **Separate management and workload clusters** - isolation and reliability
5. **Use ClusterClass** for standardized cluster templates

## Project Philosophy (Manifesto)

### Core Principles

| Principle            | Description                                                            |
| -------------------- | ---------------------------------------------------------------------- |
| **Declarative APIs** | "Kubernetes all the way down" - define target state via K8s-style APIs |
| **Simplicity**       | Hide complexity behind simple declarative API                          |
| **Stability**        | Evolve responsibly with upgrade paths and minimal disruptions          |
| **Extensibility**    | Support many providers while ensuring cohesive solution                |

### Design Goals

- **One API to rule them all** - common primitives working consistently across infrastructures
- **Controllers for consistency** - reconcile loops ensure desired state matches actual state
- **Right to be unfinished** - continuously evolve while maintaining stability

### Kubernetes Guarantees

CAPI follows same API guarantees as Kubernetes:

- Predictable release calendar
- Clear support windows
- Compatibility matrix for each release
- Obsessive focus on CI signal and test coverage
