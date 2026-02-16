# Cluster Operations

## Upgrading Clusters

### Version Compatibility

- Check CAPI version supports target Kubernetes version
- May need to upgrade CAPI components first
- **MUST upgrade Kubernetes minor versions sequentially** (v1.17→v1.18→v1.19, not v1.17→v1.19)

### Machine Images

For kubeadm clusters, ensure machine images have matching `kubeadm` and `kubelet` versions.

### Upgrade Process

**Order**: Control plane first, then workers

#### Upgrading Control Plane

**Option 1: Upgrade machine image**

1. Copy existing `MachineTemplate`
2. Modify values (image ID, instance type)
3. Create new `MachineTemplate`
4. Update `KubeadmControlPlane.spec.infrastructureRef` to reference new template

**Option 2: Upgrade Kubernetes version**

Modify `KubeadmControlPlane.spec.Version`:

```bash
kubectl patch kubeadmcontrolplane my-control-plane \
  --type merge -p '{"spec":{"version":"v1.33.0"}}'
```

**Combined upgrade** (recommended for providers like AWS):
Update both `Version` and `InfrastructureTemplate` in single transaction.

#### Scheduling Machine Rollout

Use `spec.rolloutBefore.after` for time-based rollouts:

```bash
# Trigger KubeadmControlPlane rollout
clusterctl alpha rollout restart kubeadmcontrolplane/my-kcp

# Trigger MachineDeployment rollout
clusterctl alpha rollout restart machinedeployment/my-md-0
```

#### Upgrading Workers

Modify `MachineDeployment` spec to trigger rolling update.

**Rollout Strategies:**

| Strategy      | Description                            |
| ------------- | -------------------------------------- |
| RollingUpdate | Honors `MaxUnavailable` and `MaxSurge` |
| OnDelete      | Wait for user to delete old machines   |

### Upgrading CAPI Components

```bash
clusterctl upgrade plan    # Check available upgrades
clusterctl upgrade apply   # Apply upgrade
```

## Control Plane Management (KCP)

### Kubeconfig Management

- KCP generates and manages admin kubeconfig
- Client certificate valid 1 year, auto-regenerated at 6 months remaining

### In-place Propagation (No Rollout)

Changes to these fields propagate without rollout:

- `.spec.machineTemplate.metadata.labels`
- `.spec.machineTemplate.metadata.annotations`
- `.spec.nodeDrainTimeout`
- `.spec.nodeDeletionTimeout`
- `.spec.nodeVolumeDetachTimeout`

### Running Workloads on Control Plane

**Not recommended.** If necessary:

- Leverage cordon & drain before removal
- Use `PreDrainDeleteHook` and `PreTerminateDeleteHook`

### CoreDNS

**KubeadmControlPlane only supports CoreDNS** as DNS server.

## Scaling

### Manual Scaling

```bash
# Scale MachineDeployment
kubectl scale machinedeployment my-md-0 --replicas=10

# Or patch replicas
kubectl patch machinedeployment my-md-0 \
  --type merge -p '{"spec":{"replicas":10}}'
```

### Machine Deletion Process

When deleting Machine (directly or via scale-down):

1. **Drain node** - indefinite unless `.spec.nodeDrainTimeout` set
   - Uses `kubectl drain --ignore-daemonsets=true`
   - DaemonSet eviction requires manual taints
2. **Wait for volume detach**
3. **Delete infrastructure** - indefinite
4. **Delete Node** - after infrastructure gone, unless `.spec.nodeDeletionTimeout` set

## Autoscaling (Cluster Autoscaler)

### Enable Cluster Autoscaler

Add annotations to `MachineDeployment`, `MachineSet`, or `MachinePool`:

```yaml
metadata:
  annotations:
    cluster.x-k8s.io/cluster-api-autoscaler-node-group-min-size: "1"
    cluster.x-k8s.io/cluster-api-autoscaler-node-group-max-size: "10"
```

### Autoscaler Configuration

```bash
cluster-autoscaler --cloud-provider=clusterapi \
  --node-group-auto-discovery=clusterapi:namespace=default,clusterName=my-cluster
```

**Discovery options:**

- `namespace=blue` - match namespace
- `clusterName=test1` - match cluster
- `label=value` - match labels

