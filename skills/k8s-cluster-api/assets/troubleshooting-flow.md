# Troubleshooting Decision Flowchart

Quick reference for diagnosing CAPI cluster issues.

## Primary Diagnosis Flow

```
START: Cluster Issue Reported
          │
          ▼
┌─────────────────────────┐
│ Run: clusterctl describe│
│ cluster <name>          │
└─────────────────────────┘
          │
          ▼
    ┌───────────┐
    │ Cluster   │──No──▶ Section A: Cluster Not Found
    │ Exists?   │
    └───────────┘
          │Yes
          ▼
    ┌───────────┐
    │ Cluster   │──No──▶ Section B: Cluster Not Ready
    │ Ready?    │
    └───────────┘
          │Yes
          ▼
    ┌───────────┐
    │ Control   │──No──▶ Section C: Control Plane Issues
    │ Plane OK? │
    └───────────┘
          │Yes
          ▼
    ┌───────────┐
    │ Workers   │──No──▶ Section D: Worker Issues
    │ Ready?    │
    └───────────┘
          │Yes
          ▼
    ┌───────────┐
    │ Workloads │──No──▶ Section E: Workload Issues
    │ Running?  │
    └───────────┘
          │Yes
          ▼
    Issue may be application-level
```

---

## Section A: Cluster Not Found

```
Cluster not found
      │
      ▼
┌─────────────────┐
│ Check namespace │
│ kubectl get     │
│ clusters -A     │
└─────────────────┘
      │
      ▼
  ┌─────────┐
  │ Found   │──Yes──▶ Wrong namespace, switch context
  │ in other│
  │ ns?     │
  └─────────┘
      │No
      ▼
┌─────────────────┐
│ Check API       │
│ kubectl api-    │
│ resources       │
└─────────────────┘
      │
      ▼
  ┌─────────┐
  │ CRDs    │──No──▶ CAPI not installed: clusterctl init
  │ exist?  │
  └─────────┘
      │Yes
      ▼
  Cluster was deleted or never created
  → Review apply command, check events
```

---

## Section B: Cluster Not Ready

```
Cluster exists but not Ready
          │
          ▼
┌─────────────────────────┐
│ Check conditions:       │
│ kubectl get cluster -o  │
│ yaml | grep -A20        │
│ conditions              │
└─────────────────────────┘
          │
          ▼
    ┌─────────────┐
    │Infrastructure│──False──▶ B1: Infrastructure Issue
    │Ready?        │
    └─────────────┘
          │True
          ▼
    ┌─────────────┐
    │ControlPlane │──False──▶ B2: Control Plane Issue
    │Ready?       │
    └─────────────┘
          │True
          ▼
    Check error message in condition reason
```

### B1: Infrastructure Issue

```
InfrastructureReady=False
          │
          ▼
┌─────────────────────────┐
│ Check infra cluster:    │
│ kubectl get <provider>  │
│ cluster -o yaml         │
└─────────────────────────┘
          │
          ▼
    ┌─────────┐
    │ Status  │──"Pending"──▶ Cloud credentials issue
    │ phase?  │
    └─────────┘
          │
    "Failed"│
          ▼
    ┌─────────────────────┐
    │ Check provider logs │
    │ kubectl logs -n     │
    │ <provider>-system   │
    └─────────────────────┘
          │
          ▼
Common causes:
• Invalid credentials (401/403)
• Quota exceeded
• Region/zone unavailable
• Network/VPC conflict
• Permission denied
```

---

## Section C: Control Plane Issues

```
Control plane not ready
          │
          ▼
┌─────────────────────────┐
│ kubectl get kcp         │
│ kubectl get machines    │
│   -l control-plane      │
└─────────────────────────┘
          │
          ▼
    ┌───────────┐
    │ KCP       │──No──▶ KCP creation failed
    │ exists?   │        Check events, provider logs
    └───────────┘
          │Yes
          ▼
    ┌───────────┐
    │ Machines  │
    │ count?    │
    └───────────┘
       │     │
    0 │     │ >0
       ▼     ▼
  C1: No    C2: Machines
  Machines  Not Ready
```

### C1: No Control Plane Machines

