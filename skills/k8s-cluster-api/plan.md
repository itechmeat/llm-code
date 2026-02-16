# k8s-cluster-api Skill Plan

## Overview

- **Product**: Kubernetes Cluster API
- **Version**: v1.12
- **Source**: https://cluster-api.sigs.k8s.io/
- **Purpose**: Declarative APIs and tooling to simplify provisioning, upgrading, and operating multiple Kubernetes clusters
- **Status**: Completed (92/92 pages)

## Pages Checklist (92 pages total)

### 0. Introduction & Concepts (5 pages)

- [x] 0.1 Introduction `/introduction` → SKILL.md
- [x] 0.2 Quick Start `/user/quick-start` → references/getting-started.md
- [x] 0.3 Quick Start Operator `/user/quick-start-operator` → references/getting-started.md
- [x] 0.4 Concepts `/user/concepts` → references/concepts.md
- [x] 0.5 Manifesto `/user/manifesto` → references/concepts.md

### 1. Tasks (32 pages)

#### 1.1 Certificate Management (4 pages)

- [x] 1.1.0 Certificate Management `/tasks/certs/` (index only)
- [x] 1.1.1 Using Custom Certificates `/tasks/certs/using-custom-certificates` → references/certificates.md
- [x] 1.1.2 Generating a Kubeconfig `/tasks/certs/generate-kubeconfig` → references/certificates.md
- [x] 1.1.3 Auto Rotate Certificates in KCP `/tasks/certs/auto-rotate-certificates-in-kcp` → references/certificates.md

#### 1.2 Bootstrap (4 pages)

- [x] 1.2.0 Bootstrap `/tasks/bootstrap/` (index only)
- [x] 1.2.1 Kubeadm based bootstrap `/tasks/bootstrap/kubeadm-bootstrap/` → references/bootstrap.md
- [x] 1.2.1.1 Kubelet configuration `/tasks/bootstrap/kubeadm-bootstrap/kubelet-config` → references/bootstrap.md
- [x] 1.2.2 MicroK8s based bootstrap `/tasks/bootstrap/microk8s-bootstrap` → references/bootstrap.md

#### 1.3-1.9 Core Tasks (8 pages)

- [x] 1.3 Upgrading management and workload clusters `/tasks/upgrading-clusters` → references/cluster-operations.md
- [x] 1.4 External etcd `/tasks/external-etcd` → references/cluster-operations.md
- [x] 1.5 Using kustomize `/tasks/using-kustomize` → references/cluster-operations.md
- [x] 1.6 Upgrading Cluster API components `/tasks/upgrading-cluster-api-versions` → references/cluster-operations.md
- [x] 1.7.0 Control plane management `/tasks/control-plane/` (index only)
- [x] 1.7.1 Kubeadm based control plane management `/tasks/control-plane/kubeadm-control-plane` → references/cluster-operations.md
- [x] 1.7.2 MicroK8s based control plane management `/tasks/control-plane/microk8s-control-plane` → references/cluster-operations.md
- [x] 1.8 Updating Machine Infrastructure and Bootstrap Templates `/tasks/updating-machine-templates` → references/cluster-operations.md

#### 1.9-1.10 GitOps & Machine Management (6 pages)

- [x] 1.9 Workload bootstrap using GitOps `/tasks/workload-bootstrap-gitops` → references/cluster-operations.md
- [x] 1.10.0 Automated Machine management `/tasks/automated-machine-management/` (index only)
- [x] 1.10.1 Scaling `/tasks/automated-machine-management/scaling` → references/cluster-operations.md
- [x] 1.10.2 Autoscaling `/tasks/automated-machine-management/autoscaling` → references/cluster-operations.md
- [x] 1.10.3 Healthchecking `/tasks/automated-machine-management/healthchecking` → references/cluster-operations.md
- [x] 1.10.4 Machine deletion process `/tasks/automated-machine-management/machine_deletions` → references/cluster-operations.md

#### 1.11 Experimental Features (10 pages)

