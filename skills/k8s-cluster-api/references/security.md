# Security

## Pod Security Standards

Cluster API leverages Kubernetes Pod Security Admission (PSA) to enforce Pod Security Standards.

### ClusterClass Variables

Define Pod Security Standards via ClusterClass variables:

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: ClusterClass
spec:
  variables:
    - name: podSecurityStandard
      required: false
      schema:
        openAPIV3Schema:
          type: object
          properties:
            enabled:
              type: boolean
              default: true
            enforce:
              type: string
              default: "baseline"
              enum: ["privileged", "baseline", "restricted"]
            audit:
              type: string
              default: "restricted"
              enum: ["privileged", "baseline", "restricted"]
            warn:
              type: string
              default: "restricted"
              enum: ["privileged", "baseline", "restricted"]
```

### PSS Levels

| Level          | Description                                            |
| -------------- | ------------------------------------------------------ |
| **privileged** | No restrictions (unrestricted policy)                  |
| **baseline**   | Minimal restrictions preventing known escalation       |
| **restricted** | Heavily restricted, following hardening best practices |

### AdmissionConfiguration Patch

Apply PSA configuration via KubeadmControlPlaneTemplate:

```yaml
patches:
  - name: podSecurityStandard
    enabledIf: "{{ if .podSecurityStandard.enabled }}true{{ end }}"
    definitions:
      - selector:
          apiVersion: controlplane.cluster.x-k8s.io/v1beta1
          kind: KubeadmControlPlaneTemplate
          matchResources:
            controlPlane: true
        jsonPatches:
          - op: add
            path: /spec/template/spec/kubeadmConfigSpec/clusterConfiguration/apiServer/extraArgs
            valueFrom:
              template: |
                admission-control-config-file: /etc/kubernetes/kube-apiserver-admission-pss.yaml
          - op: add
            path: /spec/template/spec/kubeadmConfigSpec/files/-
            valueFrom:
              template: |
                content: |
                  apiVersion: apiserver.config.k8s.io/v1
                  kind: AdmissionConfiguration
                  plugins:
                  - name: PodSecurity
                    configuration:
                      apiVersion: pod-security.admission.config.k8s.io/v1
                      kind: PodSecurityConfiguration
                      defaults:
                        enforce: "{{ .podSecurityStandard.enforce }}"
                        enforce-version: "latest"
                        audit: "{{ .podSecurityStandard.audit }}"
                        audit-version: "latest"
                        warn: "{{ .podSecurityStandard.warn }}"
                        warn-version: "latest"
                      exemptions:
                        usernames: []
                        runtimeClasses: []
                        namespaces:
                        - kube-system
                path: /etc/kubernetes/kube-apiserver-admission-pss.yaml
```

### kube-system Exemptions

Critical system components (kube-apiserver, kube-controller-manager, kube-scheduler, etcd, CoreDNS, kube-proxy) run in `kube-system` namespace. This namespace is typically exempted from PSS restrictions.

---

## Security Guidelines

### Auditing

#### Cluster-Level Auditing

- **Native audit logs**: Configuration of cluster operations logging
- **Audit policy**: Define what events to record with what level of detail
- **Backend types**: Log (file), Webhook (external service)
- **Best practice**: Start with comprehensive auditing, then tune down as patterns are understood

#### Node-Level Auditing

- System-level auditing on node host OS
- Monitor sensitive file access (certificates, keys, kubeconfig)
- Track process execution (especially in control plane components)

#### Cloud Provider Auditing

- Cloud-level operation tracking (VM creation/deletion, network changes)
- IAM/identity audit trails
- API call logging from cloud provider's control plane

### Least Privileges

#### Cloud Provider Credentials

**Principle**: Grant only minimum necessary permissions.

| Operation        | Required Permissions                 |
| ---------------- | ------------------------------------ |
| Cluster creation | Create VMs, networks, load balancers |
| Node scaling     | Create/delete VMs                    |
| Cluster deletion | Delete all created resources         |

**DO NOT**:

- Use organization-wide admin credentials
- Share credentials across unrelated clusters
- Grant persistent credentials when temporary tokens suffice

**DO**:

- Use scoped service accounts per cluster
- Rotate credentials regularly
- Prefer workload identity / IRSA / pod identity over static credentials

### Access Control

#### Control Plane Hardening

- **Taints on control plane nodes**: Prevent workload scheduling
- **RBAC**: Minimal permissions for administrators
- **Admission controllers**: ValidatingAdmissionPolicies, OPA/Gatekeeper
- **etcd encryption**: Enable encryption at rest for secrets

#### SSH Access

| Context     | Recommendation                          |
| ----------- | --------------------------------------- |
| Production  | Disable SSH entirely or use bastion     |
| Debugging   | Temporary access with audit trail       |
| Break-glass | Pre-configured emergency access process |

**Prohibition**: Never expose SSH directly to the internet on cluster nodes.

### Review Processes

#### GitOps ("Second Pair of Eyes")

- All cluster changes through version-controlled manifests
- Require pull request approval before applying
- Automated policy checks (linting, security scanning)
- Audit trail of who approved what changes

#### Change Management

- Documented procedures for:
  - Cluster upgrades
  - Provider updates
  - Certificate rotations
  - Emergency access

### Alerting

#### Security Events

| Event Category     | Examples                               |
| ------------------ | -------------------------------------- |
| Authentication     | Failed logins, unknown credentials     |
| Authorization      | Permission denied, RBAC violations     |
| Resource changes   | Unexpected deletions, modifications    |
| Certificate events | Expiration warnings, rotation failures |

#### Resource Activity

- Unusual scaling patterns
- Unexpected cluster operations
- API server error rate spikes

#### Resource Limits

- Quota approaching limits
- Cost thresholds
- Unusual resource consumption

### Cluster Isolation

#### Account Separation

- Separate cloud accounts/projects for:
  - Production vs non-production
  - Different security domains
  - Different teams/tenants

#### Network Boundaries

- VPC isolation between clusters
- Network policies within clusters
- Service mesh for workload-to-workload encryption

#### Certificate Authority Isolation

- Separate CA per cluster
- Don't share root CA across trust boundaries
- Regular CA rotation schedule

### Immutable Infrastructure

#### Principles

- **No in-place updates**: Replace nodes rather than patching
- **Image-based deployments**: Pre-built, tested images
- **Configuration as code**: All changes through version control

#### Benefits

- Known-good state recovery
- Faster incident response
- Reduced configuration drift

---

## Security Checklist

### Before Cluster Creation

- [ ] Define network architecture (VPC, subnets, security groups)
- [ ] Create scoped cloud credentials
- [ ] Prepare audit log destinations
- [ ] Define Pod Security Standards requirements
- [ ] Plan certificate management approach

### After Cluster Creation

- [ ] Verify PSA enforcement is active
- [ ] Confirm etcd encryption is enabled
- [ ] Test audit log flow to destination
- [ ] Validate RBAC configuration
- [ ] Document emergency access procedures

### Ongoing Operations

- [ ] Regular credential rotation
- [ ] Certificate expiration monitoring
- [ ] Audit log review
- [ ] Security scanning of cluster configuration
- [ ] Upgrade planning and testing
