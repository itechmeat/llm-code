# S3 Client Tools

Sources:

- https://github.com/seaweedfs/seaweedfs/wiki/AWS-CLI-with-SeaweedFS
- https://github.com/seaweedfs/seaweedfs/wiki/rclone-with-SeaweedFS
- https://github.com/seaweedfs/seaweedfs/wiki/restic-with-SeaweedFS

## AWS CLI with SeaweedFS

### What this page is about

- It documents how to use AWS CLI against the SeaweedFS S3 endpoint.
- It covers endpoint config, signature version, reverse-proxy caveats, presigned URLs, and encryption examples.

### Actionable takeaways

- Point AWS CLI at SeaweedFS with `--endpoint-url` and keep signature version on `s3v4`.
- Set a region and credentials even for local or test use, because the client expects them for request signing.
- Use presigned URLs when authenticated objects need temporary shareable access without exposing static credentials.
- Validate reverse-proxy subpath behavior carefully; the docs call it undefined relative to normal S3 domain conventions and require `X-Forwarded-Prefix` handling.
- Test SSE-S3, SSE-KMS, and SSE-C flows from the same CLI clients teams already use for AWS.

### Gotchas / prohibitions

- Do not rely on subpath-hosted S3 endpoints unless you have explicitly validated forwarded-prefix handling.
- Do not forget to force SigV4 when using AWS CLI with SeaweedFS.

### How to apply in a real repo

- Publish one standard AWS CLI profile or wrapper example for SeaweedFS endpoints.
- Include presign and encryption smoke tests in S3 compatibility validation.

## rclone with SeaweedFS

### What this page is about

- It shows rclone configuration against the SeaweedFS S3 endpoint, including path-style access and multipart tuning.
- It also includes an example of client-side encryption through an external KMS shim.

### Actionable takeaways

- Configure rclone as `provider = Other` with `force_path_style = true` against the SeaweedFS endpoint.
- Tune multipart thresholds such as `upload_cutoff` and `chunk_size` intentionally for your object sizes and network path.
- Use rclone for efficient bulk copy workflows where checksums and fast-listing behavior matter.
- Treat client-side encryption as separate from SeaweedFS SSE modes; the example uses an external KMS helper.

### Gotchas / prohibitions

- Do not assume reverse-proxy subpaths are standard S3 behavior; validate forwarded-prefix handling if you must use them.

## restic with SeaweedFS

### What this page is about

- It explains how to use SeaweedFS as an S3-compatible restic backend.
- It emphasizes that credentials are required even when the values are effectively arbitrary in a local setup.

### Actionable takeaways

- Provide `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in both SeaweedFS and restic environments, because restic expects non-anonymous S3 auth.
- Pre-create and authorize the target bucket before initializing a restic repository on SeaweedFS.
- Use SeaweedFS as a practical local or self-hosted S3 backend for restic repository storage.

### Gotchas / prohibitions

- Do not expect restic to work reliably against anonymous S3 access.
- Do not skip bucket creation and basic S3 auth setup before running `restic init`.

### How to apply in a real repo

- Publish tested rclone and restic examples alongside AWS CLI instructions so operators can use the tool that matches their backup workflow.
- Validate backup/restore or copy/list flows with real endpoint URLs, auth, and proxy layout.
