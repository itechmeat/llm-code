# Developer Guide

## Development Environment

### Prerequisites

- **Docker**: v19.03+ (or Lima on macOS)
- **kind**: v0.31.0+
- **Tilt**: v0.30.8+ (for rapid development)
- **kustomize**: `make kustomize`
- **envsubst**: `make envsubst`
- **helm**: v3.7.1+
- **kubebuilder**: Required for CRD development
- **cert-manager**: Must be deployed on management cluster

### Setup

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.19.3/cert-manager.yaml

# Verify cert-manager is ready
kubectl wait --for=condition=Available deployment/cert-manager-webhook -n cert-manager --timeout=300s
```

---

## Development Options

### Option 1: Tilt (Recommended)

Rapid iterative development with automatic rebuilds.

**Create kind cluster:**

```bash
# For Docker provider (CAPD)
make kind-cluster

# For KubeVirt provider
make kind-cluster-kubevirt
```

**Create tilt-settings.yaml:**

```yaml
default_registry: gcr.io/your-project
enable_providers:
  - docker
  - kubeadm-bootstrap
  - kubeadm-control-plane
```

**With external provider:**

```yaml
default_registry: gcr.io/your-project
provider_repos:
  - ../cluster-api-provider-aws
enable_providers:
  - aws
  - kubeadm-bootstrap
  - kubeadm-control-plane
kustomize_substitutions:
  AWS_B64ENCODED_CREDENTIALS: "xxx"
```

**Run Tilt:**

```bash
tilt up
```

### Tilt Settings Reference

| Field                     | Default          | Description                      |
| ------------------------- | ---------------- | -------------------------------- |
| `default_registry`        | required         | Container registry for images    |
| `enable_providers`        | `[docker]`       | Providers to enable              |
| `provider_repos`          | `[]`             | Paths to local provider clones   |
| `kustomize_substitutions` | `{}`             | Variable substitutions           |
| `template_dirs`           | docker templates | Cluster template directories     |
| `build_engine`            | `docker`         | Build engine (`docker`/`podman`) |
| `kind_cluster_name`       | `capi-test`      | Kind cluster name                |

### Option 2: Manual Build

```bash
# Build all images
make docker-build

# Push images
make docker-push

# Apply manifests
kustomize build config/default | ./hack/tools/bin/envsubst | kubectl apply -f -
kustomize build bootstrap/kubeadm/config/default | ./hack/tools/bin/envsubst | kubectl apply -f -
kustomize build controlplane/kubeadm/config/default | ./hack/tools/bin/envsubst | kubectl apply -f -
kustomize build test/infrastructure/docker/config/default | ./hack/tools/bin/envsubst | kubectl apply -f -
```

---

## Repository Structure

```
cluster-api/
├── api/                    # Core API types (Cluster, Machine, etc.)
├── bootstrap/              # Kubeadm Bootstrap Provider (CABPK)
├── controlplane/           # Kubeadm Control Plane Provider (KCP)
├── cmd/clusterctl/         # clusterctl CLI
├── config/                 # Kustomize manifests (generated)
│   ├── certmanager/        # Cert-manager resources
│   ├── crd/                # CRDs from api/
│   ├── manager/            # Controller deployment
│   ├── rbac/               # RBAC from kubebuilder markers
│   └── webhook/            # Webhook manifests
├── controllers/            # Reconciler types (public API)
├── internal/               # Internal implementations
│   ├── controllers/        # Controller implementations
│   └── webhooks/           # Webhook implementations
├── exp/                    # Experimental features
├── test/infrastructure/docker/  # Docker provider (CAPD)
├── util/                   # Shared utilities
├── feature/                # Feature gate management
├── hack/                   # Build/test scripts
└── scripts/                # CI scripts
```

---

## Testing

### Test Types

| Type            | Purpose                | Framework                   |
| --------------- | ---------------------- | --------------------------- |
| **Unit**        | Individual functions   | go test, gomega, fakeclient |
| **Integration** | Controller behavior    | envtest                     |
| **E2E**         | Full cluster workflows | Ginkgo, real infrastructure |
| **Fuzzing**     | Security/conversion    | go-fuzz, OSS-Fuzz           |

### Running Tests

```bash
# All unit + integration tests
make test

# E2E tests (build images first)
make docker-build-e2e
make test-e2e

# Specific E2E tests
GINKGO_LABEL_FILTER="PR-Blocking" ./scripts/ci-e2e.sh
```

### Test Tips

```bash
# Speed up with local kind cluster
./hack/setup-envtest-with-kind.sh

# Skip testenv if not needed
export CAPI_DISABLE_TEST_ENV=1

