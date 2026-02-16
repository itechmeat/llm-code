# Controllers

## Cluster Controller

**Responsibilities:**

- Set OwnerReference on InfraCluster object
- Set OwnerReference on ControlPlane object
- Sync Cluster status with InfraCluster/ControlPlane status
- Create kubeconfig secret (if no ControlPlane object)
- Cleanup owned objects on deletion

**Contract expectations:**

| From         | Expected                      |
| ------------ | ----------------------------- |
| InfraCluster | Report control plane endpoint |
| InfraCluster | Report failure domains        |
| InfraCluster | Report `status.ready = true`  |
| ControlPlane | Report control plane endpoint |
| ControlPlane | Report `status.ready = true`  |
| ControlPlane | Manage kubeconfig secret      |

**Kubeconfig Secret format:**

| Secret name                 | Field   | Content           |
| --------------------------- | ------- | ----------------- |
| `<cluster-name>-kubeconfig` | `value` | base64 kubeconfig |

---

## Machine Controller

**Responsibilities:**

- Set OwnerReference on InfraMachine object
- Set OwnerReference on BootstrapConfig object
- Sync Machine status with InfraMachine/BootstrapConfig status
- Find Kubernetes nodes matching providerID
- Set NodeRefs to associate machines with nodes
- Propagate labels to nodes
- Drain nodes and wait for volume detachment on deletion

**Workflow:**

1. Set OwnerReferences on InfraMachine and BootstrapConfig
2. Wait for `Status.initialization.dataSecretCreated = true` on bootstrap
3. Wait for `Status.initialization.provisioned = true` on infra
4. Copy `Spec.ProviderID` from InfraMachine to Machine
5. Watch workload cluster for node with matching ProviderID
6. Set NodeRef and transition Machine to `Running`

**Contract expectations:**

| From            | Expected                          |
| --------------- | --------------------------------- |
| InfraMachine    | Report providerID                 |
| InfraMachine    | Consider failure domain placement |
| InfraMachine    | Surface machine addresses         |
| InfraMachine    | Report `status.ready = true`      |
| BootstrapConfig | Create bootstrap data secret      |
| BootstrapConfig | Report `status.dataSecretName`    |

---

## ClusterTopology Controller

**Responsibilities:**

- Reconcile Clusters with ClusterClass and managed topology
- Create/update/delete topology-managed resources
- Reconcile Cluster-specific ClusterClass customizations

**High-level workflow:**

1. Read ClusterClass definition
2. Apply templates to create infrastructure objects
3. Reconcile control plane and worker resources
4. Handle variable substitutions and patches

---

## MachineDeployment Controller

**Responsibilities:**

- Adopt matching unassigned MachineSets
- Manage Machine deployment process
- Scale up new MachineSets on changes
- Scale down old MachineSets when replaced
- Update MachineDeployment status

**In-place propagation (no rollout):**

- `.annotations`
- `.spec.deletion.order`
- `.spec.template.metadata.labels`
- `.spec.template.metadata.annotations`
- `.spec.template.spec.minReadySeconds`
- `.spec.template.spec.deletion.*` (timeouts)

---

## MachineSet Controller

**Responsibilities:**

- Adopt unowned/unmanaged Machines
- Boot group of N machines
- Monitor machine status

**In-place propagation to Machines:**

- `.spec.template.metadata.labels`
- `.spec.template.metadata.annotations`
- `.spec.template.spec.nodeDrainTimeout`
- `.spec.template.spec.nodeDeletionTimeout`
- `.spec.template.spec.nodeVolumeDetachTimeout`

**In-place propagation to InfraMachine/BootstrapConfig:**

- `.spec.template.metadata.labels`
- `.spec.template.metadata.annotations`

---

## MachinePool Controller

**Responsibilities:**

- Set OwnerReferences to Cluster, BootstrapConfig, InfraMachinePool
- Copy bootstrap data secret name
- Set NodeRefs on MachinePool instances
- Delete Nodes when MachinePool deleted
- Sync status with InfraMachinePool

**Workflow:**

1. Set OwnerReferences
2. Wait for bootstrap and infrastructure `Status.Ready = true`
3. Copy `Spec.ProviderIDList` from InfraMachinePool
4. Watch for nodes with matching ProviderIDs
5. Increment ready replicas as nodes appear
6. Mark MachinePool `Running` when all ready

**Expected labels:**

| Resource    | Label                           | Value            |
| ----------- | ------------------------------- | ---------------- |
| MachinePool | `cluster.x-k8s.io/cluster-name` | `<cluster-name>` |

**InfraMachinePool contract:**

```go
// Required spec
type InfraMachinePoolSpec struct {
    ProviderIDList []string `json:"providerIDList"`
}

// Required status
type InfraMachinePoolStatus struct {
    Ready bool `json:"ready"`
    // Optional
    InfrastructureMachineKind string `json:"infrastructureMachineKind,omitempty"`
}
```

**Externally Managed Autoscaler:**

```yaml
metadata:
  annotations:
    cluster.x-k8s.io/replicas-managed-by: "" # or "external-autoscaler"
```

---

## MachineHealthCheck Controller

**Responsibilities:**

- Check Node health against unhealthy conditions list
- Remediate Machines for unhealthy Nodes
- Track remediation status

---

## ClusterResourceSet Controller

**Responsibilities:**

- Apply resources (pods, deployments, secrets, configMaps) to clusters
- Automatically apply to newly-created and existing Clusters
- Apply resources only once per cluster
