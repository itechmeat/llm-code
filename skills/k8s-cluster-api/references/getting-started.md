# Getting Started with Cluster API

## Prerequisites

- kubectl installed and configured
- kind and Docker installed
- Helm installed
- Kubernetes cluster v1.20.0+ (for production) or kind (for development)

## Two Installation Paths

| Path                     | Use Case                       | Approach          |
| ------------------------ | ------------------------------ | ----------------- |
| **clusterctl**           | Day-1 experience, quick start  | CLI-based         |
| **Cluster API Operator** | GitOps, declarative management | Kubernetes-native |

---

## Path 1: clusterctl (CLI)

## Bootstrap Cluster Setup

### Using kind (Development)

```bash
# Create kind cluster
kind create cluster

# Verify cluster
kubectl cluster-info
```

### For Docker Provider (CAPD)

```bash
# Create config with Docker socket mount
cat > kind-cluster-with-extramounts.yaml <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
networking:
  ipFamily: dual
nodes:
- role: control-plane
  extraMounts:
    - hostPath: /var/run/docker.sock
      containerPath: /var/run/docker.sock
EOF

kind create cluster --config kind-cluster-with-extramounts.yaml
```

### For KubeVirt Provider

Requires Calico CNI instead of kindnet:

```bash
cat <<EOF > kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
networking:
  disableDefaultCNI: true
nodes:
- role: control-plane
  extraMounts:
  - containerPath: /var/lib/kubelet/config.json
    hostPath: <YOUR DOCKER CONFIG FILE PATH>
EOF

kind create cluster --config=kind-config.yaml

# Install Calico
kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.29.1/manifests/calico.yaml
```

## Install clusterctl

### Linux

```bash
# AMD64
curl -L https://github.com/kubernetes-sigs/cluster-api/releases/download/v1.12.2/clusterctl-linux-amd64 -o clusterctl
# ARM64
curl -L https://github.com/kubernetes-sigs/cluster-api/releases/download/v1.12.2/clusterctl-linux-arm64 -o clusterctl

sudo install -o root -g root -m 0755 clusterctl /usr/local/bin/clusterctl
clusterctl version
```

### macOS

```bash
# AMD64
curl -L https://github.com/kubernetes-sigs/cluster-api/releases/download/v1.12.2/clusterctl-darwin-amd64 -o clusterctl
# ARM64 (Apple Silicon)
curl -L https://github.com/kubernetes-sigs/cluster-api/releases/download/v1.12.2/clusterctl-darwin-arm64 -o clusterctl

chmod +x ./clusterctl
sudo mv ./clusterctl /usr/local/bin/clusterctl
```

### Homebrew (macOS/Linux)

```bash
brew install clusterctl
```

### Windows (PowerShell)

```powershell
curl.exe -L https://github.com/kubernetes-sigs/cluster-api/releases/download/v1.12.2/clusterctl-windows-amd64.exe -o clusterctl.exe
```

## Initialize Management Cluster

### Enable Feature Gates (Optional)

```bash
# Enable ClusterTopology for managed topologies
export CLUSTER_TOPOLOGY=true
```

### Provider-Specific Initialization

#### Docker (Development)

```bash
clusterctl init --infrastructure docker
```

#### AWS

```bash
# Install clusterawsadm
curl -L https://github.com/kubernetes-sigs/cluster-api-provider-aws/releases/download/v2.10.1/clusterawsadm-linux-amd64 -o clusterawsadm
chmod +x clusterawsadm
sudo mv clusterawsadm /usr/local/bin

# Configure credentials
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=<your-access-key>
export AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
export AWS_SESSION_TOKEN=<session-token>  # if using temporary credentials

# Create IAM resources
clusterawsadm bootstrap iam create-cloudformation-stack

# Encode credentials
export AWS_B64ENCODED_CREDENTIALS=$(clusterawsadm bootstrap credentials encode-as-profile)

# Initialize
clusterctl init --infrastructure aws
```

#### Azure

```bash
export AZURE_SUBSCRIPTION_ID="<SubscriptionId>"
export AZURE_TENANT_ID="<Tenant>"
export AZURE_CLIENT_ID="<AppId>"
export AZURE_CLIENT_ID_USER_ASSIGNED_IDENTITY=$AZURE_CLIENT_ID
export AZURE_CLIENT_SECRET="<Password>"

export AZURE_CLUSTER_IDENTITY_SECRET_NAME="cluster-identity-secret"
export CLUSTER_IDENTITY_NAME="cluster-identity"
export AZURE_CLUSTER_IDENTITY_SECRET_NAMESPACE="default"

# Create identity secret
kubectl create secret generic "${AZURE_CLUSTER_IDENTITY_SECRET_NAME}" \
  --from-literal=clientSecret="${AZURE_CLIENT_SECRET}" \
  --namespace "${AZURE_CLUSTER_IDENTITY_SECRET_NAMESPACE}"

clusterctl init --infrastructure azure
```

#### GCP

```bash
export GCP_B64ENCODED_CREDENTIALS=$(cat /path/to/gcp-credentials.json | base64 | tr -d '\n')
clusterctl init --infrastructure gcp
```

#### Linode

```bash
export LINODE_TOKEN=<your-access-token>
clusterctl init --infrastructure linode-linode
```

#### vSphere

```bash
export VSPHERE_USERNAME="user"
export VSPHERE_PASSWORD="pass"
clusterctl init --infrastructure vsphere
```

### Init Output

```
Fetching providers
Installing cert-manager Version="v1.11.0"
Waiting for cert-manager to be available...
Installing Provider="cluster-api" Version="v1.0.0" TargetNamespace="capi-system"
Installing Provider="bootstrap-kubeadm" Version="v1.0.0" TargetNamespace="capi-kubeadm-bootstrap-system"
Installing Provider="control-plane-kubeadm" Version="v1.0.0" TargetNamespace="capi-kubeadm-control-plane-system"
Installing Provider="infrastructure-docker" Version="v1.0.0" TargetNamespace="capd-system"

Your management cluster has been initialized successfully!
```

## Create Workload Cluster

### Generate Cluster Manifest

```bash
# Docker (development)
clusterctl generate cluster capi-quickstart --flavor development \
  --kubernetes-version v1.35.0 \
  --control-plane-machine-count=3 \
  --worker-machine-count=3 \
  > capi-quickstart.yaml

# With MachinePools
clusterctl generate cluster capi-quickstart --flavor development-mp \
  --kubernetes-version v1.35.0 \
  --control-plane-machine-count=3 \
  --worker-machine-count=3 \
  > capi-quickstart.yaml
```

### Apply Cluster

```bash
kubectl apply -f capi-quickstart.yaml
```

### Monitor Provisioning

```bash
# Check cluster status
kubectl get cluster

# Detailed cluster view
clusterctl describe cluster capi-quickstart

# Check control plane
kubectl get kubeadmcontrolplane
```

## Access Workload Cluster

### Get Kubeconfig

```bash
# Standard method
clusterctl get kubeconfig capi-quickstart > capi-quickstart.kubeconfig

# For Docker Desktop with kind
kind get kubeconfig --name capi-quickstart > capi-quickstart.kubeconfig
```

### Install Cloud Provider (if needed)

```bash
# Azure example
helm install --kubeconfig=./capi-quickstart.kubeconfig \
  --repo https://raw.githubusercontent.com/kubernetes-sigs/cloud-provider-azure/master/helm/repo \
  cloud-provider-azure --generate-name \
  --set infra.clusterName=capi-quickstart \
  --set cloudControllerManager.clusterCIDR="192.168.0.0/16"
```

### Install CNI

```bash
# Calico via Helm
helm repo add projectcalico https://docs.tigera.io/calico/charts --kubeconfig=./capi-quickstart.kubeconfig
helm install calico projectcalico/tigera-operator \
  --kubeconfig=./capi-quickstart.kubeconfig \
  -f https://raw.githubusercontent.com/kubernetes-sigs/cluster-api-provider-azure/main/templates/addons/calico/values.yaml \
  --namespace tigera-operator --create-namespace

# Or upstream manifest
kubectl --kubeconfig=./capi-quickstart.kubeconfig \
  apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.1/manifests/calico.yaml
```

### Verify Nodes

```bash
kubectl --kubeconfig=./capi-quickstart.kubeconfig get nodes
```

## Cleanup

```bash
# Delete workload cluster (ALWAYS use this method)
kubectl delete cluster capi-quickstart

# Delete management cluster
kind delete cluster
```

**IMPORTANT**: Always delete cluster objects via `kubectl delete cluster`. Using `kubectl delete -f capi-quickstart.yaml` may leave infrastructure resources orphaned.

## Troubleshooting