- [x] 1.11.0 Experimental Features `/tasks/experimental-features/experimental-features` → references/experimental.md
- [x] 1.11.1 MachinePools `/tasks/experimental-features/machine-pools` → references/experimental.md
- [x] 1.11.2 MachineSetPreflightChecks `/tasks/experimental-features/machineset-preflight-checks` → references/experimental.md
- [x] 1.11.3.0 ClusterClass `/tasks/experimental-features/cluster-class/` → references/experimental.md
- [x] 1.11.3.1 Writing a ClusterClass `/tasks/experimental-features/cluster-class/write-clusterclass` → references/experimental.md
- [x] 1.11.3.2 Changing a ClusterClass `/tasks/experimental-features/cluster-class/change-clusterclass` → references/experimental.md
- [x] 1.11.3.3 Operating a managed Cluster `/tasks/experimental-features/cluster-class/operate-cluster` → references/experimental.md
- [x] 1.11.4.0 Runtime SDK `/tasks/experimental-features/runtime-sdk/` → references/experimental.md
- [x] 1.11.4.1 Implementing Runtime Extensions `/tasks/experimental-features/runtime-sdk/implement-extensions` → references/experimental.md
- [x] 1.11.4.2 Implementing In-Place Update Hooks `/tasks/experimental-features/runtime-sdk/implement-in-place-update-hooks` → references/experimental.md
- [x] 1.11.4.3 Implementing Lifecycle Hook Extensions `/tasks/experimental-features/runtime-sdk/implement-lifecycle-hooks` → references/experimental.md
- [x] 1.11.4.4 Implementing Topology Mutation Hook Extensions `/tasks/experimental-features/runtime-sdk/implement-topology-mutation-hook` → references/experimental.md
- [x] 1.11.4.5 Implementing Upgrade Plan Runtime Extensions `/tasks/experimental-features/runtime-sdk/implement-upgrade-plan-hooks` → references/experimental.md
- [x] 1.11.4.6 Deploying Runtime Extensions `/tasks/experimental-features/runtime-sdk/deploy-runtime-extension` → references/experimental.md
- [x] 1.11.5 Ignition Bootstrap configuration `/tasks/experimental-features/ignition` → references/experimental.md

#### 1.12-1.15 Additional Tasks (4 pages)

- [x] 1.12 Running multiple providers `/tasks/multiple-providers` → references/cluster-operations.md
- [x] 1.13 Verification of Container Images `/tasks/verify-container-images` → references/cluster-operations.md
- [x] 1.14 Diagnostics `/tasks/diagnostics` → references/cluster-operations.md
- [x] 1.15 ClusterResourceSet `/tasks/cluster-resource-set` → references/cluster-operations.md

### 2. Security Guidelines (3 pages)

- [x] 2.0 Security Guidelines `/security/` → references/security.md
- [x] 2.1 Pod Security Standards `/security/pod-security-standards` → references/security.md
- [x] 2.2 Security Guidelines for Cluster API Users `/security/security-guidelines` → references/security.md

### 3. clusterctl CLI (17 pages)

- [x] 3.0 clusterctl Overview `/clusterctl/overview` → references/clusterctl.md
- [x] 3.1.0 clusterctl Commands `/clusterctl/commands/commands` → references/clusterctl.md
- [x] 3.1.1 init `/clusterctl/commands/init` → references/clusterctl.md
- [x] 3.1.2 generate cluster `/clusterctl/commands/generate-cluster` → references/clusterctl.md
- [x] 3.1.3 generate provider `/clusterctl/commands/generate-provider` → references/clusterctl.md
- [x] 3.1.4 generate yaml `/clusterctl/commands/generate-yaml` → references/clusterctl.md
- [x] 3.1.5 get kubeconfig `/clusterctl/commands/get-kubeconfig` → references/clusterctl.md
- [x] 3.1.6 describe cluster `/clusterctl/commands/describe-cluster` → references/clusterctl.md
- [x] 3.1.7 move `/clusterctl/commands/move` → references/clusterctl.md
- [x] 3.1.8 upgrade `/clusterctl/commands/upgrade` → references/clusterctl.md
- [x] 3.1.9 delete `/clusterctl/commands/delete` → references/clusterctl.md
- [x] 3.1.10 completion `/clusterctl/commands/completion` → references/clusterctl.md
- [x] 3.1.11 alpha rollout `/clusterctl/commands/alpha-rollout` → references/clusterctl.md
- [x] 3.1.12 additional commands `/clusterctl/commands/additional-commands` → references/clusterctl.md
- [x] 3.2 clusterctl Configuration `/clusterctl/configuration` → references/clusterctl.md
- [x] 3.3 clusterctl for Developers `/clusterctl/developers` → references/clusterctl.md
- [x] 3.4 clusterctl Extensions with Plugins `/clusterctl/plugins` → references/clusterctl.md

### 4. Developer Guide (31 pages)

#### 4.0 Getting Started

- [x] 4.0 Developer Getting Started `/developer/getting-started` → references/developer.md

#### 4.1 Developing "core" Cluster API (12 pages)

