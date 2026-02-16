# Migration Guides

## v1.11 to v1.12

### Go & Dependencies

| Component          | Version |
| ------------------ | ------- |
| Go                 | v1.24.x |
| Controller Runtime | v0.22.x |
| Kubernetes libs    | v1.34.x |

### Implemented Proposals (v1.12)

- **In-place updates** — update machines without recreation
- **Chained and efficient upgrades** — optimized upgrade workflows
- **Taint propagation (Phase 1)** — machine taint to node taint propagation

---

## API Changes

### Machine

| Field/Condition                  | Change     | Notes                                 |
| -------------------------------- | ---------- | ------------------------------------- |
| `spec.taint`                     | **New**    | Propagate taints to nodes             |
| `HealthCheckSucceeded` condition | New reason | `UnhealthyMachine` for failed checks  |
| `UpToDate` condition             | New reason | `Updating` during in-place updates    |
| `Updating` condition             | **New**    | Status `True` during in-place updates |
| `status.phases`                  | New phase  | `Updating` phase added                |

**Updating condition reasons:**

- `NotUpdating`
- `InPlaceUpdating`
- `InPlaceUpdateFailed`

### MachineHealthCheck

```yaml
spec:
  checks:
    unhealthyMachineConditions: # NEW field
      - type: Ready
        status: "False"
        timeout: 300s
```

### Cluster (Topology)

```yaml
spec:
  topology:
    controlPlane:
      healthCheck:
        checks:
          unhealthyMachineConditions: [] # NEW
    workers:
      machineDeployments:
        - healthCheck:
            checks:
              unhealthyMachineConditions: [] # NEW
```

### ClusterClass

```yaml
spec:
  controlPlane:
    healthCheck:
      checks:
        unhealthyMachineConditions: [] # NEW
  workers:
    machineDeployments:
      - healthCheck:
          checks:
            unhealthyMachineConditions: [] # NEW
  upgrade: {} # NEW - upgrade configuration
  kubernetesVersions: [] # NEW - version constraints
```

### KubeadmConfig

```yaml
spec:
  clusterConfiguration:
    encryptionAlgorithm: RSA-2048 # NEW field
```

---

## Runtime Hooks Changes

### Lifecycle Hooks

| Hook                        | Change                                    |
| --------------------------- | ----------------------------------------- |
| `BeforeClusterUpgrade`      | Extended request with upgrade plan info   |
| `BeforeControlPlaneUpgrade` | **NEW** — before each CP upgrade step     |
| `AfterControlPlaneUpgrade`  | Extended request, called after each step  |
| `BeforeWorkersUpgrade`      | **NEW** — before each worker upgrade step |
| `AfterWorkersUpgrade`       | **NEW** — after each worker upgrade step  |
| `AfterClusterUpgrade`       | Now **blocking** (blocks next upgrade)    |

### New Hook Types

**Upgrade Plan Hooks:**

- `GenerateUpgradePlan` — compute upgrade plan for cluster

**In-Place Extension Hooks:**

- `CanUpdateMachine` — decide if machine can update in-place
- `CanUpdateMachineSet` — decide if MachineSet can update in-place
- `UpdateMachine` — perform in-place upgrade

### Hook Caching

Hooks implement smart caching:

- If hook says "retry after X seconds", CAPI won't call until X expires
- `GenerateUpgradePlan`, `CanUpdateMachine`, `CanUpdateMachineSet` use optimized caching

---

## Contract Changes

### ControlPlane Contract

New **optional** rule for in-place update support.

### MachinePool Contract

Documentation aligned with other contracts. **Action required**: MachinePool providers should verify compliance.

---

## Deprecations

### TopologyReconciled Condition Reasons

**Deprecated reasons:**

- `ControlPlaneUpgradePending`
- `MachineDeploymentsCreatePending`
- `MachineDeploymentsUpgradePending`
- `MachinePoolsUpgradePending`
- `MachinePoolsCreatePending`
- `LifecycleHookBlocking`

**New reasons:**

- `ClusterCreating`
- `ClusterUpgrading`

---

## Removals

### v1.12

- `controlplane.cluster.x-k8s.io/kubeadm-cluster-configuration` annotation on Machines

### Scheduled (August 2026)

- v1beta1 API version
- v1beta1 contract compatibility
- Custom condition type utilities (`util/conditions/deprecated/v1beta1`)
- All `status.deprecated` fields

---

## Provider Migration Checklist

### Required Actions

- [ ] Update Go to v1.24.x
- [ ] Update Controller Runtime to v0.22.x
- [ ] Update Kubernetes libs to v1.34.x
- [ ] Make `APIEndpoint.Host` and `APIEndpoint.Port` optional in InfraCluster/ControlPlane types
- [ ] Review MachinePool contract compliance (if applicable)

