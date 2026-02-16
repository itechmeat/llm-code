# Provider Version Compatibility Matrix

Version compatibility between Cluster API and providers.

## CAPI Core Version Support

| CAPI Version | Kubernetes Support | Go Version | Release Date | EOL      |
| ------------ | ------------------ | ---------- | ------------ | -------- |
| v1.12.x      | v1.31 - v1.35      | 1.24       | Oct 2025     | Current  |
| v1.11.x      | v1.30 - v1.34      | 1.24       | Jul 2025     | Apr 2026 |
| v1.10.x      | v1.29 - v1.33      | 1.23       | Apr 2025     | Jan 2026 |
| v1.9.x       | v1.28 - v1.32      | 1.23       | Jan 2025     | Oct 2025 |
| v1.8.x       | v1.27 - v1.31      | 1.22       | Oct 2024     | Jul 2025 |
| v1.7.x       | v1.26 - v1.30      | 1.22       | Jul 2024     | Apr 2025 |
| v1.6.x       | v1.25 - v1.29      | 1.21       | Apr 2024     | Jan 2025 |

## Infrastructure Providers

### AWS (CAPA)

| CAPA Version | CAPI Compatibility | AWS SDK | Notes   |
| ------------ | ------------------ | ------- | ------- |
| v2.7.x       | v1.8+              | v2.x    | Current |
| v2.6.x       | v1.7+              | v2.x    |         |
| v2.5.x       | v1.6+              | v2.x    |         |
| v2.4.x       | v1.5+              | v2.x    |         |

### Azure (CAPZ)

| CAPZ Version | CAPI Compatibility | Notes   |
| ------------ | ------------------ | ------- |
| v1.18.x      | v1.8+              | Current |
| v1.17.x      | v1.7+              |         |
| v1.16.x      | v1.6+              |         |

### vSphere (CAPV)

| CAPV Version | CAPI Compatibility | vSphere Version | Notes   |
| ------------ | ------------------ | --------------- | ------- |
| v1.12.x      | v1.8+              | 7.0+            | Current |
| v1.11.x      | v1.7+              | 7.0+            |         |
| v1.10.x      | v1.6+              | 7.0+            |         |

### Docker (CAPD)

| CAPD Version | CAPI Compatibility | Notes                                       |
| ------------ | ------------------ | ------------------------------------------- |
| v1.12.x      | v1.12              | Development only, included in CAPI releases |

### GCP (CAPG)

| CAPG Version | CAPI Compatibility | Notes   |
| ------------ | ------------------ | ------- |
| v1.9.x       | v1.8+              | Current |
| v1.8.x       | v1.7+              |         |

## Bootstrap Providers

### Kubeadm (CABPK)

Included in CAPI core releases. Version matches CAPI.

### K3s (CABP-K3s)

| Version | CAPI Compatibility | K3s Version |
| ------- | ------------------ | ----------- |
| v0.2.x  | v1.6+              | v1.27+      |

### Talos

| Version | CAPI Compatibility | Talos Version |
| ------- | ------------------ | ------------- |
| v0.6.x  | v1.6+              | 1.6+          |

## Control Plane Providers

### Kubeadm (KCP)

Included in CAPI core releases. Version matches CAPI.

### K3s

| Version | CAPI Compatibility |
| ------- | ------------------ |
| v0.2.x  | v1.6+              |

## Upgrade Paths

### CAPI Upgrades

Direct upgrades supported between minor versions (e.g., v1.6 → v1.7).

```
v1.6.x → v1.7.x → v1.8.x → v1.9.x → v1.10.x → v1.11.x → v1.12.x
```

**Note**: Skipping minor versions not recommended.

### Provider Upgrades

Always upgrade CAPI core before providers:

1. Upgrade CAPI core
2. Upgrade bootstrap provider
3. Upgrade control plane provider
4. Upgrade infrastructure provider

### Pre-upgrade Checklist

- [ ] Review release notes for breaking changes
- [ ] Verify Kubernetes version compatibility
- [ ] Backup cluster state (`clusterctl move` or export)
- [ ] Check provider version compatibility
- [ ] Run `clusterctl upgrade plan`

## API Version Timeline

| API Version | Status     | CAPI Version |
| ----------- | ---------- | ------------ |
| v1beta2     | Current    | v1.8+        |
| v1beta1     | Deprecated | v1.0 - v1.12 |
| v1alpha4    | Removed    | < v1.0       |
| v1alpha3    | Removed    | < v0.4       |

## Finding Compatible Versions

```bash
# Show upgrade plan
clusterctl upgrade plan

# Check provider contract version
kubectl get providers -A -o wide

# Verify installed versions
clusterctl version
```

## Links

- [CAPI Releases](https://github.com/kubernetes-sigs/cluster-api/releases)
- [Provider List](https://cluster-api.sigs.k8s.io/reference/providers)
- [Version Support Policy](https://cluster-api.sigs.k8s.io/reference/versions)
