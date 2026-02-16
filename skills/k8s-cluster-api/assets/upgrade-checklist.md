# Cluster Upgrade Checklist

Pre-flight and execution checklist for upgrading CAPI-managed clusters.

## Pre-Upgrade Assessment

### Environment Check

- [ ] Verify current CAPI version: `clusterctl version`
- [ ] List installed providers: `kubectl get providers -A`
- [ ] Check target version compatibility (see `provider-matrix.md`)
- [ ] Review release notes for breaking changes
- [ ] Verify Kubernetes version support matrix

### Cluster Health Check

- [ ] All clusters Ready: `kubectl get clusters -A`
- [ ] All machines Ready: `kubectl get machines -A`
- [ ] No unhealthy conditions: `kubectl get clusters -A -o yaml | grep -A5 conditions`
- [ ] Control planes initialized: `kubectl get kubeadmcontrolplanes -A`
- [ ] MachineHealthChecks not triggering: `kubectl get mhc -A`

### Backup (CRITICAL)

- [ ] Export cluster state:

  ```bash
  # Option 1: clusterctl move to backup cluster
  clusterctl move --to-kubeconfig backup-cluster.kubeconfig

  # Option 2: Export manifests
  python scripts/export_cluster_state.py <cluster-name> -o ./backup/
  ```

- [ ] Save kubeconfigs for all clusters
- [ ] Document current configuration

## Upgrade Plan

### 1. Generate Upgrade Plan

```bash
clusterctl upgrade plan
```

Review output:

- [ ] Note current versions
- [ ] Note target versions
- [ ] Identify any warnings

### 2. Upgrade Management Cluster CAPI Components

```bash
# Upgrade CAPI core
clusterctl upgrade apply --contract v1beta1

# Or specify versions
clusterctl upgrade apply \
  --core cluster-api:v1.12.0 \
  --bootstrap kubeadm:v1.12.0 \
  --control-plane kubeadm:v1.12.0 \
  --infrastructure <provider>:v<version>
```

- [ ] Core upgraded successfully
- [ ] Bootstrap provider upgraded
- [ ] Control plane provider upgraded
- [ ] Infrastructure provider upgraded

### 3. Verify Management Cluster

- [ ] All pods running: `kubectl get pods -n capi-system`
- [ ] Provider pods running: `kubectl get pods -n <provider>-system`
- [ ] CRDs updated: `kubectl get crds | grep cluster.x-k8s.io`
- [ ] No errors in logs: `kubectl logs -n capi-system -l control-plane=controller-manager`

## Workload Cluster Upgrades

### Per-Cluster Upgrade

For each workload cluster:

#### Pre-Upgrade

- [ ] Cluster name: ********\_********
- [ ] Current K8s version: ********\_********
- [ ] Target K8s version: ********\_********
- [ ] Backup completed: [ ]

#### Upgrade Control Plane

```bash
# Update KubeadmControlPlane version
kubectl patch kcp <cluster>-control-plane -n <namespace> \
  --type merge -p '{"spec":{"version":"v1.XX.Y"}}'
```

- [ ] Version field updated
- [ ] Rollout started: `kubectl get machines -l cluster.x-k8s.io/control-plane`
- [ ] Monitor progress: `clusterctl describe cluster <name>`

#### Wait for Control Plane

- [ ] All control plane machines updated
- [ ] Control plane Ready
- [ ] API server accessible

#### Upgrade Workers

```bash
# Update MachineDeployment version
kubectl patch machinedeployment <cluster>-md-0 -n <namespace> \
  --type merge -p '{"spec":{"template":{"spec":{"version":"v1.XX.Y"}}}}'
```

- [ ] Version field updated
- [ ] Rolling update started
- [ ] Old machines draining
- [ ] New machines Ready

#### Post-Cluster Verification

- [ ] All nodes updated: `kubectl --kubeconfig=<cluster>.kubeconfig get nodes`
- [ ] Workloads healthy
- [ ] No pod disruptions

## Post-Upgrade Validation

### Management Cluster

- [ ] `clusterctl describe cluster` shows no issues
- [ ] All clusters transitioned to Ready
- [ ] Provider logs clean

### Workload Clusters

For each cluster:

- [ ] Kubernetes version correct
- [ ] All nodes Ready
- [ ] CoreDNS running
- [ ] CNI functioning
- [ ] Workloads healthy
- [ ] Ingress working
- [ ] Persistent volumes accessible

### Monitoring & Alerts

- [ ] Metrics being collected
- [ ] Dashboards updated
- [ ] No new alerts triggered

## Rollback Plan (If Needed)

### CAPI Component Rollback

```bash
# Revert to previous version
clusterctl upgrade apply \
  --core cluster-api:v<previous> \
  --bootstrap kubeadm:v<previous> \
  --control-plane kubeadm:v<previous> \
  --infrastructure <provider>:v<previous>
```

### Cluster Rollback

1. Restore from backup (clusterctl move back)
2. Or re-create from saved manifests

## Sign-Off

| Role     | Name | Date | Signature |
| -------- | ---- | ---- | --------- |
| Operator |      |      |           |
| Reviewer |      |      |           |
| Approver |      |      |           |

## Notes

_Record any issues, deviations, or observations:_

---

Upgrade completed: [ ] Yes [ ] No (with issues)

Date: ******\_\_\_******

Duration: ******\_\_\_******
