# S3-Compatible Storage Options

This document evaluates S3-compatible storage options for the Forge platform.

## Options

### 1. MinIO

**Pros:**
- Apache-2.0 license
- Multi-arch support
- Kubernetes-native (operator)
- S3 API compatible

**Cons:**
- Community edition AGPLv3 (verify before adoption)
- Distribution model changed in 2025

**Configuration:**
```yaml
apiVersion: minio.io/v2
kind: Tenant
metadata:
  name: forge-minio
  namespace: forge-data
spec:
  mode: distributed
  servers: 4
  volumesPerServer: 4
  storage:
    size: 1Ti
  identity:
    ldap:
      enabled: false
  credentials:
    secretKey: minio-secret-key
    rootUser: minioadmin
    rootPassword: minio-password
```

### 2. SeaweedFS

**Pros:**
- Apache-2.0 license
- Simple architecture
- Good performance

**Cons:**
- Less Kubernetes-native
- Smaller community

### 3. Ceph RGW

**Pros:**
- Apache-2.0 license
- Production-ready
- Large community

**Cons:**
- Complex setup
- Resource intensive

## Recommendation

**For MVP:** Use SeaweedFS (Apache-2.0, simple, multi-arch)

**For production scale:** Consider Ceph RGW or MinIO (verify licensing)

## Verification Checklist

- [ ] Multipart upload works
- [ ] Pre-signed URLs work
- [ ] Versioning works
- [ ] Encryption at rest works
- [ ] IAM policies work
- [ ] Cross-namespace access works