# Debug testenv
export CAPI_TEST_ENV_KUBECONFIG=/tmp/testenv-kubeconfig
export CAPI_TEST_ENV_SKIP_STOP=1
```

### Test Best Practices

- Use **generic providers** (GenericInfrastructureCluster), not specific implementations
- Use **builders** (`sigs.k8s.io/cluster-api/util/test/builder`) for test objects
- Use **komega matchers** (`controller-runtime/pkg/envtest/komega`)
- Test by layers: unit tests for functions, integration for workflows

---

## Provider Contract

All providers must implement the **Cluster API contract** to interact with core controllers.

### Contract Rules

| Provider Type  | Required Resources                             |
| -------------- | ---------------------------------------------- |
| Infrastructure | InfraCluster, InfraMachine, (InfraMachinePool) |
| Bootstrap      | BootstrapConfig                                |
| Control Plane  | ControlPlane                                   |
| IPAM           | IPAddress, IPAddressClaim                      |

### InfraCluster Contract

**Required fields:**

```go
type FooClusterSpec struct {
    // ControlPlaneEndpoint (optional if provided by other means)
    ControlPlaneEndpoint clusterv1.APIEndpoint `json:"controlPlaneEndpoint,omitempty"`
}

type FooClusterStatus struct {
    // Ready indicates infrastructure is ready
    Ready bool `json:"ready,omitempty"`

    // FailureDomains (optional)
    FailureDomains clusterv1.FailureDomains `json:"failureDomains,omitempty"`

    // Conditions (optional)
    Conditions clusterv1.Conditions `json:"conditions,omitempty"`
}
```

**Required behaviors:**

1. Set `status.ready = true` when infrastructure ready
2. Populate `status.controlPlaneEndpoint` (if responsible)
3. Handle pause by checking `Cluster.Spec.Paused`

### InfraMachine Contract

**Required fields:**

```go
type FooMachineSpec struct {
    // ProviderID - unique identifier (cloud provider format)
    ProviderID *string `json:"providerID,omitempty"`
}

type FooMachineStatus struct {
    // Ready indicates machine is running
    Ready bool `json:"ready,omitempty"`

    // Addresses - machine network addresses
    Addresses []clusterv1.MachineAddress `json:"addresses,omitempty"`

    // FailureReason (optional)
    FailureReason *capierrors.MachineStatusError `json:"failureReason,omitempty"`

    // FailureMessage (optional)
    FailureMessage *string `json:"failureMessage,omitempty"`
}
```

**Required behaviors:**

1. Set `status.ready = true` when machine running
2. Populate `spec.providerID` with cloud provider format
3. Wait for `Machine.Spec.Bootstrap.DataSecretName` before bootstrap

### BootstrapConfig Contract

**Purpose:** Generate cloud-init or ignition data for machine initialization.

**Required fields:**

```go
type FooConfigSpec struct {
    // Provider-specific bootstrap configuration
}

type FooConfigStatus struct {
    // Ready indicates bootstrap data is generated
    Ready bool `json:"ready,omitempty"`

    // DataSecretName is the name of the secret containing bootstrap data
    DataSecretName *string `json:"dataSecretName,omitempty"`

    // FailureReason (optional)
    FailureReason string `json:"failureReason,omitempty"`

    // FailureMessage (optional)
    FailureMessage string `json:"failureMessage,omitempty"`
}
```

**Required behaviors:**

1. Create Secret with bootstrap data (cloud-init/ignition)
2. Set `status.dataSecretName` to Secret name
3. Set `status.ready = true` when data available
4. Secret format: `value` key with bootstrap payload

**Bootstrap Secret structure:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: <machine-name>-bootstrap-data
data:
  value: <base64-encoded-cloud-init-or-ignition>
  format: cloud-config # or ignition
```

### ControlPlane Contract

**Purpose:** Manage Kubernetes control plane components (API server, controller manager, scheduler, etcd).

**Required fields:**

```go
type FooControlPlaneSpec struct {
    // Replicas - number of control plane instances
    Replicas *int32 `json:"replicas,omitempty"`

    // Version - Kubernetes version
    Version string `json:"version"`

    // MachineTemplate - template for control plane machines
    MachineTemplate FooControlPlaneMachineTemplate `json:"machineTemplate,omitempty"`
}

type FooControlPlaneStatus struct {
    // Ready indicates control plane is operational
    Ready bool `json:"ready,omitempty"`

    // Initialized indicates first control plane node is up
    Initialized bool `json:"initialized,omitempty"`

    // Replicas - total number of machines
    Replicas int32 `json:"replicas,omitempty"`

    // ReadyReplicas - number of ready machines
    ReadyReplicas int32 `json:"readyReplicas,omitempty"`

    // UpdatedReplicas - number of up-to-date machines
    UpdatedReplicas int32 `json:"updatedReplicas,omitempty"`

    // UnavailableReplicas - number of unavailable machines
    UnavailableReplicas int32 `json:"unavailableReplicas,omitempty"`

    // Version - observed Kubernetes version
    Version *string `json:"version,omitempty"`

    // Conditions (optional)
    Conditions clusterv1.Conditions `json:"conditions,omitempty"`
}
```

