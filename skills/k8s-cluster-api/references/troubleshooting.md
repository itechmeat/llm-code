# Troubleshooting

## Quick Diagnosis

```bash
# Cluster overview
clusterctl describe cluster <name>

# Show all conditions
clusterctl describe cluster <name> --show-conditions all

# Machine details
kubectl describe machines -l cluster.x-k8s.io/cluster-name=<name>

# Controller logs
kubectl logs -n capi-system deployment/capi-controller-manager -f

# Provider logs
kubectl logs -n <provider-namespace> deployment/<provider>-controller-manager -f
```

---

## Common Issues

### Machine Bootstrap Failed

**Symptoms:** `BootstrapFailed` reason in Machine status

**Diagnosis:**

```bash
# Check Machine conditions
kubectl describe machine <name>

# If using Docker provider
docker logs <machine-name>

# If using cloud provider - access node via SSH
ssh <node-ip>
less /var/log/cloud-init-output.log
journalctl -u cloud-init --since "1 day ago"
```

**Common causes:**

- cloud-init misconfiguration
- Network connectivity issues
- kubeadm timeout waiting for static pods

**For kubeadm timeouts:**

```bash
# On the node
crictl ps -a
crictl logs <container-id>
journalctl -u containerd
journalctl -u kubelet --since "1 day ago"

# Increase kubelet verbosity
systemctl edit --full kubelet  # Add --v=8
systemctl restart kubelet
```

**Increase kubeadm verbosity:**

```yaml
apiVersion: bootstrap.cluster.x-k8s.io/v1beta1
kind: KubeadmConfig
spec:
  verbosity: 6 # Increase for more details
```

---

### Node Labels with Reserved Prefixes

**Error:** Cannot use `node-role.kubernetes.io/*` labels via `kubeletExtraArgs`

**Cause:** NodeRestriction admission controller blocks self-assignment of reserved labels.

**Solution:** Label nodes after bootstrap:

```bash
# Kubernetes >= 1.20
kubectl get nodes --no-headers \
  -l '!node-role.kubernetes.io/control-plane' \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}' | \
  xargs -I{} kubectl label node {} node-role.kubernetes.io/worker=''
```

---

### Docker Provider Issues

#### "Too many open files"

**Symptoms:**

```
Failed to create inotify object: Too many open files
Failed to allocate manager object: Too many open files
```

**Solution (Linux):**

```bash
sysctl fs.inotify.max_user_watches=1048576
sysctl fs.inotify.max_user_instances=8192
```

**Solution (macOS Docker Desktop 4.3-4.4):**

```bash
# Enter Docker VM
nc -U ~/Library/Containers/com.docker.docker/Data/debug-shell.sock

# Increase limits
sysctl fs.inotify.max_user_watches=1048576
sysctl fs.inotify.max_user_instances=8192
exit
```

**Best fix:** Upgrade to Docker Desktop 4.5+

#### Containers Stuck/Restarting

**Diagnosis:**

```bash
docker ps --all
docker logs <container-name>
```

**Resolution:**

```bash
# Clean up containers from previous runs
docker rm -f $(docker ps -aq)

# Clean Docker resources
docker system prune --volumes

# Check disk space
docker system df
```

---

### clusterctl init Failures

#### "failed to get cert-manager object"

**Symptoms:**

```
Error: action failed after 10 attempts: failed to get cert-manager object
```

**Cause:** Old CAPI versions (0.4.6, 1.0.3 and older) reference outdated cert-manager URL.

**Solutions:**

1. **Upgrade CAPI** to newer patch release

2. **Override cert-manager URL** in `~/.config/cluster-api/clusterctl.yaml`:

```yaml
cert-manager:
  url: "https://github.com/cert-manager/cert-manager/releases/latest/cert-manager.yaml"
```

3. **Use override file:**

```bash
# Place at:
~/.config/cluster-api/overrides/cert-manager/v1.11.0/cert-manager.yaml
```

---

### clusterctl upgrade Failures

#### "failed to update cert-manager component"

**Cause:** Breaking change in cert-manager v1.6 when upgrading from < v1.0.0.

**Solution:**

```bash
# Manually delete cert-manager CRDs if migration fails
kubectl delete crd certificates.cert-manager.io
kubectl delete crd certificaterequests.cert-manager.io
kubectl delete crd clusterissuers.cert-manager.io
kubectl delete crd issuers.cert-manager.io
kubectl delete crd orders.acme.cert-manager.io
kubectl delete crd challenges.acme.cert-manager.io

# Retry upgrade
clusterctl upgrade apply
```

---

### Outdated Image Overrides

**Symptoms:** clusterctl fails to start providers after upgrade

**Cause:** Old image tags in `~/.cluster-api/` cache

**Solution:**

```bash
# Clear clusterctl cache
rm -rf ~/.cluster-api/

# Re-initialize
clusterctl init --infrastructure <provider>
```

---

### Move Operation Failures

#### Block-move Annotation Present

**Symptoms:** `clusterctl move` hangs

**Cause:** Resource has `clusterctl.cluster.x-k8s.io/block-move` annotation

**Solution:**

```bash
# Check for blocking annotations
kubectl get clusters,machines -A \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.annotations}{"\n"}{end}' | \
  grep block-move

# Wait for operations to complete or remove annotation if safe
kubectl annotate <resource> <name> clusterctl.cluster.x-k8s.io/block-move-
```

---

### Server Side Apply Conflicts

**Symptoms:** "Failed to remove fields from lists using Server Side Apply"

**Cause:** SSA conflict when removing items from lists

**Solution:** Use strategic merge patch instead:

```bash
kubectl patch <resource> <name> --type=merge -p '{"spec":{"field":[]}}'
```

---

## Diagnostic Tools

### Controller Logs

```bash
# Core CAPI
kubectl logs -n capi-system deployment/capi-controller-manager --tail=100 -f

# Bootstrap provider
kubectl logs -n capi-kubeadm-bootstrap-system \
  deployment/capi-kubeadm-bootstrap-controller-manager -f

# Control plane provider
kubectl logs -n capi-kubeadm-control-plane-system \
  deployment/capi-kubeadm-control-plane-controller-manager -f

# Infrastructure provider (e.g., AWS)
kubectl logs -n capa-system deployment/capa-controller-manager -f
```

### Events

```bash
# Cluster events
kubectl get events -n <namespace> --sort-by='.lastTimestamp' | grep <cluster-name>

# Machine events
kubectl get events -n <namespace> --field-selector involvedObject.kind=Machine
```

### Conditions Reference

| Condition                     | Meaning                      |
| ----------------------------- | ---------------------------- |
| `Ready`                       | Resource is operational      |
| `InfrastructureReady`         | Infrastructure provisioned   |
| `ControlPlaneReady`           | Control plane is available   |
| `BootstrapReady`              | Bootstrap data generated     |
| `MachinesReady`               | All machines are ready       |
| `ScalingUp`                   | Adding new replicas          |
| `ScalingDown`                 | Removing replicas            |
| `WaitingForAvailableMachines` | Waiting for minimum replicas |
