# Certificate Management

## Overview

Cluster API Bootstrap Provider Kubeadm (CABPK) generates certificates if they don't exist. You can provide custom certificates for more control.

## Custom CA Certificates

### Required Secrets

Each certificate stored in a secret with specific naming:

| Secret Name            | Type     | Purpose                 |
| ---------------------- | -------- | ----------------------- |
| `[cluster-name]-ca`    | CA       | Kubernetes API CA       |
| `[cluster-name]-etcd`  | CA       | etcd CA                 |
| `[cluster-name]-proxy` | CA       | Front-end proxy CA      |
| `[cluster-name]-sa`    | Key Pair | Service account signing |

### Secret Format

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cluster1-ca
  labels:
    cluster.x-k8s.io/cluster-name: cluster1 # REQUIRED label
type: kubernetes.io/tls
data:
  tls.crt: <base64 encoded PEM>
  tls.key: <base64 encoded PEM>
```

**CRITICAL**: Secrets MUST be labeled with `cluster.x-k8s.io/cluster-name=[cluster-name]`

### Generate CA Certificates

```bash
# Kubernetes API CA
openssl req -x509 -subj "/CN=Kubernetes API" -new -newkey rsa:2048 -nodes \
  -keyout tls.key -sha256 -days 3650 -out tls.crt

# etcd CA
openssl req -x509 -subj "/CN=ETCD CA" -new -newkey rsa:2048 -nodes \
  -keyout tls.key -sha256 -days 3650 -out tls.crt

# Front-end Proxy CA
openssl req -x509 -subj "/CN=Front-End Proxy" -new -newkey rsa:2048 -nodes \
  -keyout tls.key -sha256 -days 3650 -out tls.crt

# Service Account Key Pair
openssl genrsa -out tls.key 2048
openssl rsa -in tls.key -pubout -out tls.crt
```

### CA Key Lifetime

**Recommendation**: Use long-lived CA (or long-lived root CA with short-lived intermediary) - CA rotation is non-trivial.

## Generate Kubeconfig with Custom CA

When using custom certificates:

### 1. Create CSR for Admin User

```bash
openssl req -subj "/CN=admin/O=system:masters" -new -newkey rsa:2048 -nodes \
  -keyout admin.key -out admin.csr
```

### 2. Sign CSR with Cluster CA

```bash
openssl x509 -req -in admin.csr -CA tls.crt -CAkey tls.key \
  -CAcreateserial -out admin.crt -days 5 -sha256
```

### 3. Update Kubeconfig

```bash
kubectl config set-credentials cluster-admin \
  --client-certificate=admin.crt \
  --client-key=admin.key \
  --embed-certs=true
```

## Automatic Certificate Rotation (KCP)

KubeadmControlPlane provider supports automatic certificate rotation via machine rollout.

### Configuration

```yaml
apiVersion: controlplane.cluster.x-k8s.io/v1beta2
kind: KubeadmControlPlane
metadata:
  name: example-control-plane
spec:
  rolloutBefore:
    certificatesExpiryDays: 21 # Minimum: 7 days
  kubeadmConfigSpec:
    clusterConfiguration: {}
    initConfiguration: {}
    joinConfiguration: {}
  machineTemplate:
    infrastructureRef: {}
  replicas: 3
  version: v1.35.0
```

### How It Works

1. KCP monitors `Machine.Status.CertificatesExpiryDate`
2. When certificates expire within `certificatesExpiryDays`, triggers rollout
3. New machines created with fresh certificates

### Certificate Expiry Source

Priority order:

1. `machine.cluster.x-k8s.io/certificates-expiry` annotation on Machine
2. `machine.cluster.x-k8s.io/certificates-expiry` annotation on Bootstrap Config

**Note**: All certificates on control plane node assumed to have same expiry time. Decision based on kube-apiserver certificate.

### Best Practice

Set `certificatesExpiryDays` large enough for complete rollout before expiration.

### Manual Certificate Rotation

If using `kubeadm certs renew`:

1. Renew certificates
2. Restart: kube-apiserver, kube-controller-manager, kube-scheduler, etcd
3. Remove annotation from KubeadmConfig to allow KCP re-discovery:

```bash
kubectl annotate kubeadmconfig <config-name> \
  machine.cluster.x-k8s.io/certificates-expiry-
```
