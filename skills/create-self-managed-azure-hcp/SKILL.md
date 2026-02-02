---
name: create-self-managed-azure-hcp
description: Automates the creation of a self-managed HyperShift (HCP) Azure cluster. This explicitly provisions a self-managed Azure cluster (using OCP control planes), NOT an AKS-managed HCP cluster. Use when users ask to create a self-managed HCP cluster on Azure.
---

# Create Self-Managed HCP Azure Cluster

## Overview

This skill guides the creation of a self-managed Azure HyperShift (HCP) hosted cluster based on the scripts available in `contrib/self-managed-azure/`. 
**Note:** This workflow is specifically for creating a self-managed HCP Azure cluster. It does **not** create or use an Azure Kubernetes Service (AKS) HCP cluster.

## Prerequisites Verification

Before executing the creation steps, ensure the workspace meets these requirements:
1. **Azure CLI (`az`)**: User must be logged in.
2. **`kubectl`** & **`jq`** & **`ccoctl`**: Must be installed and available in `PATH`.
3. **HyperShift Binary**: Must be compiled (run `make build` in the hypershift root if missing).
4. **Azure Credentials & Pull Secret**: Valid Azure credentials (e.g., `~/.azure/credentials`) and an OpenShift pull secret are required.

## Workflow: Cluster Creation

When asked to create a self-managed HCP Azure cluster, follow these steps:

### 1. Setup Configuration
1. Navigate to `contrib/self-managed-azure/` in the hypershift repository.
2. Update ${HYPERSHIFT_BINARY_PATH:-./bin} to {HYPERSHIFT_BINARY_PATH:-../../bin}" in file vars.sh
3. Copy `user-vars.sh.example` to `user-vars.sh` if it does not already exist.
4. Prompt the user for any required overrides in `user-vars.sh` (like `PREFIX`, `LOCATION`, `DNS_RECORD_NAME`, `RELEASE_IMAGE`).
5. Wait for the user to confirm the configuration.

### 2. First-Time Setup (Infrastructure & OIDC)
If the user indicates this is their first time deploying a self-managed HCP Azure cluster in their subscription (or if they are unsure):
- Ensure `ccoctl` is available in `PATH`.
- Execute `./setup_all.sh --first-time` to create the OIDC provider and the baseline Azure infrastructure for self-managed HCP.

### 3. Per-Cluster Deployment
To deploy the actual hosted cluster and install the operator:
- Execute `./setup_all.sh` (without the `--first-time` flag).
- This script will set up Azure External DNS, install the HyperShift Operator for self-managed Azure, and finally create the hosted cluster using `hypershift create cluster azure`.

### 4. Verification
1. Inform the user they can monitor cluster creation using:
   ```bash
   kubectl get hostedcluster <cluster-name> -n clusters
   ```
2. Once available, generate the kubeconfig:
   ```bash
   ./bin/hypershift create kubeconfig --name <cluster-name> --namespace clusters > cluster-kubeconfig
   ```
3. Test connectivity by running:
   ```bash
   KUBECONFIG=cluster-kubeconfig kubectl get nodes
   ```

## Troubleshooting
- If infrastructure setup fails, ensure the correct Azure subscription is active.
- Verify `ccoctl` is correctly downloaded and its location is defined in `user-vars.sh` or available in `PATH`.
