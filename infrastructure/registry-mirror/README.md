# Registry Mirror Setup (Harbor)

This directory contains configuration for setting up Harbor as a registry mirror for air-gap image distribution.

## Prerequisites

- Harbor 2.10+ installed
- Network connectivity to all k3s nodes
- TLS certificates for Harbor

## Installation

### 1. Configure k3s Registry Mirrors

Add to `/etc/rancher/k3s/config.yaml` on all nodes:

```yaml
registry:
  mirrors:
    config:
      "harbor.internal.example.com":
        tls:
          insecure_skip_verify: false
          ca_bundle: /etc/rancher/k3s/certs/harbor-ca.crt
        endpoint:
          - https://harbor.internal.example.com
  config:
    "harbor.internal.example.com":
      auth: true
      username: deploy-user
      password: "your-password"
```

### 2. Argo CD Bootstrap

Argo CD will be configured to deploy from the Git repository.

## Image Promotion

1. Build multi-arch images:
```bash
docker buildx build --platform linux/amd64,linux/arm64 \
  --push harbor.internal.example.com/forge/app:latest \
  --provenance=false \
  ./path/to/image
```

2. Sign images:
```bash
cosign sign --key env://COSIGN_KEY harbor.internal.example.com/forge/app:latest
```

3. Scan images:
```bash
trivy image --exit-code 1 harbor.internal.example.com/forge/app:latest
```

## Verification

```bash
# Verify images can be pulled
kubectl run test --image=harbor.internal.example.com/forge/app:latest --dry-run=client -oyaml

# Check image pull secrets
kubectl get secret registry-auth -oyaml
```
