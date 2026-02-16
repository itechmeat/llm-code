# k8s-cluster-api

Agent skill for Kubernetes Cluster API (CAPI) - declarative cluster lifecycle management.

## Overview

This skill provides comprehensive guidance for:

- **clusterctl CLI** - Management cluster initialization, upgrades, and migrations
- **Cluster provisioning** - Create and manage Kubernetes clusters declaratively
- **Provider ecosystem** - Infrastructure, bootstrap, and control plane providers
- **Cluster operations** - Scaling, upgrading, health checking, autoscaling
- **Experimental features** - ClusterClass, MachinePools, Runtime SDK
- **Developer workflows** - Building custom providers, Tilt development

## Documentation Source

Based on [Cluster API documentation](https://cluster-api.sigs.k8s.io/) v1.12.

## Reference Files

| File                                                      | Content                                              |
| --------------------------------------------------------- | ---------------------------------------------------- |
| [getting-started.md](references/getting-started.md)       | Quick start, clusterctl installation, provider setup |
| [concepts.md](references/concepts.md)                     | Architecture, resources, provider types              |
| [certificates.md](references/certificates.md)             | Custom CA, kubeconfig generation, auto-rotation      |
| [bootstrap.md](references/bootstrap.md)                   | Kubeadm, MicroK8s bootstrap configuration            |
| [cluster-operations.md](references/cluster-operations.md) | Upgrades, scaling, autoscaling, health checks        |
| [experimental.md](references/experimental.md)             | ClusterClass, MachinePools, Runtime SDK              |
| [clusterctl.md](references/clusterctl.md)                 | CLI reference, all commands                          |
| [developer.md](references/developer.md)                   | Tilt setup, testing, provider contracts, IPAM        |
| [troubleshooting.md](references/troubleshooting.md)       | Common issues and solutions                          |
| [api-reference.md](references/api-reference.md)           | Version support, providers list, resource schemas    |
| [security.md](references/security.md)                     | Pod Security Standards, security guidelines          |
| [controllers.md](references/controllers.md)               | CAPI controller implementations                      |
| [migrations.md](references/migrations.md)                 | Version migration guides (v1.9→v1.12)                |
| [faq.md](references/faq.md)                               | Frequently asked questions                           |
| [best-practices.md](references/best-practices.md)         | Production guidelines and checklists                 |

## When to Use

- Provisioning Kubernetes clusters across cloud providers
- Managing multiple clusters declaratively
- Automating cluster operations
- Setting up management clusters
- Implementing GitOps for cluster management
- Building custom infrastructure providers

## Quick Start

```bash
# Install clusterctl
brew install clusterctl

# Initialize management cluster (Docker)
clusterctl init --infrastructure docker

# Create workload cluster
clusterctl generate cluster my-cluster \
  --kubernetes-version v1.32.0 \
  --control-plane-machine-count 1 \
  --worker-machine-count 3 | kubectl apply -f -

# Get kubeconfig
clusterctl get kubeconfig my-cluster > my-cluster.kubeconfig
```

## Supported Providers

**Infrastructure**: AWS, Azure, GCP, vSphere, Docker, Metal3, OpenStack, Hetzner, DigitalOcean, KubeVirt, Proxmox, and 30+ more

**Bootstrap**: Kubeadm, K3s, RKE2, Talos, MicroK8s

**Control Plane**: Kubeadm, K3s, RKE2, Talos, Kamaji

## Scripts

Utility scripts in `scripts/` directory:

| Script                         | Purpose                                            |
| ------------------------------ | -------------------------------------------------- |
| `validate_manifests.py`        | Validate YAML manifests against CRD schemas        |
| `run_clusterctl_diagnose.py`   | Run clusterctl describe and save diagnostic report |
| `migration_checker.py`         | Check v1beta1→v1beta2 migration readiness          |
| `check_cluster_health.py`      | Analyze conditions across all cluster objects      |
| `analyze_conditions.py`        | Parse and report False/Unknown conditions          |
| `scaffold_provider.py`         | Generate new provider directory structure          |
| `generate_cluster_template.py` | Generate templates from ClusterClass               |
| `export_cluster_state.py`      | Export cluster state for backup/move               |
| `audit_security.py`            | Check PSS compliance and security posture          |
| `timeline_events.py`           | Build provisioning event timeline                  |
| `compare_versions.py`          | Compare CAPI version specs and API changes         |
| `check_provider_contract.py`   | Verify provider CRD compliance with contracts      |
| `lint_cluster_templates.py`    | Lint and validate CAPI manifests                   |

### Usage Examples

```bash
# Validate manifests
python scripts/validate_manifests.py cluster.yaml

# Check cluster health
python scripts/check_cluster_health.py my-cluster -n default

# Run security audit
python scripts/audit_security.py --cluster my-cluster

# Check migration readiness
python scripts/migration_checker.py -n default

# Compare CAPI versions
python scripts/compare_versions.py v1.6.0 v1.12.0 --checklist

# Generate cluster from ClusterClass
python scripts/generate_cluster_template.py my-class --name prod --workers 3

# Export cluster state
python scripts/export_cluster_state.py my-cluster -o ./backup/

# Scaffold new provider
python scripts/scaffold_provider.py mycloud --type infra

# Build event timeline
python scripts/timeline_events.py my-cluster --since 1h
```

## Assets

Reusable templates in `assets/` directory:

### Cluster Templates

| File                        | Purpose                            |
| --------------------------- | ---------------------------------- |
| `cluster-minimal.yaml`      | Dev/test cluster (Docker provider) |
| `cluster-production.yaml`   | Production HA cluster (3 CP, MHC)  |
| `cluster-clusterclass.yaml` | Topology-based cluster creation    |
| `clusterclass-example.yaml` | ClusterClass with PSS variables    |

### Provider Configs

| File                     | Purpose                         |
| ------------------------ | ------------------------------- |
| `docker-quickstart.md`   | Docker provider setup guide     |
| `aws-credentials.yaml`   | AWS CAPA credentials template   |
| `azure-credentials.yaml` | Azure CAPZ credentials template |
| `provider-matrix.md`     | Version compatibility matrix    |

### Operations

| File                       | Purpose                         |
| -------------------------- | ------------------------------- |
| `upgrade-checklist.md`     | Pre/post upgrade checklist      |
| `migration-v1beta2.md`     | v1beta1→v1beta2 migration guide |
| `troubleshooting-flow.md`  | Diagnostic decision flowchart   |
| `security-audit-report.md` | Security audit report template  |
| `dr-backup-restore.md`     | Disaster recovery playbook      |
| `etcd-backup.yaml`         | Automated etcd backup CronJob   |

### GitOps

| File                      | Purpose                            |
| ------------------------- | ---------------------------------- |
| `argocd-cluster-app.yaml` | ArgoCD Application/ApplicationSet  |
| `flux-kustomization.yaml` | Flux GitRepository + Kustomization |
| `gitops-rbac.yaml`        | RBAC for GitOps controllers        |

### Monitoring

| File                     | Purpose                   |
| ------------------------ | ------------------------- |
| `prometheus-alerts.yaml` | Prometheus alerting rules |

## Links

- [Documentation](https://cluster-api.sigs.k8s.io/)
- [GitHub](https://github.com/kubernetes-sigs/cluster-api)
- [Releases](https://github.com/kubernetes-sigs/cluster-api/releases)
