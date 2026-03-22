# Encryption

Sources:

- https://github.com/seaweedfs/seaweedfs/wiki/Server-Side-Encryption
- https://github.com/seaweedfs/seaweedfs/wiki/Server-Side-Encryption-SSE-KMS
- https://github.com/seaweedfs/seaweedfs/wiki/Server-Side-Encryption-SSE-C

## Server-Side Encryption

### What this page is about

- It introduces SeaweedFS S3-side encryption choices and positions SSE-S3 as the SeaweedFS-managed default-style option.

### Actionable takeaways

- Use SSE-S3 when you want SeaweedFS-managed encryption with low operational overhead.
- Expect SSE-S3 to work with explicit `AES256` upload headers and bucket default encryption behavior.

## SSE-KMS

### What this page is about

- It explains how SeaweedFS integrates with external key-management systems for S3 encryption.
- It covers AWS KMS, Google Cloud KMS, OpenBao/Vault, and experimental Azure Key Vault support.

### Actionable takeaways

- Use SSE-KMS when key ownership must stay in an external KMS rather than inside SeaweedFS.
- Put KMS provider configuration inside the S3 config JSON and choose a sensible default provider.
- Use bucket-to-provider mapping when different data classes need different KMS backends.
- Enable cache settings thoughtfully for Vault/OpenBao-style providers to balance latency and key-freshness needs.
- Keep KMS permissions minimal and document key rotation ownership.

### Gotchas / prohibitions

- Do not treat experimental Azure Key Vault support as equivalent to the fully supported providers.
- Do not mix KMS rollout with unclear IAM ownership; encryption and access control both live in the same S3 config surface.

## SSE-C

### What this page is about

- It explains customer-provided-key encryption where clients supply the AES-256 key on each request and SeaweedFS never stores it.

### Actionable takeaways

- Use SSE-C when clients must retain exclusive control of encryption keys while still using server-side encryption semantics.
- Expect clients to send the algorithm, base64 key, and key MD5 on upload and every subsequent encrypted-object read or copy.
- Test copy and re-encryption flows explicitly because source and destination keys may differ.
- Keep operational guidance clear that losing the client-side key means losing access to the object.

### Gotchas / prohibitions

- Do not expect SeaweedFS to recover or store SSE-C keys for you.
- Do not omit SSE-C headers when reading or copying an encrypted object.

### How to apply in a real repo

- Define approved encryption modes per workload: simple SSE-S3, externally governed SSE-KMS, or customer-controlled SSE-C.
- Keep KMS configuration, IAM policy, and bucket default encryption decisions in one operator-owned design document.
- Add encryption-mode interoperability tests for upload, download, copy, multipart, and range-request flows.
