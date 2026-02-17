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

Go-based utility tools in `scripts/` directory. Run via `go run ./tool-name` from the `scripts/` folder.

| Tool                        | Purpose                                            |
| --------------------------- | -------------------------------------------------- |
| `validate-manifests`        | Validate YAML manifests against CRD schemas        |
| `run-clusterctl-diagnose`   | Run clusterctl describe and save diagnostic report |
| `migration-checker`         | Check v1beta1→v1beta2 migration readiness          |
| `check-cluster-health`      | Analyze conditions across all cluster objects      |
| `analyze-conditions`        | Parse and report False/Unknown conditions          |
| `scaffold-provider`         | Generate new provider directory structure          |
| `generate-cluster-template` | Generate templates from ClusterClass               |
| `export-cluster-state`      | Export cluster state for backup/move               |
| `audit-security`            | Check PSS compliance and security posture          |
| `timeline-events`           | Build provisioning event timeline                  |
| `compare-versions`          | Compare CAPI version specs and API changes         |
| `check-provider-contract`   | Verify provider CRD compliance with contracts      |
| `lint-cluster-templates`    | Lint and validate CAPI manifests                   |

### Usage Examples

```bash
# From the scripts/ directory:
cd scripts/

# Validate manifests
go run ./validate-manifests cluster.yaml

# Check cluster health
go run ./check-cluster-health -n my-cluster -ns default

# Run security audit
go run ./audit-security -n my-cluster

# Check migration readiness
go run ./migration-checker -ns default

# Compare CAPI versions
go run ./compare-versions v1.6.0 v1.12.0 --checklist

# Generate cluster from ClusterClass
go run ./generate-cluster-template --class my-class -n prod --worker-replicas 3

# Export cluster state
go run ./export-cluster-state -n my-cluster -o ../backup/

# Scaffold new provider
go run ./scaffold-provider -n mycloud -t infrastructure

# Build event timeline
go run ./timeline-events -n my-cluster --since 1h
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
| `docker-quickstart.yaml` | Docker provider setup guide     |
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
