# Security Audit Report Template

Cluster API Security Assessment Report

---

## Report Information

| Field        | Value |
| ------------ | ----- |
| Cluster Name |       |
| Namespace    |       |
| Audit Date   |       |
| Auditor      |       |
| CAPI Version |       |
| Provider     |       |

---

## Executive Summary

**Overall Security Posture**: [ ] Acceptable [ ] Needs Improvement [ ] Critical Issues

| Category           | Status | Findings |
| ------------------ | ------ | -------- |
| Pod Security       |        |          |
| Network Security   |        |          |
| Authentication     |        |          |
| Authorization      |        |          |
| Secrets Management |        |          |
| Audit Logging      |        |          |

**Critical Issues**:

**Recommendations**:

---

## 1. Pod Security Standards (PSS)

### 1.1 Configuration Check

| Setting           | Value | Recommended         | Status |
| ----------------- | ----- | ------------------- | ------ |
| PSS Enforcement   |       | baseline/restricted |        |
| PSS Audit Level   |       | restricted          |        |
| PSS Warn Level    |       | restricted          |        |
| Exempt Namespaces |       | kube-system only    |        |

### 1.2 Findings

Run: `python scripts/audit_security.py --cluster <name>`

```
# Paste output here
```

### 1.3 Recommendations

- [ ]
- [ ]
- [ ]

---

## 2. Control Plane Security

### 2.1 API Server Configuration

| Setting               | Current | Recommended                 | Status |
| --------------------- | ------- | --------------------------- | ------ |
| Authorization Mode    |         | RBAC,Node                   |        |
| Anonymous Auth        |         | false                       |        |
| Audit Logging         |         | enabled                     |        |
| Admission Controllers |         | NodeRestriction,PodSecurity |        |
| Encryption at Rest    |         | enabled                     |        |

### 2.2 etcd Security

| Setting          | Current | Recommended | Status |
| ---------------- | ------- | ----------- | ------ |
| Client Cert Auth |         | true        |        |
| Peer Cert Auth   |         | true        |        |
| Encryption       |         | enabled     |        |

### 2.3 Findings

```
# KubeadmControlPlane analysis output
```

### 2.4 Recommendations

- [ ]
- [ ]

---

## 3. Network Security

### 3.1 Cluster Network

| Setting          | Current | Recommended   | Status |
| ---------------- | ------- | ------------- | ------ |
| CNI Plugin       |         | Calico/Cilium |        |
| Network Policies |         | enabled       |        |
| Pod CIDR         |         |               |        |
| Service CIDR     |         |               |        |

### 3.2 External Access

| Endpoint   | Exposure | Protection | Status |
| ---------- | -------- | ---------- | ------ |
| API Server |          | LB + Auth  |        |
| Node Ports |          | Filtered   |        |
| Ingress    |          | TLS        |        |

### 3.3 Findings

-
-

### 3.4 Recommendations

- [ ]
- [ ]

---

## 4. Authentication & Authorization

### 4.1 Service Accounts

| Item                                | Status |
| ----------------------------------- | ------ |
| Default SA token automount disabled |        |
| Custom SAs for workloads            |        |
| SA token rotation                   |        |

### 4.2 RBAC

| Item                             | Status |
| -------------------------------- | ------ |
| cluster-admin usage minimized    |        |
| Namespace-scoped roles preferred |        |
| Role bindings reviewed           |        |

### 4.3 Findings

-
-

---

## 5. Secrets Management

### 5.1 Cluster Secrets

| Secret Type          | Count | Protection                 | Status |
| -------------------- | ----- | -------------------------- | ------ |
| kubeconfig           |       | Labeled, access controlled |        |
| CA certificates      |       | Rotated, backed up         |        |
| Bootstrap tokens     |       | Time-limited               |        |
| Provider credentials |       | Scoped, rotated            |        |

### 5.2 Secret Exposure Check

Run: `python scripts/audit_security.py --cluster <name> --output report.json`

### 5.3 Findings

-
-

---

## 6. Availability & Resilience

### 6.1 Control Plane HA

| Setting               | Current | Recommended    | Status |
| --------------------- | ------- | -------------- | ------ |
| CP Replicas           |         | 3 (odd number) |        |
| Multi-AZ distribution |         | yes            |        |
| etcd backup           |         | daily          |        |

### 6.2 Worker Availability

| Setting            | Current | Recommended | Status |
| ------------------ | ------- | ----------- | ------ |
| Worker count       |         | ≥3          |        |
| MachineHealthCheck |         | enabled     |        |
| maxUnhealthy       |         | 40%         |        |
| nodeStartupTimeout |         | 10m         |        |

### 6.3 Findings

-
-

---

## 7. Audit Logging

### 7.1 Kubernetes Audit

| Setting       | Current | Recommended      | Status |
| ------------- | ------- | ---------------- | ------ |
| Audit enabled |         | yes              |        |
| Audit policy  |         | metadata+request |        |
| Log retention |         | 30 days          |        |
| Log storage   |         | external/secure  |        |

### 7.2 CAPI Component Logging

| Component            | Log Level | Status |
| -------------------- | --------- | ------ |
| CAPI controller      |           |        |
| Provider controller  |           |        |
| Bootstrap controller |           |        |

---

## 8. Compliance Checklist

### CIS Kubernetes Benchmark

| Control                | Status | Notes |
| ---------------------- | ------ | ----- |
| 1.1 Control Plane      |        |       |
| 1.2 API Server         |        |       |
| 1.3 Controller Manager |        |       |
| 2.x Worker Nodes       |        |       |
| 3.x Network            |        |       |
| 4.x Policies           |        |       |
| 5.x Authentication     |        |       |

---

## 9. Risk Assessment

### Critical (Immediate Action Required)

| Finding | Risk | Remediation | Owner | Due |
| ------- | ---- | ----------- | ----- | --- |
|         |      |             |       |     |

### High

| Finding | Risk | Remediation | Owner | Due |
| ------- | ---- | ----------- | ----- | --- |
|         |      |             |       |     |

### Medium

| Finding | Risk | Remediation | Owner | Due |
| ------- | ---- | ----------- | ----- | --- |
|         |      |             |       |     |

### Low

| Finding | Risk | Remediation | Owner | Due |
| ------- | ---- | ----------- | ----- | --- |
|         |      |             |       |     |

---

## 10. Action Items

### Immediate (0-7 days)

- [ ]

### Short-term (1-4 weeks)

- [ ]

### Long-term (1-3 months)

- [ ]

---

## Appendix

### A. Commands Used

```bash
# List commands run during audit
clusterctl describe cluster <name>
python scripts/audit_security.py --cluster <name>
kubectl get psp  # if applicable
# ...
```

### B. Raw Outputs

<details>
<summary>clusterctl describe output</summary>

```
# paste here
```

</details>

<details>
<summary>Security audit script output</summary>

```
# paste here
```

</details>

### C. References

- [CAPI Security Guidelines](https://cluster-api.sigs.k8s.io/security/)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)

---

**Report Generated**: `date`

**Next Audit Due**:
