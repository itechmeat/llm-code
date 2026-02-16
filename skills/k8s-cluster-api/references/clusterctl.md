# clusterctl CLI Reference

CLI tool for Cluster API management cluster lifecycle operations.

## Installation

```bash
# Linux
curl -L https://github.com/kubernetes-sigs/cluster-api/releases/download/v1.9.4/clusterctl-linux-amd64 -o clusterctl
chmod +x ./clusterctl && sudo mv ./clusterctl /usr/local/bin/

# macOS (Intel)
curl -L https://github.com/kubernetes-sigs/cluster-api/releases/download/v1.9.4/clusterctl-darwin-amd64 -o clusterctl

# macOS (Apple Silicon)
curl -L https://github.com/kubernetes-sigs/cluster-api/releases/download/v1.9.4/clusterctl-darwin-arm64 -o clusterctl

# Homebrew (macOS/Linux)
brew install clusterctl

# Windows (PowerShell)
curl.exe -L https://github.com/kubernetes-sigs/cluster-api/releases/download/v1.9.4/clusterctl-windows-amd64.exe -o clusterctl.exe
```

## Configuration File

Location: `$XDG_CONFIG_HOME/cluster-api/clusterctl.yaml` (typically `~/.config/cluster-api/clusterctl.yaml`)

### Custom Provider Repository

```yaml
providers:
  - name: "my-infra-provider"
    url: "https://github.com/myorg/myrepo/releases/latest/infrastructure-components.yaml"
    type: "InfrastructureProvider"
  # Override existing provider
  - name: "cluster-api"
    url: "https://github.com/myorg/myforkofclusterapi/releases/latest/core-components.yaml"
    type: "CoreProvider"
```

### Variables for Substitution

```yaml
# Variables for template substitution
AWS_B64ENCODED_CREDENTIALS: XXXXXXXX
AZURE_SUBSCRIPTION_ID: xxxxx-xxxxx-xxxxx
```

### Cert-Manager Configuration

```yaml
cert-manager:
  url: "/path/to/cert-manager.yaml" # Custom source
  version: "v1.14.0" # Override default version
  timeout: 15m # Wait timeout (default: 10m)
```

---

## Commands

### init — Initialize Management Cluster

Installs Cluster API providers into management cluster.

```bash
# Auto-detect and install default providers
clusterctl init --infrastructure docker

# Install specific provider versions
clusterctl init --infrastructure aws:v2.0.0

# Install multiple providers
clusterctl init --infrastructure aws --infrastructure vsphere

# Install to specific namespace
clusterctl init --infrastructure aws --target-namespace capa-system

# Pin provider version
clusterctl init --infrastructure docker:v1.9.4
```

**Auto-installed providers:**

- CoreProvider: cluster-api
- BootstrapProvider: kubeadm
- ControlPlaneProvider: kubeadm

**Popular infrastructure providers:**
| Provider | Flag value |
|----------|-----------|
| Docker | `docker` |
| AWS | `aws` |
| Azure | `azure` |
| GCP | `gcp` |
| vSphere | `vsphere` |
| Metal3 | `metal3` |
| OpenStack | `openstack` |

**GitHub Rate Limiting:**

```bash
export GITHUB_TOKEN=<your-token>
clusterctl init --infrastructure docker
```

---

### generate cluster — Create Cluster Manifest

Generates YAML template for workload cluster.

```bash
# Basic cluster
clusterctl generate cluster my-cluster \
  --kubernetes-version v1.28.0 \
  --control-plane-machine-count=3 \
  --worker-machine-count=3 > my-cluster.yaml

# Specify provider
clusterctl generate cluster my-cluster \
  --kubernetes-version v1.28.0 \
  --infrastructure aws > my-cluster.yaml

# Use flavor
clusterctl generate cluster my-cluster \
  --kubernetes-version v1.28.0 \
  --flavor high-availability > my-cluster.yaml

# List required variables
clusterctl generate cluster my-cluster --list-variables

# From custom template
clusterctl generate cluster my-cluster \
  --from https://github.com/myorg/templates/blob/main/template.yaml

# From local file
clusterctl generate cluster my-cluster \
  --from ~/templates/my-template.yaml

# From ConfigMap
clusterctl generate cluster my-cluster \
  --from-config-map my-templates \
  --from-config-map-namespace templates

# From stdin
cat template.yaml | clusterctl generate cluster my-cluster --from -
```

---

### move — Migrate Clusters Between Management Clusters

Moves Cluster API objects from source to target management cluster.

```bash
# Move to target cluster
clusterctl move --to-kubeconfig="path-to-target-kubeconfig.yaml"

# Move specific namespace
clusterctl move --to-kubeconfig="target.yaml" --namespace my-clusters

# Dry run
clusterctl move --to-kubeconfig="target.yaml" --dry-run

# Move to directory (backup)
clusterctl move --to-directory /backup/clusters

# Restore from directory
clusterctl move --from-directory /backup/clusters --to-kubeconfig="target.yaml"
```

**Bootstrap & Pivot Workflow:**

1. Create bootstrap cluster (kind/minikube)
2. `clusterctl init` on bootstrap
3. `clusterctl generate cluster` → create target management cluster
4. Wait for target cluster ready
5. `clusterctl init` on target cluster
6. `clusterctl move --to-kubeconfig="target.yaml"`
7. Delete bootstrap cluster

