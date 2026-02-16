# Bootstrap Provider (Kubeadm)

## Overview

Cluster API Bootstrap Provider Kubeadm (CABPK) generates cloud-init scripts to turn Machines into Kubernetes Nodes using kubeadm.

## How It Works

1. CABPK converts `KubeadmConfig` into cloud-init script
2. Script stored in secret (`KubeadmConfig.Status.DataSecretName`)
3. Infrastructure provider uses script to bootstrap machine

## Bootstrap Orchestration

CABPK orchestrates multi-node cluster bootstrap:

1. Wait for `Cluster.Status.InfrastructureReady = true`
2. Generate cloud-config for **first control plane only** (kubeadm init)
3. Wait for `ControlPlaneInitialized` condition on cluster
4. Generate cloud-config for **all other machines** (kubeadm join)

## KubeadmConfig Resource

### Default Values (Auto-filled)

| Field                                           | Default Source                                      |
| ----------------------------------------------- | --------------------------------------------------- |
| `clusterConfiguration.KubernetesVersion`        | `Machine.Spec.Version`                              |
| `clusterConfiguration.clusterName`              | `Cluster.metadata.name`                             |
| `clusterConfiguration.controlPlaneEndpoint`     | `Cluster.status.apiEndpoints[0]`                    |
| `clusterConfiguration.networking.dnsDomain`     | `Cluster.spec.clusterNetwork.serviceDomain`         |
| `clusterConfiguration.networking.serviceSubnet` | `Cluster.spec.clusterNetwork.service.cidrBlocks[0]` |
| `clusterConfiguration.networking.podSubnet`     | `Cluster.spec.clusterNetwork.pods.cidrBlocks[0]`    |
| `joinConfiguration.discovery`                   | Auto-generated short-lived BootstrapToken           |

**WARNING**: Overriding defaults can break clusters!

### Valid Configurations

| Node Type                 | Configuration Objects                       |
| ------------------------- | ------------------------------------------- |
| First control plane       | `InitConfiguration`, `ClusterConfiguration` |
| Additional control planes | `JoinConfiguration` with `controlPlane: {}` |
| Workers                   | `JoinConfiguration`                         |

### Examples

**First control plane:**

```yaml
apiVersion: bootstrap.cluster.x-k8s.io/v1beta2
kind: KubeadmConfig
metadata:
  name: my-control-plane1-config
```

**Additional control plane:**

```yaml
apiVersion: bootstrap.cluster.x-k8s.io/v1beta2
kind: KubeadmConfig
metadata:
  name: my-control-plane2-config
spec:
  joinConfiguration:
    controlPlane: {}
```

**Worker node:**

```yaml
apiVersion: bootstrap.cluster.x-k8s.io/v1beta2
kind: KubeadmConfig
metadata:
  name: my-worker1-config
```

## Customization Options

### Files

Add files to nodes (inline content or from secret):

```yaml
files:
  - path: /etc/kubernetes/cloud.json
    owner: "root:root"
    permissions: "0644"
    content: |
      {"cloud": "CustomCloud"}
  - contentFrom:
      secret:
        key: node-cloud.json
        name: ${CLUSTER_NAME}-cloud-json
    owner: root:root
    path: /etc/kubernetes/cloud.json
    permissions: "0644"
```

### Commands

```yaml
# Very early in boot
bootCommands:
  - cloud-init-per once mymkfs mkfs /dev/vdb

# Before kubeadm init/join
preKubeadmCommands:
  - hostname "{{ ds.meta_data.hostname }}"
  - echo "{{ ds.meta_data.hostname }}" >/etc/hostname

# After kubeadm init/join
postKubeadmCommands:
  - echo "success" >/var/log/my-custom-file.log
```

### Users

```yaml
users:
  - name: capiuser
    sshAuthorizedKeys:
      - "${SSH_AUTHORIZED_KEY}"
    sudo: ALL=(ALL) NOPASSWD:ALL
```

### NTP

```yaml
ntp:
  servers:
    - 0.pool.ntp.org
  enabled: true
```

### Disk Setup

```yaml
diskSetup:
  partitions:
    - device: /dev/disk/azure/scsi1/lun0
      layout: true
      overwrite: false
      tableType: gpt
  filesystems:
    - device: /dev/disk/azure/scsi1/lun0
      extraOpts:
        - -E
        - lazy_itable_init=1,lazy_journal_init=1
      filesystem: ext4
      label: etcd_disk

mounts:
  - - LABEL=etcd_disk
    - /var/lib/etcddisk
```

