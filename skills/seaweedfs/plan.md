# SeaweedFS Plan

Progress tracking for documentation ingestion.

## Base Information

- Skill name: `seaweedfs`
- Upstream repository: https://github.com/seaweedfs/seaweedfs
- Primary documentation entry: https://github.com/seaweedfs/seaweedfs/wiki/Getting-Started
- Upstream release tracked for frontmatter: `4.17` (`2026-03-11`)
- Goal: produce an operator-focused SeaweedFS skill with concise references and a short router `SKILL.md`
- Source constraints: use upstream repository and wiki only; skip low-value policy/legal pages
- Exclusions from queue: deprecated replication pages, changelog/policy/compliance pages that do not improve operator guidance

## Initialization

- [x] Visit the upstream repository root
- [x] Visit the Getting Started wiki page
- [x] Create `plan.md`
- [x] Create base `SKILL.md`
- [x] Create `references/`

## Queue

### Introduction

- [x] Getting Started
- [x] Quick Start with weed mini
- [x] Components
- [x] Production Setup
- [x] Benchmarks
- [x] FAQ
- [x] Applications

### API

- [x] Master Server API
- [x] Volume Server API
- [x] Filer Server API
- [x] Client Libraries
- [x] SeaweedFS Java Client

### Configuration

- [x] Replication
- [x] Store file with a Time To Live
- [x] Failover Master Server
- [x] Erasure Coding for warm storage
- [x] Server Startup via Systemd
- [x] Environment Variables

### Filer

- [x] Filer Setup
- [x] Directories and Files
- [x] File Operations Quick Reference
- [x] Data Structure for Large Files
- [x] Filer Data Encryption
- [x] Filer Commands and Operations
- [x] Filer JWT Use
- [x] TUS Resumable Uploads

### Filer Stores

- [x] Filer Stores
- [x] Filer Cassandra Setup
- [x] Filer Redis Setup
- [x] Super Large Directories
- [x] Path-Specific Filer Store
- [x] Choosing a Filer Store
- [x] Customize Filer Store

### Management

- [ ] Admin UI
- [ ] Worker
- [ ] Plugin Worker Scheduling

### Cloud Drive

- [x] Cloud Drive Benefits
- [ ] Cloud Drive Architecture
- [x] Configure Remote Storage
- [x] Mount Remote Storage
- [x] Cache Remote Storage
- [ ] Cloud Drive Quick Setup
- [ ] Gateway to Remote Object Storage

### AWS S3 API

- [x] Amazon S3 API
- [ ] Supported APIs vs Minio
- [ ] S3 Conditional Operations
- [ ] S3 CORS
- [ ] S3 Object Lock and Retention
- [ ] S3 Object Versioning
- [ ] S3 API Benchmark
- [ ] S3 API FAQ
- [ ] S3 Bucket Quota
- [ ] S3 Rate Limiting
- [ ] S3 API Audit log
- [ ] S3 Nginx Proxy
- [ ] Docker Compose for S3

### Advanced Filer Configurations

- [ ] Migrate to Filer Store
- [ ] Add New Filer Store
- [ ] Filer Store Replication
- [ ] Filer Active Active cross cluster continuous synchronization
- [ ] Filer as a Key-Large-Value Store
- [ ] Path Specific Configuration
- [ ] Filer Change Data Capture

### S3 Table Bucket

- [ ] S3 Table Bucket
- [ ] SeaweedFS Iceberg Catalog
- [ ] Iceberg Table Maintenance
- [ ] S3 Tables Security

### S3 Authentication & IAM

- [x] S3 Configuration
- [x] S3 Credentials
- [x] OIDC Integration
- [ ] S3 Policy Variables
- [ ] S3 Bucket Policies
- [ ] Amazon IAM API
- [ ] AWS IAM CLI

### Server-Side Encryption

- [x] Server-Side Encryption
- [x] Server-Side Encryption SSE-KMS
- [x] Server-Side Encryption SSE-C

### S3 Client Tools

- [x] AWS CLI with SeaweedFS
- [ ] s3cmd with SeaweedFS
- [x] rclone with SeaweedFS
- [x] restic with SeaweedFS
- [ ] nodejs with Seaweed S3

### Replication and Backup

- [x] Async Backup
- [x] Async Filer Metadata Backup
- [ ] Kubernetes Backups and Recovery with K8up

### Metadata Change Events

- [ ] Filer Metadata Events
- [ ] Filer Notification Webhook

### Messaging

- [ ] Structured Data Lake with SMQ and SQL
- [ ] Seaweed Message Queue
- [ ] SQL Queries on Message Queue
- [ ] SQL Quick Reference
- [ ] PostgreSQL-compatible Server weed db
- [ ] Pub-Sub to SMQ to SQL
- [ ] Kafka to Kafka Gateway to SMQ to SQL

### Use Cases

- [ ] Use Cases
- [ ] Actual Users

### Operations

- [x] System Metrics
- [x] weed shell
- [ ] Data Backup
- [ ] Deployment to Kubernetes and Minikube

### Advanced

- [ ] Large File Handling
- [ ] Optimization
- [ ] Optimization for Many Small Buckets
- [ ] Volume Management
- [ ] Tiered Storage
- [ ] Cloud Tier
- [ ] Cloud Monitoring
- [ ] Load Command Line Options from a file
- [ ] SRV Service Discovery
- [ ] Volume Files Structure

### Security

- [x] Security Overview
- [x] Security Configuration
- [ ] Cryptography and FIPS Compliance
- [ ] Run Blob Storage on Public Internet

### Misc Use Case Examples

- [ ] UrBackup with SeaweedFS
- [ ] Docker Image Registry with SeaweedFS
- [ ] SeaweedFS in Docker Swarm
- [ ] Words from SeaweedFS Users
- [ ] Independent Benchmarks
- [ ] Hardware

## Notes

- Deprecated pages intentionally skipped: `Async Replication to another Filer`, `Async Replication to Cloud`.
- Process rule: ingest exactly one queue page, update references immediately, mark it complete, then move on.