### E2E Test Configuration

Add timeouts to e2e config if running upgrade tests:

```yaml
default/wait-control-plane-upgrade: ["15m", "10s"]
default/wait-machine-deployment-upgrade: ["10m", "10s"]
```

### v1beta2 Migration

**Strong recommendation**: Start migration to v1beta2 contract.

| Item                           | Deadline    |
| ------------------------------ | ----------- |
| v1beta1 deprecation            | Now         |
| v1beta1 removal                | August 2026 |
| Contract compatibility removal | August 2026 |

### Utility Function Changes

`util.IsOwnedByObject`, `util.IsControlledBy`, `collections.OwnedMachines` now require `schema.GroupKind` parameter:

```go
// Before
util.IsOwnedByObject(obj, owner)

// After
util.IsOwnedByObject(obj, owner, schema.GroupKind{Group: "infrastructure.cluster.x-k8s.io", Kind: "FooMachine"})
```

### Rate Limiting

New `ReconcilerRateLimiting` feature gate limits reconcilers to 1 request/second.

---

## v1.10 to v1.11

### Go & Dependencies

| Component          | Version |
| ------------------ | ------- |
| Go                 | v1.24.x |
| Controller Runtime | v0.21.x |
| Kubernetes libs    | v1.33.x |

### Major Theme: v1beta2 API Introduction

v1.11 introduces the v1beta2 API version — a major step toward v1 graduation.

### Key Changes

| Area              | Change                                  |
| ----------------- | --------------------------------------- |
| Conditions        | Transition to `metav1.Conditions` types |
| Replica counters  | Consistent across all resources         |
| Object references | Simplified, GitOps-friendly             |
| Duration fields   | Now `*int32` with `Seconds` suffix      |
| Bool fields       | Changed to `*bool`                      |
| KubeadmConfig     | Aligned with kubeadm v1beta4            |

### API Import Changes

```go
// Old imports
"sigs.k8s.io/cluster-api/api/v1beta1"
"sigs.k8s.io/cluster-api/bootstrap/kubeadm/api/v1beta1"

// New imports
"sigs.k8s.io/cluster-api/api/core/v1beta1"
"sigs.k8s.io/cluster-api/api/bootstrap/kubeadm/v1beta1"
```

### Object Reference Changes

```yaml
# v1beta1
infrastructureRef:
  apiVersion: "infrastructure.cluster.x-k8s.io/v1beta1"
  kind: "AWSCluster"
  name: "my-cluster"
  namespace: "default"

# v1beta2
infrastructureRef:
  apiGroup: "infrastructure.cluster.x-k8s.io"
  kind: "AWSCluster"
  name: "my-cluster"
```

### Duration Field Changes

```yaml
# v1beta1
spec:
  nodeDeletionTimeout: 10s
  nodeDrainTimeout: 20s

# v1beta2
spec:
  deletion:
    nodeDeletionTimeoutSeconds: 10
    nodeDrainTimeoutSeconds: 20
```

### Status Structure Changes

```yaml
# v1beta1
status:
  conditions: [...]  # clusterv1beta1.Conditions
  failureReason: ""
  failureMessage: ""

# v1beta2
status:
  conditions: [...]  # metav1.Conditions
  deprecated:
    v1beta1:
      conditions: [...]
      failureReason: ""
      failureMessage: ""
```

### Deprecations (v1.11)

- v1beta1 API version deprecated (removal: August 2026)
- v1alpha1 ExtensionConfig deprecated
- `failureReason`/`failureMessage` moved to `status.deprecated.v1beta1`

---

## v1.9 to v1.10

### Go & Dependencies

| Component | Version |
| --------- | ------- |
| Go        | v1.23.x |

### Key Changes

- CRD Migrator component introduced
- CRD migration in clusterctl deprecated (removal: v1.13)

### E2EConfig Function Renames

```go
// Old
E2EConfig.GetVariable
E2EConfig.GetInt64PtrVariable
E2EConfig.GetInt32PtrVariable

// New
E2EConfig.MustGetVariable
E2EConfig.MustGetInt64PtrVariable
E2EConfig.MustGetInt32PtrVariable
```

### CRD Migrator Setup (Recommended)

1. Add `--skip-crd-migration-phases` flag
2. Setup CRDMigrator with manager
3. Configure owned CRDs
4. Add RBAC:
   - `customresourcedefinitions`: get, list, watch
   - CRD-specific: update, patch

### Provider Recommendations

- Add `spec.machineTemplate.readinessGates` for control plane providers with machine support
- Adopt CRD Migrator instead of clusterctl CRD migration