### Calico Image Pull Errors

```bash
# Create Docker Hub credentials secret
kubectl --kubeconfig=./capi-quickstart.kubeconfig create secret generic docker-creds \
  --from-file=.dockerconfigjson=<YOUR DOCKER CONFIG FILE PATH> \
  --type=kubernetes.io/dockerconfigjson \
  -n kube-system

# Patch calico-node DaemonSet
kubectl --kubeconfig=./capi-quickstart.kubeconfig patch daemonset \
  -n kube-system calico-node \
  -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"docker-creds"}]}}}}'

# Patch calico-kube-controllers Deployment
kubectl --kubeconfig=./capi-quickstart.kubeconfig patch deployment \
  -n kube-system calico-kube-controllers \
  -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"docker-creds"}]}}}}'
```

### KubeVirt CNI Conflicts

When using KubeVirt, modify Calico to avoid conflicts with management cluster CNI:

```bash
curl https://raw.githubusercontent.com/projectcalico/calico/v3.29.1/manifests/calico.yaml -o calico-workload.yaml

# Modify CIDR, CLUSTER_TYPE, IPIP, VXLAN settings
sed -i -E 's|^( +)# (- name: CALICO_IPV4POOL_CIDR)$|\1\2|g;'\
's|^( +)# (  value: )"192.168.0.0/16"|\1\2"10.243.0.0/16"|g;'\
'/- name: CLUSTER_TYPE/{ n; s/( +value: ").+/\1k8s"/g };'\
'/- name: CALICO_IPV4POOL_IPIP/{ n; s/value: "Always"/value: "Never"/ };'\
'/- name: CALICO_IPV4POOL_VXLAN/{ n; s/value: "Never"/value: "Always"/};'\
'/# Set Felix endpoint to host default action to ACCEPT./a\            - name: FELIX_VXLANPORT\n              value: "6789"' \
calico-workload.yaml

kubectl --kubeconfig=./capi-quickstart.kubeconfig create -f calico-workload.yaml
```

---

## Path 2: Cluster API Operator (Declarative/GitOps)

### Prerequisites

- Running Kubernetes cluster
- kubectl
- Helm

### Configure Credentials

Cluster API Operator uses Kubernetes secrets instead of environment variables:

```bash
export CREDENTIALS_SECRET_NAME="credentials-secret"
export CREDENTIALS_SECRET_NAMESPACE="default"

# AWS example
kubectl create secret generic "${CREDENTIALS_SECRET_NAME}" \
  --from-literal=AWS_B64ENCODED_CREDENTIALS="${AWS_B64ENCODED_CREDENTIALS}" \
  --namespace "${CREDENTIALS_SECRET_NAMESPACE}"
```

### Install Operator via Helm

```bash
# Add repositories
helm repo add capi-operator https://kubernetes-sigs.github.io/cluster-api-operator
helm repo add jetstack https://charts.jetstack.io --force-update
helm repo update

# Install cert-manager
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set installCRDs=true

# Install Cluster API Operator with provider
# IMPORTANT: --wait flag is REQUIRED
helm install capi-operator capi-operator/cluster-api-operator \
  --create-namespace -n capi-operator-system \
  --set infrastructure.docker.enabled=true \
  --set configSecret.name=${CREDENTIALS_SECRET_NAME} \
  --set configSecret.namespace=${CREDENTIALS_SECRET_NAMESPACE} \
  --wait --timeout 90s
```

### Declarative Provider Management

Deploy core provider:

```yaml
apiVersion: operator.cluster.x-k8s.io/v1alpha2
kind: CoreProvider
metadata:
  name: cluster-api
  namespace: capi-system
```

Deploy infrastructure provider with version:

```yaml
apiVersion: operator.cluster.x-k8s.io/v1alpha2
kind: InfrastructureProvider
metadata:
  name: aws
  namespace: capa-system
spec:
  version: v2.1.4
  configSecret:
    name: credentials-secret
```

### Provider Types

| CRD                    | Purpose                                 |
| ---------------------- | --------------------------------------- |
| CoreProvider           | Cluster API core controllers            |
| InfrastructureProvider | Cloud/infra specific (AWS, Azure, etc.) |
| BootstrapProvider      | Node bootstrap (kubeadm, etc.)          |
| ControlPlaneProvider   | Control plane management                |
| AddonProvider          | Add-on management                       |
| IPAMProvider           | IP address management                   |