- [x] 4.1.0 Core Overview `/developer/core/overview` → references/developer.md
- [x] 4.1.1 Rapid iterative development with Tilt `/developer/core/tilt` → references/developer.md
- [x] 4.1.2 Repository Layout `/developer/core/repository-layout` → references/developer.md
- [x] 4.1.3.0 Controllers Overview `/developer/core/controllers/overview` → references/developer.md
- [x] 4.1.3.1 Cluster controller `/developer/core/controllers/cluster` → references/developer.md
- [x] 4.1.3.2 ClusterTopology controller `/developer/core/controllers/cluster-topology` → references/developer.md
- [x] 4.1.3.3 ClusterResourceSet controller `/developer/core/controllers/cluster-resource-set` → references/developer.md
- [x] 4.1.3.4 MachineDeployment controller `/developer/core/controllers/machine-deployment` → references/developer.md
- [x] 4.1.3.5 MachineSet controller `/developer/core/controllers/machine-set` → references/developer.md
- [x] 4.1.3.6 Machine controller `/developer/core/controllers/machine` → references/developer.md
- [x] 4.1.3.7 MachinePool controller `/developer/core/controllers/machine-pool` → references/developer.md
- [x] 4.1.3.8 MachineHealthCheck controller `/developer/core/controllers/machine-health-check` → references/developer.md
- [x] 4.1.4 Logging `/developer/core/logging` → references/developer.md
- [x] 4.1.5 Testing `/developer/core/testing` → references/developer.md
- [x] 4.1.6 Developing E2E tests `/developer/core/e2e` → references/developer.md
- [x] 4.1.7 Tuning controllers `/developer/core/tuning` → references/developer.md
- [x] 4.1.8 Support multiple instances `/developer/core/support-multiple-instances` → references/developer.md

#### 4.2 Developing providers (18 pages)

- [x] 4.2.0 Providers Overview `/developer/providers/overview` → references/developer.md
- [x] 4.2.1.0 Getting started Overview `/developer/providers/getting-started/overview` → references/developer.md
- [x] 4.2.1.1 Naming `/developer/providers/getting-started/naming` → references/developer.md
- [x] 4.2.1.2 Initialize Repo and API types `/developer/providers/getting-started/initialize-repo-and-api-types` → references/developer.md
- [x] 4.2.1.3 Implement API types `/developer/providers/getting-started/implement-api-types` → references/developer.md
- [x] 4.2.1.4 Webhooks `/developer/providers/getting-started/webhooks` → references/developer.md
- [x] 4.2.1.5 Controllers and Reconciliation `/developer/providers/getting-started/controllers-and-reconciliation` → references/developer.md
- [x] 4.2.1.6 Configure the provider manifest `/developer/providers/getting-started/configure-the-deployment` → references/developer.md
- [x] 4.2.1.7 Building, Running, Testing `/developer/providers/getting-started/building-running-and-testing` → references/developer.md
- [x] 4.2.2.0 Provider contracts Overview `/developer/providers/contracts/overview` → references/developer.md
- [x] 4.2.2.1 InfraCluster `/developer/providers/contracts/infra-cluster` → references/developer.md
- [x] 4.2.2.2 InfraMachine `/developer/providers/contracts/infra-machine` → references/developer.md
- [x] 4.2.2.3 InfraMachinePool `/developer/providers/contracts/infra-machinepool` → references/developer.md
- [x] 4.2.2.4 BootstrapConfig `/developer/providers/contracts/bootstrap-config` → references/developer.md
- [x] 4.2.2.5 ControlPlane `/developer/providers/contracts/control-plane` → references/developer.md
- [x] 4.2.2.6 clusterctl `/developer/providers/contracts/clusterctl` → references/developer.md
- [x] 4.2.2.7 IPAM `/developer/providers/contracts/ipam` → references/developer.md
- [x] 4.2.3 Best practices `/developer/providers/best-practices` → references/developer.md
- [x] 4.2.4 Security guidelines `/developer/providers/security-guidelines` → references/developer.md
- [x] 4.2.5.0 Version migration Overview `/developer/providers/migrations/overview` → references/developer.md
- [x] 4.2.5.1 v1.9 to v1.10 `/developer/providers/migrations/v1.9-to-v1.10` → references/developer.md
- [x] 4.2.5.2 v1.10 to v1.11 `/developer/providers/migrations/v1.10-to-v1.11` → references/developer.md
- [x] 4.2.5.3 v1.11 to v1.12 `/developer/providers/migrations/v1.11-to-v1.12` → references/developer.md

### 5. Troubleshooting (1 page)

- [x] 5.0 Troubleshooting `/user/troubleshooting` → references/troubleshooting.md

### 6. Reference (9 pages)

- [x] 6.0 Reference `/reference/reference` → references/api-reference.md
- [x] 6.1.0 API Reference `/reference/api/reference` → references/api-reference.md
- [x] 6.1.1 Labels and Annotations `/reference/api/labels-and-annotations` → references/api-reference.md
- [x] 6.1.2 CRD relationships `/reference/api/crd-relationships` → references/api-reference.md
- [x] 6.1.3 Metadata propagation `/reference/api/metadata-propagation` → references/api-reference.md
- [x] 6.1.4 Owner References `/reference/api/owner-references` → references/api-reference.md
- [x] 6.2 Glossary `/reference/glossary` → references/api-reference.md
- [x] 6.3 Provider List `/reference/providers` → references/api-reference.md
- [x] 6.4 Ports `/reference/ports` → references/api-reference.md
- [x] 6.5 Version Support `/reference/versions` → references/api-reference.md