**Required behaviors:**

1. Set `status.initialized = true` after first node bootstrapped
2. Set `status.ready = true` when desired replicas are ready
3. Create kubeconfig Secret named `<cluster-name>-kubeconfig`
4. Manage control plane certificates (or coordinate with external PKI)
5. Handle rolling updates respecting availability

**Contract rules (v1beta2):**

| Rule                     | Mandatory | Notes                                           |
| ------------------------ | --------- | ----------------------------------------------- |
| endpoint                 | No        | Mandatory if CP provides control plane endpoint |
| replicas                 | No        | Mandatory if CP has notion of instances         |
| version                  | No        | Mandatory if CP manages Kubernetes version      |
| machines                 | No        | Mandatory if CP instances are CAPI Machines     |
| initialization completed | Yes       | Set `status.initialized`                        |
| conditions               | No        | StandardConditions recommended                  |
| terminal failures        | No        | Report via conditions                           |

**ControlPlaneTemplate (for ClusterClass):**

```go
// +kubebuilder:object:root=true
type FooControlPlaneTemplate struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    Spec FooControlPlaneTemplateSpec `json:"spec,omitempty"`
}

type FooControlPlaneTemplateSpec struct {
    Template FooControlPlaneTemplateResource `json:"template"`
}

type FooControlPlaneTemplateResource struct {
    // ObjectMeta with labels/annotations
    ObjectMeta clusterv1.ObjectMeta `json:"metadata,omitempty"`
    Spec FooControlPlaneSpec `json:"spec"`
}
```

### API Versioning

**CRD Labels (required):**

```yaml
# config/crd/kustomization.yaml
labels:
  - pairs:
      cluster.x-k8s.io/v1beta1: v1beta1
      cluster.x-k8s.io/v1beta2: v1beta2
```

**RBAC for custom API groups:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: capi-foo-clusters
  labels:
    cluster.x-k8s.io/aggregate-to-manager: "true"
rules:
  - apiGroups: ["infrastructure.foo.com"]
    resources: ["fooclusters", "foomachines"]
    verbs: ["*"]
```

---

## clusterctl Provider Contract

For clusterctl CLI support, providers must:

### 1. Repository Structure

```
releases/
└── v0.1.0/
    ├── infrastructure-components.yaml
    ├── cluster-template.yaml
    └── metadata.yaml
```

### 2. metadata.yaml

```yaml
apiVersion: clusterctl.cluster.x-k8s.io/v1alpha3
kind: Metadata
releaseSeries:
  - major: 0
    minor: 1
    contract: v1beta1
```

### 3. Component YAML Requirements

```yaml
# Required labels
labels:
  cluster.x-k8s.io/provider: infrastructure-foo
  clusterctl.cluster.x-k8s.io: ""

# Support variable substitution
env:
  - name: FOO_CREDENTIALS
    valueFrom:
      secretKeyRef:
        name: ${FOO_CREDENTIALS_SECRET_NAME}
        key: credentials
```

---

## Logging

### Log Levels

| Level | Use Case                          |
| ----- | --------------------------------- |
| 0     | Always visible (errors, warnings) |
| 1     | Important events                  |
| 2     | Detailed progress                 |
| 4+    | Debug information                 |

### Structured Logging

```go
log := ctrl.LoggerFrom(ctx)

// Key-value pairs
log.Info("Reconciling cluster", "cluster", cluster.Name, "namespace", cluster.Namespace)

// With objects (auto-extracts name/namespace)
log.Info("Machine created", "machine", klog.KObj(machine))

// Errors
log.Error(err, "Failed to create machine", "machine", machine.Name)
```

### Change Log Level at Runtime

```bash
curl "https://localhost:8443/debug/flags/v" \
  --header "Authorization: Bearer $TOKEN" \
  -X PUT -d '8' -k