### Verbosity

```yaml
verbosity: 10 # kubeadm log level
```

## Kubelet Configuration

Three methods to configure kubelet:

### Method 1: KubeletConfiguration File

Replace entire kubelet configuration:

```yaml
apiVersion: bootstrap.cluster.x-k8s.io/v1beta2
kind: KubeadmConfigTemplate
spec:
  template:
    spec:
      files:
        - path: /etc/kubernetes/kubelet/config.yaml
          owner: "root:root"
          permissions: "0644"
          content: |
            apiVersion: kubelet.config.k8s.io/v1beta1
            kind: KubeletConfiguration
            kubeReserved:
              cpu: "1"
              memory: "2Gi"
              ephemeral-storage: "1Gi"
            systemReserved:
              cpu: "500m"
              memory: "1Gi"
              ephemeral-storage: "1Gi"
            evictionHard:
              memory.available: "500Mi"
              nodefs.available: "10%"
            cgroupDriver: systemd
            clusterDNS:
            - 10.128.0.10
            clusterDomain: cluster.local
            rotateCertificates: true
      joinConfiguration:
        nodeRegistration:
          kubeletExtraArgs:
            - name: config
              value: "/etc/kubernetes/kubelet/config.yaml"
```

### Method 2: kubeletExtraArgs (Command-line Flags)

For flags not in KubeletConfiguration:

```yaml
joinConfiguration:
  nodeRegistration:
    kubeletExtraArgs:
      - name: kube-reserved
        value: "cpu=1,memory=2Gi,ephemeral-storage=1Gi"
      - name: system-reserved
        value: "cpu=500m,memory=1Gi,ephemeral-storage=1Gi"
      - name: eviction-hard
        value: "memory.available<500Mi,nodefs.available<10%"
```

### Method 3: Kubeadm Patches

Partial kubelet configuration changes (K8s 1.22+):

```yaml
spec:
  files:
    - path: /etc/kubernetes/patches/kubeletconfiguration0+strategic.json
      owner: "root:root"
      permissions: "0644"
      content: |
        {
          "apiVersion": "kubelet.config.k8s.io/v1beta1",
          "kind": "KubeletConfiguration",
          "kubeReserved": {
            "cpu": "1",
            "memory": "2Gi"
          }
        }
  joinConfiguration:
    patches:
      directory: /etc/kubernetes/patches
```

**Patch file naming**: `kubeletconfiguration{suffix}+{patchtype}.json`

- `{suffix}` - determines order (alpha-numerical)
- `{patchtype}` - `strategic`, `merge`, or `json`

## Best Practices

1. **Don't override defaults** unless necessary
2. **Use KubeletConfiguration file** for comprehensive changes
3. **Use patches** for partial changes on specific nodes
4. **Use kubeletExtraArgs** only for flags not in KubeletConfiguration
5. **Test bootstrap** in development environment first

---

## MicroK8s Bootstrap Provider (Alternative)

### Overview

CABPM (Cluster API Bootstrap Provider MicroK8s) uses MicroK8s instead of kubeadm.

### Configuration

**Control Plane:**

```yaml
apiVersion: controlplane.cluster.x-k8s.io/v1beta1
kind: MicroK8sControlPlane
spec:
  controlPlaneConfig:
    initConfiguration:
      addons:
        - dns
        - ingress
  replicas: 3
  version: v1.23.0
```

**Workers:**

```yaml
apiVersion: bootstrap.cluster.x-k8s.io/v1beta1
kind: MicroK8sConfigTemplate
metadata:
  name: capi-aws-md-0
spec:
  template:
    spec: {}
```

### Configuration Options

| Option                                        | Description                        | Default  |
| --------------------------------------------- | ---------------------------------- | -------- |
| `initConfiguration.joinTokenTTLInSecs`        | Token TTL for joining nodes        | 10 years |
| `initConfiguration.httpsProxy`                | HTTPS proxy                        | none     |
| `initConfiguration.httpProxy`                 | HTTP proxy                         | none     |
| `initConfiguration.noProxy`                   | No-proxy list                      | none     |
| `initConfiguration.addons`                    | Addons to enable                   | dns      |
| `clusterConfiguration.portCompatibilityRemap` | Reuse kubeadm security group ports | true     |

### Cloud-init Types

1. **First node** - Control plane, enables addons
2. **Control plane nodes** - Join cluster for HA
3. **Worker nodes** - Join as workers