### Kubeconfig Configuration

| Topology                              | Flags                                                                           |
| ------------------------------------- | ------------------------------------------------------------------------------- |
| Autoscaler in joined mgmt/workload    | (none - uses in-cluster)                                                        |
| Autoscaler in workload, separate mgmt | `--cloud-config=/mnt/mgmt.kubeconfig`                                           |
| Autoscaler in mgmt, separate workload | `--kubeconfig=/mnt/workload.kubeconfig --clusterapi-cloud-config-authoritative` |
| Separate all                          | `--kubeconfig=/mnt/workload.kubeconfig --cloud-config=/mnt/mgmt.kubeconfig`     |

### Scale From Zero

Add capacity annotations:

```yaml
metadata:
  annotations:
    cluster.x-k8s.io/cluster-api-autoscaler-node-group-min-size: "0"
    cluster.x-k8s.io/cluster-api-autoscaler-node-group-max-size: "5"
    capacity.cluster-autoscaler.kubernetes.io/memory: "128G"
    capacity.cluster-autoscaler.kubernetes.io/cpu: "16"
    capacity.cluster-autoscaler.kubernetes.io/ephemeral-disk: "100Gi"
    capacity.cluster-autoscaler.kubernetes.io/maxPods: "200"
    capacity.cluster-autoscaler.kubernetes.io/gpu-type: "nvidia.com/gpu"
    capacity.cluster-autoscaler.kubernetes.io/gpu-count: "2"
```

## MachineHealthCheck

### Requirements

**Only works with:**

- Machines owned by MachineSet
- Machines owned by KubeadmControlPlane
- MachineDeployment (uses MachineSet)

### Basic Configuration

```yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: MachineHealthCheck
metadata:
  name: my-cluster-mhc
spec:
  clusterName: my-cluster
  selector:
    matchLabels:
      nodepool: nodepool-0
  checks:
    nodeStartupTimeoutSeconds: 600
    unhealthyNodeConditions:
      - type: Ready
        status: Unknown
        timeoutSeconds: 300
      - type: Ready
        status: "False"
        timeoutSeconds: 300
  remediation:
    triggerIf:
      unhealthyLessThanOrEqualTo: 40%
```

### Control Plane MHC

```yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: MachineHealthCheck
metadata:
  name: my-cluster-kcp-mhc
spec:
  clusterName: my-cluster
  selector:
    matchLabels:
      cluster.x-k8s.io/control-plane: ""
  checks:
    unhealthyNodeConditions:
      - type: Ready
        status: Unknown
        timeoutSeconds: 300
  remediation:
    triggerIf:
      unhealthyLessThanOrEqualTo: 100%
```

### Short-Circuiting (Prevent Cascade Failures)

| Field                             | Effect                          |
| --------------------------------- | ------------------------------- |
| `unhealthyLessThanOrEqualTo: 40%` | Stop if >40% unhealthy          |
| `unhealthyLessThanOrEqualTo: 2`   | Stop if >2 unhealthy            |
| `unhealthyInRange: [3-5]`         | Only remediate if 3-5 unhealthy |

**Default**: `100%` (no short-circuiting)

### Skip Remediation

Add annotation to skip:

```yaml
metadata:
  annotations:
    cluster.x-k8s.io/skip-remediation: "true"
    # or
    cluster.x-k8s.io/paused: "true"
```

### KCP Remediation Strategy

```yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: KubeadmControlPlane
spec:
  remediationStrategy:
    maxRetry: 5 # Max retries for same machine
    retryPeriod: 2m # Wait between retries
    minHealthyPeriod: 2h # Reset retry count if healthy this long
```

## External etcd

### Setup

CAPI cannot manage external etcd - you manage it separately.

**Required certificates:**

1. `/etc/kubernetes/pki/apiserver-etcd-client.crt` and `.key`
2. `/etc/kubernetes/pki/etcd/ca.crt`

### Create Secrets

```bash
# API server etcd client cert
kubectl create secret tls $CLUSTER_NAME-apiserver-etcd-client \
  --cert apiserver-etcd-client.crt \
  --key apiserver-etcd-client.key

# etcd CA
kubectl create secret generic $CLUSTER_NAME-etcd \
  --from-file tls.crt=etcd-ca.crt
```

