# API Reference

## Version Support

### Release Support Matrix

| Release | Status      | Support End               |
| ------- | ----------- | ------------------------- |
| v1.12.x | Supported   | EOL when v1.15.0 releases |
| v1.11.x | Supported   | EOL when v1.14.0 releases |
| v1.10.x | Maintenance | EOL when v1.13.0 releases |
| v1.9.x  | EOL         | Since 2025-12-18          |

**Support lifecycle:**

- **Standard support**: 8 months (CI, bug fixes, patches)
- **Maintenance mode**: 4 months (critical fixes only)
- **Release cadence**: ~4 months (3 releases/year)

### API Versions

| API Version | Status     | Notes                    |
| ----------- | ---------- | ------------------------ |
| v1beta2     | Supported  | Current                  |
| v1beta1     | Deprecated | Stopped serving in v1.14 |
| v1alpha4    | EOL        | Removal in v1.13         |
| v1alpha3    | EOL        | Removal in v1.13         |

### Contract Versions

| Contract | Status     | Notes                               |
| -------- | ---------- | ----------------------------------- |
| v1beta2  | Supported  | Compatible with v1beta1 temporarily |
| v1beta1  | Deprecated | Compatibility dropped in v1.14      |

---

## Kubernetes Compatibility

### Management Cluster

| CAPI Release | Kubernetes Versions |
| ------------ | ------------------- |
| v1.12.x      | v1.28 - v1.32       |
| v1.11.x      | v1.27 - v1.31       |
| v1.10.x      | v1.26 - v1.30       |

### Workload Cluster

| CAPI Release | Kubernetes Versions |
| ------------ | ------------------- |
| v1.12.x      | v1.26 - v1.32       |
| v1.11.x      | v1.25 - v1.31       |
| v1.10.x      | v1.24 - v1.30       |

### Upgrade Rules

- **Maximum skip**: 3 minor versions (e.g., v1.6→v1.9)
- **Downgrades**: Not supported
- **Kubernetes upgrades**: Must be sequential (e.g., v1.28→v1.29→v1.30)

---

## Provider Implementations

### Bootstrap Providers

| Provider          | Description                          |
| ----------------- | ------------------------------------ |
| **Kubeadm**       | Official, uses kubeadm for bootstrap |
| **K3s**           | Lightweight Kubernetes               |
| **RKE2**          | Rancher Kubernetes Engine 2          |
| **Talos**         | Immutable Kubernetes OS              |
| **MicroK8s**      | Canonical's lightweight K8s          |
| **k0smotron/k0s** | Zero-friction Kubernetes             |
| **EKS**           | Amazon EKS bootstrap                 |

### Control Plane Providers

| Provider    | Description                     |
| ----------- | ------------------------------- |
| **Kubeadm** | Official control plane provider |
| **K3s**     | K3s control plane               |
| **RKE2**    | RKE2 control plane              |
| **Talos**   | Talos control plane             |
| **Kamaji**  | Hosted control planes           |
| **Nested**  | Nested clusters                 |

### Infrastructure Providers

| Provider          | Cloud/Platform        |
| ----------------- | --------------------- |
| **AWS**           | Amazon Web Services   |
| **Azure**         | Microsoft Azure       |
| **GCP**           | Google Cloud Platform |
| **vSphere**       | VMware vSphere        |
| **Docker**        | Development/testing   |
| **Metal3**        | Bare metal (Ironic)   |
| **OpenStack**     | OpenStack clouds      |
| **Hetzner**       | Hetzner Cloud         |
| **DigitalOcean**  | DigitalOcean          |
| **Linode/Akamai** | Akamai Cloud          |
| **Nutanix**       | Nutanix AHV           |
| **KubeVirt**      | VM-based workloads    |
| **Proxmox**       | Proxmox VE            |
| **BYOH**          | Bring Your Own Host   |
| **Harvester**     | HCI platform          |
| **OCI**           | Oracle Cloud          |
| **Vultr**         | Vultr Cloud           |

### IPAM Providers

| Provider       | Description   |
| -------------- | ------------- |
| **In-Cluster** | Built-in IPAM |
| **Metal3**     | Metal3 IPAM   |
| **Nutanix**    | Nutanix IPAM  |

### Addon Providers

| Provider  | Description                   |
| --------- | ----------------------------- |
| **Helm**  | Helm chart deployment (CAAPH) |
| **Fleet** | Rancher Fleet                 |

---

## Core Resources

### Cluster

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  name: my-cluster
  namespace: default