⚠️ **Warnings:**

- Target cluster must have same or newer provider versions
- Status subresource is never restored
- Not designed for backup/restore (race conditions during upgrades not handled)
- Cluster must be stable during move

---

### upgrade — Upgrade Providers

Upgrades provider components in management cluster.

```bash
# Show upgrade plan
clusterctl upgrade plan

# Apply upgrades (latest stable)
clusterctl upgrade apply --contract v1beta1

# Upgrade specific providers
clusterctl upgrade apply \
  --core cluster-api:v1.9.0 \
  --infrastructure docker:v1.9.0

# Upgrade to pre-release
clusterctl upgrade apply \
  --core cluster-api:v1.10.0-rc.0 \
  --bootstrap kubeadm:v1.10.0-rc.0 \
  --control-plane kubeadm:v1.10.0-rc.0
```

**Upgrade Process:**

1. Check/upgrade cert-manager
2. Delete old provider components (preserves namespace + CRDs)
3. Install new provider components

⚠️ Controller flags not set via components YAML must be re-applied after upgrade.

---

### delete — Remove Providers

```bash
# Delete specific provider
clusterctl delete --infrastructure aws

# Delete provider and namespace
clusterctl delete --infrastructure aws --include-namespace

# Delete provider and CRDs (DELETES ALL OBJECTS)
clusterctl delete --infrastructure aws --include-crd

# Delete all providers
clusterctl delete --all
```

⚠️ `--include-crd` deletes ALL objects of CRD types (all AWSCluster, AWSMachine, etc.)

---

### get kubeconfig — Retrieve Workload Cluster Credentials

```bash
# Get kubeconfig
clusterctl get kubeconfig my-cluster

# Specific namespace
clusterctl get kubeconfig my-cluster --namespace production

# Use specific management cluster context
clusterctl get kubeconfig my-cluster --kubeconfig-context mgmt-context

# Save to file
clusterctl get kubeconfig my-cluster > my-cluster-kubeconfig.yaml
```

---

### describe cluster — Visualize Cluster Status

```bash
# Basic view
clusterctl describe cluster my-cluster

# Show all machines (no grouping)
clusterctl describe cluster my-cluster --grouping=false

# Show infrastructure/bootstrap objects
clusterctl describe cluster my-cluster --echo

# Show all conditions for specific resources
clusterctl describe cluster my-cluster --show-conditions KubeadmControlPlane

# Show all conditions for everything
clusterctl describe cluster my-cluster --show-conditions all
```

---

### alpha rollout — Manage Rollouts

```bash
# Force immediate rollout
clusterctl alpha rollout restart machinedeployment/my-md-0
clusterctl alpha rollout restart kubeadmcontrolplane/my-kcp

# Pause rollout
clusterctl alpha rollout pause machinedeployment/my-md-0

# Resume rollout
clusterctl alpha rollout resume machinedeployment/my-md-0
```

**Supported resources:** MachineDeployment, KubeadmControlPlane

---

### generate yaml — Process Templates

Variable substitution on arbitrary YAML files.

```bash
# Process template
clusterctl generate yaml --from ~/template.yaml

# List variables
clusterctl generate yaml --from ~/template.yaml --list-variables

# From stdin
cat template.yaml | clusterctl generate yaml

# From URL
clusterctl generate yaml --from https://example.com/template.yaml
```

---

### Utility Commands

```bash
# List configured providers
clusterctl config repositories

# Shell completion
clusterctl completion bash > /etc/bash_completion.d/clusterctl
clusterctl completion zsh > "${fpath[1]}/_clusterctl"

# Version
clusterctl version

# List required images (for air-gapped)
clusterctl init list-images --infrastructure docker
```

---

## Variable Substitution

clusterctl uses drone/envsubst for variable substitution in templates.

**Sources (priority order):**

1. Environment variables (highest)
2. clusterctl.yaml config file
3. Default values in template

**Template syntax:**

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  name: ${CLUSTER_NAME}
spec:
  clusterNetwork:
    pods:
      cidrBlocks: ["${POD_CIDR:=192.168.0.0/16}"] # Default value
```

---

## Air-Gapped Installation

1. **List required images:**

```bash
clusterctl init list-images --infrastructure <provider> > images.txt
```

2. **Mirror images to private registry**

3. **Configure image overrides in clusterctl.yaml:**

```yaml
images:
  all:
    repository: myregistry.io/cluster-api
```

4. **Configure cert-manager from local source:**

```yaml
cert-manager:
  url: "/path/to/cert-manager.yaml"
```

---

## Troubleshooting

| Issue                      | Solution                                                                |
| -------------------------- | ----------------------------------------------------------------------- |
| GitHub rate limit          | Set `GITHUB_TOKEN` environment variable                                 |
| Provider not found         | Check `clusterctl config repositories` or add to clusterctl.yaml        |
| Variable not substituted   | Ensure var is set in env or clusterctl.yaml (UPPERCASE_WITH_UNDERSCORE) |
| Cert-manager timeout       | Increase `cert-manager.timeout` in config                               |
| Move fails with annotation | Wait for `clusterctl.cluster.x-k8s.io/block-move` annotation removal    |
