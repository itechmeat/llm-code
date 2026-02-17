# Disaster Recovery: Backup and Restore Playbook

Complete playbook for backing up and restoring Cluster API management clusters.

## Overview

Management cluster failures can orphan workload clusters. This playbook covers:

- Regular backups of management cluster state
- Restoring CAPI controllers to new management cluster
- Reconnecting orphaned workload clusters
- Pivoting ownership between management clusters

## Prerequisites

- `kubectl` configured for management cluster
- `clusterctl` v1.6+
- `velero` (optional, for full cluster backup)
- Backup storage (S3, GCS, Azure Blob)

---

## Part 1: Backup Procedures

### 1.1 Export CAPI Resources

```bash
# Export all CAPI resources from management cluster
cd scripts && go run ./export-cluster-state --all -o ../backup/

# Or export specific cluster
go run ./export-cluster-state -n my-cluster -ns clusters -o ../backup/my-cluster/
```

### 1.2 Backup Secrets

```bash
# Export kubeconfig secrets (contains cluster access credentials)
kubectl get secrets -n clusters -l cluster.x-k8s.io/cluster-name -o yaml > backup/cluster-secrets.yaml

# Export provider credentials
kubectl get secrets -n capi-system -o yaml > backup/capi-secrets.yaml

# IMPORTANT: Encrypt secrets before storing!
# Using SOPS:
sops --encrypt backup/cluster-secrets.yaml > backup/cluster-secrets.enc.yaml
```

### 1.3 Backup etcd (Management Cluster)

```bash
# For kubeadm-based management clusters
# Run on control plane node:

ETCDCTL_API=3 etcdctl snapshot save /tmp/etcd-backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Copy backup off the node
kubectl cp kube-system/etcd-<node>:/tmp/etcd-backup.db ./backup/etcd-backup.db
```

### 1.4 Automated Backup with CronJob

Apply [etcd-backup.yaml](etcd-backup.yaml) for scheduled backups.

---

## Part 2: Restore Procedures

### 2.1 Scenario: New Management Cluster

When creating a fresh management cluster to take over orphaned workload clusters.

#### Step 1: Create New Management Cluster

```bash
# Option A: Use kind for temporary management
kind create cluster --name capi-recovery

# Option B: Use existing cluster
kubectl config use-context recovery-cluster
```

#### Step 2: Initialize CAPI Components

```bash
# Install same providers as original management cluster
clusterctl init \
  --infrastructure aws \
  --control-plane kubeadm \
  --bootstrap kubeadm

# Wait for controllers
kubectl wait --for=condition=Available deployment -n capi-system --all --timeout=300s
```

#### Step 3: Restore Provider Credentials

```bash
# Decrypt and apply secrets
sops --decrypt backup/capi-secrets.enc.yaml | kubectl apply -f -
sops --decrypt backup/cluster-secrets.enc.yaml | kubectl apply -f -
```

#### Step 4: Import Cluster Definitions

```bash
# Apply exported CAPI resources
kubectl apply -f backup/clusters/

# Verify cluster objects exist
kubectl get clusters -A
```

#### Step 5: Reconnect to Workload Clusters

```bash
# For each workload cluster, verify connectivity
clusterctl describe cluster my-cluster -n clusters

# If cluster shows "Paused", unpause it
kubectl patch cluster my-cluster -n clusters --type=merge -p '{"spec":{"paused":false}}'
```

### 2.2 Scenario: Pivot Between Management Clusters

Move CAPI resources from one management cluster to another.

```bash
# On source management cluster
clusterctl move \
  --to-kubeconfig=/path/to/target-management.kubeconfig \
  --namespace=clusters

# Verify on target
kubectl --kubeconfig=/path/to/target-management.kubeconfig get clusters -A
```

### 2.3 Scenario: etcd Restore

Restore management cluster from etcd snapshot.

```bash
# On control plane node, stop API server
sudo mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/

# Restore etcd
ETCDCTL_API=3 etcdctl snapshot restore /tmp/etcd-backup.db \
  --data-dir=/var/lib/etcd-restore \
  --name=<node-name> \
  --initial-cluster=<node-name>=https://<node-ip>:2380 \
  --initial-advertise-peer-urls=https://<node-ip>:2380

# Replace etcd data
sudo mv /var/lib/etcd /var/lib/etcd.bak
sudo mv /var/lib/etcd-restore /var/lib/etcd

# Restart API server
sudo mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/
```

---

## Part 3: Verification Checklist

After restore, verify:

- [ ] All Cluster objects exist: `kubectl get clusters -A`
- [ ] All Machines are Running: `kubectl get machines -A`
- [ ] Control planes healthy: `kubectl get kcp -A`
- [ ] Kubeconfigs work: `clusterctl get kubeconfig <cluster> -n <ns>`
- [ ] Workload cluster API reachable
- [ ] Node count matches expected
- [ ] Cluster conditions all True

```bash
# Quick health check script
cd scripts && go run ./check-cluster-health --all
```

---

## Part 4: Orphaned Cluster Recovery

When management cluster is completely lost.

### 4.1 Workload Cluster Still Running

The workload cluster continues to function; only management is lost.

```bash
# 1. Create new management cluster and init CAPI
kind create cluster --name capi-recovery
clusterctl init --infrastructure <provider>

# 2. Recreate cluster manifests from backup or documentation
kubectl apply -f backup/my-cluster/

# 3. CAPI will discover existing infrastructure via provider
# The InfrastructureRef objects will reconcile with existing VMs/nodes
```

### 4.2 Adopt Pattern (Manual)

If no backup exists, manually recreate CAPI objects:

```bash
# 1. Get cluster info from workload cluster
kubectl --kubeconfig=workload.kubeconfig get nodes -o wide
kubectl --kubeconfig=workload.kubeconfig cluster-info

# 2. Create minimal Cluster object (paused)
cat <<EOF | kubectl apply -f -
apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  name: recovered-cluster
  namespace: clusters
spec:
  paused: true
  controlPlaneEndpoint:
    host: <api-server-ip>
    port: 6443
EOF

# 3. Create Machine objects for existing nodes
# Match providerID from node spec
```

---

## Part 5: Prevention Best Practices

1. **Regular Backups**: Schedule daily backups via CronJob
2. **Multiple Management Clusters**: Run HA or standby management
3. **GitOps**: Store all manifests in Git for easy recreation
4. **Documentation**: Document provider-specific recovery steps
5. **Test Restores**: Quarterly disaster recovery drills

---

## Related Assets

- [etcd-backup.yaml](etcd-backup.yaml) - CronJob for automated etcd backups
- [upgrade-checklist.md](upgrade-checklist.md) - Pre-upgrade backup checklist

## Related Scripts

- `scripts/export-cluster-state` - Export CAPI resources (`go run ./export-cluster-state`)
- `scripts/check-cluster-health` - Verify cluster health post-restore (`go run ./check-cluster-health`)