spec:
  clusterNetwork:
    pods:
      cidrBlocks: ["192.168.0.0/16"]
    services:
      cidrBlocks: ["10.96.0.0/12"]
    serviceDomain: "cluster.local"
  controlPlaneRef:
    apiVersion: controlplane.cluster.x-k8s.io/v1beta1
    kind: KubeadmControlPlane
    name: my-cluster-control-plane
  infrastructureRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
    kind: <InfraCluster>
    name: my-cluster
```

### Machine

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: Machine
metadata:
  name: my-machine
spec:
  clusterName: my-cluster
  version: v1.28.0
  bootstrap:
    configRef:
      apiVersion: bootstrap.cluster.x-k8s.io/v1beta1
      kind: KubeadmConfig
      name: my-machine-bootstrap
  infrastructureRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
    kind: <InfraMachine>
    name: my-machine
```

### MachineDeployment

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineDeployment
metadata:
  name: my-cluster-md-0
spec:
  clusterName: my-cluster
  replicas: 3
  selector:
    matchLabels:
      cluster.x-k8s.io/cluster-name: my-cluster
  template:
    spec:
      clusterName: my-cluster
      version: v1.28.0
      bootstrap:
        configRef:
          apiVersion: bootstrap.cluster.x-k8s.io/v1beta1
          kind: KubeadmConfigTemplate
          name: my-cluster-md-0
      infrastructureRef:
        apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
        kind: <InfraMachineTemplate>
        name: my-cluster-md-0
```

### MachineHealthCheck

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineHealthCheck
metadata:
  name: my-cluster-mhc
spec:
  clusterName: my-cluster
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
  maxUnhealthy: 40%
  nodeStartupTimeout: 10m
```

### KubeadmControlPlane

```yaml
apiVersion: controlplane.cluster.x-k8s.io/v1beta1
kind: KubeadmControlPlane
metadata:
  name: my-cluster-control-plane
spec:
  replicas: 3
  version: v1.28.0
  machineTemplate:
    infrastructureRef:
      apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
      kind: <InfraMachineTemplate>
      name: my-cluster-control-plane
  kubeadmConfigSpec:
    clusterConfiguration:
      apiServer:
        extraArgs:
          cloud-provider: external
      controllerManager:
        extraArgs:
          cloud-provider: external
    initConfiguration:
      nodeRegistration:
        kubeletExtraArgs:
          cloud-provider: external
    joinConfiguration:
      nodeRegistration:
        kubeletExtraArgs:
          cloud-provider: external
```

---

## Glossary

| Term                   | Definition                                        |
| ---------------------- | ------------------------------------------------- |
| **Management Cluster** | Kubernetes cluster running CAPI controllers       |
| **Workload Cluster**   | Kubernetes cluster managed by CAPI                |
| **Bootstrap Cluster**  | Temporary cluster for initial setup               |
| **Provider**           | Component implementing cloud-specific logic       |
| **InfraCluster**       | Cloud-specific cluster infrastructure resource    |
| **InfraMachine**       | Cloud-specific machine resource                   |
| **ControlPlane**       | Control plane management resource                 |
| **MachineClass**       | Deprecated, replaced by ClusterClass              |
| **ClusterClass**       | Template for cluster topology                     |
| **Pivot**              | Moving CAPI resources between management clusters |
| **Contract**           | API compatibility rules for providers             |

---

## Labels and Annotations

### Standard Labels

| Label                             | Purpose                       |
| --------------------------------- | ----------------------------- |
| `cluster.x-k8s.io/cluster-name`   | Identifies cluster membership |
| `cluster.x-k8s.io/control-plane`  | Marks control plane machines  |
| `cluster.x-k8s.io/provider`       | Provider identifier           |
| `topology.cluster.x-k8s.io/owned` | ClusterClass managed          |

### Standard Annotations

| Annotation                               | Purpose              |
| ---------------------------------------- | -------------------- |
| `cluster.x-k8s.io/paused`                | Pause reconciliation |
| `cluster.x-k8s.io/delete-machine`        | Mark for deletion    |
| `cluster.x-k8s.io/cloned-from-name`      | Source template name |
| `clusterctl.cluster.x-k8s.io/block-move` | Block move operation |

### Autoscaler Annotations

| Annotation                                                    | Purpose          |
| ------------------------------------------------------------- | ---------------- |
| `cluster.x-k8s.io/cluster-api-autoscaler-node-group-min-size` | Minimum replicas |
| `cluster.x-k8s.io/cluster-api-autoscaler-node-group-max-size` | Maximum replicas |
| `capacity.cluster-autoscaler.kubernetes.io/memory`            | Memory capacity  |
| `capacity.cluster-autoscaler.kubernetes.io/cpu`               | CPU capacity     |
