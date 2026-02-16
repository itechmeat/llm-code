# Cluster API FAQ

Frequently asked questions about Cluster API operations.

## General

### What is the difference between management and workload clusters?

**Management Cluster**: Runs CAPI controllers that manage the lifecycle of workload clusters. Contains Cluster, Machine, and other CAPI resources.

**Workload Cluster**: The actual Kubernetes cluster where applications run. Created and managed by resources in the management cluster.

### Can a cluster be both management and workload?

Yes, but not recommended for production. The management cluster can run workloads, but for reliability:

- Keep management cluster dedicated to CAPI operations
- Consider high availability for management cluster
- Isolate failure domains

### How do I check which CAPI version is installed?

```bash
clusterctl version
kubectl get deployments -n capi-system -o jsonpath='{.items[0].spec.template.spec.containers[0].image}'
```

## Cluster Operations

### Why is my cluster stuck in "Provisioning"?

Common causes:

1. **Infrastructure issues**: Cloud provider quota, permissions, or API errors
2. **Control plane bootstrap**: Kubeadm bootstrap timing out
3. **Network issues**: VPC/subnet misconfiguration

Debug steps:

```bash
# Check cluster conditions
clusterctl describe cluster <name> -n <namespace>

# Check Machine events
kubectl describe machine -n <namespace> -l cluster.x-k8s.io/cluster-name=<name>

# Check provider-specific resources
kubectl get <provider>machines -n <namespace>
```

### How do I delete a stuck cluster?

If normal deletion hangs:

```bash
# 1. Check for finalizers
kubectl get cluster <name> -n <namespace> -o jsonpath='{.metadata.finalizers}'

# 2. If infrastructure is already deleted, remove finalizer
kubectl patch cluster <name> -n <namespace> \
  -p '{"metadata":{"finalizers":null}}' --type=merge

# 3. For machines
kubectl patch machine <name> -n <namespace> \
  -p '{"metadata":{"finalizers":null}}' --type=merge
```

**Warning**: Only remove finalizers if you're certain infrastructure is cleaned up!

### How do I pause cluster reconciliation?

```bash
# Pause
kubectl patch cluster <name> -n <namespace> \
  --type=merge -p '{"spec":{"paused":true}}'

# Unpause
kubectl patch cluster <name> -n <namespace> \
  --type=merge -p '{"spec":{"paused":false}}'
```

## Upgrades

### How do I upgrade Kubernetes version?

For topology-based clusters (ClusterClass):

```bash
kubectl patch cluster <name> -n <namespace> \
  --type=merge -p '{"spec":{"topology":{"version":"v1.29.0"}}}'
```

For non-ClusterClass clusters:

```bash
# Update KubeadmControlPlane
kubectl patch kubeadmcontrolplane <name> -n <namespace> \
  --type=merge -p '{"spec":{"version":"v1.29.0"}}'

# Then update MachineDeployments
kubectl patch machinedeployment <name>-md-0 -n <namespace> \
  --type=merge -p '{"spec":{"template":{"spec":{"version":"v1.29.0"}}}}'
```

### What's the upgrade order?

1. Management cluster CAPI components (`clusterctl upgrade apply`)
2. Workload cluster control plane
3. Workload cluster workers

Never skip versions (e.g., 1.27→1.29). Always upgrade sequentially.

### Can I rollback a failed upgrade?

Control plane: No automatic rollback. The upgrade process is designed to be safe and non-destructive. If upgrade fails mid-way:

- Investigate the cause (usually node bootstrap issues)
- Fix the issue and retry
- Manual intervention may be needed

Workers: Rolling updates can be stopped by pausing the cluster.

## Providers

### Which provider should I use?

| Provider         | Use Case              |
| ---------------- | --------------------- |
| Docker (CAPD)    | Local dev, CI testing |
| AWS (CAPA)       | Production on AWS     |
| Azure (CAPZ)     | Production on Azure   |
| GCP (CAPG)       | Production on GCP     |
| vSphere (CAPV)   | On-premises VMware    |
| Metal3 (CAPM3)   | Bare metal            |
| OpenStack (CAPO) | OpenStack clouds      |

### How do I switch providers?

You can't migrate a cluster between providers. To switch:

1. Create new cluster with new provider
2. Migrate workloads (backup/restore)
3. Delete old cluster

### Provider credentials rotated. Now what?

Update the secret containing credentials:

```bash
kubectl create secret generic <provider>-credentials \
  --from-file=credentials=new-creds.json \
  --dry-run=client -o yaml | kubectl apply -f -
```

Controllers will pick up new credentials. No cluster restart needed.

## ClusterClass / Topology

### What's the benefit of ClusterClass?

- **Standardization**: Define cluster "blueprint" once
- **Simplified updates**: Change ClusterClass, all clusters update
- **Variables**: Customize without duplicating manifests
- **Patches**: Inject provider-specific configuration

### When should I NOT use ClusterClass?

- Very simple, single-cluster setup
- Provider doesn't support ClusterClass well
- Need fine-grained control over each resource

### How do I update all clusters using a ClusterClass?

Changes to ClusterClass propagate automatically to all Clusters using it. The reconciliation respects rollout strategies.

```bash
# Edit ClusterClass
kubectl edit clusterclass <name>

# Monitor rollout
kubectl get clusters -l topology.cluster.x-k8s.io/owned
```

## Troubleshooting

### Machines keep getting replaced

Check MachineHealthCheck settings:

```bash
kubectl get machinehealthcheck -n <namespace>
kubectl describe machinehealthcheck <name> -n <namespace>
```

Common causes:

- Unhealthy conditions threshold too aggressive
- Node not ready due to CNI issues
- kubelet problems

### "Error: failed to get provider components"

clusterctl can't fetch provider manifests:

1. Check internet connectivity
2. Verify `~/.cluster-api/clusterctl.yaml` configuration
3. Try explicit version: `clusterctl init --infrastructure aws:v2.0.0`

### etcd cluster unhealthy after scaling

etcd is sensitive to cluster membership. After scaling control plane:

```bash
# Check etcd health
kubectl exec -n kube-system etcd-<node> -- etcdctl \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  endpoint health --cluster
```

If unhealthy, you may need to manually remove stale members.

## Migration

### Migrating from kubeadm to CAPI

CAPI doesn't adopt existing non-CAPI clusters. Options:

1. Create new CAPI-managed cluster, migrate workloads
2. Use `clusterctl move` for existing CAPI clusters only

### v1alpha3/v1alpha4 to v1beta1

See [migration-v1beta2.md](../assets/migration-v1beta2.md) for detailed guide.

## Resources

- [Official Documentation](https://cluster-api.sigs.k8s.io/)
- [GitHub Issues](https://github.com/kubernetes-sigs/cluster-api/issues)
- [Kubernetes Slack #cluster-api](https://kubernetes.slack.com/messages/cluster-api)
