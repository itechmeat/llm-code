# Migration Guide: v1beta1 → v1beta2 API

Guide for migrating CAPI resources from v1beta1 to v1beta2 API format.

## Overview

The v1beta2 API introduces:

- Structured conditions with clearer semantics
- TypedObjectReference for references
- Duration fields as strings
- Improved status reporting

## Preparation

### 1. Check Current State

```bash
# Run migration checker script
python scripts/migration_checker.py -n <namespace>

# Or manually check API versions in use
kubectl get clusters -A -o yaml | grep apiVersion
```

### 2. Backup Everything

```bash
# Export cluster state
python scripts/export_cluster_state.py <cluster-name> -o ./backup/

# Or use clusterctl move
clusterctl move --to-kubeconfig backup.kubeconfig -n <namespace>
```

## API Changes Reference

### Conditions (v1beta2 format)

**Old (v1beta1):**

```yaml
status:
  conditions:
    - type: Ready
      status: "True"
      reason: ClusterReady
      message: Cluster is ready
      lastTransitionTime: "2024-01-01T00:00:00Z"
```

**New (v1beta2):**

```yaml
status:
  v1beta2:
    conditions:
      - type: Available
        status: "True"
        reason: Available
        message: Cluster is available
        lastTransitionTime: "2024-01-01T00:00:00Z"
```

Key changes:

- Conditions moved to `status.v1beta2.conditions`
- New condition types: `Available`, `Ready`, `Deleting`
- Clearer positive/negative polarity

### TypedObjectReference

**Old:**

```yaml
spec:
  infrastructureRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
    kind: AWSCluster
    name: my-cluster
    namespace: default
```

**New:**

```yaml
spec:
  infrastructureRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
    kind: AWSCluster
    name: my-cluster
    # namespace is optional if same as parent
```

### Duration Fields

**Old (integer seconds):**

```yaml
spec:
  nodeStartupTimeout: 600
```

**New (string duration):**

```yaml
spec:
  nodeStartupTimeout: 10m
```

### Phase → Conditions

**Old:**

```yaml
status:
  phase: Running
```

**New (use conditions instead):**

```yaml
status:
  v1beta2:
    conditions:
      - type: Available
        status: "True"
```

## Migration Steps

### Step 1: Update CAPI to v1.8+

v1beta2 conditions require CAPI v1.8 or later.

```bash
clusterctl upgrade plan
clusterctl upgrade apply --contract v1beta1
```

### Step 2: Enable v1beta2 Conditions

Feature gate (if not default):

```bash
# In provider deployment
--feature-gates=V1Beta2Conditions=true
```

### Step 3: Update Manifests

#### Cluster Resources

```yaml
# Before
apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
spec:
  infrastructureRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
    kind: AWSCluster
    name: my-cluster
    namespace: default
  controlPlaneRef:
    apiVersion: controlplane.cluster.x-k8s.io/v1beta1
    kind: KubeadmControlPlane
    name: my-cluster-cp
    namespace: default

# After (namespace optional)
apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
spec:
  infrastructureRef:
    apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
    kind: AWSCluster
    name: my-cluster
  controlPlaneRef:
    apiVersion: controlplane.cluster.x-k8s.io/v1beta1
    kind: KubeadmControlPlane
    name: my-cluster-cp
```

#### MachineHealthCheck

```yaml
# Before
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineHealthCheck
spec:
  nodeStartupTimeout: 600

# After
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineHealthCheck
spec:
  nodeStartupTimeout: 10m
```

### Step 4: Update Monitoring/Alerting

Update queries that check conditions:

```yaml
# Before: check status.conditions
kubectl get cluster -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}'

# After: check status.v1beta2.conditions (when available)
kubectl get cluster -o jsonpath='{.status.v1beta2.conditions[?(@.type=="Available")].status}'
```

### Step 5: Update Automation

Update scripts that parse status:

```python
# Before
ready = status.get('phase') == 'Provisioned'

# After
conditions = status.get('v1beta2', {}).get('conditions', [])
ready = any(c['type'] == 'Available' and c['status'] == 'True' for c in conditions)
```

## Validation

```bash
# Check for deprecated patterns
python scripts/migration_checker.py --namespace default

# Verify conditions format
kubectl get cluster -o yaml | grep -A10 v1beta2

# Check no errors
kubectl logs -n capi-system -l control-plane=controller-manager | grep -i error
```

## Condition Type Mapping

| v1beta1 Condition   | v1beta2 Equivalent      | Notes                          |
| ------------------- | ----------------------- | ------------------------------ |
| Ready               | Available               | For Cluster, positive polarity |
| ControlPlaneReady   | ControlPlaneAvailable   |                                |
| InfrastructureReady | InfrastructureAvailable |                                |
| MachinesReady       | WorkersAvailable        |                                |
| Initialized         | Initialized             | Unchanged                      |

## Troubleshooting

### Conditions Not Appearing in v1beta2

Check feature gate is enabled:

```bash
kubectl get deploy -n capi-system capi-controller-manager -o yaml | grep -A5 args
```

### Old Automations Breaking

During transition, check both locations:

```python
# Compatibility check
def get_conditions(status):
    # Try v1beta2 first
    v1beta2 = status.get('v1beta2', {})
    if v1beta2.get('conditions'):
        return v1beta2['conditions']
    # Fall back to v1beta1
    return status.get('conditions', [])
```

### Mixed Version Clusters

If some clusters show v1beta2 and others don't:

- Ensure all providers are upgraded
- Check clusterctl versions match
- Verify feature gates consistent

## Rollback

If issues arise:

1. Revert to previous CAPI version
2. Revert manifest changes
3. Restore from backup if needed

```bash
clusterctl upgrade apply \
  --core cluster-api:v1.7.x \
  --bootstrap kubeadm:v1.7.x \
  --control-plane kubeadm:v1.7.x
```

## Timeline

- **v1.8**: v1beta2 conditions alpha
- **v1.9**: v1beta2 conditions beta
- **v1.12**: v1beta2 conditions GA
- **v1.14+**: v1beta1 conditions deprecated (planned)
- **v2.0**: v1beta1 conditions removed (planned)