### Skip (не включаем)

- Code of Conduct
- Contributing
- Code Review in Cluster API

## Reference Files Mapping

| Reference File        | Covers Sections                              |
| --------------------- | -------------------------------------------- |
| getting-started.md    | 0.2, 0.3 Quick Start                         |
| concepts.md           | 0.4, 0.5 Concepts, Manifesto                 |
| certificates.md       | 1.1.x Certificate Management                 |
| bootstrap.md          | 1.2.x Bootstrap                              |
| cluster-operations.md | 1.3-1.10 Core operations                     |
| experimental.md       | 1.11.x Experimental features                 |
| clusterctl.md         | 3.x clusterctl CLI                           |
| security.md           | 2.x Security Guidelines & PSS                |
| developer.md          | 4.x Developer Guide, Contracts, IPAM, Tuning |
| controllers.md        | 4.1.3.x Controller implementations           |
| migrations.md         | 4.2.5.x Version migrations (v1.9→v1.12)      |
| troubleshooting.md    | 5.0 Troubleshooting                          |
| api-reference.md      | 6.x Reference                                |

## Progress

- **Total pages**: 92
- **Completed**: 92
- **Reference files**: 13
- **Status**: COMPLETE

---

## Scripts (Phase 2) — COMPLETE

### Development Utilities

- [x] `scripts/validate_manifests.py` — Validate YAML manifests against CRD schemas
- [x] `scripts/check_provider_contract.py` — Verify provider CRD compliance with CAPI contract
- [x] `scripts/scaffold_provider.py` — Generate new provider structure

### CLI Wrappers

- [x] `scripts/run_clusterctl_diagnose.py` — Run clusterctl describe and save report
- [x] `scripts/check_cluster_health.py` — Analyze conditions across cluster objects
- [x] `scripts/generate_cluster_template.py` — Generate templates from ClusterClass

### Operations

- [x] `scripts/migration_checker.py` — Check v1beta1→v1beta2 migration readiness
- [x] `scripts/export_cluster_state.py` — Export cluster state for backup/move
- [x] `scripts/audit_security.py` — Check PSS compliance and security posture

### Diagnostics

- [x] `scripts/analyze_conditions.py` — Parse and report False/Unknown conditions
- [x] `scripts/timeline_events.py` — Build provisioning event timeline
- [x] `scripts/compare_versions.py` — Compare CAPI version specs

### Documentation

- [x] Updated `README.md` — Scripts section added

---

## Assets (Phase 3) — COMPLETE

### Cluster Templates

- [x] `assets/cluster-minimal.yaml` — Dev/test Docker cluster
- [x] `assets/cluster-production.yaml` — Production HA cluster (3 CP, MHC)
- [x] `assets/cluster-clusterclass.yaml` — Topology-based cluster
- [x] `assets/clusterclass-example.yaml` — Full ClusterClass with PSS variables

### Provider Configs

- [x] `assets/docker-quickstart.md` — Docker provider setup guide
- [x] `assets/aws-credentials.yaml` — AWS CAPA credentials template
- [x] `assets/azure-credentials.yaml` — Azure CAPZ credentials template
- [x] `assets/provider-matrix.md` — Version compatibility matrix

### Operations

- [x] `assets/upgrade-checklist.md` — Pre/post upgrade checklist
- [x] `assets/migration-v1beta2.md` — v1beta1→v1beta2 migration guide
- [x] `assets/troubleshooting-flow.md` — Diagnostic decision flowchart
- [x] `assets/security-audit-report.md` — Security audit report template

### Documentation

- [x] Updated `README.md` — Assets section added

---

## Improvements (Phase 4) — COMPLETE

### Lint & Validation

- [x] `scripts/lint_cluster_templates.py` — Lint and validate CAPI manifests

### GitOps Templates

- [x] `assets/argocd-cluster-app.yaml` — ArgoCD Application/ApplicationSet for CAPI
- [x] `assets/flux-kustomization.yaml` — Flux GitRepository + Kustomization
- [x] `assets/gitops-rbac.yaml` — RBAC for GitOps controllers

### Disaster Recovery

- [x] `assets/dr-backup-restore.md` — Complete DR playbook
- [x] `assets/etcd-backup.yaml` — Automated etcd backup CronJob

### Monitoring

- [x] `assets/prometheus-alerts.yaml` — Prometheus alerting rules for CAPI

### Documentation

- [x] `references/faq.md` — Frequently asked questions
- [x] `references/best-practices.md` — Production guidelines and checklists
- [x] Updated `README.md` — All new additions documented