### Configure KubeadmConfig

```yaml
spec:
  clusterConfiguration:
    etcd:
      external:
        endpoints:
          - https://10.0.0.230:2379
        caFile: /etc/kubernetes/pki/etcd/ca.crt
        certFile: /etc/kubernetes/pki/apiserver-etcd-client.crt
        keyFile: /etc/kubernetes/pki/apiserver-etcd-client.key
```

## Using Kustomize

### Structure

```
.
├── base
│   ├── base.yaml
│   └── kustomization.yaml
└── overlays
    ├── custom-ami
    │   ├── custom-ami.json
    │   └── kustomization.yaml
```

### Custom Machine Image

```yaml
# kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
patchesJson6902:
  - path: custom-ami.json
    target:
      group: infrastructure.cluster.x-k8s.io
      kind: AWSMachineTemplate
      name: ".*"
      version: v1alpha3
```

```json
// custom-ami.json
[{ "op": "add", "path": "/spec/template/spec/ami", "value": "ami-042db61632f72f145" }]
```

### Add MachineHealthCheck

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
  - workload-mhc.yaml
```

---

## Updating Machine Templates

Infrastructure machine templates are **immutable**. Correct update process:

1. **Export existing template:**

```bash
kubectl get AWSMachineTemplate my-template -o yaml > new-template.yaml
```

2. **Modify desired fields** (SSH key, instance type, image, etc.)

3. **Change `metadata.name`** to new unique name

4. **Remove extraneous metadata** (resourceVersion, uid, etc.)

5. **Create new template:**

```bash
kubectl apply -f new-template.yaml
```

6. **Update reference** in parent resource:

**KubeadmControlPlane:**

```yaml
spec:
  infrastructureTemplate:
    name: new-template # Update to new template name
```

**MachineDeployment:**

```yaml
spec:
  template:
    spec:
      infrastructureRef:
        name: new-template # Triggers rolling update
```

⚠️ Some providers support in-place modifications for certain fields (memory, CPU). In those cases, CAPI does NOT trigger rolling update.

### Bootstrap Template Updates

Same process applies — templates are immutable:

1. Copy existing bootstrap template
2. Modify fields
3. Give new name
4. Create new template
5. Update `spec.template.spec.bootstrap.configRef.name`

---

## Running Multiple Providers

Cluster API supports multiple infrastructure/bootstrap/control plane providers on same management cluster.

```bash
# Install multiple providers
clusterctl init \
  --infrastructure aws \
  --infrastructure vsphere \
  --infrastructure azure
```

**Requirements:**

- All providers must support same Cluster API contract version
- Use `clusterctl init` to ensure compatibility

⚠️ Not covered by Cluster API E2E tests — validate your combination before production.

---

## Container Image Verification

Verify authenticity of CAPI container images using cosign.

**Images:**

- `registry.k8s.io/cluster-api/cluster-api-controller`
- `registry.k8s.io/cluster-api/kubeadm-bootstrap-controller`
- `registry.k8s.io/cluster-api/kubeadm-control-plane-controller`
- `registry.k8s.io/cluster-api/clusterctl`

**Verify signature:**

```bash
cosign verify registry.k8s.io/cluster-api/cluster-api-controller:v1.9.0 \
  --certificate-identity krel-trust@k8s-releng-prod.iam.gserviceaccount.com \
  --certificate-oidc-issuer https://accounts.google.com | jq .
```

---

## Diagnostics

### Secure Metrics Endpoint

Default (v1.6+): metrics served via HTTPS on port 8443 with authentication.

```yaml
args:
  - "--diagnostics-address=${CAPI_DIAGNOSTICS_ADDRESS:=:8443}"
```

**Insecure mode (development only):**

```yaml
args:
  - "--diagnostics-address=localhost:8080"
  - "--insecure-diagnostics"
```

### Scraping Metrics

**Prometheus configuration:**

```yaml
scheme: https
authorization:
  type: Bearer
  credentials_file: /var/run/secrets/kubernetes.io/serviceaccount/token
tls_config:
  ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
  insecure_skip_verify: true # Self-signed cert
