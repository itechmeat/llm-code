# Cluster API Best Practices

Production guidelines for managing Kubernetes clusters with Cluster API.

## Management Cluster

### High Availability

**Requirement**: Production management clusters MUST be highly available.

```yaml
# Minimum HA configuration
controlPlane:
  replicas: 3

# Across availability zones
spec:
  infrastructureRef:
    topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
```

### Isolation

- **Dedicated cluster**: Don't run workloads on management cluster
- **Separate failure domain**: Management cluster in different region/account than workloads
- **Limited access**: Only cluster administrators access management cluster

### Backup Strategy

| What                     | Frequency | Retention           |
| ------------------------ | --------- | ------------------- |
| etcd snapshot            | Daily     | 30 days             |
| CAPI resources           | Daily     | 30 days             |
| Provider credentials     | On change | Forever (versioned) |
| ClusterClass definitions | On change | Git history         |

Use automated backup: [etcd-backup.yaml](../assets/etcd-backup.yaml)

## Workload Clusters

### Naming Conventions

```
<environment>-<purpose>-<region>-<sequence>
```

Examples:

- `prod-api-us-east-001`
- `staging-ml-eu-west-001`
- `dev-team-alpha-001`

### Labels and Annotations

Required labels:

```yaml
metadata:
  labels:
    environment: production
    team: platform
    cost-center: engineering
    cluster-api.cattle.io/version: "1.28"
```

### Resource Sizing

| Workload Type | Control Plane | Workers         |
| ------------- | ------------- | --------------- |
| Dev/Test      | 1 × t3.medium | 1-3 × t3.medium |
| Staging       | 3 × t3.large  | 3-5 × t3.large  |
| Production    | 3 × t3.xlarge | 5+ × t3.xlarge  |

Control plane sizing rules:

- 100 nodes: 2 vCPU, 8GB RAM
- 500 nodes: 4 vCPU, 16GB RAM
- 1000+ nodes: 8 vCPU, 32GB RAM

## Security

### Pod Security Standards

**MANDATORY**: All CAPI namespaces MUST enforce PSS.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: clusters
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### RBAC

Principle of least privilege:

```yaml
# Cluster creators (can create, not delete)
rules:
  - apiGroups: ["cluster.x-k8s.io"]
    resources: ["clusters"]
    verbs: ["get", "list", "watch", "create", "patch"]

# Cluster operators (full access)
rules:
  - apiGroups: ["cluster.x-k8s.io"]
    resources: ["*"]
    verbs: ["*"]
```

### Secrets Management

**NEVER**:

- Commit credentials to Git
- Use hardcoded credentials in manifests
- Share credentials across environments

**ALWAYS**:

- Use external secrets management (Vault, AWS Secrets Manager)
- Rotate credentials regularly
- Audit secret access

```yaml
# Use external secrets operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: cloud-credentials
spec:
  secretStoreRef:
    name: vault
```

### Network Policies

Restrict management cluster network:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: capi-deny-all
  namespace: capi-system
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
  egress:
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
      ports:
        - protocol: TCP
          port: 443 # Cloud API only
```

## Operations

### Health Monitoring

Required checks:

- [ ] Cluster conditions all True
- [ ] Machine Ready conditions
- [ ] Control plane availability (>66%)
- [ ] Certificate expiration (30-day warning)
- [ ] Provider quota usage

Implement with: [prometheus-alerts.yaml](../assets/prometheus-alerts.yaml)

### MachineHealthCheck Configuration

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: MachineHealthCheck
metadata:
  name: production-mhc
spec:
  clusterName: prod-cluster
  maxUnhealthy: 40% # Don't remediate if >40% unhealthy
  nodeStartupTimeout: 10m
  unhealthyConditions:
    - type: Ready
      status: "False"
      timeout: 5m # Give nodes time to recover
    - type: Ready
      status: Unknown
      timeout: 5m
```

Best practices:

- Set `maxUnhealthy` to prevent cascade failures
- Allow sufficient `nodeStartupTimeout` for bootstrap
- Don't make `timeout` too aggressive

### Upgrade Strategy

1. **Staging first**: Always test upgrades in staging
2. **One version at a time**: Never skip Kubernetes minor versions
3. **Schedule maintenance**: Upgrade during low-traffic windows
4. **Backup before upgrade**: Full etcd and CAPI resource backup
5. **Monitor rollout**: Watch MachineDeployment/KCP status

Pre-upgrade checklist: [upgrade-checklist.md](../assets/upgrade-checklist.md)

### Scaling Best Practices

Control plane:

- Always odd numbers (1, 3, 5) for etcd quorum
- Scale up before high-load events
- Monitor etcd storage usage

Workers:

- Use MachineDeployments for stateless workers
- Set PodDisruptionBudgets before scaling down
- Consider cluster autoscaler for dynamic workloads

```yaml
# Autoscaler annotations
metadata:
  annotations:
    cluster.x-k8s.io/cluster-api-autoscaler-node-group-min-size: "3"
    cluster.x-k8s.io/cluster-api-autoscaler-node-group-max-size: "10"
```

## GitOps Integration

### Repository Structure

```
clusters/
├── base/                    # Shared ClusterClasses
│   └── clusterclass.yaml
├── production/
│   ├── kustomization.yaml
│   └── cluster.yaml
└── staging/
    ├── kustomization.yaml
    └── cluster.yaml
```

### Review Process

All cluster changes MUST:

1. Pass CI validation (lint, schema check)
2. Require approval from platform team
3. Apply to staging before production
4. Have rollback plan documented

### Drift Detection

Configure GitOps tool to alert on drift:

```yaml
# ArgoCD Application
spec:
  syncPolicy:
    automated:
      selfHeal: true # Auto-correct drift
      prune: false # Don't auto-delete
```

## Disaster Recovery

### RTO/RPO Targets

| Scenario                        | RTO    | RPO |
| ------------------------------- | ------ | --- |
| Management cluster failure      | 30 min | 24h |
| Single workload cluster failure | 15 min | 0   |
| Multi-cluster failure           | 2h     | 24h |

### Runbooks

Document for each cluster:

- [ ] Contact escalation path
- [ ] Recovery procedure
- [ ] Required credentials/access
- [ ] Verification steps

DR playbook: [dr-backup-restore.md](../assets/dr-backup-restore.md)

## Cost Optimization

### Right-sizing

- Use spot/preemptible instances for dev/test
- Implement cluster autoscaler
- Delete unused clusters (test clusters, POCs)
- Consider smaller machine types for control plane in dev

### Monitoring

Track metrics:

- Cluster count by environment
- Node count per cluster
- Idle cluster detection (low utilization >7 days)

## Documentation

Every production cluster MUST have:

1. **Architecture diagram**: Network topology, dependencies
2. **Runbook**: Day-to-day operations
3. **On-call guide**: Incident response
4. **Change history**: What/when/why

## Checklist: Production Readiness

- [ ] HA management cluster (3+ control plane nodes)
- [ ] Automated backups configured and tested
- [ ] Monitoring and alerting configured
- [ ] PSS enforced on all namespaces
- [ ] Network policies applied
- [ ] RBAC configured with least privilege
- [ ] GitOps integration with approval workflow
- [ ] DR procedure documented and tested
- [ ] On-call rotation established
- [ ] Upgrade procedure documented