```
Machines count = 0
      │
      ▼
Check KCP events:
kubectl describe kcp <name>
      │
      ▼
Common causes:
• InfrastructureMachineTemplate not found
• Invalid machine template spec
• Provider quota exceeded
```

### C2: Machines Not Ready

```
Machines exist but not Ready
          │
          ▼
┌─────────────────────────┐
│ kubectl get machine     │
│ <name> -o yaml          │
└─────────────────────────┘
          │
          ▼
    ┌───────────┐
    │Bootstrap  │──False──▶ Bootstrap data not ready
    │Ready?     │           Check kubeadmconfig
    └───────────┘
          │True
          ▼
    ┌───────────┐
    │Infra      │──False──▶ VM not provisioned
    │Ready?     │           Check <provider>machine
    └───────────┘
          │True
          ▼
    ┌───────────┐
    │NodeRef    │──Empty──▶ Node not joined
    │ set?      │           Check kubeadm logs
    └───────────┘
```

---

## Section D: Worker Issues

```
Workers not ready
        │
        ▼
┌─────────────────────┐
│ kubectl get         │
│ machinedeployment   │
└─────────────────────┘
        │
        ▼
  ┌───────────┐
  │Replicas   │──Mismatch──▶ D1: Scaling issue
  │correct?   │
  └───────────┘
        │Match
        ▼
  ┌───────────┐
  │Machines   │──Not Ready──▶ D2: Machine issue
  │Ready?     │
  └───────────┘
        │Ready
        ▼
  Check workload cluster directly
```

### D1: Scaling Issue

```
Desired ≠ Current replicas
          │
          ▼
Check MachineSet:
kubectl get machineset
          │
          ▼
  ┌─────────────┐
  │MachineSet   │──Not Ready──▶ Template issue
  │Ready?       │
  └─────────────┘
          │
          ▼
  ┌─────────────┐
  │Machines     │──Pending──▶ Provider capacity
  │creating?    │
  └─────────────┘
          │
          ▼
Check MachineHealthCheck:
kubectl get mhc
→ May be deleting unhealthy machines
```

---

## Section E: Workload Issues

```
Workloads not running
        │
        ▼
┌─────────────────────┐
│ Get workload        │
│ kubeconfig:         │
│ clusterctl get      │
│ kubeconfig <name>   │
└─────────────────────┘
        │
        ▼
  ┌─────────────┐
  │Can connect  │──No──▶ API endpoint issue
  │to API?      │        Check load balancer/DNS
  └─────────────┘
        │Yes
        ▼
  ┌─────────────┐
  │Nodes        │──Not Ready──▶ CNI not installed
  │Ready?       │               or kubelet issue
  └─────────────┘
        │Ready
        ▼
  ┌─────────────┐
  │CoreDNS      │──Not Running──▶ Network/CNI issue
  │Running?     │
  └─────────────┘
        │Running
        ▼
  Application-level troubleshooting
```

---

## Quick Commands Reference

```bash
# Overall status
clusterctl describe cluster <name> --show-conditions all

# Check all resources
kubectl get clusters,machines,machinedeployments,kcp -A

# Provider logs
kubectl logs -n capi-system -l control-plane=controller-manager --tail=100
kubectl logs -n <provider>-system -l control-plane=controller-manager --tail=100

# Events
kubectl get events --sort-by='.lastTimestamp' -n <namespace>

# Machine details
kubectl describe machine <name>

# Bootstrap status
kubectl get kubeadmconfig -o wide

# Health checks triggering
kubectl get mhc -A -o wide
```

---

## Common Error Patterns

| Error Pattern         | Likely Cause       | Fix                          |
| --------------------- | ------------------ | ---------------------------- |
| `no matches for kind` | CRDs not installed | `clusterctl init`            |
| `connection refused`  | API not accessible | Check LB, security groups    |
| `unauthorized`        | Bad credentials    | Update provider secret       |
| `quota exceeded`      | Cloud limits       | Request quota increase       |
| `subnet not found`    | Network mismatch   | Check VPC/subnet config      |
| `timeout waiting`     | Slow provisioning  | Increase timeouts            |
| `bootstrap not ready` | Cloud-init failed  | Check machine serial console |