```

**kubectl access:**

```bash
# Deploy RBAC
kubectl apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: default-metrics
rules:
- nonResourceURLs: ["/metrics"]
  verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: default-metrics
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: default-metrics
subjects:
- kind: ServiceAccount
  name: default
  namespace: default
EOF

# Port-forward and scrape
kubectl -n capi-system port-forward deployments/capi-controller-manager 8443
TOKEN=$(kubectl create token default)
curl https://localhost:8443/metrics --header "Authorization: Bearer $TOKEN" -k
```

### Profiling (pprof)

```bash
# Get goroutine dump
curl "https://localhost:8443/debug/pprof/goroutine?debug=2" \
  --header "Authorization: Bearer $TOKEN" -k > ./goroutine.txt

# Get CPU profile
curl "https://localhost:8443/debug/pprof/profile?seconds=10" \
  --header "Authorization: Bearer $TOKEN" -k > ./profile.out
go tool pprof -http=:8080 ./profile.out
```

### Dynamic Log Level

```bash
# Change log level to 8
curl "https://localhost:8443/debug/flags/v" \
  --header "Authorization: Bearer $TOKEN" -X PUT -d '8' -k
```

---

## ClusterResourceSet

Automatically apply resources (CNI, CSI, cloud providers) to matching workload clusters.

### Example: Auto-install Cloud Provider

```yaml
apiVersion: addons.cluster.x-k8s.io/v1beta2
kind: ClusterResourceSet
metadata:
  name: cloud-provider-openstack
  namespace: default
spec:
  strategy: Reconcile # or ApplyOnce
  clusterSelector:
    matchLabels:
      cloud: openstack
  resources:
    - name: cloud-provider-openstack
      kind: ConfigMap
    - name: cloud-config
      kind: Secret
```

### Create Resources

```bash
# Secret (requires special type)
kubectl create secret generic cloud-config \
  --from-file=cloud.conf \
  --type=addons.cluster.x-k8s.io/resource-set

# ConfigMap
kubectl create configmap cloud-provider-openstack \
  --from-file=cloud-provider-openstack.yaml
```

**Strategies:**

- `ApplyOnce` — Apply once, never reconcile
- `Reconcile` — Continuously reconcile (strategy is immutable after creation)

---

## GitOps Integration

Use Cluster API Addon Provider for Helm (CAAPH) with GitOps agents.

### Setup

```bash
# Install with Helm addon provider
clusterctl init --infrastructure aws --addon helm
```

### ArgoCD Bootstrap

1. **Label cluster:**

```yaml
apiVersion: cluster.x-k8s.io/v1beta2
kind: Cluster
metadata:
  name: my-cluster
  labels:
    argoCDChart: enabled
    guestbook: enabled
```

2. **Create HelmChartProxy:**

```yaml
apiVersion: addons.cluster.x-k8s.io/v1alpha1
kind: HelmChartProxy
metadata:
  name: argocd
spec:
  clusterSelector:
    matchLabels:
      argoCDChart: enabled
  repoURL: https://argoproj.github.io/argo-helm
  chartName: argo-cd
  options:
    waitForJobs: true
    wait: true
    timeout: 5m
    install:
      createNamespace: true
---
apiVersion: addons.cluster.x-k8s.io/v1alpha1
kind: HelmChartProxy
metadata:
  name: argocdguestbook
spec:
  clusterSelector:
    matchLabels:
      guestbook: enabled
  repoURL: https://argoproj.github.io/argo-helm
  chartName: argocd-apps
  valuesTemplate: |
    applications:
      - name: guestbook
        namespace: argocd
        project: default
        sources:
          - repoURL: https://github.com/argoproj/argocd-example-apps.git
            path: guestbook
            targetRevision: HEAD
        destination:
          server: https://kubernetes.default.svc
          namespace: guestbook
        syncPolicy:
          automated:
            prune: false
            selfHeal: false
          syncOptions:
          - CreateNamespace=true
```

3. **Access ArgoCD:**

```bash
kubectl get secrets argocd-initial-admin-secret -n argocd \
  --template="{{index .data.password | base64decode}}"
kubectl port-forward service/argocd-server -n argocd 8080:443
# Open https://localhost:8080
```

Same pattern works with **FluxCD** using Flux Helm charts.