```

---

## IPAM Provider Contract

### Overview

IPAM providers manage IP address allocation for cluster machines. IPAM is **optional** — infrastructure providers need explicit IPAM support.

**Note**: IPAM contract is single-stack. For dual-stack (IPv4 + IPv6), create two pools and two IPAddressClaims.

### Required Resources

1. **IP Pool CRD** — provider-specific pool definition
2. **IPAddressClaim** — request for IP allocation (created by infra provider)
3. **IPAddress** — allocated address (created by IPAM provider)

### IP Pool Requirements

```go
type FooIPPoolStatus struct {
    // Ready condition - overall operational state
    Conditions clusterv1.Conditions `json:"conditions,omitempty"`
}
```

### IPAM Provider Behavior

**On IPAddressClaim creation:**

1. Skip if `spec.poolRef` doesn't reference managed pool
2. Check if referenced Cluster is paused → skip if paused
3. Add provider finalizers
4. Allocate IP address from pool
5. Create IPAddress resource:
   - Same name as claim
   - Owner reference to Claim (`controller: true`, `blockOwnerDeletion: true`)
   - Owner reference to Pool (`controller: false`, `blockOwnerDeletion: true`)
   - Finalizer: `ipam.cluster.x-k8s.io/protect-address`
6. Set `status.addressRef` on IPAddressClaim

**On IPAddressClaim deletion:**

1. Check cluster pause state
2. Deallocate IP address
3. Delete IPAddress resource (remove finalizers)
4. Remove finalizer from claim

### Infrastructure Provider Integration

**Creating IPAddressClaim:**

```yaml
apiVersion: ipam.cluster.x-k8s.io/v1beta1
kind: IPAddressClaim
metadata:
  name: <machine-name>-ip
  ownerReferences:
    - apiVersion: infrastructure.example.com/v1beta1
      kind: FooMachine
      name: <machine-name>
      controller: true
      blockOwnerDeletion: true
spec:
  poolRef:
    apiGroup: ipam.example.com
    kind: FooIPPool
    name: my-ip-pool
  clusterName: my-cluster
```

**Workflow:**

1. Create IPAddressClaim referencing pool
2. Watch for `status.addressRef` to be set
3. Fetch IPAddress resource for allocated address
4. Use address in machine provisioning
5. Claim deleted automatically with machine (via owner reference)

### clusterctl Move Support

Pools must have `cluster.x-k8s.io/cluster-name` label to be moved with clusters.

---

## Infrastructure Provider Security

### Critical Security Areas

1. **Cloud credentials management** — quotas, rate limiting
2. **Secure VM access** — proper authentication for troubleshooting
3. **Controlled manual operations** — oversight on cloud changes
4. **Resource housekeeping** — cleanup unused resources
5. **Bootstrap data security** — protect sensitive metadata

### Security Recommendations

| Area                | Recommendation                                                                |
| ------------------- | ----------------------------------------------------------------------------- |
| Credentials         | Least-privilege; restrict controller namespace access to cloud admins         |
| Authentication      | 2FA for all maintainer accounts; "second pair of eyes" for privileged actions |
| Credential lifetime | Short-lived credentials with automatic renewal via node attestation           |
| Rate limiting       | Implement limits on create/delete/update of cloud resources                   |
| Housekeeping        | Auto-delete unlinked cloud resources after configurable period                |
| Bootstrap data      | Protect metadata or clean up immediately post-bootstrap                       |

### Bootstrap Data Protection

Bootstrap data stored in machine metadata may contain:

- Cluster secrets
- User credentials
- SSH certificates

**Actions:**

- Encrypt metadata at rest
- Restrict metadata API access
- Clear bootstrap data after machine initialization

---

## Controller Tuning

### Observability Stack (via Tilt)

- Grafana, Loki, Alloy, Prometheus
- kube-state-metrics with CAPI metrics
- Parca (profiling), Tempo (tracing)

### Runtime Tuning Options

| Option      | Flag                                | Effect                                 |
| ----------- | ----------------------------------- | -------------------------------------- |
| API QPS     | `--kube-api-qps`                    | Max API calls/second                   |
| API Burst   | `--kube-api-burst`                  | Spike tolerance                        |
| Concurrency | `--kubeadmcontrolplane-concurrency` | Parallel reconciles                    |
| Resync      | `--sync-period`                     | Full reconcile interval (default: 10m) |

**Caution**: Increasing QPS/burst/concurrency increases API server load.

### Performance Diagnosis

1. Check client-go rate limiting logs ("client-side throttling")
2. Check work queue depth (Controller-Runtime dashboard)
3. Check reconcile duration per controller
4. Analyze traces for slow spans

### Code Optimization Tips

**Avoid work:**

- Use watches instead of polling
- Filter irrelevant events
- Skip unnecessary API calls

**Minimize expensive operations:**

- Certificate key generation
- Kubernetes client creation
- Uncached list calls with selectors

**Best practices:**

- Use controller-runtime's cached client (reads from shared informers)
- Use `patch.Helper` with defer to batch writes
- Reuse long-lived clients for external services
- Prefer async callbacks over status polling
