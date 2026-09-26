# k3s HA Setup for DGX GB10

This directory contains configuration for installing k3s HA on NVIDIA DGX GB10 nodes.

## Prerequisites

- 3 DGX GB10 nodes (or more for production scale)
- DGX OS with cgroup v2 enabled
- Network connectivity between nodes
- SSH access to all nodes

## Installation

### Node Roles

| Node | Role |
|------|------|
| gb10-01 | k3s server |
| gb10-02 | k3s server |
| gb10-03 | k3s server |
| gb10-04+ | k3s agent |

### Steps

1. On first server node:
```bash
export INSTALL_K3S_VERSION=v1.31.4+k3s1
export K3S_TOKEN="your-secret-token"
export K3S_NODE_NAME="gb10-01"
export K3S_KUBELET_KUBECONFIG="/etc/rancher/k3s/kubeconfig"
export K3S_CLUSTER_SECRET="cluster-secret"

curl -sfL https://get.k3s.io | sh -s - server \
  --disable=traefik \
  --disable=local-storage \
  --flannel-backend=none \
  --cluster-init
```

2. On subsequent server nodes:
```bash
export INSTALL_K3S_VERSION=v1.31.4+k3s1
export K3S_TOKEN="your-secret-token"
export K3S_NODE_NAME="gb10-02"
export K3S_K3S_URL="https://gb10-01:6443"

curl -sfL https://get.k3s.io | sh -s - server \
  --disable=traefik \
  --disable=local-storage \
  --flannel-backend=none \
  --server https://gb10-01:6443
```

3. On agent nodes:
```bash
export INSTALL_K3S_VERSION=v1.31.4+k3s1
export K3S_TOKEN="your-secret-token"
export K3S_NODE_NAME="gb10-04"
export K3S_K3S_URL="https://gb10-01:6443"

curl -sfL https://get.k3s.io | sh -s - agent \
  --node-label "forge/role=batch"
```

## Verification

```bash
# Check all nodes are Ready
kubectl get nodes

# Verify cgroup v2
kubectl debug node/gb10-01 -it --image=busybox -- cat /sys/fs/cgroup/cgroup.controllers
```

## Troubleshooting

If cgroup v2 is not enabled:
```bash
# Add to GRUB_CMDLINE_LINUX in /etc/default/grub
systemd.unified_cgroup_hierarchy=1

# Update GRUB and reboot
update-grub
reboot
```
